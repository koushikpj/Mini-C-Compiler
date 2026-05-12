"""Command-line interface for the Mini-C compiler."""

from __future__ import annotations

import argparse
from pathlib import Path

from .lexer import Lexer, LexicalError
from .parser import ParseError
from .pipeline import format_stage_output, format_tokens, run_pipeline
from .semantic import SemanticError


def print_section(title: str, body: str) -> None:
    print(title)
    print("-" * len(title))
    if body:
        print(body)


def compile_source(
    source: str,
    show_tokens: bool = False,
    show_ast: bool = False,
    show_symbols: bool = False,
    show_tac: bool = False,
    show_all: bool = False,
) -> int:
    if show_tokens:
        try:
            tokens = Lexer(source).scan_tokens()
        except LexicalError as error:
            print(error)
            return 1
        print_section("TOKENS", format_tokens(tokens))
        return 0

    try:
        result = run_pipeline(source)
    except (LexicalError, ParseError, SemanticError) as error:
        print(error)
        return 1

    if show_ast:
        print(format_stage_output(result, "ast"))
        return 0

    if show_symbols:
        print(format_stage_output(result, "symbols"))
        return 0

    if show_tac:
        print(format_stage_output(result, "tac"))
    elif show_all:
        print(format_stage_output(result, "all"))
    else:
        print("Lexical analysis completed successfully.")
        print(f"Token count: {len(result.tokens)}")
        print("Syntax analysis completed successfully.")
        print("Semantic analysis completed successfully.")

    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mini-C compiler")
    parser.add_argument("source", help="Path to a Mini-C source file")
    parser.add_argument("--tokens", action="store_true", help="Print lexer tokens")
    parser.add_argument("--ast", action="store_true", help="Print parser AST")
    parser.add_argument("--symbols", action="store_true", help="Print symbol table")
    parser.add_argument("--tac", action="store_true", help="Print three-address code")
    parser.add_argument("--all", action="store_true", help="Print all compiler stage outputs")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    source_path = Path(args.source)

    if not source_path.exists():
        print(f"Error: source file not found: {source_path}")
        return 1

    return compile_source(
        source_path.read_text(encoding="utf-8"),
        show_tokens=args.tokens,
        show_ast=args.ast,
        show_symbols=args.symbols,
        show_tac=args.tac,
        show_all=args.all,
    )
