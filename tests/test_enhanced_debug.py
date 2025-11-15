"""Tests for enhanced debug commands in the REPL."""

import sys
import os
import io
from contextlib import redirect_stdout
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.debugger.repl import AgenticScriptREPL
from agenticscript.core.interpreter import AgenticScriptInterpreter
from agenticscript.core.parser import parse_agenticscript
from agenticscript.runtime.message_bus import message_bus
from agenticscript.runtime.tool_registry import tool_registry


def test_debug_messages_command():
    """Test the enhanced debug messages command."""
    repl = AgenticScriptREPL()

    # Clear message bus state
    message_bus.clear_history()

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_messages()

    output = f.getvalue()

    # Should show real message bus statistics
    assert "Message Bus Status" in output
    assert "Total Messages Sent:" in output
    assert "Total Messages Delivered:" in output
    assert "Registered Agents:" in output


def test_debug_tools_command():
    """Test the new debug tools command."""
    repl = AgenticScriptREPL()

    # Use some tools to generate statistics
    tool_registry.execute_tool("WebSearch", "test query")
    tool_registry.execute_tool("Calculator", "2 + 2")

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_tools()

    output = f.getvalue()

    # Should show tool registry information
    assert "Tool Registry" in output
    assert "WebSearch" in output
    assert "Calculator" in output
    assert "Usage Count" in output
    assert "Tool Summary" in output


def test_debug_system_command():
    """Test the enhanced debug system command."""
    repl = AgenticScriptREPL()

    # Create some agents
    code = '''
agent a = spawn Agent{ openai/gpt-4o }
agent b = spawn Agent{ claude/sonnet }
'''
    ast = parse_agenticscript(code)
    repl.interpreter.interpret(ast)

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_system()

    output = f.getvalue()

    # Should show enhanced system information
    assert "System Status" in output
    assert "Active Agents: 2" in output
    assert "Available Tools:" in output
    assert "Total Tool Executions:" in output


def test_debug_dump_enhanced():
    """Test the enhanced debug dump command."""
    repl = AgenticScriptREPL()

    # Create an agent
    code = '''
agent test_agent = spawn Agent{ openai/gpt-4o }
*test_agent->goal = "Test agent for debugging"
'''
    ast = parse_agenticscript(code)
    repl.interpreter.interpret(ast)

    # Send a tell message to the agent to populate message queue
    agent = repl.interpreter.get_agent_status("test_agent")
    if agent and hasattr(agent, 'tell'):
        agent.tell("Test message for debug")

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_dump_agent("test_agent")

    output = f.getvalue()

    # Should show enhanced agent information
    assert "Agent Details (test_agent)" in output
    assert "Name: test_agent" in output
    assert "Model: openai/gpt-4o" in output
    assert "goal: Test agent for debugging" in output

    # Should show new enhanced features
    if hasattr(agent, 'get_agent_id'):
        assert "Agent ID:" in output
    if hasattr(agent, '_processing_thread'):
        assert "Background Processing:" in output
    if hasattr(agent, 'has_tool'):
        assert "Registry Tools" in output


def test_debug_commands_integration():
    """Test integration of debug commands with runtime systems."""
    repl = AgenticScriptREPL()

    # Create agents and use tools
    code = '''
agent worker = spawn Agent{ openai/gpt-4o }
print(worker.ask("Hello"))
'''
    ast = parse_agenticscript(code)

    # Capture interpreter output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.interpreter.interpret(ast)

    # Now test debug commands show the activity
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_messages()
        repl.debug_system()
        repl.debug_agents()

    output = f.getvalue()

    # Should show activity from the agent interactions
    assert "Message Bus Status" in output
    assert "System Status" in output
    assert "Active Agents" in output


def test_debug_help_updated():
    """Test that debug help includes new commands."""
    repl = AgenticScriptREPL()

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.help_debug()

    output = f.getvalue()

    # Should include new debug tools command
    assert "debug tools" in output
    assert "Tool registry and usage statistics" in output
    assert "debug messages" in output
    assert "Message bus statistics" in output


def test_debug_error_handling():
    """Test debug commands handle missing runtime components gracefully."""
    repl = AgenticScriptREPL()

    # Test commands should not crash even if components are missing
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_messages()
        repl.debug_tools()
        repl.debug_system()

    output = f.getvalue()

    # Should produce output without crashing
    assert len(output) > 0


def test_debug_agents_with_enhanced_agents():
    """Test debug agents command with enhanced agent features."""
    repl = AgenticScriptREPL()

    # Create agents
    code = '''
agent enhanced_a = spawn Agent{ openai/gpt-4o }
agent enhanced_b = spawn Agent{ claude/sonnet }
*enhanced_a->goal = "Enhanced agent A"
*enhanced_b->goal = "Enhanced agent B"
'''
    ast = parse_agenticscript(code)
    repl.interpreter.interpret(ast)

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_agents()

    output = f.getvalue()

    # Should show agents in table format
    assert "Active Agents" in output
    assert "enhanced_a" in output
    assert "enhanced_b" in output
    assert "openai/gpt-4o" in output
    assert "claude/sonnet" in output


if __name__ == "__main__":
    # Clean state before tests
    message_bus.clear_history()

    test_debug_messages_command()
    print("✓ Debug messages command works")

    test_debug_tools_command()
    print("✓ Debug tools command works")

    test_debug_system_command()
    print("✓ Debug system command enhanced")

    test_debug_dump_enhanced()
    print("✓ Debug dump command enhanced")

    test_debug_commands_integration()
    print("✓ Debug commands integration works")

    test_debug_help_updated()
    print("✓ Debug help updated with new commands")

    test_debug_error_handling()
    print("✓ Debug error handling works")

    test_debug_agents_with_enhanced_agents()
    print("✓ Debug agents with enhanced features works")

    print("All enhanced debug tests passed!")