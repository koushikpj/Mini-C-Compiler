"""Recursive descent parser for Mini-C."""

from __future__ import annotations

from . import ast_nodes as ast
from .tokens import Token, TokenType


class ParseError(Exception):
    """Raised when token order does not match the Mini-C grammar."""


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ast.Program:
        statements = []
        while not self._check(TokenType.EOF):
            statements.append(self._statement())
        self._consume(TokenType.EOF, "Expected end of file.")
        return ast.Program(statements)

    def _statement(self) -> ast.Statement:
        if self._match(TokenType.INT, TokenType.FLOAT):
            return self._declaration(self._previous())
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.PRINT):
            statement = self._print_statement()
            self._consume(TokenType.SEMICOLON, "Expected ';' after print statement.")
            return statement
        if self._match(TokenType.LBRACE):
            return self._block()
        if self._check(TokenType.IDENTIFIER):
            statement = self._assignment()
            self._consume(TokenType.SEMICOLON, "Expected ';' after assignment.")
            return statement

        raise self._error(self._peek(), "Expected statement.")

    def _block(self) -> ast.Block:
        statements = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            statements.append(self._statement())

        self._consume(TokenType.RBRACE, "Expected '}' after block.")
        return ast.Block(statements)

    def _declaration(self, type_token: Token) -> ast.Statement:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name after type.")

        if self._match(TokenType.LBRACKET):
            size = self._consume(TokenType.INT_LITERAL, "Expected integer array size.")
            self._consume(TokenType.RBRACKET, "Expected ']' after array size.")
            self._consume(TokenType.SEMICOLON, "Expected ';' after array declaration.")
            return ast.ArrayDeclaration(type_token.lexeme, name.lexeme, int(size.lexeme))

        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return ast.VarDeclaration(type_token.lexeme, name.lexeme, initializer)

    def _assignment(self) -> ast.Assignment:
        target = self._location()
        self._consume(TokenType.ASSIGN, "Expected '=' in assignment.")
        value = self._expression()
        return ast.Assignment(target, value)

    def _if_statement(self) -> ast.IfStatement:
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition.")
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return ast.IfStatement(condition, then_branch, else_branch)

    def _while_statement(self) -> ast.WhileStatement:
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while condition.")
        body = self._statement()
        return ast.WhileStatement(condition, body)

    def _print_statement(self) -> ast.PrintStatement:
        self._consume(TokenType.LPAREN, "Expected '(' after 'print'.")
        expression = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after print expression.")
        return ast.PrintStatement(expression)

    def _expression(self) -> ast.Expression:
        return self._equality()

    def _equality(self) -> ast.Expression:
        expression = self._comparison()

        while self._match(TokenType.EQ, TokenType.NEQ):
            operator = self._previous().lexeme
            right = self._comparison()
            expression = ast.BinaryExpression(expression, operator, right)

        return expression

    def _comparison(self) -> ast.Expression:
        expression = self._term()

        while self._match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self._previous().lexeme
            right = self._term()
            expression = ast.BinaryExpression(expression, operator, right)

        return expression

    def _term(self) -> ast.Expression:
        expression = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().lexeme
            right = self._factor()
            expression = ast.BinaryExpression(expression, operator, right)

        return expression

    def _factor(self) -> ast.Expression:
        expression = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous().lexeme
            right = self._unary()
            expression = ast.BinaryExpression(expression, operator, right)

        return expression

    def _unary(self) -> ast.Expression:
        if self._match(TokenType.MINUS):
            operator = self._previous().lexeme
            operand = self._unary()
            return ast.UnaryExpression(operator, operand)

        return self._primary()

    def _primary(self) -> ast.Expression:
        if self._match(TokenType.INT_LITERAL):
            return ast.Literal(int(self._previous().lexeme), "int")
        if self._match(TokenType.FLOAT_LITERAL):
            return ast.Literal(float(self._previous().lexeme), "float")
        if self._check(TokenType.IDENTIFIER):
            return self._location()
        if self._match(TokenType.LPAREN):
            expression = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expression

        raise self._error(self._peek(), "Expected expression.")

    def _location(self) -> ast.Location:
        name = self._consume(TokenType.IDENTIFIER, "Expected identifier.")
        index = None
        if self._match(TokenType.LBRACKET):
            index = self._expression()
            self._consume(TokenType.RBRACKET, "Expected ']' after array index.")
        return ast.Location(name.lexeme, index)

    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, token: Token, message: str) -> ParseError:
        if token.type == TokenType.EOF:
            location = f"line {token.line}, column {token.column} at end"
        else:
            location = f"line {token.line}, column {token.column} near {token.lexeme!r}"
        return ParseError(f"Syntax error at {location}: {message}")


def _tree_lines(node: ast.ASTNode) -> list[str]:
    """Return lines for a visual tree representation of an AST node."""

    if isinstance(node, ast.Program):
        return _branch("Program", [("stmt", s) for s in node.statements])

    if isinstance(node, ast.Block):
        return _branch("Block", [("stmt", s) for s in node.statements])

    if isinstance(node, ast.VarDeclaration):
        children = [("type", node.var_type), ("name", node.name)]
        if node.initializer is not None:
            children.append(("init", node.initializer))
        return _branch("VarDecl", children)

    if isinstance(node, ast.ArrayDeclaration):
        return _branch("ArrayDecl", [
            ("type", node.element_type),
            ("name", node.name),
            ("size", node.size),
        ])

    if isinstance(node, ast.Assignment):
        return _branch("Assign", [("target", node.target), ("value", node.value)])

    if isinstance(node, ast.IfStatement):
        children = [("cond", node.condition), ("then", node.then_branch)]
        if node.else_branch is not None:
            children.append(("else", node.else_branch))
        return _branch("If", children)

    if isinstance(node, ast.WhileStatement):
        return _branch("While", [("cond", node.condition), ("body", node.body)])

    if isinstance(node, ast.PrintStatement):
        return _branch("Print", [("expr", node.expression)])

    if isinstance(node, ast.BinaryExpression):
        return _branch(f"BinOp [{node.operator}]", [
            ("left", node.left),
            ("right", node.right),
        ])

    if isinstance(node, ast.UnaryExpression):
        return _branch(f"UnaryOp [{node.operator}]", [("operand", node.operand)])

    if isinstance(node, ast.Location):
        if node.index is not None:
            return _branch(f"Location [{node.name}]", [("index", node.index)])
        return [f"Location [{node.name}]"]

    if isinstance(node, ast.Literal):
        return [f"Literal [{node.value}] ({node.literal_type})"]

    return [repr(node)]


def _branch(label: str, children: list[tuple[str, object]]) -> list[str]:
    """Build tree lines for a node with labelled children."""
    lines = [label]
    for i, (child_label, child) in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        if isinstance(child, ast.ASTNode):
            child_lines = _tree_lines(child)
            lines.append(f"{connector}{child_label}: {child_lines[0]}")
            for extra_line in child_lines[1:]:
                lines.append(f"{extension}{extra_line}")
        else:
            lines.append(f"{connector}{child_label}: {child}")

    return lines


def format_ast(node: ast.ASTNode) -> str:
    return "\n".join(_tree_lines(node))

