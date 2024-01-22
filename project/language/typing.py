from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.cfg import CFG
from networkx.drawing.nx_pydot import read_dot
from typing import Set, Any
from project.automata.utils import regex_to_dfa, graph_to_nfa
from project.automata.decomposed_fa import DecomposedFA
from project.cfg.ecfg import ECFG
from project.automata.rsm import RecursiveStateMachine


class MySet:
    def __init__(self, st):
        self.__set = set(st)
        if len(st) == 0:
            self.__elem_type = Any
        else:
            self.__elem_type = type(next(iter(st)))

            if any(not isinstance(elem, self.__elem_type) for elem in st):
                raise TypeError("Set elements must be of the same type")

    def __str__(self):
        return self.__set.__str__()

    @property
    def data(self):
        return self.__set


class MyAutomaton:
    def __init__(self, nfa):
        self.nfa: NondeterministicFiniteAutomaton = nfa

    @staticmethod
    def from_regex(regex):
        return MyAutomaton(regex_to_dfa(Regex(regex)))

    @staticmethod
    def from_graph(graph):
        return MyAutomaton(graph_to_nfa(graph))

    @staticmethod
    def from_dot(path):
        return MyAutomaton.from_graph(read_dot(path))

    def set_start(self, start_states):
        result_nfa = self.nfa.copy()
        for state in self.nfa.start_states:
            result_nfa.remove_start_state(state)
        for state in start_states.data:
            result_nfa.add_start_state(state)

        return MyAutomaton(result_nfa)

    def set_final(self, final_states):
        result_nfa = self.nfa.copy()
        for state in self.nfa.final_states:
            result_nfa.remove_final_state(state)
        for state in final_states.data:
            result_nfa.add_final_state(state)

        return MyAutomaton(result_nfa)

    def add_start(self, start_states):
        result_nfa = self.nfa.copy()
        for state in start_states.data:
            result_nfa.add_start_state(state)
        return MyAutomaton(result_nfa)

    def add_final(self, final_states):
        result_nfa = self.nfa.copy()
        for state in final_states.data:
            result_nfa.add_final_state(state)
        return MyAutomaton(result_nfa)

    def get_start(self):
        return MySet(self.nfa.start_states)

    def get_final(self):
        return MySet(self.nfa.final_states)

    def get_edges(self):
        return MySet(
            {
                (s_from, label, s_to)
                for s_from, d in self.nfa._transition_function._transitions.items()
                for label, d_to in d.items()
                for s_to in d_to
            }
        )

    def get_labels(self):
        return MySet(self.nfa.symbols)

    def get_vertices(self):
        return MySet({state.value for state in self.nfa.states})

    def intersect(self, other):
        left = DecomposedFA.from_fa(self.nfa)
        right = DecomposedFA.from_fa(other.nfa)
        return MyAutomaton(left.intersect(right).to_fa())

    def get_reachable(self):
        dfa = DecomposedFA.from_fa(self.nfa)

        states_by_indices = {i: state for state, i in dfa.states_with_indices.items()}
        return MySet(
            set(
                states_by_indices[state_to]
                for state_from, state_to in zip(*dfa.transitive_closure().nonzero())
                if states_by_indices[state_from] in dfa.start_states
                and states_by_indices[state_to] in dfa.final_states
            )
        )

    def union(self, other):
        return MyAutomaton(self.nfa.union(other.nfa).to_deterministic())

    def concat(self, other):
        return MyAutomaton(self.nfa.concatenate(other.nfa).to_deterministic())

    def kleene(self):
        return MyAutomaton(self.nfa.kleene_star().to_deterministic())


class MyCFG:
    def __init__(self, cfg):
        self.__cfg: CFG = cfg

    @staticmethod
    def from_text(cfg):
        return MyCFG(CFG.from_text(cfg))

    def __str__(self):
        return self.__cfg.to_text()

    def get_reachable(self):
        ecfg = ECFG.from_cfg(self.__cfg)
        rsm = RecursiveStateMachine.from_ecfg(ecfg)
        dfa = DecomposedFA.from_rsm(rsm)

        states_by_indices = {i: state for state, i in dfa.states_with_indices.items()}
        return MySet(
            set(
                (states_by_indices[state_from], states_by_indices[state_to])
                for state_from, state_to in zip(*dfa.transitive_closure().nonzero())
                if states_by_indices[state_from] in dfa.start_states
                and states_by_indices[state_to] in dfa.final_states
            )
        )

    def intersect(self, other):
        return MyCFG(self.__cfg.intersection(other.nfa))

    def union(self, other):
        return MyCFG(self.__cfg.union(other.__cfg))

    def concat(self, other):
        return MyCFG(self.__cfg.concatenate(other.__cfg))
