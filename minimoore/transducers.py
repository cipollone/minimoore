"""Interfaces for finite transducers."""

from abc import ABC, abstractmethod
from typing import Generic, Hashable, Iterable, Optional, Sequence, Set, Tuple, TypeVar

# Types
InputSymT = TypeVar("InputSymT", bound=Hashable)
OutputSymT = TypeVar("OutputSymT", bound=Hashable)
StateT = int
StatesT = Set[StateT]
TransitionT = Tuple[StateT, InputSymT, StateT]


class FiniteTransducer(Generic[InputSymT, OutputSymT], ABC):
    """Superclass of a finite transducer.

    States are contiguous integers from 0 to n_states -1.
    """

    def __init__(self):
        """Initialize an empty transducer."""
        self.n_states = 0
        self.init_states = set()

    def __eq__(self, other) -> bool:
        """Test for equality.

        Compare two objects. This returns true only if the members are the
        same. Call this in subclasses.
        """
        if other is None:
            return False
        if self is other:
            return True
        if not isinstance(other, FiniteTransducer):
            return False

        # Check fields
        if self.n_states != other.n_states:
            return False
        if self.init_states != other.init_states:
            return False
        if set(self.input_alphabet) != set(other.input_alphabet):
            return False
        if set(self.output_alphabet) != set(other.output_alphabet):
            return False
        if set(self.transitions) != set(other.transitions):
            return False

        return True

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
    def arcs_from(self, state: StateT) -> Set[InputSymT]:
        """Return the set of input symbols that can be read from a state."""
        pass

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
            nondeterminism. If a transition is not defined, the set can be
            empty.
        """
        pass

    @property
    def states(self) -> Iterable[StateT]:
        """An iterable on states."""
        return range(self.n_states)

    @property
    @abstractmethod
    def input_alphabet(self) -> Iterable[InputSymT]:
        """Return an iterable on the entire input aphabet."""
        pass

    @property
    @abstractmethod
    def output_alphabet(self) -> Iterable[OutputSymT]:
        """Return an iterable on the entire output aphabet."""
        pass

    @property
    @abstractmethod
    def transitions(self) -> Iterable[TransitionT]:
        """Return an iterable on all transitions."""
        pass

    def save_graphviz(self, out_path: str):
        """Save a graph to out_path using graphviz."""
        raise NotImplementedError("Should be overridden in subclasses")

    def is_complete(self) -> bool:
        """Check if this machine is complete.

        :return: true if all inputs are applicable in every state.
        """
        in_aphabet = set(self.input_alphabet)
        for s in self.states:
            if len(self.arcs_from(s)) < len(in_aphabet):
                return False
        return True


class FiniteDetTransducer(FiniteTransducer[InputSymT, OutputSymT]):
    """A deterministic finite transducer."""

    def __init__(self):
        """Initialize and empty transducer."""
        super().__init__()
        self.init_state: Optional[StateT] = None

    def set_initial(self, state: StateT):
        """Set state as initial."""
        # Substitute the previous initial state
        self.init_states.clear()
        super().set_initial(state)
        self.init_state = state

    def det_step(
        self,
        state: StateT,
        symbol: InputSymT,
    ) -> Optional[Tuple[StateT, OutputSymT]]:
        """Deterministic step.

        :param state: first state.
        :param symbol: input symbol
        :return: (next_state, output_symbol) or None if no transition exists.
        """
        assert self.is_state(state)
        if symbol not in self.arcs_from(state):
            return None

        transitions = self.step(state, symbol)

        assert len(transitions) == 1, "Model is not deterministic"
        next_state, output_symbol = next(iter(transitions))

        return next_state, output_symbol

    def process_word_from(
        self,
        state: StateT,
        word: Sequence[InputSymT],
        strict=True,
    ) -> Tuple[Sequence[OutputSymT], StateT]:
        """Transforms an entire word starting from a specific state.

        :param state: the initial state.
        :param word: the input word.
        :param strict: if True, a transition which doesn't exists causes
            a ValueError. If False, a shorter output word is returned.
        :return: the sequence of symbols produced in output, and the state
            reached at the end of the computation.
        """
        assert self.is_state(state)
        output_word = []
        for symbol in word:
            arc = self.det_step(state, symbol)
            if arc is not None:
                state, output_symbol = arc
                output_word.append(output_symbol)
            else:
                if strict:
                    raise ValueError(f"Transition {state, symbol} doesn't exists")
                else:
                    break
        return output_word, state

    def process_word(
        self,
        word: Sequence[InputSymT],
        strict=True,
    ) -> Sequence[OutputSymT]:
        """Transforms an entire word with the automaton.

        :param word: an entire trace of symbols.
        :param strict: if True, a transition which doesn't exists causes
            a ValueError. If False, a shorter output word is returned.
        :return: the sequence of symbols produced in output.
        """
        assert self.init_state is not None, "Initial state not set"
        output_word, _ = self.process_word_from(self.init_state, word, strict=strict)
        return output_word
