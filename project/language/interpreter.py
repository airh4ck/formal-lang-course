from project.language.parser import parse
from project.language.visitor import Visitor


def interpret(program: str):
    parser = parse(program)
    ast = parser.prog()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise RuntimeError("Syntax error")

    return Visitor().visitProg(ast)
