from typing import Set
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Terminal, Variable

from project.cfg.cfg import cfg_to_wcnf


def cfpq(
    graph: MultiDiGraph,
    cfg: CFG,
    algorithm: callable,
    start_variable: Variable = Variable("S"),
    start_vertices: "Set | None" = None,
    final_vertices: "Set | None" = None,
) -> Set:
    if not start_vertices:
        start_vertices = set(graph.nodes)
    if not final_vertices:
        final_vertices = set(graph.nodes)

    result = algorithm(graph, cfg)
    return set(
        (v_from, v_to)
        for variable, v_from, v_to in result
        if variable == start_variable
        and v_from in start_vertices
        and v_to in final_vertices
    )
