from typing import Set
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Terminal, Variable

from project.cfg.cfg import cfg_to_wcnf

from loguru import logger


def hellings(graph: MultiDiGraph, cfg: CFG) -> Set:
    wcnf = cfg_to_wcnf(cfg)

    epsilon_productions = set()
    terminal_productions = set()
    variable_productions = set()

    for production in wcnf.productions:
        head, body = production.head, production.body
        if len(body) == 0:
            epsilon_productions.add(head)

        if len(body) == 1:
            terminal_productions.add((head, body[0]))

        if len(body) == 2:
            variable_productions.add((head, body[0], body[1]))

    result = set()
    for v_from, v_to, label in graph.edges(data="label"):
        for variable, _ in filter(
            lambda prod: prod[1] == Terminal(label), terminal_productions
        ):
            result.add((variable, v_from, v_to))

    for vertice in graph.nodes:
        for variable in epsilon_productions:
            result.add((variable, vertice, vertice))

    queue = result.copy()
    while len(queue) > 0:
        var_i, v_from, v_to = queue.pop()
        for var_j, u_from, u_to in result:
            if u_to == v_from:
                for var_k, _, _ in filter(
                    lambda prod: prod[1] == var_j
                    and prod[2] == var_i
                    and (prod[0], u_from, v_to) not in result,
                    variable_productions,
                ):
                    queue.add((var_k, u_from, v_to))

            if u_from == v_to:
                for var_k, _, _ in filter(
                    lambda prod: prod[1] == var_i
                    and prod[2] == var_j
                    and (prod[0], v_from, u_to) not in result,
                    variable_productions,
                ):
                    queue.add((var_k, v_from, u_to))
        result |= queue

    return result


def cfpq_hellings(
    graph: MultiDiGraph,
    cfg: CFG,
    start_variable: Variable = Variable("S"),
    start_vertices: Set | None = None,
    final_vertices: Set | None = None,
) -> Set:
    if not start_vertices:
        start_vertices = set(graph.nodes)
    if not final_vertices:
        final_vertices = set(graph.nodes)

    hellings_result = hellings(graph, cfg)
    return set(
        (v_from, v_to)
        for variable, v_from, v_to in hellings_result
        if variable == start_variable
        and v_from in start_vertices
        and v_to in final_vertices
    )
