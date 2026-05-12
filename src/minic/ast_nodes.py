"""Abstract Syntax Tree node definitions for Mini-C."""

from __future__ import annotations

from dataclasses import dataclass


class ASTNode:
    pass


class Statement(ASTNode):
    pass


class Expression(ASTNode):
    pass


@dataclass(frozen=True)
class Program(ASTNode):
    statements: list[Statement]


@dataclass(frozen=True)
class Block(Statement):
    statements: list[Statement]


@dataclass(frozen=True)
class VarDeclaration(Statement):
    var_type: str
    name: str
    initializer: Expression | None = None


@dataclass(frozen=True)
class ArrayDeclaration(Statement):
    element_type: str
    name: str
    size: int


@dataclass(frozen=True)
class Assignment(Statement):
    target: "Location"
    value: Expression


@dataclass(frozen=True)
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Statement | None = None


@dataclass(frozen=True)
class WhileStatement(Statement):
    condition: Expression
    body: Statement


@dataclass(frozen=True)
class PrintStatement(Statement):
    expression: Expression


@dataclass(frozen=True)
class Location(Expression):
    name: str
    index: Expression | None = None


@dataclass(frozen=True)
class Literal(Expression):
    value: int | float
    literal_type: str


@dataclass(frozen=True)
class UnaryExpression(Expression):
    operator: str
    operand: Expression


@dataclass(frozen=True)
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

