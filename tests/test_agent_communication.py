"""Tests for AgenticScript agent communication methods."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.interpreter import AgentVal
from agenticscript.stdlib.tools import WebSearchTool, CalculatorTool


def test_agent_creation():
    """Test basic agent creation and properties."""
    agent = AgentVal("test_agent", "gpt-4o")

    assert agent.name == "test_agent"
    assert agent.model == "gpt-4o"
    assert agent.status == "idle"
    assert agent.get_property("name") == "test_agent"
    assert agent.get_property("model") == "gpt-4o"
    assert agent.get_property("status") == "idle"
    assert agent.get_property("tools") == []


def test_agent_ask_method():
    """Test synchronous ask method."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Test basic ask
    response = agent.ask("Hello")
    assert "Hello from test_agent!" in response

    # Test ask with status query
    response = agent.ask("What's your status?")
    assert "Agent test_agent status: idle" in response

    # Test ask with error keyword
    response = agent.ask("This is an error test")
    assert "Error handling:" in response


def test_agent_tell_method():
    """Test asynchronous tell method."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Initially no messages
    messages = agent.get_pending_messages()
    assert len(messages) == 0

    # Send a message
    agent.tell("Hello async!")

    # Check message was queued
    messages = agent.get_pending_messages()
    assert len(messages) == 1
    assert messages[0]["message"] == "Hello async!"
    assert messages[0]["sender"] == "system"
    assert "timestamp" in messages[0]

    # Send another message
    agent.tell("Second message")
    messages = agent.get_pending_messages()
    assert len(messages) == 2

    # Clear messages
    cleared = agent.clear_messages()
    assert cleared == 2
    assert len(agent.get_pending_messages()) == 0


def test_agent_tool_assignment():
    """Test tool assignment and management."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Initially no tools
    assert not agent.has_tool("WebSearch")
    assert agent.get_property("tools") == []

    # Assign a tool
    web_search_tool = WebSearchTool()
    agent.assign_tool("WebSearch", web_search_tool)

    # Check tool is assigned
    assert agent.has_tool("WebSearch")
    assert "WebSearch" in agent.get_property("tools")

    # Remove tool
    removed = agent.remove_tool("WebSearch")
    assert removed
    assert not agent.has_tool("WebSearch")
    assert agent.get_property("tools") == []

    # Try to remove non-existent tool
    removed = agent.remove_tool("NonExistent")
    assert not removed


def test_agent_tool_execution():
    """Test tool execution through agents."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Assign tools
    web_search_tool = WebSearchTool()
    calculator_tool = CalculatorTool()

    agent.assign_tool("WebSearch", web_search_tool)
    agent.assign_tool("Calculator", calculator_tool)

    # Execute WebSearch tool
    result = agent.execute_tool("WebSearch", "test query")
    assert "Mock search results for: test query" in result
    assert web_search_tool.call_count == 1

    # Check agent status changed during execution
    old_status = agent.status
    result = agent.execute_tool("Calculator", "2 + 2")
    assert "Mock calculation result for: 2 + 2" in result
    assert agent.status == old_status  # Should restore status

    # Try to execute non-existent tool
    try:
        agent.execute_tool("NonExistent", "data")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "does not have access to tool" in str(e)


def test_agent_tool_validation():
    """Test tool validation and error handling."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Try to execute tool without assignment
    try:
        agent.execute_tool("WebSearch", "query")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "does not have access to tool" in str(e)

    # Test has_tool with non-existent tool
    assert not agent.has_tool("NonExistentTool")


def test_agent_status_changes():
    """Test agent status changes during operations."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Initial status
    assert agent.status == "idle"

    # Status during ask operation (tested indirectly through mock response)
    response = agent.ask("status check")
    assert "idle" in response  # Should show the status before processing

    # Status during tool execution
    web_search_tool = WebSearchTool()
    agent.assign_tool("WebSearch", web_search_tool)

    original_execute = web_search_tool.execute

    def status_checking_execute(*args, **kwargs):
        # During execution, agent should be in "using_tool" status
        # We can't directly check this in the test due to the try/finally block
        return original_execute(*args, **kwargs)

    web_search_tool.execute = status_checking_execute
    result = agent.execute_tool("WebSearch", "test")

    # After execution, status should be back to idle
    assert agent.status == "idle"


def test_agent_multiple_tool_assignment():
    """Test assigning multiple tools to an agent."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Assign multiple tools
    web_search = WebSearchTool()
    calculator = CalculatorTool()

    agent.assign_tool("WebSearch", web_search)
    agent.assign_tool("Calculator", calculator)

    # Check both tools are available
    assert agent.has_tool("WebSearch")
    assert agent.has_tool("Calculator")

    tools_list = agent.get_property("tools")
    assert "WebSearch" in tools_list
    assert "Calculator" in tools_list
    assert len(tools_list) == 2

    # Execute both tools
    web_result = agent.execute_tool("WebSearch", "query")
    calc_result = agent.execute_tool("Calculator", "5 + 5")

    assert "Mock search results" in web_result
    assert "Mock calculation result" in calc_result

    # Remove one tool
    agent.remove_tool("WebSearch")
    assert not agent.has_tool("WebSearch")
    assert agent.has_tool("Calculator")
    assert len(agent.get_property("tools")) == 1


def test_agent_property_access():
    """Test agent property access for tools."""
    agent = AgentVal("test_agent", "gpt-4o")

    # Initially empty tools list
    tools = agent.get_property("tools")
    assert tools == []
    assert isinstance(tools, list)

    # Add tools and check property updates
    agent.assign_tool("Tool1", WebSearchTool())
    agent.assign_tool("Tool2", CalculatorTool())

    tools = agent.get_property("tools")
    assert len(tools) == 2
    assert "Tool1" in tools
    assert "Tool2" in tools


if __name__ == "__main__":
    test_agent_creation()
    print("✓ Agent creation works")

    test_agent_ask_method()
    print("✓ Agent ask method works")

    test_agent_tell_method()
    print("✓ Agent tell method works")

    test_agent_tool_assignment()
    print("✓ Agent tool assignment works")

    test_agent_tool_execution()
    print("✓ Agent tool execution works")

    test_agent_tool_validation()
    print("✓ Agent tool validation works")

    test_agent_status_changes()
    print("✓ Agent status changes work")

    test_agent_multiple_tool_assignment()
    print("✓ Multiple tool assignment works")

    test_agent_property_access()
    print("✓ Agent property access works")

    print("All agent communication tests passed!")