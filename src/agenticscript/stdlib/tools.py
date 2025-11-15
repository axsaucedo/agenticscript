"""Standard library tools for AgenticScript."""

from abc import ABC, abstractmethod
from typing import Any, List


class Tool(ABC):
    """Base class for all AgenticScript tools."""

    def __init__(self, name: str):
        self.name = name
        self.call_count = 0
        self.last_used = None

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass


class WebSearchTool(Tool):
    """Mock web search tool."""

    def __init__(self):
        super().__init__("WebSearch")

    def execute(self, query: str) -> str:
        """Mock web search execution."""
        self.call_count += 1
        import datetime
        self.last_used = datetime.datetime.now()

        # Mock response based on query
        return f"Mock search results for: {query}"


class FileManagerTool(Tool):
    """Mock file manager tool."""

    def __init__(self):
        super().__init__("FileManager")

    def execute(self, operation: str) -> str:
        """Mock file manager execution."""
        self.call_count += 1
        import datetime
        self.last_used = datetime.datetime.now()

        return f"Mock file operation: {operation}"


class CalculatorTool(Tool):
    """Mock calculator tool."""

    def __init__(self):
        super().__init__("Calculator")

    def execute(self, expression: str) -> str:
        """Mock calculator execution."""
        self.call_count += 1
        import datetime
        self.last_used = datetime.datetime.now()

        return f"Mock calculation result for: {expression}"


class AgentRoutingTool(Tool):
    """Agent routing tool for delegating to other agents."""

    def __init__(self, agents: List[str] = None):
        super().__init__("AgentRouting")
        self.agents = agents or []
        self._message_bus = None

    def _get_message_bus(self):
        """Lazy initialization of message bus."""
        if self._message_bus is None:
            try:
                from ..runtime.message_bus import message_bus
                self._message_bus = message_bus
            except ImportError:
                # Fallback if message bus not available
                self._message_bus = None
        return self._message_bus

    def execute(self, message: str, agent_name: str = None, sender: str = "system") -> str:
        """Route message to specified agent or first available."""
        self.call_count += 1
        import datetime
        self.last_used = datetime.datetime.now()

        # Determine target agent
        target = agent_name or (self.agents[0] if self.agents else None)

        if not target:
            return "Error: No target agent specified or available"

        # Try to route through message bus
        message_bus = self._get_message_bus()
        if message_bus:
            # Check if target agent is registered
            available_agents = message_bus.list_agents()

            # Find agent by name or ID
            target_agent_id = None
            for agent_id in available_agents:
                if target in agent_id or agent_id.startswith(f"{target}_"):
                    target_agent_id = agent_id
                    break

            if target_agent_id:
                # Send message through message bus
                message_id = message_bus.send_message(
                    sender=sender,
                    recipient=target_agent_id,
                    content=message,
                    message_type="routed_message"
                )

                if message_id:
                    return f"Message routed to agent '{target}' (ID: {target_agent_id}), message ID: {message_id}"
                else:
                    return f"Failed to route message to agent '{target}' - queue may be full"
            else:
                return f"Agent '{target}' not found in registered agents: {available_agents}"
        else:
            # Fallback to mock behavior
            return f"Mock routed '{message}' to agent: {target}"

    def add_agent(self, agent_name: str):
        """Add an agent to the routing list."""
        if agent_name not in self.agents:
            self.agents.append(agent_name)

    def remove_agent(self, agent_name: str):
        """Remove an agent from the routing list."""
        if agent_name in self.agents:
            self.agents.remove(agent_name)

    def list_agents(self) -> List[str]:
        """List available agents for routing."""
        return self.agents.copy()

    def get_registered_agents(self) -> List[str]:
        """Get list of agents registered with the message bus."""
        message_bus = self._get_message_bus()
        if message_bus:
            return message_bus.list_agents()
        return []


# Registry of available tools
AVAILABLE_TOOLS = {
    "WebSearch": WebSearchTool,
    "FileManager": FileManagerTool,
    "Calculator": CalculatorTool,
    "AgentRouting": AgentRoutingTool,
}