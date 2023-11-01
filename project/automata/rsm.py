from pyformlang.finite_automaton import FiniteAutomaton
from project.cfg.ecfg import ECFG


class RecursiveStateMachine:
    def __init__(self):
        self.terminals = []
        self.nonterminals = []
        self.start_nonterminal = []
        self.automaton = FiniteAutomaton()

    @staticmethod
    def from_ecfg(ecfg: ECFG) -> "RecursiveStateMachine":
        pass

    @staticmethod
    def from_ecfg(path: str) -> "RecursiveStateMachine":
        pass

    def minimize(self) -> "RecursiveStateMachine":
        pass
