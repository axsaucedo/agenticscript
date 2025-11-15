"""AST Node definitions for AgenticScript using Python dataclasses."""

from dataclasses import dataclass
from typing import Any, List, Optional, Union
from abc import ABC, abstractmethod


@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass


# Value nodes
@dataclass
class StringValue(ASTNode):
    value: str


@dataclass
class NumberValue(ASTNode):
    value: Union[int, float]


@dataclass
class BooleanValue(ASTNode):
    value: bool


@dataclass
class ListValue(ASTNode):
    elements: List[ASTNode]


@dataclass
class DictValue(ASTNode):
    pairs: List[tuple[Union[str, ASTNode], ASTNode]]


@dataclass
class Identifier(ASTNode):
    name: str


# Expression nodes
@dataclass
class PropertyAccess(ASTNode):
    object: str
    property: str


@dataclass
class MethodCall(ASTNode):
    object: str
    method: str
    arguments: List[ASTNode]


# Agent-specific nodes
@dataclass
class ModelSpec(ASTNode):
    path: str  # e.g., "openai/gpt-4o"


@dataclass
class ConfigPair(ASTNode):
    key: str
    value: ASTNode


@dataclass
class AgentConstructor(ASTNode):
    model: ModelSpec
    config: List[ConfigPair]


@dataclass
class AgentDeclaration(ASTNode):
    name: str
    constructor: AgentConstructor


@dataclass
class PropertyAssignment(ASTNode):
    agent_name: str
    property_name: str
    value: ASTNode


@dataclass
class AssignmentStatement(ASTNode):
    variable_name: str
    value: ASTNode


# Statement nodes
@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode


@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


# Phase 2: New AST nodes for imports, tools, and control flow

# Import-related nodes
@dataclass
class ModulePath(ASTNode):
    path: List[str]  # e.g., ["agenticscript", "stdlib", "tools"]


@dataclass
class ImportList(ASTNode):
    imports: List[str]  # e.g., ["WebSearch", "AgentRouting"]


@dataclass
class ImportStatement(ASTNode):
    module_path: ModulePath
    import_list: ImportList


# Tool-related nodes
@dataclass
class ToolSpec(ASTNode):
    name: str


@dataclass
class AgentRouting(ASTNode):
    tool_name: str
    agent_list: List[str]  # List of agent names


@dataclass
class ToolList(ASTNode):
    tools: List[Union[ToolSpec, AgentRouting]]


@dataclass
class ToolAssignment(ASTNode):
    agent_name: str
    operator: str  # "=" or "+="
    tool_list: ToolList


# Control flow nodes
@dataclass
class ComparisonExpression(ASTNode):
    left: ASTNode
    operator: str  # "==", "!=", "<", ">", "<=", ">="
    right: ASTNode


@dataclass
class BooleanExpression(ASTNode):
    left: ASTNode
    operator: Optional[str]  # "and", "or", or None for single expressions
    right: Optional[ASTNode]


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_statements: List[ASTNode]
    else_statements: Optional[List[ASTNode]] = None


# Enhanced method call with named arguments
@dataclass
class NamedArgument(ASTNode):
    name: str
    value: ASTNode


@dataclass
class EnhancedMethodCall(ASTNode):
    object: str
    method: str
    arguments: List[Union[ASTNode, NamedArgument]]


# F-string support
@dataclass
class FStringContent(ASTNode):
    text: Optional[str] = None
    expression: Optional[ASTNode] = None


@dataclass
class FString(ASTNode):
    contents: List[FStringContent]


# Union type for any value (updated for Phase 2)
ValueType = Union[StringValue, NumberValue, BooleanValue, ListValue, DictValue, Identifier, FString]
ExpressionType = Union[PropertyAccess, MethodCall, EnhancedMethodCall, ComparisonExpression, BooleanExpression, ValueType]
StatementType = Union[ImportStatement, AgentDeclaration, PropertyAssignment, ToolAssignment, IfStatement, PrintStatement, ExpressionStatement]