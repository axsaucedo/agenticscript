"""Tests for the AgenticScript interpreter."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.parser import parse_agenticscript
from agenticscript.core.interpreter import AgenticScriptInterpreter, interpret_agenticscript


def test_agent_declaration():
    """Test interpreting agent declaration."""
    code = 'agent a = spawn Agent{ openai/gpt-4o }'

    ast = parse_agenticscript(code)
    interpreter = interpret_agenticscript(ast)

    # Check that agent was created
    assert 'a' in interpreter.agents
    agent = interpreter.agents['a']
    assert agent.name == 'a'
    assert agent.model == 'openai/gpt-4o'
    assert agent.status == 'idle'


def test_property_assignment():
    """Test interpreting property assignment."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    *a->goal = "Test agent"
    '''

    ast = parse_agenticscript(code)
    interpreter = interpret_agenticscript(ast)

    # Check that property was set
    agent = interpreter.agents['a']
    assert agent.get_property('goal') == "Test agent"


def test_property_access():
    """Test interpreting property access."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    print(a.status)
    '''

    ast = parse_agenticscript(code)
    interpreter = interpret_agenticscript(ast)

    # Check that we can access the agent
    agent = interpreter.agents['a']
    assert agent.get_property('status') == 'idle'


def test_complete_workflow():
    """Test complete workflow from the plan."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    *a->goal = "Test agent"
    print(a.status)
    print(a.model)
    '''

    ast = parse_agenticscript(code)
    interpreter = interpret_agenticscript(ast)

    # Verify agent was created with correct properties
    agent = interpreter.agents['a']
    assert agent.name == 'a'
    assert agent.model == 'openai/gpt-4o'
    assert agent.get_property('goal') == "Test agent"
    assert agent.status == 'idle'


if __name__ == "__main__":
    # Quick test run
    test_agent_declaration()
    test_property_assignment()
    test_property_access()
    test_complete_workflow()
    print("All interpreter tests passed!")