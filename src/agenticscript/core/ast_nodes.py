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


# Union type for any value
ValueType = Union[StringValue, NumberValue, BooleanValue, ListValue, DictValue, Identifier]
ExpressionType = Union[PropertyAccess, MethodCall, ValueType]
StatementType = Union[AgentDeclaration, PropertyAssignment, PrintStatement, ExpressionStatement]