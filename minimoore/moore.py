"""Moore machine."""

from pathlib import Path
from typing import AbstractSet, Dict, FrozenSet, Iterable, Optional, Set, Tuple

from graphviz import Digraph  # type: ignore

from minimoore.transducers import (
    FiniteDetTransducer,
    InputSymT,
    OutputSymT,
    StateT,
    TransitionT,
)

# Types
SplitterT = Tuple[AbstractSet[StateT], InputSymT]


class MooreDetMachine(FiniteDetTransducer[InputSymT, OutputSymT]):
    """Deterministic Moore Machine."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        # Store
        self.__output_table: Dict[StateT, Optional[OutputSymT]] = dict()
        self.__transitions: Dict[StateT, Dict[InputSymT, TransitionT]] = dict()
        self.__input_symbols: Set[InputSymT] = set()
        self.__output_symbols: Set[OutputSymT] = set()

    def _register_state(self, state: StateT):
        """Ops on the new state."""
        self.__output_table[state] = None
        self.__transitions[state] = dict()

    def set_state_output(self, state: StateT, output: OutputSymT):
        """Assign an output symbol to a state."""
        assert self.is_state(state)
        self.__output_table[state] = output
        self.__output_symbols.add(output)

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
        self.__input_symbols.add(symbol)

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

    @property
    def input_alphabet(self) -> Iterable[InputSymT]:
        """Return an iterable on the entire input aphabet."""
        return self.__input_symbols

    @property
    def output_alphabet(self) -> Iterable[OutputSymT]:
        """Return an iterable on the entire output aphabet."""
        return self.__output_symbols

    def save_graphviz(self, out_path: str):
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
        path = Path(out_path).with_suffix(".dot")
        graph.render(filename=path)

    def minimize(self) -> "FiniteDetTransducer[InputSymT, OutputSymT]":
        """Return a new minimized transducer equivalent to this."""
        return self._hopcroft_minimize()

    def _hopcroft_minimize(self) -> "FiniteDetTransducer[InputSymT, OutputSymT]":
        """Variant of Hopcroft minimization algorithm for transducers.

        This assumes the transition function to be complete.
        """
        # Init
        waiting_set: Set[SplitterT] = set()
        partition = self.__output_partitions()  # Initial partitions

        # Initial list of splitters
        for symbol in self.input_alphabet:
            for group in partition:
                waiting_set.add((group, symbol))

        # Until done
        while len(waiting_set) > 0:
            new_partition = set()

            # Split each set
            splitter = waiting_set.pop()
            for group in partition:
                sub_partition = self.__apply_splitter(
                    group=group,
                    symbol=splitter[1],
                    test_set=splitter[0],
                )

                # Add result of split
                new_partition.update(sub_partition)

                # Not split. Nothing to do
                if len(sub_partition) == 1:
                    continue

                # Update waiting set
                for symbol in self.input_alphabet:
                    waiting_set.discard((group, symbol))
                    waiting_set.update({
                        (sub_group, symbol) for sub_group in sub_partition
                    })

            # Next
            partition = new_partition

        return self.__from_partitions(partition)

    def __output_partitions(self) -> Set[FrozenSet[StateT]]:
        """Return a partition of states based on the output function.

        If two states have the same output associated, they will be in the
        same class. Auxiliary function for minimize.
        :param states: a set of states to partition.
        :return: a complete partition of states.
        """
        partitions_map: Dict[OutputSymT, Set[StateT]] = dict()
        for state in self.states:
            out = self.output_fn(state)
            states_class = partitions_map.setdefault(out, set())
            states_class.add(state)
        return {frozenset(states) for states in partitions_map.values()}

    def __apply_splitter(
        self,
        group: AbstractSet[StateT],
        symbol: InputSymT,
        test_set: AbstractSet[StateT],
    ) -> Set[FrozenSet[StateT]]:
        """Applies the splitter (test_set, symbol) to create a partition of group.

        Applying a splitter means checking whether every state in the group,
        for the given symbol leads to the equivalence class test_set, with
        an equivalent transition.
        :param group: set of states to split.
        :param symbol: input test symbol.
        :param test_set: checking whether transitions will go to this set.
        :return: a partition of group
        """
        # Distinguished by next state and output symbol
        partitions_map: Dict[Tuple[bool, OutputSymT], Set[StateT]] = dict()

        for state in group:
            transition = self.det_step(state, symbol)
            assert transition is not None, "Transition function is not complete"
            next_state, output_symbol = transition

            inside = next_state in test_set
            states_class = partitions_map.setdefault(
                (inside, output_symbol), set())
            states_class.add(state)
        return {frozenset(states) for states in partitions_map.values()}

    def __from_partitions(
        self,
        partition: AbstractSet[AbstractSet[StateT]],
    ) -> "FiniteDetTransducer[InputSymT, OutputSymT]":
        """Creates a new machine from a partition of states.

        Given a set of equivalence classes, the partition, this function builds
        a new automaton equivalent to this. Assumes a complete automaton.
        :param partition: a partition of states of this automaton in
            equivalence classes.
        :return: a new minimized automaton.
        """
        automa = MooreDetMachine[InputSymT, OutputSymT]()

        # TODO: this is ugly. better to collect transitions together with
        #  partitions

        # Inits
        partition_list = list(partition)
        partition_states: Dict[int, StateT] = dict()

        # A state and output for each class
        for i, group in enumerate(partition_list):
            any_state = next(iter(group))
            group_output = self.output_fn(any_state)
            created_state = automa.new_state_output(group_output)
            partition_states[i] = created_state

            # Initial?
            for s in group:
                if self.init_state == s:
                    automa.set_initial(created_state)

        # A transition for each class
        for i, group in enumerate(partition_list):
            any_state = next(iter(group))

            # Copy arcs
            for symbol in self.input_alphabet:
                transition = self.det_step(any_state, symbol)
                assert transition is not None, "Transition fn is not complete"
                for j, next_group in enumerate(partition_list):
                    if transition[0] in next_group:
                        new_state = partition_states[i]
                        new_next_state = partition_states[j]
                        automa.new_transition(new_state, symbol, new_next_state)
                        break

        return automa
