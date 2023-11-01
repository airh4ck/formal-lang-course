from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from networkx import MultiDiGraph
from typing import Set


def regex_to_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    return (
        regex.to_epsilon_nfa()
        .remove_epsilon_transitions()
        .to_deterministic()
        .minimize()
    )


def regex_equivalence(self: Regex, other: Regex):
    return regex_to_dfa(self) == regex_to_dfa(other)


Regex.__eq__ = regex_equivalence


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int] = set(), final_states: Set[int] = set()
) -> NondeterministicFiniteAutomaton:
    if len(start_states) == 0:
        start_states = graph.nodes
    graph.nodes(data="is_start", default=False)
    for state in start_states:
        graph.nodes[state]["is_start"] = True

    if len(final_states) == 0:
        final_states = graph.nodes
    graph.nodes(data="is_final", default=False)
    for state in final_states:
        graph.nodes[state]["is_final"] = True

    return NondeterministicFiniteAutomaton.from_networkx(
        graph
    ).remove_epsilon_transitions()
