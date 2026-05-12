"""Simple tree-walking interpreter for Mini-C."""

from __future__ import annotations

from . import ast_nodes as ast


class RuntimeError(Exception):
    """Raised when a Mini-C program encounters an error during execution."""


class Interpreter:
    def __init__(self):
        self.scopes: list[dict[str, int | float | list]] = [{}]
        self.output_lines: list[str] = []

    def execute(self, program: ast.Program) -> str:
        for statement in program.statements:
            self._exec_statement(statement)
        return "\n".join(self.output_lines)

    def _exec_statement(self, statement: ast.Statement) -> None:
        if isinstance(statement, ast.VarDeclaration):
            value = 0 if statement.var_type == "int" else 0.0
            if statement.initializer is not None:
                value = self._eval(statement.initializer)
                if statement.var_type == "int":
                    value = int(value)
            self._define(statement.name, value)

        elif isinstance(statement, ast.ArrayDeclaration):
            self._define(statement.name, [0] * statement.size)

        elif isinstance(statement, ast.Assignment):
            value = self._eval(statement.value)
            if statement.target.index is not None:
                arr = self._resolve(statement.target.name)
                idx = int(self._eval(statement.target.index))
                if idx < 0 or idx >= len(arr):
                    raise RuntimeError(
                        f"Array index {idx} out of bounds for '{statement.target.name}' "
                        f"(size {len(arr)})"
                    )
                arr[idx] = value
            else:
                self._assign(statement.target.name, value)

        elif isinstance(statement, ast.PrintStatement):
            value = self._eval(statement.expression)
            # Format: drop trailing .0 for whole floats to match C-style output
            if isinstance(value, float) and value == int(value):
                self.output_lines.append(str(int(value)))
            else:
                self.output_lines.append(str(value))

        elif isinstance(statement, ast.IfStatement):
            condition = self._eval(statement.condition)
            if condition:
                self._exec_statement(statement.then_branch)
            elif statement.else_branch is not None:
                self._exec_statement(statement.else_branch)

        elif isinstance(statement, ast.WhileStatement):
            limit = 100_000
            iterations = 0
            while self._eval(statement.condition):
                self._exec_statement(statement.body)
                iterations += 1
                if iterations >= limit:
                    raise RuntimeError(
                        f"Infinite loop detected (exceeded {limit} iterations)"
                    )

        elif isinstance(statement, ast.Block):
            self.scopes.append({})
            for nested in statement.statements:
                self._exec_statement(nested)
            self.scopes.pop()

    def _eval(self, expression: ast.Expression) -> int | float:
        if isinstance(expression, ast.Literal):
            return expression.value

        if isinstance(expression, ast.Location):
            value = self._resolve(expression.name)
            if expression.index is not None:
                idx = int(self._eval(expression.index))
                if idx < 0 or idx >= len(value):
                    raise RuntimeError(
                        f"Array index {idx} out of bounds for '{expression.name}' "
                        f"(size {len(value)})"
                    )
                return value[idx]
            return value

        if isinstance(expression, ast.UnaryExpression):
            operand = self._eval(expression.operand)
            if expression.operator == "-":
                return -operand
            raise RuntimeError(f"Unknown unary operator: {expression.operator}")

        if isinstance(expression, ast.BinaryExpression):
            left = self._eval(expression.left)
            right = self._eval(expression.right)
            return self._binary_op(expression.operator, left, right)

        raise RuntimeError(f"Unsupported expression: {type(expression).__name__}")

    def _binary_op(self, op: str, left: int | float, right: int | float) -> int | float:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        if op == "<":
            return int(left < right)
        if op == ">":
            return int(left > right)
        if op == "<=":
            return int(left <= right)
        if op == ">=":
            return int(left >= right)
        if op == "==":
            return int(left == right)
        if op == "!=":
            return int(left != right)
        raise RuntimeError(f"Unknown operator: {op}")

    def _define(self, name: str, value) -> None:
        self.scopes[-1][name] = value

    def _resolve(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"Undefined variable: {name}")

    def _assign(self, name: str, value) -> None:
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        raise RuntimeError(f"Undefined variable: {name}")
