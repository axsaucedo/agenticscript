"""Tests for Phase 2 parser features."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.parser import parse_agenticscript
from agenticscript.core import ast_nodes as ast


def test_import_statement():
    """Test parsing import statements."""
    code = 'import agenticscript.stdlib.tools { WebSearch, AgentRouting }'

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1

    stmt = result.statements[0]
    assert isinstance(stmt, ast.ImportStatement)
    assert stmt.module_path.path == ["agenticscript", "stdlib", "tools"]
    assert stmt.import_list.imports == ["WebSearch", "AgentRouting"]


def test_tool_assignment():
    """Test parsing tool assignment."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    *a->tools = { WebSearch }
    '''

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 2

    # Check agent declaration
    assert isinstance(result.statements[0], ast.AgentDeclaration)

    # Check tool assignment
    tool_stmt = result.statements[1]
    assert isinstance(tool_stmt, ast.ToolAssignment)
    assert tool_stmt.agent_name == "a"
    assert tool_stmt.operator == "="
    assert len(tool_stmt.tool_list.tools) == 1
    assert isinstance(tool_stmt.tool_list.tools[0], ast.ToolSpec)
    assert tool_stmt.tool_list.tools[0].name == "WebSearch"


def test_if_statement():
    """Test parsing if statements."""
    code = '''
    agent a = spawn Agent{ openai/gpt-4o }
    if a.status == "idle" {
        print("Agent is idle")
    }
    '''

    result = parse_agenticscript(code)

    assert isinstance(result, ast.Program)
    assert len(result.statements) == 2

    # Check if statement
    if_stmt = result.statements[1]
    assert isinstance(if_stmt, ast.IfStatement)
    assert len(if_stmt.then_statements) == 1
    assert if_stmt.else_statements is None


if __name__ == "__main__":
    try:
        test_import_statement()
        print("✓ Import statement parsing works")

        test_tool_assignment()
        print("✓ Tool assignment parsing works")

        test_if_statement()
        print("✓ If statement parsing works")

        print("All Phase 2 parser tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()