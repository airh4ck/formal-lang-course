from networkx import MultiDiGraph
from pyformlang.cfg import CFG
from scipy.sparse import csr_matrix
from typing import Set
import pycubool as pcb

from project.automata.decomposed_fa import DecomposedFA
from project.automata.cb_decomposed_fa import CbDecomposedFA
from project.automata.rsm import RecursiveStateMachine
from project.automata.utils import graph_to_nfa
from project.cfg.ecfg import ECFG


def tensor_based(
    graph: MultiDiGraph,
    cfg: CFG,
) -> Set:
    graph_decomposed = DecomposedFA.from_fa(graph_to_nfa(graph))
    rsm = RecursiveStateMachine.from_ecfg(ECFG.from_cfg(cfg))
    rsm_decomposed = DecomposedFA.from_rsm(rsm)

    for production in cfg.productions:
        if len(production.body) != 0:
            continue

        variable = production.head
        if variable not in graph_decomposed.matrices:
            graph_decomposed.matrices[variable] = csr_matrix(
                (graph_decomposed.num_states, graph_decomposed.num_states), dtype=bool
            )

        for vertice in range(graph_decomposed.num_states):
            graph_decomposed.matrices[variable][vertice, vertice] = True

    transitive_closure = csr_matrix(
        (graph_decomposed.num_states, graph_decomposed.num_states), dtype=bool
    )
    matrix_changed = True
    states_by_indices = {
        i: state for state, i in rsm_decomposed.states_with_indices.items()
    }
    while matrix_changed:
        matrix_changed = False

        prev_nnz = transitive_closure.nnz
        transitive_closure = rsm_decomposed.intersect(
            graph_decomposed
        ).transitive_closure()
        matrix_changed |= prev_nnz != transitive_closure.nnz

        for idx_from, idx_to in zip(*transitive_closure.nonzero()):
            state_from = states_by_indices[idx_from // graph_decomposed.num_states]
            variable = state_from.value[0]

            if variable not in cfg.variables:
                continue

            state_to = states_by_indices[idx_to // graph_decomposed.num_states]
            if (
                state_from in rsm_decomposed.start_states
                and state_to in rsm_decomposed.final_states
            ):
                if variable not in graph_decomposed.matrices:
                    graph_decomposed.matrices[variable] = csr_matrix(
                        (graph_decomposed.num_states, graph_decomposed.num_states),
                        dtype=bool,
                    )

                graph_decomposed.matrices[variable][
                    idx_from % graph_decomposed.num_states,
                    idx_to % graph_decomposed.num_states,
                ] = True

    return set(
        (variable, v_from, v_to)
        for variable, matrix in graph_decomposed.matrices.items()
        for v_from, v_to in zip(*matrix.nonzero())
        if variable in cfg.variables
    )


def cb_tensor_based(
    graph: MultiDiGraph,
    cfg: CFG,
) -> Set:
    graph_decomposed = CbDecomposedFA.from_fa(graph_to_nfa(graph))
    rsm = RecursiveStateMachine.from_ecfg(ECFG.from_cfg(cfg))
    rsm_decomposed = CbDecomposedFA.from_rsm(rsm)

    if graph_decomposed.num_states == 0:
        return set()

    for production in cfg.productions:
        if len(production.body) != 0:
            continue

        variable = production.head
        if variable not in graph_decomposed.matrices:
            graph_decomposed.matrices[variable] = pcb.Matrix.empty(
                shape=(graph_decomposed.num_states, graph_decomposed.num_states)
            )

        for vertice in range(graph_decomposed.num_states):
            graph_decomposed.matrices[variable][vertice, vertice] = True

    transitive_closure = pcb.Matrix.empty(
        shape=(graph_decomposed.num_states, graph_decomposed.num_states)
    )
    matrix_changed = True
    states_by_indices = {
        i: state for state, i in rsm_decomposed.states_with_indices.items()
    }
    while matrix_changed:
        matrix_changed = False

        prev_nnz = transitive_closure.nvals
        transitive_closure = rsm_decomposed.intersect(
            graph_decomposed
        ).transitive_closure()
        matrix_changed |= prev_nnz != transitive_closure.nvals

        for idx_from, idx_to in transitive_closure:
            state_from = states_by_indices[idx_from // graph_decomposed.num_states]
            variable = state_from.value[0]

            if variable not in cfg.variables:
                continue

            state_to = states_by_indices[idx_to // graph_decomposed.num_states]
            if (
                state_from in rsm_decomposed.start_states
                and state_to in rsm_decomposed.final_states
            ):
                if variable not in graph_decomposed.matrices:
                    graph_decomposed.matrices[variable] = pcb.Matrix.empty(
                        (graph_decomposed.num_states, graph_decomposed.num_states)
                    )

                graph_decomposed.matrices[variable][
                    idx_from % graph_decomposed.num_states,
                    idx_to % graph_decomposed.num_states,
                ] = True

    return set(
        (variable, v_from, v_to)
        for variable, matrix in graph_decomposed.matrices.items()
        for v_from, v_to in matrix
        if variable in cfg.variables
    )
