import pytest
from project.graphs import utils
import os
import cfpq_data
import filecmp


def test_save_to_dot():
    graph = cfpq_data.labeled_cycle_graph(5)
    utils.graph_to_dot(graph, "tests/resources/received_graph.dot")
    assert filecmp.cmp(
        "tests/resources/expected_graph.dot", "tests/resources/received_graph.dot"
    )
    os.remove("tests/resources/received_graph.dot")


def test_trivial_two_cycles_graph():
    graph = utils.create_labeled_two_cycles_graph(1, 1, ("a", "b"))
    utils.graph_to_dot(graph, "tests/resources/received_graph.dot")
    assert filecmp.cmp(
        "tests/resources/trivial_two_cycles_graph.dot",
        "tests/resources/received_graph.dot",
    )
    os.remove("tests/resources/received_graph.dot")


def test_two_cycles_graph():
    graph = utils.create_labeled_two_cycles_graph(1, 1, ("a", "b"))
    utils.graph_to_dot(graph, "tests/resources/received_graph.dot")
    assert filecmp.cmp(
        "tests/resources/trivial_two_cycles_graph.dot",
        "tests/resources/received_graph.dot",
    )
    os.remove("tests/resources/received_graph.dot")
