from typing import Dict, Set
from pyformlang.cfg import Variable, Terminal
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from project.cfg.ecfg import ECFG
from project.automata.utils import regex_to_dfa
import os

from loguru import logger


class RecursiveStateMachine:
    def __init__(
        self,
        variables: Set[Variable] = set(),
        terminals: Set[Terminal] = set(),
        start: Variable = Variable("S"),
        automata: Dict[Variable, DeterministicFiniteAutomaton] = dict(),
    ):
        self.variables = variables
        self.terminals = terminals
        self.start = start
        self.automata = automata

    @staticmethod
    def from_ecfg(ecfg: ECFG) -> "RecursiveStateMachine":
        automata = dict()
        # logger.info(result.automata)
        for variable, regex in ecfg.productions.items():
            automata[variable] = regex_to_dfa(regex)

        return RecursiveStateMachine(
            ecfg.variables, ecfg.terminals, ecfg.start, automata
        )

    @staticmethod
    def from_ecfg_text(text: str) -> "RecursiveStateMachine":
        return RecursiveStateMachine.from_ecfg(ECFG.from_text(text))

    @staticmethod
    def from_ecfg_file(path: str) -> "RecursiveStateMachine":
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        return RecursiveStateMachine.from_ecfg(ECFG.from_file(path))

    def minimize(self) -> "RecursiveStateMachine":
        result = RecursiveStateMachine(self.variables, self.terminals, self.start)

        for variable, dfa in self.automata.items():
            result.automata[variable] = dfa.minimize()

        return result
