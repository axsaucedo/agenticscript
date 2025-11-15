"""Parser for AgenticScript using Lark."""

import os
from pathlib import Path
from typing import Any, List, Union

from lark import Lark, Transformer
from lark.exceptions import LarkError

from . import ast_nodes as ast


class AgenticScriptTransformer(Transformer):
    """Transforms Lark parse tree into AgenticScript AST."""

    def start(self, children: List[Any]) -> ast.Program:
        return ast.Program(statements=children)

    def statement(self, children: List[Any]) -> ast.StatementType:
        return children[0]

    def agent_declaration(self, children: List[Any]) -> ast.AgentDeclaration:
        # Lark removes literal tokens, so we just get name and constructor
        name, constructor = children
        return ast.AgentDeclaration(name=name.name, constructor=constructor)

    def agent_constructor(self, children: List[Any]) -> ast.AgentConstructor:
        # children should be the parsed content inside { }
        model_spec = None
        config_pairs = []

        for child in children:
            if isinstance(child, ast.ModelSpec):
                model_spec = child
            elif isinstance(child, ast.ConfigPair):
                config_pairs.append(child)

        if model_spec is None:
            raise ValueError("No model specification found in agent constructor")

        return ast.AgentConstructor(model=model_spec, config=config_pairs)

    def model_spec(self, children: List[Any]) -> ast.ModelSpec:
        return ast.ModelSpec(path=children[0].value)

    def config_pair(self, children: List[Any]) -> ast.ConfigPair:
        key, _, value = children
        return ast.ConfigPair(key=key.value, value=value)

    def property_assignment(self, children: List[Any]) -> ast.PropertyAssignment:
        # Lark removes literal tokens, so we get: agent_name, prop_name, value
        agent_name, prop_name, value = children
        return ast.PropertyAssignment(
            agent_name=agent_name.name,
            property_name=prop_name.name,
            value=value
        )

    def assignment_statement(self, children: List[Any]) -> ast.AssignmentStatement:
        # Lark removes literal tokens, so we get: variable_name, value
        variable_name, value = children
        return ast.AssignmentStatement(
            variable_name=variable_name.name,
            value=value
        )

    def print_statement(self, children: List[Any]) -> ast.PrintStatement:
        # Lark removes literal tokens, so we just get the expression
        expr = children[0]
        return ast.PrintStatement(expression=expr)

    def expression_statement(self, children: List[Any]) -> ast.ExpressionStatement:
        return ast.ExpressionStatement(expression=children[0])

    def expression(self, children: List[Any]) -> ast.ExpressionType:
        return children[0]

    def property_access(self, children: List[Any]) -> ast.PropertyAccess:
        obj, prop = children
        return ast.PropertyAccess(object=obj.name, property=prop.name)

    def method_call(self, children: List[Any]) -> ast.MethodCall:
        # Lark removes literal tokens, so we get obj, method, args
        if len(children) == 3:
            obj, method, args = children
            arguments = args if args else []
        else:
            obj, method = children
            arguments = []
        return ast.MethodCall(object=obj.name, method=method.name, arguments=arguments)

    def arguments(self, children: List[Any]) -> List[ast.ASTNode]:
        return children

    def value(self, children: List[Any]) -> ast.ValueType:
        return children[0]

    def string(self, children: List[Any]) -> ast.StringValue:
        # Remove quotes from string
        value = children[0].value[1:-1]  # Remove surrounding quotes
        # Handle escape sequences
        value = value.replace('\\"', '"').replace('\\\\', '\\')
        return ast.StringValue(value=value)

    def number(self, children: List[Any]) -> ast.NumberValue:
        value = children[0].value
        if '.' in value:
            return ast.NumberValue(value=float(value))
        else:
            return ast.NumberValue(value=int(value))

    def boolean(self, children: List[Any]) -> ast.BooleanValue:
        return ast.BooleanValue(value=children[0].value == "true")

    def list(self, children: List[Any]) -> ast.ListValue:
        # Skip brackets, get elements
        if len(children) <= 2:  # Just brackets
            return ast.ListValue(elements=[])
        elements = children[1:-1]  # Skip [ and ]
        return ast.ListValue(elements=elements)

    def dict(self, children: List[Any]) -> ast.DictValue:
        # Skip braces, get pairs
        if len(children) <= 2:  # Just braces
            return ast.DictValue(pairs=[])
        pairs = children[1:-1]  # Skip { and }
        return ast.DictValue(pairs=pairs)

    def dict_pair(self, children: List[Any]) -> tuple[Union[str, ast.ASTNode], ast.ASTNode]:
        key, _, value = children
        if hasattr(key, 'value'):
            return (key.value, value)
        else:
            return (key, value)

    # Phase 2: New transformer methods for imports, tools, and control flow

    def import_statement(self, children: List[Any]) -> ast.ImportStatement:
        module_path, import_list = children
        return ast.ImportStatement(module_path=module_path, import_list=import_list)

    def module_path(self, children: List[Any]) -> ast.ModulePath:
        # Extract identifier names from tokens
        path_parts = [child.name for child in children]
        return ast.ModulePath(path=path_parts)

    def import_list(self, children: List[Any]) -> ast.ImportList:
        # Extract identifier names from tokens
        imports = [child.name for child in children]
        return ast.ImportList(imports=imports)

    def tool_assignment(self, children: List[Any]) -> ast.ToolAssignment:
        if len(children) == 3:
            # agent_name, operator, tool_list
            agent_name, operator, tool_list = children
            op = operator if isinstance(operator, str) else "="
        elif len(children) == 2:
            # agent_name, tool_list (operator removed by Lark)
            agent_name, tool_list = children
            op = "="
        else:
            raise ValueError(f"Unexpected number of children in tool_assignment: {len(children)}")

        return ast.ToolAssignment(
            agent_name=agent_name.name,
            operator=op,
            tool_list=tool_list
        )

    def tool_operator(self, children: List[Any]) -> str:
        # Lark removes literal tokens, so we need to infer from context
        # This will be handled by the parent rule
        return children[0] if children else "="

    def tool_list(self, children: List[Any]) -> ast.ToolList:
        return ast.ToolList(tools=children)

    def tool_spec(self, children: List[Any]) -> Union[ast.ToolSpec, ast.AgentRouting]:
        if hasattr(children[0], 'name'):
            # Simple identifier token
            return ast.ToolSpec(name=children[0].name)
        else:
            # AgentRouting object
            return children[0]

    def agent_routing(self, children: List[Any]) -> ast.AgentRouting:
        tool_name, agent_list = children
        return ast.AgentRouting(tool_name=tool_name.name, agent_list=agent_list)

    def identifier_list(self, children: List[Any]) -> List[str]:
        return [child.name for child in children]

    def if_statement(self, children: List[Any]) -> ast.IfStatement:
        # First child is always the condition
        condition = children[0]

        # The rest are statements - we need to figure out which are then_statements vs else_statements
        # For now, assume no else clause and all remaining are then_statements
        # TODO: Handle else clause properly when we encounter it
        then_statements = children[1:]

        return ast.IfStatement(
            condition=condition,
            then_statements=then_statements,
            else_statements=None
        )

    def condition(self, children: List[Any]) -> ast.ASTNode:
        return children[0]

    def boolean_expression(self, children: List[Any]) -> ast.BooleanExpression:
        if len(children) == 1:
            # Single expression (no operator)
            return ast.BooleanExpression(left=children[0], operator=None, right=None)
        elif len(children) == 3:
            # left operator right
            left, operator, right = children
            return ast.BooleanExpression(left=left, operator=operator, right=right)
        else:
            # Handle parentheses or other cases
            return children[0]

    def comparison_expression(self, children: List[Any]) -> ast.ComparisonExpression:
        if len(children) == 3:
            # left operator right
            left, operator, right = children
            return ast.ComparisonExpression(left=left, operator=operator, right=right)
        else:
            # Single method call or expression
            return children[0]

    def comparison_operator(self, children: List[Any]) -> str:
        # Lark removes literal tokens, so this might be empty
        return children[0] if children else "=="

    def f_string(self, children: List[Any]) -> ast.FString:
        # Remove F_STRING_START and F_STRING_END, keep contents
        contents = children[1:-1] if len(children) > 2 else []
        return ast.FString(contents=contents)

    def f_string_content(self, children: List[Any]) -> ast.FStringContent:
        if len(children) == 1:
            # Text content
            if hasattr(children[0], 'value'):
                return ast.FStringContent(text=children[0].value)
            else:
                # Expression content
                return ast.FStringContent(expression=children[0])
        else:
            # Expression in braces
            return ast.FStringContent(expression=children[1])  # Skip braces

    def argument(self, children: List[Any]) -> Union[ast.ASTNode, ast.NamedArgument]:
        if len(children) == 1:
            # Regular argument
            return children[0]
        else:
            # Named argument: name = value
            name, value = children
            return ast.NamedArgument(name=name.name, value=value)

    # Enhanced method call that handles named arguments
    def enhanced_method_call(self, children: List[Any]) -> ast.EnhancedMethodCall:
        if len(children) == 3:
            obj, method, args = children
            arguments = args if args else []
        else:
            obj, method = children
            arguments = []
        return ast.EnhancedMethodCall(object=obj.name, method=method.name, arguments=arguments)

    # Handle terminals
    def IDENTIFIER(self, token) -> ast.Identifier:
        return ast.Identifier(name=token.value)

    def MODEL_PATH(self, token) -> str:
        return token

    def ESCAPED_STRING(self, token) -> str:
        return token

    def F_STRING_START(self, token) -> str:
        return token

    def F_STRING_END(self, token) -> str:
        return token

    def F_STRING_TEXT(self, token) -> str:
        return token


class AgenticScriptParser:
    """Main parser class for AgenticScript."""

    def __init__(self):
        # Load grammar from file
        grammar_path = Path(__file__).parent / "grammar.lark"
        with open(grammar_path, 'r') as f:
            grammar = f.read()

        self.parser = Lark(
            grammar,
            parser='lalr',
            transformer=AgenticScriptTransformer(),
            debug=False
        )

    def parse(self, source_code: str) -> ast.Program:
        """Parse AgenticScript source code into AST."""
        try:
            result = self.parser.parse(source_code)
            return result
        except LarkError as e:
            raise SyntaxError(f"Parse error: {e}")

    def parse_file(self, file_path: str) -> ast.Program:
        """Parse AgenticScript file into AST."""
        with open(file_path, 'r') as f:
            source_code = f.read()
        return self.parse(source_code)


# Convenience function
def parse_agenticscript(source_code: str) -> ast.Program:
    """Parse AgenticScript source code into AST."""
    parser = AgenticScriptParser()
    return parser.parse(source_code)