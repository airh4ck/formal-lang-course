import sys
from project.language.interpreter import interpret

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        code = f.read()

    interpret(code)
