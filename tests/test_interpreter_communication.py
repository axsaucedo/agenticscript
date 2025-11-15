"""Tests for AgenticScript interpreter with agent communication methods."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.parser import parse_agenticscript
from agenticscript.core.interpreter import AgenticScriptInterpreter
from agenticscript.stdlib.tools import WebSearchTool


def test_interpreter_agent_ask():
    """Test agent ask method through interpreter."""
    code = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.ask("Hello there"))
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    # Capture print output
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue().strip()
    assert "Hello from a!" in output


def test_interpreter_agent_tell():
    """Test agent tell method through interpreter."""
    code = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.tell("Async message"))
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    # Capture print output
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue().strip()
    assert "message sent" in output

    # Check that agent has the message in queue
    agent = interpreter.get_agent_status("a")
    messages = agent.get_pending_messages()
    assert len(messages) == 1
    assert messages[0]["message"] == "Async message"


def test_interpreter_agent_has_tool():
    """Test agent has_tool method through interpreter."""
    code = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.has_tool("WebSearch"))
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    # Capture print output
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue().strip()
    assert "false" in output.lower()


def test_interpreter_agent_tool_assignment():
    """Test agent tool assignment and execution through interpreter."""
    # First manually assign tool to agent, then test has_tool and execute_tool
    interpreter = AgenticScriptInterpreter()

    # Create agent first
    code1 = '''
agent a = spawn Agent{ openai/gpt-4o }
'''
    ast1 = parse_agenticscript(code1)
    interpreter.interpret(ast1)

    # Manually assign tool to agent (simulating tool assignment functionality)
    agent = interpreter.get_agent_status("a")
    web_search_tool = WebSearchTool()
    agent.assign_tool("WebSearch", web_search_tool)

    # Now test has_tool
    code2 = '''
print(a.has_tool("WebSearch"))
'''
    ast2 = parse_agenticscript(code2)

    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast2)

    output = f.getvalue().strip()
    assert "true" in output.lower()

    # Test execute_tool
    code3 = '''
print(a.execute_tool("WebSearch", "test query"))
'''
    ast3 = parse_agenticscript(code3)

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast3)

    output = f.getvalue().strip()
    assert "Mock search results for: test query" in output


def test_interpreter_method_call_errors():
    """Test error handling for method calls."""
    interpreter = AgenticScriptInterpreter()

    # Test ask without arguments
    code1 = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.ask())
'''
    ast1 = parse_agenticscript(code1)

    try:
        interpreter.interpret(ast1)
        assert False, "Should have raised InterpreterError"
    except Exception as e:
        assert "requires at least 1 argument" in str(e)

    # Test execute_tool on non-existent tool
    code2 = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.execute_tool("NonExistent", "data"))
'''
    ast2 = parse_agenticscript(code2)

    try:
        interpreter.interpret(ast2)
        assert False, "Should have raised InterpreterError"
    except Exception as e:
        assert "does not have access to tool" in str(e)


def test_interpreter_ask_with_timeout():
    """Test agent ask method with timeout parameter."""
    code = '''
agent a = spawn Agent{ openai/gpt-4o }
print(a.ask("Hello", 5.0))
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    # Capture print output
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue().strip()
    assert "Hello from a!" in output


if __name__ == "__main__":
    test_interpreter_agent_ask()
    print("✓ Interpreter agent ask works")

    test_interpreter_agent_tell()
    print("✓ Interpreter agent tell works")

    test_interpreter_agent_has_tool()
    print("✓ Interpreter agent has_tool works")

    test_interpreter_agent_tool_assignment()
    print("✓ Interpreter tool assignment and execution works")

    test_interpreter_method_call_errors()
    print("✓ Interpreter method call error handling works")

    test_interpreter_ask_with_timeout()
    print("✓ Interpreter ask with timeout works")

    print("All interpreter communication tests passed!")