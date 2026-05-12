"""Token definitions for Mini-C."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    PRINT = "PRINT"

    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"

    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"

    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    EQ = "EQ"
    NEQ = "NEQ"
    ASSIGN = "ASSIGN"

    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"

    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.line}:{self.column:<3} {self.type.value:<14} {self.lexeme}"

