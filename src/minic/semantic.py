"""Semantic analysis and symbol table construction for Mini-C."""

from __future__ import annotations

from dataclasses import dataclass

from . import ast_nodes as ast


@dataclass(frozen=True)
class Symbol:
    name: str
    type: str
    scope: str
    kind: str
    size: int | None = None


class SemanticError(Exception):
    """Raised when a Mini-C program is syntactically valid but semantically invalid."""


class SemanticAnalyzer:
    def __init__(self):
        self.scopes: list[dict[str, Symbol]] = [{}]
        self.scope_names: list[str] = ["global"]
        self.symbols: list[Symbol] = []
        self.errors: list[str] = []
        self.block_counter = 0

    def analyze(self, program: ast.Program) -> list[Symbol]:
        for statement in program.statements:
            self._analyze_statement(statement)

        if self.errors:
            raise SemanticError("\n".join(self.errors))

        return self.symbols

    def _analyze_statement(self, statement: ast.Statement) -> None:
        if isinstance(statement, ast.VarDeclaration):
            self._declare_variable(statement)
        elif isinstance(statement, ast.ArrayDeclaration):
            self._declare_array(statement)
        elif isinstance(statement, ast.Assignment):
            self._analyze_assignment(statement)
        elif isinstance(statement, ast.IfStatement):
            self._expression_type(statement.condition)
            self._analyze_statement(statement.then_branch)
            if statement.else_branch is not None:
                self._analyze_statement(statement.else_branch)
        elif isinstance(statement, ast.WhileStatement):
            self._expression_type(statement.condition)
            self._analyze_statement(statement.body)
        elif isinstance(statement, ast.PrintStatement):
            self._expression_type(statement.expression)
        elif isinstance(statement, ast.Block):
            self._enter_scope()
            for nested_statement in statement.statements:
                self._analyze_statement(nested_statement)
            self._exit_scope()
        else:
            self._error(f"unsupported statement type {type(statement).__name__}")

    def _declare_variable(self, declaration: ast.VarDeclaration) -> None:
        symbol = Symbol(
            name=declaration.name,
            type=declaration.var_type,
            scope=self._current_scope_name(),
            kind="var",
        )
        self._define(symbol)

        if declaration.initializer is not None:
            value_type = self._expression_type(declaration.initializer)
            self._check_assignment_compatible(declaration.var_type, value_type, declaration.name)

    def _declare_array(self, declaration: ast.ArrayDeclaration) -> None:
        if declaration.element_type != "int":
            self._error(f"array '{declaration.name}' must have type int")
        if declaration.size <= 0:
            self._error(f"array '{declaration.name}' size must be positive")

        symbol = Symbol(
            name=declaration.name,
            type=f"{declaration.element_type}[]",
            scope=self._current_scope_name(),
            kind="array",
            size=declaration.size,
        )
        self._define(symbol)

    def _analyze_assignment(self, assignment: ast.Assignment) -> None:
        target_symbol = self._resolve(assignment.target.name)
        target_type = "error"

        if target_symbol is None:
            self._error(f"variable '{assignment.target.name}' used before declaration")
        elif target_symbol.kind == "array":
            if assignment.target.index is None:
                self._error(f"cannot assign directly to array '{assignment.target.name}'")
            else:
                self._check_array_index(assignment.target)
                target_type = target_symbol.type.removesuffix("[]")
        else:
            if assignment.target.index is not None:
                self._error(f"variable '{assignment.target.name}' is not an array")
                self._expression_type(assignment.target.index)
            target_type = target_symbol.type

        value_type = self._expression_type(assignment.value)
        self._check_assignment_compatible(target_type, value_type, assignment.target.name)

    def _expression_type(self, expression: ast.Expression) -> str:
        if isinstance(expression, ast.Literal):
            return expression.literal_type
        if isinstance(expression, ast.Location):
            return self._location_type(expression)
        if isinstance(expression, ast.UnaryExpression):
            operand_type = self._expression_type(expression.operand)
            if operand_type not in {"int", "float", "error"}:
                self._error(f"operator '{expression.operator}' cannot be applied to {operand_type}")
                return "error"
            return operand_type
        if isinstance(expression, ast.BinaryExpression):
            left_type = self._expression_type(expression.left)
            right_type = self._expression_type(expression.right)
            return self._binary_type(expression.operator, left_type, right_type)

        self._error(f"unsupported expression type {type(expression).__name__}")
        return "error"

    def _location_type(self, location: ast.Location) -> str:
        symbol = self._resolve(location.name)
        if symbol is None:
            self._error(f"variable '{location.name}' used before declaration")
            if location.index is not None:
                self._expression_type(location.index)
            return "error"

        if symbol.kind == "array":
            if location.index is None:
                return symbol.type
            self._check_array_index(location)
            return symbol.type.removesuffix("[]")

        if location.index is not None:
            self._error(f"variable '{location.name}' is not an array")
            self._expression_type(location.index)
            return "error"

        return symbol.type

    def _check_array_index(self, location: ast.Location) -> None:
        if location.index is None:
            return
        index_type = self._expression_type(location.index)
        if index_type != "int" and index_type != "error":
            self._error(f"array index for '{location.name}' must be int")

    def _binary_type(self, operator: str, left_type: str, right_type: str) -> str:
        if "error" in {left_type, right_type}:
            return "error"

        if operator in {"+", "-", "*", "/"}:
            if left_type not in {"int", "float"} or right_type not in {"int", "float"}:
                self._error(f"operator '{operator}' requires numeric operands")
                return "error"
            if "float" in {left_type, right_type}:
                return "float"
            return "int"

        if operator in {"<", ">", "<=", ">=", "==", "!="}:
            if left_type not in {"int", "float"} or right_type not in {"int", "float"}:
                self._error(f"operator '{operator}' requires numeric operands")
                return "error"
            return "int"

        self._error(f"unsupported binary operator '{operator}'")
        return "error"

    def _check_assignment_compatible(self, target_type: str, value_type: str, name: str) -> None:
        if "error" in {target_type, value_type}:
            return
        if target_type == value_type:
            return
        if target_type == "float" and value_type == "int":
            return
        self._error(f"cannot assign {value_type} value to {target_type} variable '{name}'")

    def _define(self, symbol: Symbol) -> None:
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            self._error(
                f"duplicate declaration of '{symbol.name}' in scope '{self._current_scope_name()}'"
            )
            return

        current_scope[symbol.name] = symbol
        self.symbols.append(symbol)

    def _resolve(self, name: str) -> Symbol | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _enter_scope(self) -> None:
        self.block_counter += 1
        self.scopes.append({})
        self.scope_names.append(f"block{self.block_counter}")

    def _exit_scope(self) -> None:
        self.scopes.pop()
        self.scope_names.pop()

    def _current_scope_name(self) -> str:
        return self.scope_names[-1]

    def _error(self, message: str) -> None:
        self.errors.append(f"Semantic error: {message}")


def format_symbol_table(symbols: list[Symbol]) -> str:
    headers = ["Name", "Type", "Scope", "Kind", "Size"]
    rows = [
        [symbol.name, symbol.type, symbol.scope, symbol.kind, str(symbol.size or "-")]
        for symbol in symbols
    ]
    widths = [
        max(len(row[index]) for row in [headers, *rows]) if rows else len(headers[index])
        for index in range(len(headers))
    ]

    def format_row(row: list[str]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    lines = [format_row(headers), format_row(["-" * width for width in widths])]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)

