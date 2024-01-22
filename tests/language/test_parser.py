import pytest
from project.language.parser import parse_check, parse_to_dot

import os
import filecmp

RESOURCES_PATH = "tests/resources/parser"

positive_tests = [
    'x = "string"',
    "x = 20",
    "x = true",
    "x = /regex/",
    "x = g/S -> a/",
    "x = set_start graph set",
    "x = set_final graph final_set",
    "newx = add_start graph1 some_set",
    "x = add_final gg set1",
    'x = load "pizza"',
    "set = get_start graph",
    "x = map (lambda x -> x) set",
    "x = filter (lambda -> elem) set",
    "set = [1, 2]",
    "set = [1..100]",
    "x = []",
    "x = g1 & g2",
    "x = g1*",
    "x = true && false",
    "x = -2",
    "print g1",
]

negative_tests = [
    "x = 20x",
    "2 = 2",
    "x = set_strt graph",
    "x = map lambda set",
    "x = filter (lambda x -> x) (lambda -> 2)",
    "x = [lambda x -> x]",
    "x = 10 + 20",
]


@pytest.mark.parametrize(
    "program, expected",
    [(test, True) for test in positive_tests]
    + [(test, False) for test in negative_tests],
)
def test_check(program, expected):
    assert parse_check(program) == expected


@pytest.mark.parametrize(
    "program, expected_filename",
    [
        ("x = map (lambda g -> g*) lst", "expected1.dot"),
        ("x = filter (lambda -> true) [1..100]", "expected2.dot"),
    ],
)
def test_dot(program, expected_filename):
    tmp_path = os.path.join(RESOURCES_PATH, "tmp.dot")
    expected_path = os.path.join(RESOURCES_PATH, expected_filename)
    parse_to_dot(program, tmp_path)

    assert filecmp.cmp(
        tmp_path,
        expected_path,
    )
    os.remove(tmp_path)
