import pytest
from project.automata import utils
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
    TransitionFunction,
    NondeterministicTransitionFunction,
    Symbol,
)
import networkx as nx


def test_trivial_regex_to_dfa():
    regex = Regex("")
    automaton = utils.regex_to_dfa(regex)

    assert automaton == DeterministicFiniteAutomaton()


def test_regex_to_dfa():
    regex = Regex("(0|1)*1(0|1)")

    transition_function = TransitionFunction()
    transition_function.add_transition(State(0), Symbol("0"), State(0))
    transition_function.add_transition(State(0), Symbol("1"), State(1))
    transition_function.add_transition(State(1), Symbol("0"), State(3))
    transition_function.add_transition(State(1), Symbol("1"), State(2))
    transition_function.add_transition(State(2), Symbol("0"), State(3))
    transition_function.add_transition(State(2), Symbol("1"), State(2))
    transition_function.add_transition(State(3), Symbol("0"), State(0))
    transition_function.add_transition(State(3), Symbol("1"), State(1))
    expected_automaton = DeterministicFiniteAutomaton(
        {State(i) for i in range(4)},
        {Symbol("0"), Symbol("1")},
        transition_function,
        State(0),
        {State(2), State(3)},
    )

    assert utils.regex_to_dfa(regex) == expected_automaton


def test_graph_to_nfa():
    graph = nx.drawing.nx_pydot.read_dot("tests/resources/regex_graph.dot")

    transition_function = NondeterministicTransitionFunction()
    transition_function.add_transition(State("0"), Symbol("0"), State("0"))
    transition_function.add_transition(State("0"), Symbol("1"), State("0"))
    transition_function.add_transition(State("0"), Symbol("1"), State("1"))
    transition_function.add_transition(State("1"), Symbol("0"), State("2"))
    transition_function.add_transition(State("1"), Symbol("1"), State("3"))
    assert utils.graph_to_nfa(
        graph, start_states={"0"}, final_states={"2", "3"}
    ) == NondeterministicFiniteAutomaton(
        {State(str(i)) for i in range(4)},
        {Symbol("0"), Symbol("1")},
        transition_function,
        {State("0")},
        {State("2"), State("3")},
    )


def test_graph_to_nfa_no_states():
    graph = nx.drawing.nx_pydot.read_dot("tests/resources/regex_graph.dot")

    transition_function = NondeterministicTransitionFunction()
    transition_function.add_transition(State("0"), Symbol("0"), State("0"))
    transition_function.add_transition(State("0"), Symbol("1"), State("0"))
    transition_function.add_transition(State("0"), Symbol("1"), State("1"))
    transition_function.add_transition(State("1"), Symbol("0"), State("2"))
    transition_function.add_transition(State("1"), Symbol("1"), State("3"))
    assert utils.graph_to_nfa(graph) == NondeterministicFiniteAutomaton(
        {State(str(i)) for i in range(4)},
        {Symbol("0"), Symbol("1")},
        transition_function,
        {State(str(i)) for i in range(4)},
        {State(str(i)) for i in range(4)},
    )


def test_two_cycles_graph():
    graph = nx.drawing.nx_pydot.read_dot("tests/resources/trivial_two_cycles_graph.dot")
    regex = Regex("(a.a|b.b)*")

    assert utils.graph_to_nfa(
        graph, start_states={"0"}, final_states={"0"}
    ) == utils.regex_to_dfa(regex)
