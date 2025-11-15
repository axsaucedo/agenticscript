"""Tests for the AgenticScript message bus system."""

import sys
import os
import time
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.runtime.message_bus import MessageBus, Message, MessagePriority, MessageStatus


def test_message_bus_initialization():
    """Test message bus initialization."""
    bus = MessageBus(max_queue_size=500)
    assert bus.max_queue_size == 500
    assert len(bus.list_agents()) == 0

    stats = bus.get_statistics()
    assert stats.total_sent == 0
    assert stats.total_delivered == 0
    assert stats.active_subscriptions == 0


def test_agent_registration():
    """Test agent registration and unregistration."""
    bus = MessageBus()

    # Register agents
    assert bus.register_agent("agent1")
    assert bus.register_agent("agent2")

    # Check agents are listed
    agents = bus.list_agents()
    assert "agent1" in agents
    assert "agent2" in agents
    assert len(agents) == 2

    # Try to register same agent again
    assert not bus.register_agent("agent1")

    # Unregister agent
    assert bus.unregister_agent("agent1")
    assert "agent1" not in bus.list_agents()
    assert len(bus.list_agents()) == 1

    # Try to unregister non-existent agent
    assert not bus.unregister_agent("nonexistent")


def test_basic_message_sending():
    """Test basic message sending and receiving."""
    bus = MessageBus()
    bus.register_agent("sender")
    bus.register_agent("receiver")

    # Send message
    message_id = bus.send_message("sender", "receiver", "Hello World!")
    assert message_id is not None
    assert message_id.startswith("msg_")

    # Check pending count
    assert bus.get_pending_count("receiver") == 1
    assert bus.get_pending_count("sender") == 0

    # Receive message
    message = bus.receive_message("receiver")
    assert message is not None
    assert message.sender == "sender"
    assert message.recipient == "receiver"
    assert message.content == "Hello World!"
    assert message.status == MessageStatus.DELIVERED
    assert message.delivered_at is not None

    # No more messages
    assert bus.get_pending_count("receiver") == 0
    message2 = bus.receive_message("receiver")
    assert message2 is None


def test_message_priorities():
    """Test message priority handling."""
    bus = MessageBus()
    bus.register_agent("sender")
    bus.register_agent("receiver")

    # Send messages with different priorities
    low_id = bus.send_message("sender", "receiver", "Low priority", priority=MessagePriority.LOW)
    urgent_id = bus.send_message("sender", "receiver", "Urgent!", priority=MessagePriority.URGENT)
    normal_id = bus.send_message("sender", "receiver", "Normal", priority=MessagePriority.NORMAL)

    assert low_id is not None
    assert urgent_id is not None
    assert normal_id is not None

    # Messages should be received in priority order (urgent first)
    msg1 = bus.receive_message("receiver")
    msg2 = bus.receive_message("receiver")
    msg3 = bus.receive_message("receiver")

    assert msg1.content == "Urgent!"
    assert msg2.content == "Normal"
    assert msg3.content == "Low priority"


def test_message_to_nonexistent_agent():
    """Test sending message to non-existent agent."""
    bus = MessageBus()
    bus.register_agent("sender")

    # Try to send to non-existent agent
    message_id = bus.send_message("sender", "nonexistent", "Hello")
    assert message_id is None


def test_receive_from_nonexistent_agent():
    """Test receiving message for non-existent agent."""
    bus = MessageBus()

    message = bus.receive_message("nonexistent")
    assert message is None

    count = bus.get_pending_count("nonexistent")
    assert count == -1


def test_message_timeout():
    """Test message timeout functionality."""
    bus = MessageBus()
    bus.start()  # Start worker thread for timeout processing

    try:
        bus.register_agent("sender")
        bus.register_agent("receiver")

        # Send message with short timeout
        message_id = bus.send_message(
            "sender", "receiver", "Timeout test",
            timeout=0.1  # 100ms timeout
        )
        assert message_id is not None

        # Wait for timeout to occur
        time.sleep(0.2)

        # Check message history for timeout status
        history = bus.get_message_history()
        timeout_message = next((msg for msg in history if msg.id == message_id), None)
        assert timeout_message is not None
        assert timeout_message.status == MessageStatus.TIMEOUT

    finally:
        bus.stop()


def test_broadcast_message():
    """Test broadcast messaging."""
    bus = MessageBus()
    bus.register_agent("broadcaster")
    bus.register_agent("agent1")
    bus.register_agent("agent2")
    bus.register_agent("agent3")

    # Broadcast to all agents
    message_ids = bus.broadcast_message("broadcaster", "Broadcast message!")
    assert len(message_ids) == 3  # Excludes broadcaster

    # Check all agents received the message
    for agent in ["agent1", "agent2", "agent3"]:
        assert bus.get_pending_count(agent) == 1
        message = bus.receive_message(agent)
        assert message.content == "Broadcast message!"
        assert message.message_type == "broadcast"

    # Broadcast with exclusions
    message_ids = bus.broadcast_message(
        "broadcaster", "Selective broadcast",
        exclude=["agent2"]
    )
    assert len(message_ids) == 2  # Excludes broadcaster and agent2

    assert bus.get_pending_count("agent1") == 1
    assert bus.get_pending_count("agent2") == 0
    assert bus.get_pending_count("agent3") == 1


