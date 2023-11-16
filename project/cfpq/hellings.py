from typing import Set
from networkx import MultiDiGraph
from pyformlang.cfg import CFG

from project.cfg.cfg import cfg_to_wcnf


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
        for variable, _ in filter(lambda prod: prod[1] == label, terminal_productions):
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
                    lambda prod: prod[1] == var_j and prod[2] == var_i,
                    terminal_productions,
                ):
                    queue.add((var_k, u_from, v_to))
                    result.add((var_k, u_from, v_to))

            if u_from == v_to:
                for var_k, _, _ in filter(
                    lambda prod: prod[1] == var_i and prod[2] == var_j,
                    terminal_productions,
                ):
                    queue.add((var_k, v_from, u_to))
                    result.add((var_k, v_from, u_to))

    return result
