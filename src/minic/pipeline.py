"""Shared compiler pipeline helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser, format_ast
from .semantic import SemanticAnalyzer, format_symbol_table
from .tac import TACGenerator, format_tac
from .tokens import Token


@dataclass(frozen=True)
class CompilerResult:
    tokens: list[Token]
    ast: str
    symbols: str
    tac: str
    output: str


def format_tokens(tokens: list[Token]) -> str:
    return "\n".join(str(token) for token in tokens)


def run_pipeline(source: str) -> CompilerResult:
    tokens = Lexer(source).scan_tokens()
    program = Parser(tokens).parse()
    symbols = SemanticAnalyzer().analyze(program)
    instructions = TACGenerator().generate(program)
    program_output = Interpreter().execute(program)

    return CompilerResult(
        tokens=tokens,
        ast=format_ast(program),
        symbols=format_symbol_table(symbols),
        tac=format_tac(instructions),
        output=program_output,
    )


def section(title: str, body: str) -> str:
    if body:
        return f"{title}\n{'-' * len(title)}\n{body}"
    return f"{title}\n{'-' * len(title)}"


def format_stage_output(result: CompilerResult, stage: str) -> str:
    if stage == "output":
        return section("PROGRAM OUTPUT", result.output if result.output else "(no output)")
    if stage == "tokens":
        return section("TOKENS", format_tokens(result.tokens))
    if stage == "ast":
        return section("AST", result.ast)
    if stage == "symbols":
        return section("SYMBOL TABLE", result.symbols)
    if stage == "tac":
        return section("THREE-ADDRESS CODE", result.tac)
    if stage == "all":
        return "\n\n".join(
            [
                section("TOKENS", format_tokens(result.tokens)),
                section("AST", result.ast),
                section("SYMBOL TABLE", result.symbols),
                section("THREE-ADDRESS CODE", result.tac),
            ]
        )

    raise ValueError(f"Unknown compiler stage: {stage}")

