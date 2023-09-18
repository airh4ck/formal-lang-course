import pytest
from project.graphs.graph_info import get_graph_info


def test_get_pizza_graph():
    expected_vertices = 671
    expected_edges = 1980

    expected_labels = {
        "first",
        "versionInfo",
        "unionOf",
        "subPropertyOf",
        "inverseOf",
        "complementOf",
        "comment",
        "range",
        "someValuesFrom",
        "minCardinality",
        "label",
        "hasValue",
        "equivalentClass",
        "rest",
        "intersectionOf",
        "onProperty",
        "domain",
        "oneOf",
        "subClassOf",
        "allValuesFrom",
        "type",
        "disjointWith",
        "distinctMembers",
    }

    graph_info = get_graph_info("pizza")

    assert expected_vertices == graph_info.vertices
    assert expected_edges == graph_info.edges
    assert expected_labels == graph_info.labels
