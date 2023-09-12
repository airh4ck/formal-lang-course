import cfpq_data
import networkx as nx


def create_labeled_two_cycles_graph(
    n: int, m: int, labels: tuple[str, str]
) -> nx.MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)


def graph_to_dot(graph: nx.MultiDiGraph, output_path: str) -> None:
    pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(output_path)
