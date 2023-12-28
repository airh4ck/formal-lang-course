from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from typing import Set
import scipy.sparse as sp

from project.automata.utils import graph_to_nfa, regex_to_dfa
from project.automata.decomposed_fa import DecomposedFA
from project.rpq.bfs_based_rpq_helpers import (
    states_to_indices,
    create_masks,
    set_start_verts,
    transform_rows,
    extract_right_sub_matrix,
)


def bfs_based_rpq(
    graph: MultiDiGraph,
    regex: Regex,
    start_states: Set = set(),
    final_states: Set = set(),
) -> Set:
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

    mask = create_masks(decomposed_regex.num_states, decomposed_graph.num_states)
    mask = set_start_verts(mask, start_states, r_start_states)

    matrix_changed = True
    visited = mask.copy()
    while matrix_changed:
        new_matrix = sp.csr_matrix(mask.shape, dtype=bool)
        for label in direct_sum:
            new_matrix += transform_rows(mask @ direct_sum[label])

        prev_nnz = visited.nnz
        visited += new_matrix

        if prev_nnz == visited.nnz:
            matrix_changed = False
        else:
            mask = new_matrix

    result = set()
    for row, col in zip(*extract_right_sub_matrix(visited).nonzero()):
        if row in r_final_states:
            result.add(col)
    return result
