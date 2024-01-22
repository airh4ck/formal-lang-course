import pytest
from io import StringIO
from contextlib import redirect_stdout

from project.language.interpreter import interpret


@pytest.mark.parametrize(
    "input, expected_output",
    [
        (
            """
            x = "string"
            print x
            """,
            "string\n",
        ),
        (
            """
            x = 20
            print x
            """,
            "20\n",
        ),
        (
            """
            x = true
            print x
            """,
            "True\n",
        ),
        (
            """
            x = g/S -> a/
            print x
            """,
            "S -> a\n\n",
        ),
        (
            """
            s = [1, 2, 3]
            print s
            """,
            "{1, 2, 3}\n",
        ),
        (
            """
            s = [1..5]
            print s
            """,
            "{1, 2, 3, 4, 5}\n",
        ),
        (
            """
            s = []
            print s
            """,
            "set()\n",
        ),
        (
            """
            g = load "tests/resources/interpreter/sample.dot"
            g = set_start g [0]
            s = get_start g
            print s
            """,
            "{0}\n",
        ),
        (
            """
            g = load "tests/resources/interpreter/sample.dot"
            g = set_start g []
            g = add_start g [2]
            s = get_start g
            print s
            """,
            "{2}\n",
        ),
        (
            """
            g = load "tests/resources/interpreter/sample.dot"
            g = set_final g []
            g = add_final g [3]
            s = get_final g
            print s
            """,
            "{3}\n",
        ),
        (
            """
            g = load "tests/resources/interpreter/sample.dot"
            s = get_labels g
            print s
            """,
            "{a, b}\n",
        ),
        (
            """
            s = [10]
            s = map (lambda x -> -x) s
            print s
            """,
            "{-10}\n",
        ),
    ],
)
def test_interpret(input, expected_output):
    output = StringIO()
    with redirect_stdout(output):
        interpret(input)

    result = output.getvalue()
    output.close()
    assert result == expected_output


@pytest.mark.parametrize(
    "input, expected_exception",
    [
        (
            """
            x = true && 1
            print x
            """,
            TypeError,
        ),
        (
            """
            s = [1..10]
            x = s || false
            print x
            """,
            TypeError,
        ),
        (
            """
            print unknown_identifier
            """,
            RuntimeError,
        ),
        (
            """
            r = /regex/
            g = g/S -> a/
            result = r & g
            """,
            TypeError,
        ),
        (
            """
            g1 = g/S1 -> b/
            g2 = g/S2 -> a/
            result = g1 & g2
            """,
            TypeError,
        ),
        (
            """
            g = load "tests/resources/interpreter/sample.dot"
            flag = true
            g1 = map (lambda x -> x && flag) g
            """,
            TypeError,
        ),
    ],
)
def test_neg_interpret(input, expected_exception):
    with pytest.raises(expected_exception):
        interpret(input)


@pytest.mark.parametrize(
    "input",
    [
        """
        r1 = /(a.b)*(b|a)/
        graph = load "tests/resources/interpreter/sample.dot"
        grammar = g/S -> a/
        tmp1 = grammar & graph & r1
        rez = get_reachable tmp1
        """,
        """
        r1 = /(a.b)*(b|a)/
        r2 = /(a|b)*/
        tmp = r1 & r2
        rez = get_reachable tmp
        print rez
        """,
        """
        g1 = g/S -> a | b | eps/
        g2 = g/S -> a/
        tmp = g1 | g2 . g2
        rez = get_reachable tmp
        print rez
        """,
    ],
)
def test_pos_interpret(input):
    interpret(input)
