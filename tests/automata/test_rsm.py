import pytest
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.cfg import Variable, Terminal
from project.automata.rsm import RecursiveStateMachine
from project.cfg.ecfg import ECFG
import os

ECFG_RESOURCES_PATH = "tests/resources/ecfg"


def create_dfa(start_state=None, transitions=None, final_states=None):
    dfa = DeterministicFiniteAutomaton(
        start_state=start_state, final_states=final_states
    )
    dfa.add_transitions(transitions)
    return dfa


@pytest.mark.parametrize(
    "rsm",
    [
        RecursiveStateMachine(
            {Variable("S")},
            {Terminal("a")},
            Variable("S"),
            {
                Variable("S"): create_dfa(
                    start_state=0,
                    transitions=[(0, "S", 1), (1, "a", 2)],
                    final_states={2},
                )
            },
        ),
        RecursiveStateMachine(
            {Variable("S"), Variable("N")},
            {Terminal("a")},
            Variable("S"),
            {
                Variable("S"): create_dfa(
                    start_state=0,
                    transitions=[(0, "a", 1), (1, "a", 1), (2, "a", 3)],
                    final_states={1, 2},
                ),
                Variable("N"): create_dfa(
                    start_state=0,
                    transitions=[(0, "a", 0)],
                ),
            },
        ),
        RecursiveStateMachine(
            {Variable("S"), Variable("N"), Variable("M")},
            {Terminal("a"), Terminal("b"), Terminal("c")},
            Variable("N"),
            {
                Variable("S"): create_dfa(
                    start_state=0,
                    transitions=[
                        (0, "a", 1),
                        (0, "b", 1),
                        (1, "S", 1),
                        (1, "N", 2),
                        (3, "M", 2),
                    ],
                    final_states={0, 1, 2},
                ),
                Variable("N"): create_dfa(
                    start_state=0,
                    transitions=[
                        (0, "S", 1),
                        (0, "c", 1),
                        (1, "M", 1),
                        (1, "c", 2),
                        (3, "M", 2),
                        (0, "N", 3),
                        (2, "b", 1),
                    ],
                    final_states={1, 2},
                ),
                Variable("S"): create_dfa(
                    start_state=0,
                    transitions=[
                        (0, "a", 1),
                        (0, "b", 1),
                        (0, "c", 1),
                        (0, "S", 1),
                        (0, "N", 1),
                        (0, "M", 1),
                    ],
                    final_states={1},
                ),
            },
        ),
    ],
)
def test_rsm_minimize(rsm):
    received = rsm.minimize()
    for variable, dfa in rsm.automata.items():
        assert dfa == received.automata[variable]


@pytest.mark.parametrize("filename", [f"grammar{i}.cfg" for i in range(3)])
def test_rsm_from_ecfg(filename):
    ecfg = ECFG.from_file(os.path.join(ECFG_RESOURCES_PATH, filename))
    received = RecursiveStateMachine.from_ecfg_file(
        os.path.join(ECFG_RESOURCES_PATH, filename)
    )

    assert ecfg.productions.keys() == received.automata.keys()
    for variable in ecfg.productions.keys():
        assert (
            received.automata[variable] == ecfg.productions[variable].to_epsilon_nfa()
        )
