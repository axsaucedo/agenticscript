"""Tests for the AgenticScript module system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.module_system import ModuleSystem
from agenticscript.stdlib.tools import WebSearchTool, AgentRoutingTool
from agenticscript.stdlib.agents import SupervisorAgent


def test_import_tools():
    """Test importing tools from stdlib."""
    module_system = ModuleSystem()

    # Import tools
    imports = module_system.import_module(
        ["agenticscript", "stdlib", "tools"],
        ["WebSearch", "AgentRouting"]
    )

    assert "WebSearch" in imports
    assert "AgentRouting" in imports
    assert imports["WebSearch"] == WebSearchTool
    assert imports["AgentRouting"] == AgentRoutingTool

    # Check they're available
    assert module_system.is_tool_available("WebSearch")
    assert module_system.is_tool_available("AgentRouting")
    assert not module_system.is_tool_available("NonExistentTool")


def test_import_agents():
    """Test importing agent types from stdlib."""
    module_system = ModuleSystem()

    # Import agent types
    imports = module_system.import_module(
        ["agenticscript", "stdlib", "agents"],
        ["SupervisorAgent"]
    )

    assert "SupervisorAgent" in imports
    assert imports["SupervisorAgent"] == SupervisorAgent

    # Check it's available
    assert module_system.is_agent_available("SupervisorAgent")
    assert not module_system.is_agent_available("NonExistentAgent")


def test_tool_instantiation():
    """Test that imported tools can be instantiated."""
    module_system = ModuleSystem()

    # Import tool
    module_system.import_module(
        ["agenticscript", "stdlib", "tools"],
        ["WebSearch"]
    )

    # Get tool class and instantiate
    WebSearch = module_system.get_tool_class("WebSearch")
    tool_instance = WebSearch()

    assert tool_instance.name == "WebSearch"
    assert tool_instance.call_count == 0

    # Test execution
    result = tool_instance.execute("test query")
    assert "Mock search results for: test query" in result
    assert tool_instance.call_count == 1


def test_import_error():
    """Test import error handling."""
    module_system = ModuleSystem()

    try:
        module_system.import_module(
            ["agenticscript", "stdlib", "tools"],
            ["NonExistentTool"]
        )
        assert False, "Should have raised ImportError"
    except ImportError as e:
        assert "NonExistentTool" in str(e)


if __name__ == "__main__":
    test_import_tools()
    print("✓ Tool import works")

    test_import_agents()
    print("✓ Agent import works")

    test_tool_instantiation()
    print("✓ Tool instantiation works")

    test_import_error()
    print("✓ Import error handling works")

    print("All module system tests passed!")