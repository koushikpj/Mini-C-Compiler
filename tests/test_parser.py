import unittest

from src.minic.ast_nodes import (
    ArrayDeclaration,
    Assignment,
    BinaryExpression,
    Block,
    IfStatement,
    Literal,
    Location,
    PrintStatement,
    VarDeclaration,
    WhileStatement,
)
from src.minic.lexer import Lexer
from src.minic.parser import ParseError, Parser


class ParserTests(unittest.TestCase):
    def parse(self, source):
        tokens = Lexer(source).scan_tokens()
        return Parser(tokens).parse()

    def test_parses_variable_and_array_declarations(self):
        program = self.parse("int x; float y = 10.5; int list[10];")

        self.assertEqual(len(program.statements), 3)
        self.assertEqual(program.statements[0], VarDeclaration("int", "x", None))
        self.assertEqual(
            program.statements[1],
            VarDeclaration("float", "y", Literal(10.5, "float")),
        )
        self.assertEqual(program.statements[2], ArrayDeclaration("int", "list", 10))

    def test_parses_expression_precedence(self):
        program = self.parse("x = 5 + 3 * 2;")
        statement = program.statements[0]

        self.assertIsInstance(statement, Assignment)
        self.assertEqual(statement.target, Location("x"))
        self.assertEqual(
            statement.value,
            BinaryExpression(
                Literal(5, "int"),
                "+",
                BinaryExpression(Literal(3, "int"), "*", Literal(2, "int")),
            ),
        )

    def test_parses_if_else_and_print(self):
        source = "if (x > 10) { print(x); } else { print(y); }"
        statement = self.parse(source).statements[0]

        self.assertIsInstance(statement, IfStatement)
        self.assertEqual(
            statement.condition,
            BinaryExpression(Location("x"), ">", Literal(10, "int")),
        )
        self.assertIsInstance(statement.then_branch, Block)
        self.assertIsInstance(statement.then_branch.statements[0], PrintStatement)
        self.assertIsInstance(statement.else_branch, Block)
        self.assertIsInstance(statement.else_branch.statements[0], PrintStatement)

    def test_parses_while_and_array_assignment(self):
        source = "while (i < 10) { list[i] = i; i = i + 1; }"
        statement = self.parse(source).statements[0]

        self.assertIsInstance(statement, WhileStatement)
        self.assertEqual(
            statement.condition,
            BinaryExpression(Location("i"), "<", Literal(10, "int")),
        )
        self.assertIsInstance(statement.body, Block)
        self.assertEqual(
            statement.body.statements[0],
            Assignment(Location("list", Location("i")), Location("i")),
        )

    def test_missing_semicolon_raises_parse_error(self):
        with self.assertRaisesRegex(ParseError, "Expected ';' after variable declaration"):
            self.parse("int x")


if __name__ == "__main__":
    unittest.main()

