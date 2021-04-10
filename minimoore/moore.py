"""Moore machine."""

from typing import Dict, Optional

from minimoore.transducers import FiniteDetTransducer, OutputSymT, StateT


class MooreDetMachine(FiniteDetTransducer):
    """Deterministic Moore Machine."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        # Locals
        self.__output_table: Dict[StateT, Optional[OutputSymT]] = dict()

    def _register_state(self, state: StateT):
        """Ops on the new state."""
        self.__output_table[state] = None

    def set_state_output(self, state: StateT, output: OutputSymT):
        """Assign an output symbol to a state."""
        assert self.is_state(state)
        self.__output_table[state] = output

    def new_state_output(self, output: OutputSymT) -> StateT:
        """Create a new state and associate an output symbol."""
        state = self.new_state()
        self.set_state_output(state, output)
        return state

    def output_fn(self, state: StateT) -> OutputSymT:
        """Outputs are associated to states.

        :param state: input state.
        :return: output symbol.
        """
        assert self.is_state(state)
        output = self.__output_table[state]
        assert output is not None, f"Output not assigned for state {state}"
        return output
