import unittest

from src.minic import Lexer, LexicalError, TokenType


class LexerTests(unittest.TestCase):
    def token_types(self, source):
        return [token.type for token in Lexer(source).scan_tokens()]

    def test_declaration_and_assignment_tokens(self):
        source = "int x;\nfloat y = 10.5;\nx = 5 + 3 * 2;"

        self.assertEqual(
            self.token_types(source),
            [
                TokenType.INT,
                TokenType.IDENTIFIER,
                TokenType.SEMICOLON,
                TokenType.FLOAT,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.FLOAT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.INT_LITERAL,
                TokenType.PLUS,
                TokenType.INT_LITERAL,
                TokenType.STAR,
                TokenType.INT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ],
        )

    def test_control_flow_and_relational_tokens(self):
        source = "if (x >= 10) { print(x); } else { while (x != 0) x = x - 1; }"

        self.assertEqual(
            self.token_types(source),
            [
                TokenType.IF,
                TokenType.LPAREN,
                TokenType.IDENTIFIER,
                TokenType.GTE,
                TokenType.INT_LITERAL,
                TokenType.RPAREN,
                TokenType.LBRACE,
                TokenType.PRINT,
                TokenType.LPAREN,
                TokenType.IDENTIFIER,
                TokenType.RPAREN,
                TokenType.SEMICOLON,
                TokenType.RBRACE,
                TokenType.ELSE,
                TokenType.LBRACE,
                TokenType.WHILE,
                TokenType.LPAREN,
                TokenType.IDENTIFIER,
                TokenType.NEQ,
                TokenType.INT_LITERAL,
                TokenType.RPAREN,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.IDENTIFIER,
                TokenType.MINUS,
                TokenType.INT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.RBRACE,
                TokenType.EOF,
            ],
        )

    def test_comments_are_ignored(self):
        source = "int x; // comment\nx = 1;"

        self.assertEqual(
            self.token_types(source),
            [
                TokenType.INT,
                TokenType.IDENTIFIER,
                TokenType.SEMICOLON,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.INT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ],
        )

    def test_invalid_character_raises_lexical_error(self):
        with self.assertRaisesRegex(LexicalError, "unexpected character '@'"):
            Lexer("x = 10 @ 2;").scan_tokens()


if __name__ == "__main__":
    unittest.main()
