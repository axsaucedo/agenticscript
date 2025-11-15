"""Tests for message flow visualization and statistics commands."""

import sys
import os
import io
from contextlib import redirect_stdout
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.debugger.repl import AgenticScriptREPL
from agenticscript.core.interpreter import AgentVal
from agenticscript.runtime.message_bus import message_bus
from agenticscript.runtime.tool_registry import tool_registry
from agenticscript.core.parser import parse_agenticscript


def test_debug_flow_visualization():
    """Test the debug flow command shows message visualization."""
    repl = AgenticScriptREPL()

    # Clear and create some message activity
    message_bus.clear_history()

    # Create agents and simulate communication
    agent1 = AgentVal("sender", "gpt-4o")
    agent2 = AgentVal("receiver", "claude")

    try:
        # Generate some message traffic
        agent1.ask("Hello receiver")
        agent1.tell("Async message")
        agent2.ask("Reply from receiver")

        # Also send some direct messages through message bus
        message_bus.send_message("system", agent1.get_agent_id(), "System message", "system_msg")
        message_bus.send_message(agent1.get_agent_id(), agent2.get_agent_id(), "Direct message", "direct")

        # Test debug flow command
        f = io.StringIO()
        with redirect_stdout(f):
            repl.debug_flow()

        output = f.getvalue()

        # Should show message flow analysis
        assert "Message Flow Analysis" in output
        assert "Communication Flows:" in output
        assert "Agent Activity:" in output
        assert "Message Types:" in output

        # Should show agent communication
        assert "sender" in output or "receiver" in output
        assert "system" in output

    finally:
        agent1.cleanup()
        agent2.cleanup()


def test_debug_stats_command():
    """Test the debug stats command shows detailed statistics."""
    repl = AgenticScriptREPL()

    # Generate some activity
    tool_registry.execute_tool("WebSearch", "test1")
    tool_registry.execute_tool("Calculator", "test2")
    tool_registry.execute_tool("WebSearch", "test3")

    # Create some agents
    code = '''
agent stats_agent1 = spawn Agent{ openai/gpt-4o }
agent stats_agent2 = spawn Agent{ claude/sonnet }
*stats_agent1->goal = "Test statistics"
'''
    ast = parse_agenticscript(code)
    repl.interpreter.interpret(ast)

    # Test debug stats command
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_stats()

    output = f.getvalue()

    # Should show comprehensive statistics
    assert "System Statistics" in output
    assert "Message Bus Performance:" in output
    assert "Tool Usage Patterns:" in output
    assert "Agent Statistics:" in output
    assert "Performance Metrics:" in output

    # Should show actual data
    assert "Total Tool Executions: 3" in output
    assert "WebSearch:" in output
    assert "Calculator:" in output
    assert "Total Agents: 2" in output


def test_debug_flow_with_no_messages():
    """Test debug flow handles empty message history gracefully."""
    repl = AgenticScriptREPL()

    # Clear all messages
    message_bus.clear_history()

    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_flow()

    output = f.getvalue()

    # Should handle empty state gracefully
    assert "No message history available" in output


def test_debug_stats_performance_metrics():
    """Test that debug stats shows performance metrics."""
    repl = AgenticScriptREPL()

    # Create agents to register with message bus
    agent1 = AgentVal("perf_agent1", "gpt-4o")
    agent2 = AgentVal("perf_agent2", "claude")

    try:
        # Generate some message activity
        message_bus.send_message("test", agent1.get_agent_id(), "Performance test", "perf_test")

        f = io.StringIO()
        with redirect_stdout(f):
            repl.debug_stats()

        output = f.getvalue()

        # Should show performance metrics
        assert "Performance Metrics:" in output
        assert "Message Bus Registrations:" in output

        # Should show success rate calculation
        assert "Success Rate:" in output
        assert "Average Delivery Time:" in output

    finally:
        agent1.cleanup()
        agent2.cleanup()


