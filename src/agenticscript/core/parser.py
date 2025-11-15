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
        _, name, _, _, constructor = children
        return ast.AgentDeclaration(name=name.value, constructor=constructor)

    def agent_constructor(self, children: List[Any]) -> ast.AgentConstructor:
        _, _, config, _ = children
        if isinstance(config, ast.ModelSpec):
            # Only model specified
            return ast.AgentConstructor(model=config, config=[])
        else:
            # Model + additional config
            model = config[0]
            config_pairs = config[1:] if len(config) > 1 else []
            return ast.AgentConstructor(model=model, config=config_pairs)

    def agent_config(self, children: List[Any]) -> List[Union[ast.ModelSpec, ast.ConfigPair]]:
        return children

    def model_spec(self, children: List[Any]) -> ast.ModelSpec:
        return ast.ModelSpec(path=children[0].value)

    def config_pair(self, children: List[Any]) -> ast.ConfigPair:
        key, _, value = children
        return ast.ConfigPair(key=key.value, value=value)

    def property_assignment(self, children: List[Any]) -> ast.PropertyAssignment:
        _, agent_name, _, prop_name, _, value = children
        return ast.PropertyAssignment(
            agent_name=agent_name.value,
            property_name=prop_name.value,
            value=value
        )

    def print_statement(self, children: List[Any]) -> ast.PrintStatement:
        _, _, expr, _ = children
        return ast.PrintStatement(expression=expr)

    def expression_statement(self, children: List[Any]) -> ast.ExpressionStatement:
        return ast.ExpressionStatement(expression=children[0])

    def expression(self, children: List[Any]) -> ast.ExpressionType:
        return children[0]

    def property_access(self, children: List[Any]) -> ast.PropertyAccess:
        obj, _, prop = children
        return ast.PropertyAccess(object=obj.value, property=prop.value)

    def method_call(self, children: List[Any]) -> ast.MethodCall:
        obj, _, method, _, args = children[:5]
        arguments = args if args else []
        return ast.MethodCall(object=obj.value, method=method.value, arguments=arguments)

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

    # Handle terminals
    def IDENTIFIER(self, token) -> ast.Identifier:
        return ast.Identifier(name=token.value)

    def MODEL_PATH(self, token) -> str:
        return token

    def ESCAPED_STRING(self, token) -> str:
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