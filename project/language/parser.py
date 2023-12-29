from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.Errors import ParseCancellationException

from project.language.langLexer import langLexer
from project.language.langParser import langParser
from project.language.dotListener import DotListener

from pydot import Dot


def parse(program: str) -> langParser:
    input_stream = InputStream(program)
    lexer = langLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    return langParser(token_stream)


def parse_check(program: str) -> bool:
    parser = parse(program)
    parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0


def parse_to_dot(program: str, path: str):
    if not parse_check(program):
        raise ParseCancellationException()

    ast = parse(program).prog()
    dot = Dot("ast", graph_type="digraph")
    listener = DotListener(dot, langParser.ruleNames)
    ParseTreeWalker().walk(listener, ast)

    dot.write(path)
    return path
