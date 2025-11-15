"""Module system for AgenticScript import resolution."""

from typing import Dict, Any, List
from ..stdlib import STDLIB_MODULES, resolve_import
from ..stdlib.tools import AVAILABLE_TOOLS
from ..stdlib.agents import AVAILABLE_AGENTS


class ModuleSystem:
    """Handles module imports and resolution for AgenticScript."""

    def __init__(self):
        self.imported_modules: Dict[str, Dict[str, Any]] = {}
        self.available_tools: Dict[str, Any] = {}
        self.available_agents: Dict[str, Any] = {}

    def import_module(self, module_path: List[str], imports: List[str]) -> Dict[str, Any]:
        """Import specified items from a module."""
        module_path_str = ".".join(module_path)
        imported_items = {}

        for import_name in imports:
            try:
                # Resolve the import
                class_path = resolve_import(module_path_str, import_name)

                # Load the appropriate class
                if "tools" in module_path_str:
                    if import_name in AVAILABLE_TOOLS:
                        imported_items[import_name] = AVAILABLE_TOOLS[import_name]
                        self.available_tools[import_name] = AVAILABLE_TOOLS[import_name]
                elif "agents" in module_path_str:
                    if import_name in AVAILABLE_AGENTS:
                        imported_items[import_name] = AVAILABLE_AGENTS[import_name]
                        self.available_agents[import_name] = AVAILABLE_AGENTS[import_name]
                else:
                    raise ImportError(f"Unknown module type: {module_path_str}")

            except ImportError as e:
                raise ImportError(f"Cannot import {import_name} from {module_path_str}: {e}")

        # Store imported module
        self.imported_modules[module_path_str] = imported_items

        return imported_items

    def get_tool_class(self, tool_name: str):
        """Get a tool class by name."""
        if tool_name in self.available_tools:
            return self.available_tools[tool_name]
        else:
            raise NameError(f"Tool '{tool_name}' not found. Did you import it?")

    def get_agent_class(self, agent_name: str):
        """Get an agent class by name."""
        if agent_name in self.available_agents:
            return self.available_agents[agent_name]
        else:
            raise NameError(f"Agent type '{agent_name}' not found. Did you import it?")

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available."""
        return tool_name in self.available_tools

    def is_agent_available(self, agent_name: str) -> bool:
        """Check if an agent type is available."""
        return agent_name in self.available_agents

    def list_imported_modules(self) -> List[str]:
        """List all imported modules."""
        return list(self.imported_modules.keys())

    def list_available_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.available_tools.keys())

    def list_available_agents(self) -> List[str]:
        """List all available agent types."""
        return list(self.available_agents.keys())

    def clear_imports(self):
        """Clear all imports (useful for testing)."""
        self.imported_modules.clear()
        self.available_tools.clear()
        self.available_agents.clear()


# Global module system instance
module_system = ModuleSystem()