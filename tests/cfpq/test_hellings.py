import pytest
from typing import Set
from pyformlang.cfg import CFG, Production, Variable, Terminal
from networkx import MultiDiGraph

from project.cfpq.hellings import hellings, cfpq_hellings

test_graphs = [
    MultiDiGraph(),
    MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "b"}),
            (2, 3, {"label": "a"}),
        ]
    ),
    MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "a"}),
            (2, 0, {"label": "a"}),
            (2, 3, {"label": "b"}),
            (3, 2, {"label": "b"}),
        ]
    ),
]

test_cfgs = [
    CFG(start_symbol="S", productions={Production(Variable("S"), [])}),
    CFG(
        start_symbol="S",
        productions={
            Production(Variable("S"), [Variable("N1"), Variable("N2")]),
            Production(Variable("N1"), [Terminal("a")]),
            Production(Variable("N2"), [Variable("N2"), Variable("N3")]),
            Production(Variable("N2"), [Terminal("b")]),
            Production(Variable("N3"), [Terminal("a")]),
            Production(Variable("N3"), []),
        },
    ),
    CFG(
        start_symbol="S",
        productions={
            Production(Variable("S"), [Variable("A"), Variable("B")]),
            Production(Variable("A"), [Terminal("a")]),
            Production(Variable("S"), [Variable("A"), Variable("S1")]),
            Production(Variable("B"), [Terminal("b")]),
            Production(Variable("S1"), [Variable("S"), Variable("B")]),
        },
    ),
]


@pytest.mark.parametrize(
    "graph, cfg, expected",
    zip(
        test_graphs,
        test_cfgs,
        [
            set(),
            {
                (Variable("N3"), 3, 3),
                (Variable("N2"), 1, 3),
                (Variable("N3"), 2, 3),
                (Variable("N3"), 0, 1),
                (Variable("N2"), 1, 2),
                (Variable("N1"), 2, 3),
                (Variable("N1"), 0, 1),
                (Variable("N3"), 0, 0),
                (Variable("N3"), 2, 2),
                (Variable("N3"), 1, 1),
                (Variable("S"), 0, 3),
                (Variable("S"), 0, 2),
            },
            {
                (Variable("A"), 0, 1),
                (Variable("A"), 1, 2),
                (Variable("A"), 2, 0),
                (Variable("B"), 2, 3),
                (Variable("B"), 3, 2),
                (Variable("S"), 1, 3),
                (Variable("S1"), 1, 2),
                (Variable("S"), 0, 2),
                (Variable("S1"), 0, 3),
                (Variable("S"), 2, 3),
                (Variable("S1"), 2, 2),
                (Variable("S"), 1, 2),
                (Variable("S1"), 1, 3),
                (Variable("S"), 0, 3),
                (Variable("S1"), 0, 2),
                (Variable("S"), 2, 2),
                (Variable("S1"), 2, 3),
            },
        ],
    ),
)
def test_hellings(graph: MultiDiGraph, cfg: CFG, expected: Set):
    assert hellings(graph, cfg) == expected


@pytest.mark.parametrize(
    "graph, cfg, expected",
    zip(
        test_graphs,
        test_cfgs,
        [set(), {(0, 2), (0, 3)}, {(1, 3), (0, 2), (2, 3), (1, 2), (0, 3), (2, 2)}],
    ),
)
def test_cfpq_hellings(graph: MultiDiGraph, cfg: CFG, expected: Set):
    assert cfpq_hellings(graph, cfg) == expected
