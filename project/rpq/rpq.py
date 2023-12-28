from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from typing import Set, Dict

from project.automata.utils import graph_to_nfa, regex_to_dfa
from project.automata.decomposed_fa import DecomposedFA
import scipy.sparse as sp


def rpq(
    graph: MultiDiGraph,
    regex: Regex,
    start_states: Set = set(),
    final_states: Set = set(),
) -> Set:
    graph_decomposed_fa = DecomposedFA.from_fa(
        graph_to_nfa(graph, start_states, final_states)
    )
    regex_decomposed_fa = DecomposedFA.from_fa(regex_to_dfa(regex))

    intersection = graph_decomposed_fa.intersect(regex_decomposed_fa)
    transitive_closure = intersection.transitive_closure()

    return set(
        (
            s_from // regex_decomposed_fa.num_states,
            s_to // regex_decomposed_fa.num_states,
        )
        for s_from, s_to in zip(*transitive_closure.nonzero())
        if s_from in intersection.start_states and s_to in intersection.final_states
    )
