"""Message bus system for AgenticScript inter-agent communication.

Provides centralized message routing, delivery, and management for agent systems.
"""

import queue
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageStatus(Enum):
    """Message delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Message:
    """Represents a message in the system."""
    id: str
    sender: str
    recipient: str
    content: str
    message_type: str = "general"
    priority: MessagePriority = MessagePriority.NORMAL
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    status: MessageStatus = MessageStatus.PENDING
    response_to: Optional[str] = None  # For reply messages
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """For priority queue comparison."""
        # Higher priority values should come first (lower in queue)
        return self.priority.value > other.priority.value


@dataclass
class MessageStats:
    """Message bus statistics."""
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    total_timeout: int = 0
    average_delivery_time: float = 0.0
    active_subscriptions: int = 0


class MessageBus:
    """Central message bus for inter-agent communication."""

    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self._queues: Dict[str, queue.PriorityQueue] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_history: List[Message] = []
        self._stats = MessageStats()
        self._lock = threading.RLock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._message_counter = 0
        self._delivery_times: List[float] = []

    def start(self):
        """Start the message bus worker thread."""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()

    def stop(self):
        """Stop the message bus worker thread."""
        with self._lock:
            self._running = False
            if self._worker_thread and self._worker_thread.is_alive():
                self._worker_thread.join(timeout=1.0)

    def register_agent(self, agent_id: str) -> bool:
        """Register an agent with the message bus.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            True if registration successful, False if agent already registered
        """
        with self._lock:
            if agent_id in self._queues:
                return False

            self._queues[agent_id] = queue.PriorityQueue(maxsize=self.max_queue_size)
            self._subscribers[agent_id] = []
            return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the message bus.

        Args:
            agent_id: Agent identifier

        Returns:
            True if unregistration successful, False if agent not found
        """
        with self._lock:
            if agent_id not in self._queues:
                return False

            # Clear the queue
            while not self._queues[agent_id].empty():
                try:
                    self._queues[agent_id].get_nowait()
                except queue.Empty:
                    break

            del self._queues[agent_id]
            del self._subscribers[agent_id]
            return True

    def send_message(
        self,
        sender: str,
        recipient: str,
        content: str,
        message_type: str = "general",
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout: Optional[float] = None,
        response_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Send a message from one agent to another.

        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            content: Message content
            message_type: Type of message
            priority: Message priority
            timeout: Optional timeout in seconds
            response_to: ID of message this is responding to
            metadata: Additional message metadata

        Returns:
            Message ID if sent successfully, None otherwise
        """
        with self._lock:
            # Check if recipient exists
            if recipient not in self._queues:
                return None

            # Generate message ID
            self._message_counter += 1
            message_id = f"msg_{self._message_counter:06d}"

            # Create message
            message = Message(
                id=message_id,
                sender=sender,
                recipient=recipient,
                content=content,
                message_type=message_type,
                priority=priority,
                timeout=timeout,
                response_to=response_to,
                metadata=metadata or {}
            )

            # Add to recipient's queue
            try:
                self._queues[recipient].put_nowait(message)
                self._message_history.append(message)
                self._stats.total_sent += 1
                return message_id
            except queue.Full:
                return None

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Receive a message for an agent.

        Args:
            agent_id: Agent identifier
            timeout: Optional timeout in seconds

        Returns:
            Message if available, None if no messages or timeout
        """
        with self._lock:
            if agent_id not in self._queues:
                return None

            agent_queue = self._queues[agent_id]

        try:
            if timeout is not None:
                message = agent_queue.get(timeout=timeout)
            else:
                message = agent_queue.get_nowait()

            # Update delivery status
            message.delivered_at = datetime.now()
            message.status = MessageStatus.DELIVERED

            # Update statistics
            with self._lock:
                self._stats.total_delivered += 1
                delivery_time = (message.delivered_at - message.created_at).total_seconds()
                self._delivery_times.append(delivery_time)

                # Keep only last 100 delivery times for average calculation
                if len(self._delivery_times) > 100:
                    self._delivery_times = self._delivery_times[-100:]

                self._stats.average_delivery_time = sum(self._delivery_times) / len(self._delivery_times)

            return message

        except queue.Empty:
            return None

    def get_pending_count(self, agent_id: str) -> int:
        """Get the number of pending messages for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of pending messages, -1 if agent not found
        """
        with self._lock:
            if agent_id not in self._queues:
                return -1
            return self._queues[agent_id].qsize()

    def broadcast_message(
        self,
        sender: str,
        content: str,
        message_type: str = "broadcast",
        priority: MessagePriority = MessagePriority.NORMAL,
        exclude: Optional[List[str]] = None
    ) -> List[str]:
        """Broadcast a message to all registered agents.

        Args:
            sender: Sender agent ID
            content: Message content
            message_type: Type of message
            priority: Message priority
            exclude: List of agent IDs to exclude from broadcast

        Returns:
            List of message IDs for successfully sent messages
        """
        exclude = exclude or []
        message_ids = []

        with self._lock:
            recipients = [agent_id for agent_id in self._queues.keys()
                         if agent_id != sender and agent_id not in exclude]

        for recipient in recipients:
            message_id = self.send_message(
                sender=sender,
                recipient=recipient,
                content=content,
                message_type=message_type,
                priority=priority
            )
            if message_id:
                message_ids.append(message_id)

        return message_ids

    def subscribe_to_messages(self, agent_id: str, callback: Callable[[Message], None]) -> bool:
        """Subscribe to messages for an agent with a callback.

        Args:
            agent_id: Agent identifier
            callback: Function to call when message is received

        Returns:
            True if subscription successful, False if agent not found
        """
        with self._lock:
            if agent_id not in self._subscribers:
                return False

            self._subscribers[agent_id].append(callback)
            self._stats.active_subscriptions = sum(len(subs) for subs in self._subscribers.values())
            return True

    def unsubscribe_from_messages(self, agent_id: str, callback: Callable[[Message], None]) -> bool:
        """Unsubscribe from messages for an agent.

        Args:
            agent_id: Agent identifier
            callback: Callback function to remove

        Returns:
            True if unsubscription successful, False if not found
        """
        with self._lock:
            if agent_id not in self._subscribers:
                return False

            try:
                self._subscribers[agent_id].remove(callback)
                self._stats.active_subscriptions = sum(len(subs) for subs in self._subscribers.values())
                return True
            except ValueError:
                return False

    def get_message_history(self, limit: int = 100) -> List[Message]:
        """Get recent message history.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of recent messages
        """
        with self._lock:
            return self._message_history[-limit:] if limit > 0 else self._message_history.copy()

    def get_agent_message_history(self, agent_id: str, limit: int = 50) -> List[Message]:
        """Get message history for a specific agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of messages to return

        Returns:
            List of messages involving the agent
        """
        with self._lock:
            agent_messages = [
                msg for msg in self._message_history
                if msg.sender == agent_id or msg.recipient == agent_id
            ]
            return agent_messages[-limit:] if limit > 0 else agent_messages

    def get_statistics(self) -> MessageStats:
        """Get message bus statistics.

        Returns:
            Current statistics
        """
        with self._lock:
            return MessageStats(
                total_sent=self._stats.total_sent,
                total_delivered=self._stats.total_delivered,
                total_failed=self._stats.total_failed,
                total_timeout=self._stats.total_timeout,
                average_delivery_time=self._stats.average_delivery_time,
                active_subscriptions=self._stats.active_subscriptions
            )

    def list_agents(self) -> List[str]:
        """List all registered agents.

        Returns:
            List of agent IDs
        """
        with self._lock:
            return list(self._queues.keys())

    def clear_history(self):
        """Clear message history (useful for testing)."""
        with self._lock:
            self._message_history.clear()
            self._delivery_times.clear()
            self._stats = MessageStats()

    def _worker_loop(self):
        """Background worker loop for handling timeouts and subscriptions."""
        while self._running:
            try:
                self._process_timeouts()
                self._notify_subscribers()
                time.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception:
                # Continue running even if there are errors
                pass

    def _process_timeouts(self):
        """Process message timeouts."""
        current_time = datetime.now()
        with self._lock:
            for message in self._message_history:
                if (message.status == MessageStatus.PENDING and
                    message.timeout is not None and
                    (current_time - message.created_at).total_seconds() > message.timeout):

                    message.status = MessageStatus.TIMEOUT
                    self._stats.total_timeout += 1

    def _notify_subscribers(self):
        """Notify subscribers of new messages."""
        # This is a simplified implementation
        # In a full implementation, this would check for new messages
        # and notify callbacks for each agent
        pass


# Global message bus instance
message_bus = MessageBus()