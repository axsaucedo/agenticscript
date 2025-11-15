"""Tests for the AgenticScript tool registry system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime
from agenticscript.runtime.tool_registry import ToolRegistry, ToolMetadata
from agenticscript.stdlib.tools import Tool, WebSearchTool, AgentRoutingTool


class MockTool(Tool):
    """Mock tool for testing."""

    def __init__(self):
        super().__init__("MockTool")

    def execute(self, data: str) -> str:
        self.call_count += 1
        return f"Mock processed: {data}"


class PluginTool(Tool):
    """Plugin tool for testing."""

    def __init__(self):
        super().__init__("PluginTool")

    def execute(self, query: str) -> str:
        self.call_count += 1
        return f"Plugin result: {query}"


def test_registry_initialization():
    """Test that registry initializes with stdlib tools."""
    registry = ToolRegistry()

    # Check that stdlib tools are auto-registered
    tools = registry.list_tools()
    assert "WebSearch" in tools
    assert "AgentRouting" in tools
    assert "FileManager" in tools
    assert "Calculator" in tools

    # Check tool availability
    assert registry.is_tool_available("WebSearch")
    assert registry.is_tool_available("AgentRouting")


def test_tool_registration():
    """Test tool registration functionality."""
    registry = ToolRegistry()
    registry.clear_registry()  # Start fresh

    # Register a tool
    success = registry.register_tool(
        name="TestTool",
        tool_class=MockTool,
        description="Test tool",
        version="2.0.0",
        author="test_author",
        tags=["test", "mock"]
    )
    assert success

    # Check tool is registered
    assert registry.is_tool_available("TestTool")
    tools = registry.list_tools()
    assert "TestTool" in tools

    # Get metadata
    metadata = registry.get_tool_metadata("TestTool")
    assert metadata is not None
    assert metadata.name == "TestTool"
    assert metadata.tool_class == MockTool
    assert metadata.description == "Test tool"
    assert metadata.version == "2.0.0"
    assert metadata.author == "test_author"
    assert "test" in metadata.tags
    assert "mock" in metadata.tags


def test_tool_registration_conflicts():
    """Test tool registration conflict handling."""
    registry = ToolRegistry()
    registry.clear_registry()

    # Register tool first time
    success1 = registry.register_tool("ConflictTool", MockTool)
    assert success1

    # Try to register same name again
    success2 = registry.register_tool("ConflictTool", MockTool)
    assert not success2  # Should fail due to name conflict


def test_tool_validation():
    """Test tool class validation."""
    registry = ToolRegistry()

    # Try to register invalid tool class
    class InvalidTool:
        pass

    try:
        registry.register_tool("InvalidTool", InvalidTool)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must inherit from Tool" in str(e)


def test_tool_instances():
    """Test tool instance creation and management."""
    registry = ToolRegistry()
    registry.clear_registry()
    registry.register_tool("MockTool", MockTool)

    # Get tool instance
    instance1 = registry.get_tool_instance("MockTool")
    assert instance1 is not None
    assert isinstance(instance1, MockTool)
    assert instance1.name == "MockTool"
    assert instance1.call_count == 0

    # Should return same instance on subsequent calls
    instance2 = registry.get_tool_instance("MockTool")
    assert instance1 is instance2

    # Non-existent tool should return None
    instance3 = registry.get_tool_instance("NonExistent")
    assert instance3 is None


def test_tool_execution():
    """Test tool execution through registry."""
    registry = ToolRegistry()
    registry.clear_registry()
    registry.register_tool("MockTool", MockTool)

    # Execute tool
    result = registry.execute_tool("MockTool", "test data")
    assert result == "Mock processed: test data"

    # Check usage statistics were updated
    metadata = registry.get_tool_metadata("MockTool")
    assert metadata.usage_count == 1
    assert metadata.last_used is not None
    assert isinstance(metadata.last_used, datetime)

    # Execute again
    result2 = registry.execute_tool("MockTool", "more data")
    assert result2 == "Mock processed: more data"

    # Check updated statistics
    metadata = registry.get_tool_metadata("MockTool")
    assert metadata.usage_count == 2


def test_tool_execution_errors():
    """Test tool execution error handling."""
    registry = ToolRegistry()

    # Try to execute non-existent tool
    try:
        registry.execute_tool("NonExistent", "data")
        assert False, "Should have raised NameError"
    except NameError as e:
        assert "not found" in str(e)


def test_tool_enable_disable():
    """Test tool enable/disable functionality."""
    registry = ToolRegistry()
    registry.clear_registry()
    registry.register_tool("DisableTest", MockTool)

    # Tool should be enabled by default
    assert registry.is_tool_available("DisableTest")
    instance = registry.get_tool_instance("DisableTest")
    assert instance is not None

    # Disable tool
    success = registry.disable_tool("DisableTest")
    assert success
    assert not registry.is_tool_available("DisableTest")

    # Should not be able to get instance when disabled
    instance = registry.get_tool_instance("DisableTest")
    assert instance is None

    # Re-enable tool
    success = registry.enable_tool("DisableTest")
    assert success
    assert registry.is_tool_available("DisableTest")


def test_tool_unregistration():
    """Test tool unregistration."""
    registry = ToolRegistry()
    registry.clear_registry()
    registry.register_tool("UnregisterTest", MockTool)

    # Tool should be available
    assert registry.is_tool_available("UnregisterTest")

    # Unregister tool
    success = registry.unregister_tool("UnregisterTest")
    assert success
    assert not registry.is_tool_available("UnregisterTest")

    # Try to unregister non-existent tool
    success = registry.unregister_tool("NonExistent")
    assert not success


def test_tool_filtering():
    """Test tool listing with filters."""
    registry = ToolRegistry()
    registry.clear_registry()

    # Register tools with different tags
    registry.register_tool("Tool1", MockTool, tags=["tag1", "common"])
    registry.register_tool("Tool2", MockTool, tags=["tag2", "common"])
    registry.register_tool("Tool3", MockTool, tags=["tag3"])

    # Test filtering by tags
    tag1_tools = registry.list_tools(tags=["tag1"])
    assert "Tool1" in tag1_tools
    assert "Tool2" not in tag1_tools

    common_tools = registry.list_tools(tags=["common"])
    assert "Tool1" in common_tools
    assert "Tool2" in common_tools
    assert "Tool3" not in common_tools

    # Test enabled_only filter
    registry.disable_tool("Tool1")
    enabled_tools = registry.list_tools(enabled_only=True)
    assert "Tool1" not in enabled_tools
    assert "Tool2" in enabled_tools

    all_tools = registry.list_tools(enabled_only=False)
    assert "Tool1" in all_tools
    assert "Tool2" in all_tools


def test_plugin_system():
    """Test plugin registration and management."""
    registry = ToolRegistry()
    registry.clear_registry()

    # Create plugin tools
    plugin_tools = {
        "PluginTool1": PluginTool,
        "PluginTool2": MockTool
    }

    # Register plugin
    registered = registry.register_plugin("TestPlugin", plugin_tools)
    assert len(registered) == 2
    assert "PluginTool1" in registered
    assert "PluginTool2" in registered

    # Check plugin is listed
    plugins = registry.list_plugins()
    assert "TestPlugin" in plugins

    # Check tools have plugin tags
    metadata1 = registry.get_tool_metadata("PluginTool1")
    assert "plugin" in metadata1.tags
    assert "TestPlugin" in metadata1.tags

    # Unregister plugin
    unregistered = registry.unregister_plugin("TestPlugin")
    assert len(unregistered) == 2
    assert "PluginTool1" in unregistered

    # Check plugin is removed
    plugins = registry.list_plugins()
    assert "TestPlugin" not in plugins

    # Check tools are unregistered
    assert not registry.is_tool_available("PluginTool1")
    assert not registry.is_tool_available("PluginTool2")


def test_tool_stats():
    """Test tool usage statistics."""
    registry = ToolRegistry()
    registry.clear_registry()
    registry.register_tool("StatsTool", MockTool)

    # Execute tool a few times
    registry.execute_tool("StatsTool", "data1")
    registry.execute_tool("StatsTool", "data2")

    # Get stats
    stats = registry.get_tool_stats()
    assert "StatsTool" in stats
    tool_stats = stats["StatsTool"]
    assert tool_stats["usage_count"] == 2
    assert tool_stats["last_used"] is not None
    assert tool_stats["enabled"] is True
    assert tool_stats["version"] == "1.0.0"


def test_stdlib_tool_instances():
    """Test stdlib tool instance creation."""
    registry = ToolRegistry()

    # Get WebSearch tool instance
    web_search = registry.get_tool_instance("WebSearch")
    assert web_search is not None
    assert isinstance(web_search, WebSearchTool)

    # Test execution
    result = registry.execute_tool("WebSearch", "test query")
    assert "Mock search results for: test query" in result

    # Get AgentRouting tool instance
    agent_routing = registry.get_tool_instance("AgentRouting")
    assert agent_routing is not None
    assert isinstance(agent_routing, AgentRoutingTool)


if __name__ == "__main__":
    test_registry_initialization()
    print("✓ Registry initialization works")

    test_tool_registration()
    print("✓ Tool registration works")

    test_tool_registration_conflicts()
    print("✓ Tool registration conflict handling works")

    test_tool_validation()
    print("✓ Tool validation works")

    test_tool_instances()
    print("✓ Tool instance management works")

    test_tool_execution()
    print("✓ Tool execution works")

    test_tool_execution_errors()
    print("✓ Tool execution error handling works")

    test_tool_enable_disable()
    print("✓ Tool enable/disable works")

    test_tool_unregistration()
    print("✓ Tool unregistration works")

    test_tool_filtering()
    print("✓ Tool filtering works")

    test_plugin_system()
    print("✓ Plugin system works")

    test_tool_stats()
    print("✓ Tool statistics work")

    test_stdlib_tool_instances()
    print("✓ Stdlib tool instances work")

    print("All tool registry tests passed!")