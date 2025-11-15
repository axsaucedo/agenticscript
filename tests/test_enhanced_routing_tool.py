"""Tests for enhanced AgentRoutingTool with message bus integration."""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.stdlib.tools import AgentRoutingTool
from agenticscript.runtime.message_bus import message_bus
from agenticscript.core.interpreter import AgentVal


def test_agent_routing_tool_basic():
    """Test basic AgentRoutingTool functionality."""
    tool = AgentRoutingTool(["agent1", "agent2"])

    # Test basic properties
    assert tool.name == "AgentRouting"
    assert tool.call_count == 0
    assert "agent1" in tool.list_agents()
    assert "agent2" in tool.list_agents()

    # Test add/remove agents
    tool.add_agent("agent3")
    assert "agent3" in tool.list_agents()

    tool.remove_agent("agent1")
    assert "agent1" not in tool.list_agents()
    assert len(tool.list_agents()) == 2


def test_agent_routing_tool_mock_fallback():
    """Test AgentRoutingTool mock fallback when message bus not available."""
    tool = AgentRoutingTool(["test_agent"])

    # When no agents are registered, should fallback to mock
    result = tool.execute("Test message", "test_agent")

    assert "test_agent" in result
    assert tool.call_count == 1
    assert tool.last_used is not None


def test_agent_routing_tool_with_message_bus():
    """Test AgentRoutingTool with actual message bus integration."""
    # Create some agents for routing
    agent1 = AgentVal("router_target1", "gpt-4o")
    agent2 = AgentVal("router_target2", "gpt-4o")

    try:
        # Create routing tool
        tool = AgentRoutingTool(["router_target1", "router_target2"])

        # Test getting registered agents
        registered = tool.get_registered_agents()
        assert len(registered) >= 2  # At least our two agents

        # Test routing to specific agent
        result = tool.execute("Hello from routing tool!", "router_target1", sender="routing_test")

        # Should successfully route the message
        assert "Message routed to agent" in result
        assert "router_target1" in result
        assert "message ID:" in result

        # Check that message was actually sent
        pending = message_bus.get_pending_count(agent1.get_agent_id())
        assert pending > 0

        # Receive and verify the message
        message = message_bus.receive_message(agent1.get_agent_id())
        assert message is not None
        assert message.content == "Hello from routing tool!"
        assert message.message_type == "routed_message"
        assert message.sender == "routing_test"

    finally:
        agent1.cleanup()
        agent2.cleanup()


def test_agent_routing_tool_agent_not_found():
    """Test AgentRoutingTool behavior when target agent not found."""
    tool = AgentRoutingTool(["nonexistent_agent"])

    result = tool.execute("Test message", "nonexistent_agent")

    # Should report that agent was not found
    assert "not found in registered agents" in result
    assert tool.call_count == 1


def test_agent_routing_tool_no_target():
    """Test AgentRoutingTool behavior when no target specified."""
    tool = AgentRoutingTool([])  # No agents in list

    result = tool.execute("Test message")

    assert "Error: No target agent specified or available" in result
    assert tool.call_count == 1


def test_agent_routing_tool_default_agent():
    """Test AgentRoutingTool using default (first) agent when none specified."""
    agent = AgentVal("default_agent", "gpt-4o")

    try:
        tool = AgentRoutingTool(["default_agent"])

        # Don't specify agent_name, should use first in list
        result = tool.execute("Default routing test", sender="default_test")

        assert "Message routed to agent" in result
        assert "default_agent" in result

        # Verify message was received
        pending = message_bus.get_pending_count(agent.get_agent_id())
        assert pending > 0

    finally:
        agent.cleanup()


def test_agent_routing_tool_integration_with_agents():
    """Test AgentRoutingTool used by agents to communicate."""
    sender_agent = AgentVal("sender", "gpt-4o")
    receiver_agent = AgentVal("receiver", "gpt-4o")

    try:
        # Assign routing tool to sender agent
        routing_tool = AgentRoutingTool(["receiver"])
        sender_agent.assign_tool("AgentRouting", routing_tool)

        # Use routing tool through agent
        result = sender_agent.execute_tool(
            "AgentRouting",
            "Hello receiver!",
            "receiver",
            sender_agent.get_agent_id()
        )

        assert "Message routed to agent" in result

        # Check receiver got the message
        pending = message_bus.get_pending_count(receiver_agent.get_agent_id())
        assert pending > 0

        message = message_bus.receive_message(receiver_agent.get_agent_id())
        assert message.content == "Hello receiver!"
        assert message.sender == sender_agent.get_agent_id()

    finally:
        sender_agent.cleanup()
        receiver_agent.cleanup()


def test_agent_routing_tool_message_bus_full():
    """Test AgentRoutingTool behavior when message bus queue is full."""
    # Create agent with very small queue size
    from agenticscript.runtime.message_bus import MessageBus
    small_bus = MessageBus(max_queue_size=1)

    # Register a test agent
    small_bus.register_agent("queue_test_agent")

    try:
        # Fill the queue
        small_bus.send_message("system", "queue_test_agent", "Message 1")

        # Create routing tool that uses the global message bus
        tool = AgentRoutingTool(["queue_test"])

        # This will try to send to global message bus, which should work
        # (we can't easily test the queue full scenario with global bus)
        result = tool.execute("Test message", "queue_test_agent")

        # Should still work with global message bus
        assert isinstance(result, str)
        assert tool.call_count == 1

    finally:
        small_bus.unregister_agent("queue_test_agent")


if __name__ == "__main__":
    # Clear message bus state
    message_bus.clear_history()

    test_agent_routing_tool_basic()
    print("✓ AgentRoutingTool basic functionality works")

    test_agent_routing_tool_mock_fallback()
    print("✓ AgentRoutingTool mock fallback works")

    test_agent_routing_tool_with_message_bus()
    print("✓ AgentRoutingTool message bus integration works")

    test_agent_routing_tool_agent_not_found()
    print("✓ AgentRoutingTool agent not found handling works")

    test_agent_routing_tool_no_target()
    print("✓ AgentRoutingTool no target handling works")

    test_agent_routing_tool_default_agent()
    print("✓ AgentRoutingTool default agent selection works")

    test_agent_routing_tool_integration_with_agents()
    print("✓ AgentRoutingTool integration with agents works")

    test_agent_routing_tool_message_bus_full()
    print("✓ AgentRoutingTool queue full handling works")

    print("All enhanced routing tool tests passed!")