from typing import Set
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Terminal, Variable

from project.cfg.cfg import cfg_to_wcnf


def hellings(graph: MultiDiGraph, cfg: CFG) -> Set:
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

    result = set(
        (variable, vertice, vertice)
        for variable in epsilon_productions
        for vertice in graph.nodes
    ) | set(
        (variable, v_from, v_to)
        for variable, terminal in terminal_productions
        for v_from, v_to, label in graph.edges(data="label")
        if terminal == Terminal(label)
    )

    queue = result.copy()
    while len(queue) > 0:
        var_i, v_from, v_to = queue.pop()

        queue |= set(
            triple
            for var_k, l_var, r_var in variable_productions
            for var_j, u_from, u_to in result
            if (
                # in case (var_j, u_from, v_from) \in result
                # and there is a production var_k -> var_j var_i
                path := (u_from, v_to)
                if u_to == v_from and l_var == var_j and r_var == var_i
                else (
                    # in case (var_j, v_to, u_to) \in result
                    # and there is a production var_k -> var_i var_j
                    (v_from, u_to)
                    if u_from == v_to and l_var == var_i and r_var == var_j
                    else None
                )
            )
            and (triple := (var_k,) + path) not in result
        )
        result |= queue

    return result
