import os
import pytest
from pyformlang.cfg import Terminal, Production
from project.cfg.cfg import cfg_from_file, cfg_to_wcnf

RESOURCES_PATH = "tests/resources/wcnf"


def test_cfg_from_file():
    assert cfg_from_file(os.path.join(RESOURCES_PATH, "grammar1.cfg")).productions == {
        Production("N", ["S"]),
        Production("S", [Terminal("a"), "S", Terminal("b"), "S"]),
        Production("S", []),
    }


def test_cfg_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        cfg_from_file("no_such_file.cfg")


@pytest.mark.parametrize(
    "expected_filename, received_filename",
    [pytest.param(f"grammar{i}_expected.cfg", f"grammar{i}.cfg") for i in range(4)],
)
def test_wcnf(expected_filename, received_filename):
    expected = cfg_from_file(os.path.join(RESOURCES_PATH, expected_filename))
    received = cfg_to_wcnf(
        cfg_from_file(os.path.join(RESOURCES_PATH, received_filename))
    )

    assert set(expected.productions) == set(received.productions)
