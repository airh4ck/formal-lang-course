from typing import Set
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Terminal
from scipy.sparse import csr_matrix

from project.cfg.cfg import cfg_to_wcnf


def mprod_based_algorithm(graph: MultiDiGraph, cfg: CFG) -> Set:
    wcnf = cfg_to_wcnf(cfg)

    epsilon_productions = set(
        production.head for production in wcnf.productions if len(production.body) == 0
    )
    terminal_productions = set(
        (production.head, production.body[0])
        for production in wcnf.productions
        if len(production.body) == 1
    )
    variable_productions = set(
        (production.head, production.body[0], production.body[1])
        for production in wcnf.productions
        if len(production.body) == 2
    )

    num_nodes = graph.number_of_nodes()
    nodes = {vertice: i for i, vertice in enumerate(graph.nodes)}
    matrices = {
        var: csr_matrix((num_nodes, num_nodes), dtype=bool) for var in wcnf.variables
    }

    for vertice in nodes:
        for variable in epsilon_productions:
            matrices[variable][vertice, vertice] = True

    for v_from, v_to, label in graph.edges(data="label"):
        for variable, terminal in terminal_productions:
            if terminal == Terminal(label):
                matrices[variable][nodes[v_from], nodes[v_to]] = True

    matrix_changed = True
    while matrix_changed:
        matrix_changed = False
        for variable, l_var, r_var in variable_productions:
            prev_nnz = matrices[variable].nnz
            matrices[variable] += matrices[l_var] @ matrices[r_var]
            matrix_changed |= prev_nnz != matrices[variable].nnz

    nodes_by_indices = {i: vertice for vertice, i in nodes.items()}
    return {
        (variable, nodes_by_indices[v_from], nodes_by_indices[v_to])
        for variable, matrix in matrices.items()
        for v_from, v_to in zip(*matrix.nonzero())
    }
