from antlr4 import InputStream, CommonTokenStream

from project.language.langLexer import langLexer
from project.language.langParser import langParser


def parse(program: str) -> langParser:
    input_stream = InputStream(program)
    lexer = langLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    return langParser(token_stream)


def parse_check(program: str) -> bool:
    parser = parse(program)
    parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0
