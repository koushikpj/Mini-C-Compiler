"""Lexical analysis for Mini-C."""

from __future__ import annotations

from .tokens import Token, TokenType


KEYWORDS = {
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
}


SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.ASSIGN,
    "<": TokenType.LT,
    ">": TokenType.GT,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}


TWO_CHAR_TOKENS = {
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
}


class LexicalError(Exception):
    """Raised when the lexer finds a character sequence Mini-C does not support."""


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1
        self.tokens: list[Token] = []

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def _scan_token(self) -> None:
        char = self._advance()

        if char in " \r\t":
            return
        if char == "\n":
            self.line += 1
            self.column = 1
            return

        if char == "/" and self._match("/"):
            self._skip_line_comment()
            return

        two_char = char + self._peek()
        if two_char in TWO_CHAR_TOKENS:
            self._advance()
            self._add_token(TWO_CHAR_TOKENS[two_char])
            return

        if char in SINGLE_CHAR_TOKENS:
            self._add_token(SINGLE_CHAR_TOKENS[char])
            return

        if char.isdigit():
            self._number()
            return

        if self._is_identifier_start(char):
            self._identifier()
            return

        message = (
            f"Lexical error at line {self.start_line}, column {self.start_column}: "
            f"unexpected character {char!r}"
        )
        raise LexicalError(message)

    def _identifier(self) -> None:
        while self._is_identifier_part(self._peek()):
            self._advance()

        lexeme = self.source[self.start : self.current]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()

        token_type = TokenType.INT_LITERAL
        if self._peek() == "." and self._peek_next().isdigit():
            token_type = TokenType.FLOAT_LITERAL
            self._advance()
            while self._peek().isdigit():
                self._advance()

        self._add_token(token_type)

    def _skip_line_comment(self) -> None:
        while self._peek() != "\n" and not self._is_at_end():
            self._advance()

    def _add_token(self, token_type: TokenType) -> None:
        lexeme = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, lexeme, self.start_line, self.start_column))

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        next_index = self.current + 1
        if next_index >= len(self.source):
            return "\0"
        return self.source[next_index]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char.isalpha() or char == "_"

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return char.isalnum() or char == "_"

