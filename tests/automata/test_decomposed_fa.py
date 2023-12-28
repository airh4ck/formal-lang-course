import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from scipy.sparse import csr_matrix

from project.automata.decomposed_fa import DecomposedFA


def test_conversions_empty():
    nfa = NondeterministicFiniteAutomaton()
    assert nfa == DecomposedFA.from_fa(nfa).to_fa()


def test_conversions():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions([(0, "a", 1), (0, "b", 0), (1, "b", 0), (1, "a", 1)])
    nfa.add_start_state(0)
    nfa.add_final_state(1)

    assert nfa == DecomposedFA.from_fa(nfa).to_fa()


def test_intersect_empty():
    nfa = NondeterministicFiniteAutomaton()
    decomposed_nfa = DecomposedFA.from_fa(nfa)

    assert nfa == decomposed_nfa.intersect(decomposed_nfa).to_fa()


def test_trivial_intersect():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions([(0, "a", 1), (0, "b", 0), (1, "b", 0), (1, "a", 1)])
    nfa.add_start_state(0)
    nfa.add_final_state(1)

    decomposed_nfa = DecomposedFA.from_fa(nfa)
    assert nfa == decomposed_nfa.intersect(decomposed_nfa).to_fa()


def test_intersect():
    left_nfa = NondeterministicFiniteAutomaton()
    left_nfa.add_transitions([(0, "a", 0), (0, "a", 1)])
    left_nfa.add_start_state(0)
    left_nfa.add_final_state(1)

    right_nfa = NondeterministicFiniteAutomaton()
    right_nfa.add_transitions([(0, "a", 0), (0, "a", 1), (1, "b", 1)])
    right_nfa.add_start_state(0)
    right_nfa.add_final_state(1)

    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_transitions([(0, "a", 0), (0, "a", 1)])
    expected_nfa.add_start_state(0)
    expected_nfa.add_final_state(1)

    assert (
        expected_nfa
        == DecomposedFA.from_fa(left_nfa)
        .intersect(DecomposedFA.from_fa(right_nfa))
        .to_fa()
    )


def test_intersect_with_parallel_edges():
    left_nfa = NondeterministicFiniteAutomaton()
    left_nfa.add_transitions([(0, "a", 0), (0, "a", 1), (0, "b", 1)])
    left_nfa.add_start_state(0)
    left_nfa.add_final_state(1)

    right_nfa = NondeterministicFiniteAutomaton()
    right_nfa.add_transitions([(0, "a", 0), (0, "a", 1), (0, "b", 1), (1, "b", 1)])
    right_nfa.add_start_state(0)
    right_nfa.add_final_state(1)

    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_transitions([(0, "a", 0), (0, "a", 1), (0, "b", 1)])
    expected_nfa.add_start_state(0)
    expected_nfa.add_final_state(1)

    assert (
        expected_nfa
        == DecomposedFA.from_fa(left_nfa)
        .intersect(DecomposedFA.from_fa(right_nfa))
        .to_fa()
    )


def test_transitive_closure_empty():
    decomposed_fa = DecomposedFA()

    assert decomposed_fa.transitive_closure().sum() == 0


def test_trivial_transitive_closure():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transition(0, "a", 0)
    nfa.add_start_state(0)
    nfa.add_final_state(0)

    assert DecomposedFA.from_fa(nfa).transitive_closure().sum() == 1


def test_transitive_closure():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions(
        [(0, "a", 0), (0, "a", 1), (0, "b", 1), (1, "b", 2), (2, "a", 2)]
    )
    nfa.add_start_state(0)
    nfa.add_final_state(1)

    assert DecomposedFA.from_fa(nfa).transitive_closure().sum() == 5


def test_direct_sum_empty():
    nfa = NondeterministicFiniteAutomaton()
    decomposed_nfa = DecomposedFA.from_fa(nfa)
    assert decomposed_nfa.direct_sum(decomposed_nfa) == dict()


def test_direct_sum():
    left = NondeterministicFiniteAutomaton()
    left.add_transitions(
        [(0, "a", 0), (0, "a", 1), (0, "b", 1), (1, "b", 0), (1, "b", 1)]
    )

    right = NondeterministicFiniteAutomaton()
    right.add_transitions(
        [
            (0, "a", 1),
            (1, "a", 1),
            (1, "a", 2),
            (2, "a", 2),
            (0, "b", 0),
            (1, "b", 0),
            (1, "b", 1),
            (1, "b", 2),
        ]
    )

    direct_sum = DecomposedFA.from_fa(left).direct_sum(DecomposedFA.from_fa(right))
    a_matrix = [
        [1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 1],
    ]

    b_matrix = [
        [0, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0],
    ]

    assert direct_sum.keys() == {"a", "b"}
    assert (direct_sum["a"].toarray() != a_matrix).sum() == 0
    assert (direct_sum["b"].toarray() != b_matrix).sum() == 0
