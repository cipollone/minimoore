"""Moore machine."""

from typing import Dict, Optional, Set, Tuple

from minimoore.transducers import FiniteDetTransducer, InputSymT, OutputSymT, StateT

TransitionT = Tuple[StateT, InputSymT, StateT]


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

    def is_arc(self, state: StateT, symbol: InputSymT):
        """Check whether a transition exists from a node."""
        return symbol in self.__transitions[state]

    def step(
        self,
        state: StateT,
        symbol: InputSymT,
    ) -> Set[Tuple[StateT, OutputSymT]]:
        """Process one input (see super)."""
        assert self.is_state(state)
        arcs = set()
        if self.is_arc(state, symbol):
            _, _, state2 = self.__transitions[state][symbol]
            output_symbol = self.output_fn(state)  # Output from current state
            arcs.add((state2, output_symbol))
        return arcs
