from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from typing import Set, Dict
import scipy.sparse as sp

from project.automata.utils import graph_to_nfa, regex_to_dfa
from project.automata.decomposed_fa import DecomposedFA
from project.rpq.bfs_based_rpq_helpers import (
    create_masks,
    transform_rows,
    extract_right_sub_matrix,
    states_to_indices,
)


def bfs_based_rpq_by_vertice(
    graph: MultiDiGraph,
    regex: Regex,
    start_states: Set = set(),
    final_states: Set = set(),
) -> Dict:
    graph_nfa = graph_to_nfa(graph, start_states, final_states)
    regex_dfa = regex_to_dfa(regex)

    decomposed_graph = DecomposedFA.from_fa(graph_nfa)
    decomposed_regex = DecomposedFA.from_fa(regex_dfa)
    r_start_states = states_to_indices(
        decomposed_regex.states_with_indices,
        lambda state: state in decomposed_regex.start_states,
    )
    r_final_states = states_to_indices(
        decomposed_regex.states_with_indices,
        lambda state: state in decomposed_regex.final_states,
    )

    direct_sum = decomposed_regex.direct_sum(decomposed_graph)

    masks = {
        state: create_masks(decomposed_regex.num_states, decomposed_graph.num_states)
        for state in start_states
    }
    for g_state in start_states:
        for r_state in r_start_states:
            masks[g_state][r_state, decomposed_regex.num_states + g_state] = True

    matrix_changed = True
    visited = masks.copy()
    while matrix_changed:
        matrix_changed = False
        for g_state in start_states:
            new_matrix = sp.csr_matrix(masks[g_state].shape, dtype=bool)
            for label in direct_sum:
                new_matrix += transform_rows(masks[g_state] @ direct_sum[label])

            prev_nnz = visited[g_state].nnz
            visited[g_state] += new_matrix

            if prev_nnz != visited[g_state].nnz:
                matrix_changed = True
                masks[g_state] = new_matrix

    result = dict()
    for g_state_from in start_states:
        result[g_state_from] = set()
        for r_state, g_state_to in zip(
            *extract_right_sub_matrix(visited[g_state_from]).nonzero()
        ):
            if r_state in r_final_states:
                result[g_state_from].add(g_state_to)

    return result
