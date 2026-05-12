import unittest

from src.minic.lexer import Lexer
from src.minic.parser import Parser
from src.minic.semantic import SemanticAnalyzer
from src.minic.tac import TACGenerator


class TACGeneratorTests(unittest.TestCase):
    def generate(self, source):
        tokens = Lexer(source).scan_tokens()
        program = Parser(tokens).parse()
        SemanticAnalyzer().analyze(program)
        return TACGenerator().generate(program)

    def test_generates_tac_for_expression_precedence(self):
        instructions = self.generate("int x; x = 5 + 3 * 2;")

        self.assertEqual(
            instructions,
            [
                "t1 = 3 * 2",
                "t2 = 5 + t1",
                "x = t2",
            ],
        )

    def test_generates_tac_for_declaration_initializer_and_print(self):
        instructions = self.generate("float y = 10.5; print(y);")

        self.assertEqual(
            instructions,
            [
                "y = 10.5",
                "param y",
                "call print, 1",
            ],
        )

    def test_generates_tac_for_if_else(self):
        instructions = self.generate(
            """
            int x;
            float y;
            if (x > 10) { print(x); } else { print(y); }
            """
        )

        self.assertEqual(
            instructions,
            [
                "t1 = x > 10",
                "ifFalse t1 goto L1",
                "param x",
                "call print, 1",
                "goto L2",
                "L1:",
                "param y",
                "call print, 1",
                "L2:",
            ],
        )

    def test_generates_tac_for_while_loop(self):
        instructions = self.generate(
            """
            int x;
            while (x < 20) { x = x + 1; }
            """
        )

        self.assertEqual(
            instructions,
            [
                "L1:",
                "t1 = x < 20",
                "ifFalse t1 goto L2",
                "t2 = x + 1",
                "x = t2",
                "goto L1",
                "L2:",
            ],
        )

    def test_generates_tac_for_array_assignment(self):
        instructions = self.generate(
            """
            int i;
            int list[10];
            list[i] = i + 1;
            """
        )

        self.assertEqual(
            instructions,
            [
                "list = alloc 10",
                "t1 = i + 1",
                "list[i] = t1",
            ],
        )


if __name__ == "__main__":
    unittest.main()

