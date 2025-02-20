from pyformlang.finite_automaton import (
    FiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from scipy.sparse import csr_matrix, kron, block_diag
from project.automata.rsm import RecursiveStateMachine

from typing import Dict, Any


class DecomposedFA:
    def __init__(self):
        self.matrices = dict()
        self.start_states = set()
        self.final_states = set()
        self.states_with_indices = dict()
        self.num_states = 0

    @staticmethod
    def from_fa(finite_automaton: FiniteAutomaton) -> "DecomposedFA":
        result = DecomposedFA()
        result.start_states = finite_automaton.start_states
        result.final_states = finite_automaton.final_states
        result.num_states = len(finite_automaton.states)
        result.states_with_indices = dict(
            zip(finite_automaton.states, range(result.num_states))
        )

        for s_from, label, s_to in finite_automaton:
            if label not in result.matrices:
                result.matrices[label] = csr_matrix(
                    (result.num_states, result.num_states), dtype=bool
                )
            result.matrices[label][
                result.states_with_indices[s_from], result.states_with_indices[s_to]
            ] = True

        return result

    @staticmethod
    def from_rsm(rsm: RecursiveStateMachine) -> "DecomposedFA":
        result = DecomposedFA()
        states = set()
        result.start_states = set()
        result.final_states = set()

        for variable, dfa in rsm.automata.items():
            for st in dfa.states:
                state = State((variable, st.value))
                states.add(state)
                if st in dfa.start_states:
                    result.start_states.add(state)
                if st in dfa.final_states:
                    result.final_states.add(state)

        result.num_states = len(states)
        result.states_with_indices = dict(zip(states, range(result.num_states)))
        for variable, dfa in rsm.automata.items():
            for s_from, label, s_to in dfa:
                if label not in result.matrices:
                    result.matrices[label] = csr_matrix(
                        (result.num_states, result.num_states), dtype=bool
                    )

                result.matrices[label][
                    result.states_with_indices[State((variable, s_from.value))],
                    result.states_with_indices[State((variable, s_to.value))],
                ] = True

        return result

    def to_fa(self) -> NondeterministicFiniteAutomaton:
        result = NondeterministicFiniteAutomaton()

        for label in self.matrices:
            result.add_transitions(
                map(lambda x: (x[0], label, x[1]), zip(*self.matrices[label].nonzero()))
            )

        for state in self.start_states:
            result.add_start_state(state)

        for state in self.final_states:
            result.add_final_state(state)

        return result

    def intersect(self, other: "DecomposedFA") -> "DecomposedFA":
        result = DecomposedFA()

        for label in self.matrices.keys() & other.matrices.keys():
            result.matrices[label] = kron(self.matrices[label], other.matrices[label])

        for self_index, self_state in enumerate(self.states_with_indices.keys()):
            for other_index, other_state in enumerate(other.states_with_indices.keys()):
                result_state = self_index * other.num_states + other_index
                result.states_with_indices[result_state] = result_state

                if (
                    self_state in self.start_states
                    and other_state in other.start_states
                ):
                    result.start_states.add(result_state)

                if (
                    self_state in self.final_states
                    and other_state in other.final_states
                ):
                    result.final_states.add(result_state)

        result.num_states = self.num_states * other.num_states
        return result

    def transitive_closure(self) -> csr_matrix:
        if self.num_states == 0:
            return csr_matrix((0, 0), dtype=bool)

        result = sum(self.matrices.values())

        for _ in range(self.num_states):
            result += result @ result

        return result

    def direct_sum(self, other: "DecomposedFA") -> Dict[Any, csr_matrix]:
        result = dict()

        for label in self.matrices.keys() | other.matrices.keys():
            self_matrix = self.matrices.get(
                label, csr_matrix((self.num_states, self.num_states), dtype=bool)
            )
            other_matrix = other.matrices.get(
                label, csr_matrix((other.num_states, other.num_states), dtype=bool)
            )

            result[label] = block_diag(
                (self_matrix, other_matrix), format="csr", dtype=bool
            )

        return result
