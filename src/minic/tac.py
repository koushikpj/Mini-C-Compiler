"""Three-address code generation for Mini-C."""

from __future__ import annotations

from . import ast_nodes as ast


class TACGenerator:
    def __init__(self):
        self.instructions: list[str] = []
        self.temp_count = 0
        self.label_count = 0

    def generate(self, program: ast.Program) -> list[str]:
        for statement in program.statements:
            self._statement(statement)
        return self.instructions

    def _statement(self, statement: ast.Statement) -> None:
        if isinstance(statement, ast.VarDeclaration):
            if statement.initializer is not None:
                value = self._expression(statement.initializer)
                self.instructions.append(f"{statement.name} = {value}")
        elif isinstance(statement, ast.ArrayDeclaration):
            self.instructions.append(f"{statement.name} = alloc {statement.size}")
        elif isinstance(statement, ast.Assignment):
            value = self._expression(statement.value)
            target = self._location(statement.target)
            self.instructions.append(f"{target} = {value}")
        elif isinstance(statement, ast.PrintStatement):
            value = self._expression(statement.expression)
            self.instructions.append(f"param {value}")
            self.instructions.append("call print, 1")
        elif isinstance(statement, ast.Block):
            for nested_statement in statement.statements:
                self._statement(nested_statement)
        elif isinstance(statement, ast.IfStatement):
            self._if_statement(statement)
        elif isinstance(statement, ast.WhileStatement):
            self._while_statement(statement)

    def _if_statement(self, statement: ast.IfStatement) -> None:
        else_label = self._new_label()
        end_label = self._new_label()
        condition = self._expression(statement.condition)

        self.instructions.append(f"ifFalse {condition} goto {else_label}")
        self._statement(statement.then_branch)

        if statement.else_branch is None:
            self.instructions.append(f"{else_label}:")
            return

        self.instructions.append(f"goto {end_label}")
        self.instructions.append(f"{else_label}:")
        self._statement(statement.else_branch)
        self.instructions.append(f"{end_label}:")

    def _while_statement(self, statement: ast.WhileStatement) -> None:
        start_label = self._new_label()
        end_label = self._new_label()

        self.instructions.append(f"{start_label}:")
        condition = self._expression(statement.condition)
        self.instructions.append(f"ifFalse {condition} goto {end_label}")
        self._statement(statement.body)
        self.instructions.append(f"goto {start_label}")
        self.instructions.append(f"{end_label}:")

    def _expression(self, expression: ast.Expression) -> str:
        if isinstance(expression, ast.Literal):
            return str(expression.value)
        if isinstance(expression, ast.Location):
            return self._location(expression)
        if isinstance(expression, ast.UnaryExpression):
            operand = self._expression(expression.operand)
            temp = self._new_temp()
            self.instructions.append(f"{temp} = {expression.operator}{operand}")
            return temp
        if isinstance(expression, ast.BinaryExpression):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            temp = self._new_temp()
            self.instructions.append(f"{temp} = {left} {expression.operator} {right}")
            return temp

        raise TypeError(f"Unsupported expression type: {type(expression).__name__}")

    def _location(self, location: ast.Location) -> str:
        if location.index is None:
            return location.name
        index = self._expression(location.index)
        return f"{location.name}[{index}]"

    def _new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def _new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"


def format_tac(instructions: list[str]) -> str:
    return "\n".join(instructions)

