from pyformlang.finite_automaton import (
    FiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
import pycubool as pcb
from typing import Dict, Any


class CbDecomposedFA:
    def __init__(self):
        self.matrices = dict()
        self.start_states = set()
        self.final_states = set()
        self.states_with_indices = dict()
        self.num_states = 0

    @staticmethod
    def from_fa(finite_automaton: FiniteAutomaton) -> "CbDecomposedFA":
        result = CbDecomposedFA()
        result.start_states = finite_automaton.start_states
        result.final_states = finite_automaton.final_states
        result.num_states = len(finite_automaton.states)
        result.states_with_indices = dict(
            zip(finite_automaton.states, range(result.num_states))
        )

        for s_from, label, s_to in finite_automaton:
            if label not in result.matrices:
                result.matrices[label] = pcb.Matrix.empty(
                    shape=(result.num_states, result.num_states)
                )
            result.matrices[label][
                result.states_with_indices[s_from], result.states_with_indices[s_to]
            ] = True

        return result

    @staticmethod
    def from_rsm(rsm) -> "CbDecomposedFA":
        result = CbDecomposedFA()
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
                    result.matrices[label] = pcb.Matrix.empty(
                        shape=(result.num_states, result.num_states)
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
                map(lambda x: (x[0], label, x[1]), self.matrices[label])
            )

        for state in self.start_states:
            result.add_start_state(state)

        for state in self.final_states:
            result.add_final_state(state)

        return result

    def intersect(self, other: "CbDecomposedFA") -> "CbDecomposedFA":
        result = CbDecomposedFA()

        for label in self.matrices.keys() & other.matrices.keys():
            result.matrices[label] = self.matrices[label].kronecker(
                other.matrices[label]
            )

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

    def transitive_closure(self):
        if self.num_states == 0:
            return pcb.Matrix.empty(shape=(0, 0))

        result = pcb.Matrix.empty(list(self.matrices.values())[0].shape)
        for matrix in self.matrices.values():
            result.ewiseadd(matrix, out=result)

        for _ in range(self.num_states):
            result.mxm(result, out=result, accumulate=True)

        return result
