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


def create_masks(regex_num_states: int, graph_num_states: int):
    return sp.hstack(
        [
            sp.eye(regex_num_states, regex_num_states, format="csr", dtype=bool),
            sp.csr_matrix((regex_num_states, graph_num_states), dtype=bool),
        ],
        format="csr",
        dtype=bool,
    )


def set_start_verts(
    mask_matrix: sp.csr_matrix, start_states: Set, regex_start_states: Set
) -> sp.csr_matrix:
    regex_num_states = mask_matrix.shape[0]
    for row in range(regex_num_states):
        if row in regex_start_states:
            for col in start_states:
                mask_matrix[row, regex_num_states + col] = True
    return mask_matrix


def extract_left_sub_matrix(mask_matrix: sp.csr_matrix) -> sp.csr_matrix:
    return mask_matrix[:, : mask_matrix.shape[0]]


def extract_right_sub_matrix(mask_matrix: sp.csr_matrix) -> sp.csr_matrix:
    return mask_matrix[:, mask_matrix.shape[0] :]


def transform_rows(mask_matrix: sp.csr_matrix) -> sp.csr_matrix:
    t = extract_left_sub_matrix(mask_matrix)
    i_row, i_col = t.nonzero()

    result = sp.csr_matrix(mask_matrix.shape, dtype=bool)
    for col in range(len(i_col)):
        row = mask_matrix.getrow(i_row[col])
        result[i_col[col], :] += row

    return result


def reduce_vector(matrix: sp.csr_matrix) -> sp.csr_matrix:
    return sum(matrix.getrow(row) for row in range(matrix.shape[0]))


def bfs_based_rpq(
    graph: MultiDiGraph,
    regex: Regex,
    start_states: Set = set(),
    final_states: Set = set(),
) -> Set:
    graph_nfa = graph_to_nfa(graph, start_states, final_states)
    regex_dfa = regex_to_dfa(regex)

    graph_decomposed_fa = DecomposedFA.from_fa(graph_nfa)

    regex_decomposed_fa = DecomposedFA.from_fa(regex_dfa)
    regex_start_states = {
        index
        for state, index in regex_decomposed_fa.states_with_indices.items()
        if state in regex_decomposed_fa.start_states
    }

    regex_final_states = {
        index
        for state, index in regex_decomposed_fa.states_with_indices.items()
        if state in regex_decomposed_fa.final_states
    }

    direct_sum = regex_decomposed_fa.direct_sum(graph_decomposed_fa)

    mask_matrix = create_masks(
        regex_decomposed_fa.num_states, graph_decomposed_fa.num_states
    )
    mask_matrix = set_start_verts(mask_matrix, start_states, regex_start_states)

    matrix_changed = True
    visited_matrix = mask_matrix.copy()
    while matrix_changed:
        new_matrix = sp.csr_matrix(mask_matrix.shape, dtype=bool)
        for label in direct_sum:
            new_matrix += transform_rows(mask_matrix @ direct_sum[label])

        prev_nnz = visited_matrix.nnz
        visited_matrix += new_matrix

        if prev_nnz == visited_matrix.nnz:
            matrix_changed = False
        else:
            mask_matrix = new_matrix

    result = set()
    for row, col in zip(*extract_right_sub_matrix(visited_matrix).nonzero()):
        if row in regex_final_states:
            result.add(col)
    return result


def bfs_based_rpq_by_vertice(
    graph: MultiDiGraph,
    regex: Regex,
    start_states: Set = set(),
    final_states: Set = set(),
) -> Dict:
    graph_decomposed_fa = DecomposedFA.from_fa(
        graph_to_nfa(graph, start_states, final_states)
    )
    graph_start_states = {
        index
        for state, index in graph_decomposed_fa.states_with_indices.items()
        if state in graph_decomposed_fa.start_states
    }

    regex_decomposed_fa = DecomposedFA.from_fa(regex_to_dfa(regex))
    regex_start_states = {
        index
        for state, index in regex_decomposed_fa.states_with_indices.items()
        if state in regex_decomposed_fa.start_states
    }
    regex_final_states = {
        index
        for state, index in regex_decomposed_fa.states_with_indices.items()
        if state in regex_decomposed_fa.final_states
    }

    direct_sum = regex_decomposed_fa.direct_sum(graph_decomposed_fa)

    mask_matrices = {
        state: create_masks(
            regex_decomposed_fa.num_states, graph_decomposed_fa.num_states
        )
        for state in start_states
    }
    for col in start_states:
        for row in regex_start_states:
            mask_matrices[col][row, regex_decomposed_fa.num_states + col] = True

    matrix_changed = True
    visited_matrices = mask_matrices.copy()
    while matrix_changed:
        matrix_changed = False
        for i in start_states:
            new_matrix = sp.csr_matrix(mask_matrices[i].shape, dtype=bool)
            for label in direct_sum:
                new_matrix += transform_rows(mask_matrices[i] @ direct_sum[label])

            prev_nnz = visited_matrices[i].nnz
            visited_matrices[i] += new_matrix

            if prev_nnz != visited_matrices[i].nnz:
                matrix_changed = True
                mask_matrices[i] = new_matrix

    result = dict()
    for i in start_states:
        result[i] = set()
        for row, col in zip(*extract_right_sub_matrix(visited_matrices[i]).nonzero()):
            if row in regex_final_states:
                result[i].add(col)

    return result