def test_debug_flow_message_types():
    """Test that debug flow shows different message types."""
    repl = AgenticScriptREPL()
    message_bus.clear_history()

    # Create agents
    agent1 = AgentVal("type_agent1", "gpt-4o")
    agent2 = AgentVal("type_agent2", "claude")

    try:
        # Send different types of messages
        message_bus.send_message(agent1.get_agent_id(), agent2.get_agent_id(), "Ask message", "ask_request")
        message_bus.send_message(agent2.get_agent_id(), agent1.get_agent_id(), "Response", "ask_response")
        message_bus.send_message("system", agent1.get_agent_id(), "Tell message", "tell")
        message_bus.send_message(agent1.get_agent_id(), "system", "Tool usage", "tool_usage")

        f = io.StringIO()
        with redirect_stdout(f):
            repl.debug_flow()

        output = f.getvalue()

        # Should show different message types
        assert "Message Types:" in output
        assert "ask_request" in output or "ask_response" in output
        assert "tell" in output or "tool_usage" in output

    finally:
        agent1.cleanup()
        agent2.cleanup()


def test_debug_stats_tool_usage_distribution():
    """Test that debug stats shows tool usage distribution."""
    repl = AgenticScriptREPL()

    # Get baseline tool stats
    baseline_stats = tool_registry.get_tool_stats()
    baseline_web = baseline_stats.get("WebSearch", {}).get("usage_count", 0)
    baseline_calc = baseline_stats.get("Calculator", {}).get("usage_count", 0)

    # Use tools with different frequencies
    for _ in range(3):
        tool_registry.execute_tool("WebSearch", "frequent")
    for _ in range(1):
        tool_registry.execute_tool("Calculator", "less frequent")

    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_stats()

    output = f.getvalue()

    # Should show usage distribution structure
    assert "Usage Distribution:" in output
    assert "WebSearch:" in output
    assert "Calculator:" in output

    # Should show percentages
    assert "%" in output

    # Verify the tools show up with increased counts
    new_stats = tool_registry.get_tool_stats()
    new_web = new_stats.get("WebSearch", {}).get("usage_count", 0)
    new_calc = new_stats.get("Calculator", {}).get("usage_count", 0)

    assert new_web > baseline_web
    assert new_calc > baseline_calc


def test_debug_help_includes_new_commands():
    """Test that debug help includes the new flow and stats commands."""
    repl = AgenticScriptREPL()

    f = io.StringIO()
    with redirect_stdout(f):
        repl.help_debug()

    output = f.getvalue()

    # Should include new commands
    assert "debug flow" in output
    assert "debug stats" in output
    assert "Message flow visualization between agents" in output
    assert "Detailed system performance statistics" in output


def test_debug_commands_integration():
    """Test integration of flow and stats commands with active system."""
    repl = AgenticScriptREPL()

    # Create a realistic scenario
    code = '''
agent coordinator = spawn Agent{ openai/gpt-4o }
agent worker1 = spawn Agent{ claude/sonnet }
agent worker2 = spawn Agent{ gemini/pro }
*coordinator->goal = "Coordinate tasks"
*worker1->goal = "Process data"
*worker2->goal = "Generate reports"
'''
    ast = parse_agenticscript(code)
    repl.interpreter.interpret(ast)

    # Simulate some activity
    coordinator = repl.interpreter.get_agent_status("coordinator")
    worker1 = repl.interpreter.get_agent_status("worker1")

    if coordinator and worker1:
        coordinator.ask("Status check")
        worker1.tell("Task complete")

    # Use some tools
    tool_registry.execute_tool("WebSearch", "research")
    tool_registry.execute_tool("Calculator", "compute")

    # Test both commands work together
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_flow()
        repl.debug_stats()

    output = f.getvalue()

    # Should show comprehensive system state
    assert "Message Flow Analysis" in output
    assert "System Statistics" in output
    assert "coordinator" in output
    assert "worker1" in output or "worker2" in output


if __name__ == "__main__":
    # Clean state
    message_bus.clear_history()

    test_debug_flow_visualization()
    print("✓ Debug flow visualization works")

    test_debug_stats_command()
    print("✓ Debug stats command works")

    test_debug_flow_with_no_messages()
    print("✓ Debug flow handles empty state")

    test_debug_stats_performance_metrics()
    print("✓ Debug stats performance metrics work")

    test_debug_flow_message_types()
    print("✓ Debug flow message types work")

    test_debug_stats_tool_usage_distribution()
    print("✓ Debug stats tool usage distribution works")

    test_debug_help_includes_new_commands()
    print("✓ Debug help includes new commands")

    test_debug_commands_integration()
    print("✓ Debug commands integration works")

    print("All message flow visualization tests passed!")