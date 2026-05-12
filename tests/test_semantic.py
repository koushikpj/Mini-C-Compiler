import unittest

from src.minic.lexer import Lexer
from src.minic.parser import Parser
from src.minic.semantic import SemanticAnalyzer, SemanticError


class SemanticAnalyzerTests(unittest.TestCase):
    def analyze(self, source):
        tokens = Lexer(source).scan_tokens()
        program = Parser(tokens).parse()
        return SemanticAnalyzer().analyze(program)

    def assert_semantic_error(self, source, expected_message):
        with self.assertRaisesRegex(SemanticError, expected_message):
            self.analyze(source)

    def test_builds_symbol_table_for_valid_program(self):
        symbols = self.analyze(
            """
            int x;
            float y = 10.5;
            int list[10];
            x = 5 + 3 * 2;
            while (x < 20) { x = x + 1; }
            """
        )

        self.assertEqual([symbol.name for symbol in symbols], ["x", "y", "list"])
        self.assertEqual([symbol.type for symbol in symbols], ["int", "float", "int[]"])
        self.assertEqual([symbol.kind for symbol in symbols], ["var", "var", "array"])
        self.assertEqual(symbols[2].size, 10)

    def test_allows_int_assigned_to_float(self):
        symbols = self.analyze("float y; y = 2;")

        self.assertEqual(symbols[0].name, "y")
        self.assertEqual(symbols[0].type, "float")

    def test_rejects_float_assigned_to_int(self):
        self.assert_semantic_error(
            "int x; x = 2.5;",
            "cannot assign float value to int variable 'x'",
        )

    def test_rejects_undeclared_variable(self):
        self.assert_semantic_error(
            "int x; z = x + 1;",
            "variable 'z' used before declaration",
        )

    def test_rejects_duplicate_declaration_in_same_scope(self):
        self.assert_semantic_error(
            "int x; float x;",
            "duplicate declaration of 'x'",
        )

    def test_rejects_direct_array_assignment(self):
        self.assert_semantic_error(
            "int list[10]; list = 1;",
            "cannot assign directly to array 'list'",
        )

    def test_rejects_float_array_index(self):
        self.assert_semantic_error(
            "int list[10]; float i; list[i] = 1;",
            "array index for 'list' must be int",
        )

    def test_rejects_indexing_non_array(self):
        self.assert_semantic_error(
            "int x; x[0] = 1;",
            "variable 'x' is not an array",
        )


if __name__ == "__main__":
    unittest.main()

