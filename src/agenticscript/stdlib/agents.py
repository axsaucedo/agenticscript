"""Standard library agent types for AgenticScript."""

from typing import List, Dict, Any, Optional


class SupervisorAgent:
    """Agent that supervises and manages other agents."""

    def __init__(self, name: str, children: List[str], restart_policy: str = "one_for_one"):
        self.name = name
        self.children = children
        self.restart_policy = restart_policy
        self.status = "idle"
        self.properties = {}
        self.tools = []

    def add_child(self, agent_name: str):
        """Add a child agent to supervision."""
        if agent_name not in self.children:
            self.children.append(agent_name)

    def remove_child(self, agent_name: str):
        """Remove a child agent from supervision."""
        if agent_name in self.children:
            self.children.remove(agent_name)

    def restart_agent(self, agent_name: str):
        """Mock restart of a child agent."""
        if agent_name in self.children:
            return f"Restarted agent: {agent_name}"
        else:
            return f"Agent {agent_name} is not under supervision"

    def broadcast_to_children(self, message: str):
        """Send message to all child agents."""
        return f"Broadcast to {len(self.children)} children: {message}"

    def get_property(self, name: str) -> Any:
        """Get agent property."""
        if name == "status":
            return self.status
        elif name == "name":
            return self.name
        elif name == "children":
            return self.children
        elif name == "restart_policy":
            return self.restart_policy
        else:
            return self.properties.get(name)

    def set_property(self, name: str, value: Any):
        """Set agent property."""
        if name in ("status", "name", "children", "restart_policy"):
            setattr(self, name, value)
        else:
            self.properties[name] = value

    def __str__(self):
        return f"SupervisorAgent({self.name}, children={len(self.children)})"

    def __repr__(self):
        return f'SupervisorAgent(name="{self.name}", children={self.children})'


# Registry of available agent types
AVAILABLE_AGENTS = {
    "SupervisorAgent": SupervisorAgent,
}