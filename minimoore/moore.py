"""Moore machine."""

from pathlib import Path
from typing import Dict, FrozenSet, Iterable, Optional, Set, Tuple

from graphviz import Digraph  # type: ignore

from minimoore.transducers import (
    FiniteDetTransducer,
    InputSymT,
    OutputSymT,
    StateT,
    TransitionT,
)


class MooreDetMachine(FiniteDetTransducer[InputSymT, OutputSymT]):
    """Deterministic Moore Machine."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        # Store
        self.__output_table: Dict[StateT, Optional[OutputSymT]] = dict()
        self.__transitions: Dict[StateT, Dict[InputSymT, TransitionT]] = dict()

    def _register_state(self, state: StateT):
        """Ops on the new state."""
        self.__output_table[state] = None
        self.__transitions[state] = dict()

    def set_state_output(self, state: StateT, output: OutputSymT):
        """Assign an output symbol to a state."""
        assert self.is_state(state)
        self.__output_table[state] = output

    def new_state_output(self, output: OutputSymT) -> StateT:
        """Create a new state and associate an output symbol."""
        state = self.new_state()
        self.set_state_output(state, output)
        return state

    def new_transition(
        self,
        state1: StateT,
        symbol: InputSymT,
        state2: StateT,
    ):
        """Add a new transition between esisting states."""
        assert self.is_state(state1)
        assert self.is_state(state2)
        transition = (state1, symbol, state2)
        self.__transitions[state1][symbol] = transition

    def output_fn(self, state: StateT) -> OutputSymT:
        """Outputs are associated to states.

        :param state: input state.
        :return: output symbol.
        """
        output = self.__output_table[state]
        assert output is not None, f"Output not assigned for state {state}"
        return output

    def arcs_from(self, state: StateT) -> Set[InputSymT]:
        """Return the set of input symbols that can be read from a state."""
        return set(self.__transitions[state].keys())

    def step(
        self,
        state: StateT,
        symbol: InputSymT,
    ) -> Set[Tuple[StateT, OutputSymT]]:
        """Process one input (see super)."""
        assert self.is_state(state)
        arcs = set()
        if symbol in self.arcs_from(state):
            _, _, state2 = self.__transitions[state][symbol]
            output_symbol = self.output_fn(state)  # Output from current state
            arcs.add((state2, output_symbol))
        return arcs

    @property
    def transitions(self) -> Iterable[TransitionT]:
        """An iterable on all transitions."""
        for state, arcs in self.__transitions.items():
            for symbol, transition in arcs.items():
                yield transition

    def save_graphviz(self, out_path: Path):
        """Save a graph to out_path using graphviz."""
        # Create an empty graph
        graph = Digraph(name="MooreMachine")

        # Create states
        for state in self.states:
            output_sym = self.output_fn(state)
            label = f"{state}: {output_sym}"
            graph.node(str(state), label, root=str(state == self.init_state))

        # Add arcs
        for transition in self.transitions:
            state1, input_sym, state2 = transition
            graph.edge(str(state1), str(state2), label=str(input_sym))

        # Add an arrow for the initial state
        graph.node("init", shape="plaintext")
        graph.edge("init", str(self.init_state))

        # Save
        out_path = out_path.with_suffix(".dot")
        graph.render(filename=out_path)

    def minimize(self) -> "FiniteDetTransducer[InputSymT, OutputSymT]":
        """Return a new minimized transducer equivalent to this.

        This function implements the Hopcroft minimization algorithm for automata.
        The implementation is based on the description in:
        http://arxiv.org/abs/1010.5318.
        """
        pass

    def _output_partitions(self) -> Set[FrozenSet[StateT]]:
        """Return a partition of states based on the output function.

        If two states have the same output associated, they will be in the
        same class.
        :return: a complete partition of states.
        """
        partitions_map: Dict[OutputSymT, Set[StateT]] = dict()
        for state in self.states:
            out = self.output_fn(state)
            states_class = partitions_map.setdefault(out, set())
            states_class.add(state)
        return {frozenset(states) for states in partitions_map.values()}
