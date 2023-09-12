from dataclasses import dataclass
from typing import Any, Set
import cfpq_data


@dataclass
class GraphInfo:
    vertices: int
    edges: int
    labels: Set[Any]


def get_graph_info(name: str) -> GraphInfo:
    path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(path)

    return GraphInfo(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        set(cfpq_data.get_sorted_labels(graph)),
    )
