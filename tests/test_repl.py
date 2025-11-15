"""Tests for the AgenticScript REPL."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.debugger.repl import AgenticScriptREPL
from io import StringIO


def test_repl_agent_creation():
    """Test REPL agent creation and debug commands."""
    repl = AgenticScriptREPL()

    # Test agent creation
    repl.default("agent a = spawn Agent{ openai/gpt-4o }")

    # Verify agent was created
    assert "a" in repl.interpreter.agents
    agent = repl.interpreter.agents["a"]
    assert agent.name == "a"
    assert agent.model == "openai/gpt-4o"


def test_repl_property_assignment():
    """Test REPL property assignment."""
    repl = AgenticScriptREPL()

    # Create agent and set property
    repl.default("agent a = spawn Agent{ openai/gpt-4o }")
    repl.default('*a->goal = "Test goal"')

    # Verify property was set
    agent = repl.interpreter.agents["a"]
    assert agent.get_property("goal") == "Test goal"


def test_repl_debug_commands():
    """Test debug commands work without errors."""
    repl = AgenticScriptREPL()

    # Create some agents
    repl.default("agent a = spawn Agent{ openai/gpt-4o }")
    repl.default("agent b = spawn Agent{ gemini/gemini-2.5-flash }")

    # Test debug commands (they should not raise exceptions)
    repl.do_debug("agents")
    repl.do_debug("dump a")
    repl.do_debug("system")
    repl.do_debug("messages")
    repl.do_debug("memory")
    repl.do_debug("trace on")
    repl.do_debug("trace off")


def test_repl_error_handling():
    """Test REPL error handling."""
    repl = AgenticScriptREPL()

    # Test syntax error
    repl.default("invalid syntax here")

    # Test accessing non-existent agent
    repl.do_debug("dump nonexistent")

    # REPL should continue working after errors
    repl.default("agent a = spawn Agent{ openai/gpt-4o }")
    assert "a" in repl.interpreter.agents


if __name__ == "__main__":
    test_repl_agent_creation()
    test_repl_property_assignment()
    test_repl_debug_commands()
    test_repl_error_handling()
    print("All REPL tests passed!")