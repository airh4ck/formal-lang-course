import os
import pytest
from pyformlang.cfg import Terminal, Production, Variable
from pyformlang.regular_expression import Regex
from project.cfg.ecfg import ECFG

RESOURCES_PATH = "tests/resources/ecfg"


def test_ecfg_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        ECFG.from_file("no_such_file.cfg")


@pytest.mark.parametrize(
    "filename, expected_productions",
    [
        (
            "grammar0.cfg",
            {
                Variable("N"): Regex("S"),
                Variable("S"): Regex("$|a.S.b.S"),
            },
        ),
        ("grammar1.cfg", {Variable("S"): Regex("N|b"), Variable("N"): Regex("a|$")}),
        (
            "grammar2.cfg",
            {
                Variable("S"): Regex("S1|S2"),
                Variable("S1"): Regex("N1.N2"),
                Variable("N1"): Regex("a.N1.b|$"),
                Variable("N2"): Regex("$|c.N2"),
                Variable("M1"): Regex("a.M1|$"),
                Variable("S2"): Regex("M1.M2"),
                Variable("M2"): Regex("b.M2.c|$"),
            },
        ),
    ],
)
def test_ecfg_from_file(filename, expected_productions):
    received = ECFG.from_file(os.path.join(RESOURCES_PATH, filename))

    assert expected_productions == received.productions