def test_message_subscription():
    """Test message subscription system."""
    bus = MessageBus()
    bus.register_agent("sender")
    bus.register_agent("subscriber")

    received_messages = []

    def message_callback(message):
        received_messages.append(message)

    # Subscribe to messages
    assert bus.subscribe_to_messages("subscriber", message_callback)

    # Check subscription count
    stats = bus.get_statistics()
    assert stats.active_subscriptions == 1

    # Send message (callback won't be triggered in this simplified implementation)
    bus.send_message("sender", "subscriber", "Test subscription")

    # Unsubscribe
    assert bus.unsubscribe_from_messages("subscriber", message_callback)
    stats = bus.get_statistics()
    assert stats.active_subscriptions == 0

    # Try to subscribe to non-existent agent
    assert not bus.subscribe_to_messages("nonexistent", message_callback)


def test_message_history():
    """Test message history functionality."""
    bus = MessageBus()
    bus.register_agent("agent1")
    bus.register_agent("agent2")

    # Send some messages
    bus.send_message("agent1", "agent2", "Message 1")
    bus.send_message("agent2", "agent1", "Message 2")
    bus.send_message("agent1", "agent2", "Message 3")

    # Check global history
    history = bus.get_message_history()
    assert len(history) == 3
    assert history[0].content == "Message 1"
    assert history[2].content == "Message 3"

    # Check agent-specific history
    agent1_history = bus.get_agent_message_history("agent1")
    assert len(agent1_history) == 3  # agent1 involved in all messages

    agent2_history = bus.get_agent_message_history("agent2")
    assert len(agent2_history) == 3  # agent2 also involved in all messages

    # Test history limits
    limited_history = bus.get_message_history(limit=2)
    assert len(limited_history) == 2
    assert limited_history[1].content == "Message 3"


def test_message_statistics():
    """Test message statistics tracking."""
    bus = MessageBus()
    bus.register_agent("agent1")
    bus.register_agent("agent2")

    # Send and receive messages
    bus.send_message("agent1", "agent2", "Test 1")
    bus.send_message("agent1", "agent2", "Test 2")

    stats = bus.get_statistics()
    assert stats.total_sent == 2
    assert stats.total_delivered == 0  # Not received yet

    # Receive messages
    bus.receive_message("agent2")
    bus.receive_message("agent2")

    stats = bus.get_statistics()
    assert stats.total_sent == 2
    assert stats.total_delivered == 2
    assert stats.average_delivery_time >= 0


def test_message_metadata():
    """Test message metadata functionality."""
    bus = MessageBus()
    bus.register_agent("sender")
    bus.register_agent("receiver")

    metadata = {
        "conversation_id": "conv_123",
        "priority_reason": "urgent_task",
        "custom_field": "test_value"
    }

    message_id = bus.send_message(
        "sender", "receiver", "Test with metadata",
        message_type="task",
        metadata=metadata,
        response_to="previous_msg_id"
    )

    message = bus.receive_message("receiver")
    assert message.message_type == "task"
    assert message.metadata["conversation_id"] == "conv_123"
    assert message.metadata["custom_field"] == "test_value"
    assert message.response_to == "previous_msg_id"


def test_receive_with_timeout():
    """Test receiving messages with timeout."""
    bus = MessageBus()
    bus.register_agent("receiver")

    # Try to receive with timeout when no messages
    start_time = time.time()
    message = bus.receive_message("receiver", timeout=0.1)
    elapsed = time.time() - start_time

    assert message is None
    assert elapsed >= 0.1  # Should wait at least the timeout period


def test_queue_size_limit():
    """Test queue size limits."""
    bus = MessageBus(max_queue_size=2)  # Very small queue
    bus.register_agent("sender")
    bus.register_agent("receiver")

    # Fill the queue
    id1 = bus.send_message("sender", "receiver", "Message 1")
    id2 = bus.send_message("sender", "receiver", "Message 2")

    assert id1 is not None
    assert id2 is not None

    # Queue should be full now, next message should fail
    id3 = bus.send_message("sender", "receiver", "Message 3")
    assert id3 is None  # Should fail due to full queue


def test_clear_history():
    """Test clearing message history."""
    bus = MessageBus()
    bus.register_agent("agent1")
    bus.register_agent("agent2")

    # Send some messages
    bus.send_message("agent1", "agent2", "Test message")
    bus.receive_message("agent2")

    # Check history exists
    history = bus.get_message_history()
    assert len(history) > 0

    stats = bus.get_statistics()
    assert stats.total_sent > 0

    # Clear history
    bus.clear_history()

    # Check history is cleared
    history = bus.get_message_history()
    assert len(history) == 0

    stats = bus.get_statistics()
    assert stats.total_sent == 0
    assert stats.total_delivered == 0


if __name__ == "__main__":
    test_message_bus_initialization()
    print("✓ Message bus initialization works")

    test_agent_registration()
    print("✓ Agent registration works")

    test_basic_message_sending()
    print("✓ Basic message sending works")

    test_message_priorities()
    print("✓ Message priorities work")

    test_message_to_nonexistent_agent()
    print("✓ Nonexistent agent handling works")

    test_receive_from_nonexistent_agent()
    print("✓ Receive from nonexistent agent works")

    test_message_timeout()
    print("✓ Message timeout works")

    test_broadcast_message()
    print("✓ Broadcast messaging works")

    test_message_subscription()
    print("✓ Message subscription works")

    test_message_history()
    print("✓ Message history works")

    test_message_statistics()
    print("✓ Message statistics work")

    test_message_metadata()
    print("✓ Message metadata works")

    test_receive_with_timeout()
    print("✓ Receive with timeout works")

    test_queue_size_limit()
    print("✓ Queue size limits work")

    test_clear_history()
    print("✓ Clear history works")

    print("All message bus tests passed!")