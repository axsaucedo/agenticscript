"""Tool registry system for AgenticScript runtime.

Manages tool discovery, registration, and execution with plugin pattern support.
"""

from typing import Dict, Any, List, Optional, Type, Set
from dataclasses import dataclass, field
from datetime import datetime
import threading
import inspect
from ..stdlib.tools import Tool, AVAILABLE_TOOLS


@dataclass
class ToolMetadata:
    """Metadata for registered tools."""
    name: str
    tool_class: Type[Tool]
    description: str = ""
    version: str = "1.0.0"
    author: str = "unknown"
    tags: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    enabled: bool = True


class ToolRegistry:
    """Central registry for managing tools in AgenticScript runtime."""

    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._instances: Dict[str, Tool] = {}
        self._lock = threading.RLock()
        self._plugins: Set[str] = set()

        # Auto-register stdlib tools on initialization
        self._register_stdlib_tools()

    def _register_stdlib_tools(self):
        """Register all tools from the standard library."""
        for name, tool_class in AVAILABLE_TOOLS.items():
            self.register_tool(
                name=name,
                tool_class=tool_class,
                description=f"Standard library {name} tool",
                tags=["stdlib", "builtin"]
            )

    def register_tool(
        self,
        name: str,
        tool_class: Type[Tool],
        description: str = "",
        version: str = "1.0.0",
        author: str = "unknown",
        tags: List[str] = None
    ) -> bool:
        """Register a tool class with the registry.

        Args:
            name: Tool name
            tool_class: Tool class (must inherit from Tool)
            description: Tool description
            version: Tool version
            author: Tool author
            tags: List of tags for categorization

        Returns:
            True if registration successful, False otherwise
        """
        with self._lock:
            # Validate tool class
            if not issubclass(tool_class, Tool):
                raise ValueError(f"Tool class {tool_class.__name__} must inherit from Tool")

            # Check for name conflicts
            if name in self._tools:
                return False

            # Create metadata
            metadata = ToolMetadata(
                name=name,
                tool_class=tool_class,
                description=description or f"{name} tool",
                version=version,
                author=author,
                tags=tags or []
            )

            self._tools[name] = metadata
            return True

    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool from the registry.

        Args:
            name: Tool name to unregister

        Returns:
            True if unregistration successful, False if tool not found
        """
        with self._lock:
            if name not in self._tools:
                return False

            # Remove tool and its instance
            del self._tools[name]
            if name in self._instances:
                del self._instances[name]

            return True

    def get_tool_instance(self, name: str) -> Optional[Tool]:
        """Get or create a tool instance.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if tool not found
        """
        with self._lock:
            if name not in self._tools:
                return None

            # Return existing instance or create new one
            if name not in self._instances:
                metadata = self._tools[name]
                if not metadata.enabled:
                    return None

                # Create tool instance based on constructor requirements
                tool_class = metadata.tool_class
                sig = inspect.signature(tool_class.__init__)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'

                if not params:
                    # No arguments needed
                    self._instances[name] = tool_class()
                elif len(params) == 1 and params[0] == 'agents':
                    # AgentRoutingTool needs agents list
                    self._instances[name] = tool_class([])
                else:
                    # Default construction
                    self._instances[name] = tool_class()

            return self._instances[name]

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name
            *args: Positional arguments for tool execution
            **kwargs: Keyword arguments for tool execution

        Returns:
            Tool execution result

        Raises:
            NameError: If tool not found
            Exception: Any exception from tool execution
        """
        tool_instance = self.get_tool_instance(name)
        if tool_instance is None:
            raise NameError(f"Tool '{name}' not found or disabled")

        # Update usage statistics
        with self._lock:
            if name in self._tools:
                self._tools[name].usage_count += 1
                self._tools[name].last_used = datetime.now()

        # Execute tool
        return tool_instance.execute(*args, **kwargs)

    def is_tool_available(self, name: str) -> bool:
        """Check if a tool is available for use.

        Args:
            name: Tool name

        Returns:
            True if tool is registered and enabled
        """
        with self._lock:
            return name in self._tools and self._tools[name].enabled

    def list_tools(self, tags: List[str] = None, enabled_only: bool = True) -> List[str]:
        """List available tools.

        Args:
            tags: Filter by tags (optional)
            enabled_only: Only return enabled tools

        Returns:
            List of tool names
        """
        with self._lock:
            tools = []
            for name, metadata in self._tools.items():
                # Filter by enabled status
                if enabled_only and not metadata.enabled:
                    continue

                # Filter by tags
                if tags and not any(tag in metadata.tags for tag in tags):
                    continue

                tools.append(name)

            return sorted(tools)

    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool.

        Args:
            name: Tool name

        Returns:
            ToolMetadata or None if tool not found
        """
        with self._lock:
            return self._tools.get(name)

    def get_tool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all tools.

        Returns:
            Dictionary of tool statistics
        """
        with self._lock:
            stats = {}
            for name, metadata in self._tools.items():
                stats[name] = {
                    "usage_count": metadata.usage_count,
                    "last_used": metadata.last_used.isoformat() if metadata.last_used else None,
                    "enabled": metadata.enabled,
                    "tags": metadata.tags,
                    "version": metadata.version
                }
            return stats

    def enable_tool(self, name: str) -> bool:
        """Enable a tool for use.

        Args:
            name: Tool name

        Returns:
            True if successful, False if tool not found
        """
        with self._lock:
            if name not in self._tools:
                return False
            self._tools[name].enabled = True
            return True

    def disable_tool(self, name: str) -> bool:
        """Disable a tool from use.

        Args:
            name: Tool name

        Returns:
            True if successful, False if tool not found
        """
        with self._lock:
            if name not in self._tools:
                return False
            self._tools[name].enabled = False
            # Remove instance to prevent further use
            if name in self._instances:
                del self._instances[name]
            return True

    def register_plugin(self, plugin_name: str, tools: Dict[str, Type[Tool]]) -> List[str]:
        """Register tools from a plugin.

        Args:
            plugin_name: Name of the plugin
            tools: Dictionary of tool name -> tool class mappings

        Returns:
            List of successfully registered tool names
        """
        registered = []

        for name, tool_class in tools.items():
            success = self.register_tool(
                name=name,
                tool_class=tool_class,
                description=f"{name} from {plugin_name} plugin",
                author=plugin_name,
                tags=["plugin", plugin_name]
            )
            if success:
                registered.append(name)

        if registered:
            self._plugins.add(plugin_name)

        return registered

    def unregister_plugin(self, plugin_name: str) -> List[str]:
        """Unregister all tools from a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            List of unregistered tool names
        """
        unregistered = []

        # Find all tools from this plugin
        with self._lock:
            plugin_tools = [
                name for name, metadata in self._tools.items()
                if plugin_name in metadata.tags
            ]

        # Unregister each tool
        for name in plugin_tools:
            if self.unregister_tool(name):
                unregistered.append(name)

        if plugin_name in self._plugins:
            self._plugins.remove(plugin_name)

        return unregistered

    def list_plugins(self) -> List[str]:
        """List all registered plugins.

        Returns:
            List of plugin names
        """
        return sorted(list(self._plugins))

    def clear_registry(self):
        """Clear all registered tools (useful for testing)."""
        with self._lock:
            self._tools.clear()
            self._instances.clear()
            self._plugins.clear()


# Global tool registry instance
tool_registry = ToolRegistry()