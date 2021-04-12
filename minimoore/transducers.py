"""Interfaces for finite transducers."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, Set, Tuple, TypeVar

# Types
InputSymT = TypeVar("InputSymT")
OutputSymT = TypeVar("OutputSymT")
StateT = int
StatesT = Set[StateT]

# TODO: complete arcs


class FiniteTransducer(Generic[InputSymT, OutputSymT], ABC):
    """Superclass of a finite transducer.

    States are contiguous integers from 0 to n_states -1.
    """

    def __init__(self):
        """Initialize an empty transducer."""
        self.n_states = 0
        self.init_states = set()

    def new_state(self) -> StateT:
        """Create a new state and return the id."""
        state = self.n_states
        self.n_states += 1
        self._register_state(state)
        return state

    @abstractmethod
    def _register_state(self, state: StateT):
        """Callback operations on the new state.

        Subclasses might need to do something for each new state.
        :param state: the new state id.
        """
        pass

    def set_initial(self, state: StateT):
        """Add to initial states."""
        if not self.is_state(state):
            raise ValueError("Not a valid state")
        self.init_states.add(state)

    def is_state(self, state: StateT):
        """Check whether it's a valid state."""
        return state is not None and 0 <= state < self.n_states

    @abstractmethod
    def step(
        self,
        state: StateT,
        symbol: InputSymT,
    ) -> Set[Tuple[StateT, OutputSymT]]:
        """Process one input from a state.

        :param state: first state.
        :param symbol: input symbol
        :return: a set of (next_state, output_symbol) because of possible
            nondeterminism.
        """
        pass


class FiniteDetTransducer(FiniteTransducer[InputSymT, OutputSymT]):
    """A deterministic finite transducer."""

    def __init__(self):
        """Initialize and empty transducer."""
        super().__init__()
        self.init_state: Optional[StateT] = None

    def set_initial(self, state: StateT):
        """Set state as initial."""
        assert (
            self.init_state is None and len(self.init_states) == 0
        ), "Initial state already set"
        super().set_initial(state)
        self.init_state = state

    def det_step(
        self,
        state: StateT,
        symbol: InputSymT,
    ) -> Tuple[StateT, OutputSymT]:
        """Deterministic step.

        :param state: first state.
        :param symbol: input symbol
        :return: (next_state, output_symbol).
        """
        assert self.is_state(state)
        transitions = self.step(state, symbol)
        assert len(transitions) == 1, "Model is not deterministic"
        next_state, output_symbol = next(iter(transitions))
        return next_state, output_symbol

    def process_word_from(
        self,
        state: StateT,
        word: Sequence[InputSymT],
    ) -> Tuple[Sequence[OutputSymT], StateT]:
        """Transforms an entire word starting from a specific state.

        :param state: the initial state.
        :param word: the input word.
        :return: the sequence of symbols produced in output, and the state
            reached at the end of the computation.
        """
        assert self.is_state(state)
        output_word = []
        for symbol in word:
            state, output_symbol = self.det_step(state, symbol)
            output_word.append(output_symbol)
        return output_word, state

    def process_word(self, word: Sequence[InputSymT]) -> Sequence[OutputSymT]:
        """Transforms an entire word with the automaton.

        :param word: an entire trace of symbols.
        :return: the sequence of symbols produced in output.
        """
        assert self.init_state is not None, "Initial state not set"
        output_word, _ = self.process_word_from(self.init_state, word)
        return output_word
