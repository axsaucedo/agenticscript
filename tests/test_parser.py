"""Tests for the AgenticScript parser."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.parser import parse_agenticscript
from agenticscript.core import ast_nodes as ast


def test_basic_agent_declaration():
    """Test parsing basic agent declaration."""
    code = 'agent a = spawn Agent{ openai/gpt-4o }'

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1

    stmt = result.statements[0]
    assert isinstance(stmt, ast.AgentDeclaration)
    assert stmt.name == "a"
    assert isinstance(stmt.constructor, ast.AgentConstructor)
    assert stmt.constructor.model.path == "openai/gpt-4o"


def test_property_assignment():
    """Test parsing property assignment."""
    code = '*a->goal = "Test agent"'

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1

    stmt = result.statements[0]
    assert isinstance(stmt, ast.PropertyAssignment)
    assert stmt.agent_name == "a"
    assert stmt.property_name == "goal"
    assert isinstance(stmt.value, ast.StringValue)
    assert stmt.value.value == "Test agent"


def test_print_statement():
    """Test parsing print statement."""
    code = 'print(a.status)'

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1

    stmt = result.statements[0]
    assert isinstance(stmt, ast.PrintStatement)
    assert isinstance(stmt.expression, ast.PropertyAccess)
    assert stmt.expression.object == "a"
    assert stmt.expression.property == "status"


def test_complete_example():
    """Test parsing complete example from the plan."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    *a->goal = "Test agent"
    print(a.status)
    '''

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 3

    # Check each statement type
    assert isinstance(result.statements[0], ast.AgentDeclaration)
    assert isinstance(result.statements[1], ast.PropertyAssignment)
    assert isinstance(result.statements[2], ast.PrintStatement)


if __name__ == "__main__":
    # Quick test run
    test_basic_agent_declaration()
    test_property_assignment()
    test_print_statement()
    test_complete_example()
    print("All parser tests passed!")