import pytest
from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.rpq.rpq import rpq
from project.rpq.bfs_based_rpq import bfs_based_rpq
from project.rpq.bfs_based_rpq_by_vertice import bfs_based_rpq_by_vertice


def test_rpq_empty():
    assert len(rpq(MultiDiGraph(), Regex(""))) == 0


def test_trivial_rpq():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transition(0, "a", 1)
    nfa.add_start_state(0)
    nfa.add_final_state(1)

    assert rpq(nfa.to_networkx(), Regex("a*"), {0}, {1}) == {(0, 1)}


def test_rpq():
    regex = Regex("(a|b)*b(a|b)")
    graph = MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (1, 1, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (2, 3, {"label": "c"}),
        ]
    )

    assert rpq(graph, regex, {0, 1}, {2}) == {(0, 2), (1, 2)}


def test_bfs_based_rpq1():
    regex = Regex("b*a.b")
    graph = MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (0, 3, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (2, 0, {"label": "a"}),
            (3, 0, {"label": "b"}),
        ]
    )

    assert bfs_based_rpq(graph, regex, {0}, {}) == {2}


def test_bfs_based_rpq2():
    regex = Regex("(a|b)*b(a|b)")
    graph = MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (1, 1, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (2, 3, {"label": "c"}),
        ]
    )

    assert bfs_based_rpq(graph, regex, {0, 1}, {2}) == {1, 2}


def test_bfs_based_rpq_by_vertice1():
    regex = Regex("b*a.b")
    graph = MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (0, 3, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (2, 0, {"label": "a"}),
            (3, 0, {"label": "b"}),
        ]
    )

    assert bfs_based_rpq_by_vertice(graph, regex, {0}, {}) == {0: {2}}


def test_bfs_based_rpq_by_vertice2():
    regex = Regex("(a|b)*b(a|b)")
    graph = MultiDiGraph(
        [
            (0, 1, {"label": "a"}),
            (1, 1, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (2, 3, {"label": "c"}),
        ]
    )

    assert bfs_based_rpq_by_vertice(graph, regex, {0, 1}, {2}) == {0: {1, 2}, 1: {1, 2}}
