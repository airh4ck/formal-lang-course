from typing import Set, Dict, Callable
import scipy.sparse as sp


def states_to_indices(
    states_with_indices: Dict, filter: Callable = lambda _: True
) -> Set:
    return {index for state, index in states_with_indices.items() if filter(state)}


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
