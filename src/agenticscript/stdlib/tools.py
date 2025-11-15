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

    def __init__(self, agents: List[str]):
        super().__init__("AgentRouting")
        self.agents = agents

    def execute(self, message: str, agent_name: str = None) -> str:
        """Route message to specified agent or first available."""
        self.call_count += 1
        import datetime
        self.last_used = datetime.datetime.now()

        target = agent_name or self.agents[0] if self.agents else "unknown"
        return f"Routed '{message}' to agent: {target}"


# Registry of available tools
AVAILABLE_TOOLS = {
    "WebSearch": WebSearchTool,
    "FileManager": FileManagerTool,
    "Calculator": CalculatorTool,
    "AgentRouting": AgentRoutingTool,
}