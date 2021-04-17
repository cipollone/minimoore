"""Tests for moore module."""

import pytest

from minimoore.moore import MooreDetMachine


class TestMooreDetMachine:
    """Test MooreDetMachine."""

    def test_empty(self):
        """Test initialization."""
        automaton = MooreDetMachine[str, str]()
        assert automaton.n_states == 0

    def test_states(self):
        """Test creation of state and is_state."""
        automaton = MooreDetMachine[str, str]()
        assert automaton.new_state() == 0
        assert automaton.new_state() == 1
        assert automaton.new_state() == 2

        assert automaton.n_states == 3

        # is state
        assert automaton.is_state(0)
        assert not automaton.is_state(-1)
        assert not automaton.is_state(3)

        # Initial
        automaton.set_initial(1)
        assert len(automaton.init_states) == 1
        assert automaton.init_state == 1
        with pytest.raises(AssertionError):
            automaton.set_initial(0)

    def test_arcs(self):
        """Test creation of arcs."""

        m = MooreDetMachine[str, str]()
        m.new_state()
        m.new_state()
        m.new_state()

        m.set_initial(0)

        m.new_transition(0, "in1", 1)
        m.new_transition(1, "in2", 2)
        m.new_transition(2, "in3", 2)
        m.set_state_output(0, "a")
        m.set_state_output(1, "long")
        m.set_state_output(2, "word")

        assert m.step(0, "in1") == {(1, "a")}
        assert m.step(2, "in3") == {(2, "word")}

        ret = m.process_word(["in1", "in2", "in3", "in3", "in3"])
        assert " ".join(ret) == "a long word word word"

        # Missing arcs
        assert "err" not in m.arcs_from(2)

        in_word = ["in1", "in2", "err", "err"]
        with pytest.raises(ValueError):
            m.process_word(in_word, strict=True)
        ret = m.process_word(in_word, strict=False)
        assert " ".join(ret) == "a long"

    def test_iteration(self):
        """Test iterations."""
        m = MooreDetMachine[str, str]()
        m.new_state()
        m.new_state()
        m.new_state()

        m.new_transition(0, "in1", 1)
        m.new_transition(1, "in2", 2)
        m.new_transition(2, "in3", 2)
        m.new_transition(2, "in1", 0)

        count = 0
        for state in m.states:
            count += 1
        assert count == 3

        count = 0
        for transition in m.transitions:
            count += 1
        assert count == 4

    def test_output_partitions(self):
        """Test output partitions."""
        m = MooreDetMachine[bool, str]()
        m.new_state_output("a")
        m.new_state_output("b")
        m.new_state_output("c")

        # Test partitions
        assert m._MooreDetMachine__output_partitions() == {
            frozenset({0}), frozenset({1}), frozenset({2}),
        }
        m.new_state_output("c")
        m.new_state_output("b")
        assert m._MooreDetMachine__output_partitions() == {
            frozenset({0}), frozenset({1, 4}), frozenset({2, 3}),
        }

    def test_splitters(self):
        """Test the application of a splitter."""
        m = MooreDetMachine[bool, str]()
        m.new_state_output("a")
        m.new_state_output("a")
        m.new_state_output("a")

        # Add transitions
        m.new_transition(0, True, 1)
        m.new_transition(0, False, 0)
        m.new_transition(1, True, 2)
        m.new_transition(1, False, 0)
        m.new_transition(2, True, 2)
        m.new_transition(2, False, 2)

        assert m._MooreDetMachine__apply_splitter(m.states, True, {2}) == {
            frozenset({1, 2}), frozenset({0}),
        }
        assert m._MooreDetMachine__apply_splitter(m.states, True, {0}) == {
            frozenset({0, 1, 2}),
        }
        assert m._MooreDetMachine__apply_splitter(m.states, False, {0}) == {
            frozenset({0, 1}), frozenset({2}),
        }

        m.new_state_output("b")
        m.new_transition(3, True, 0)
        assert m._MooreDetMachine__apply_splitter({0, 3}, True, {}) == {
            frozenset({3}), frozenset({0}),
        }

    def test_aphabet(self):
        """Test the size of the aplhabets."""
        m = MooreDetMachine[int, str]()
        m.new_state_output("a")
        m.new_state_output("b")
        m.new_state_output("c")
        m.new_state_output("c")
        m.new_transition(0, 0, 1)
        m.new_transition(1, 1, 2)
        m.new_transition(2, 2, 3)
        m.new_transition(3, 3, 3)
        m.new_transition(3, -50, 0)
        m.new_transition(2, -50, 0)

        assert m.input_alphabet == {0, 1, 2, 3, -50}
        assert m.output_alphabet == {"a", "b", "c"}

    def test_minimize(self):
        """Test minimization of the machine."""
        # Words to translate
        test_words = [
            [0],
            [1],
            [0, 0, 0],
            [1, 1, 1],
            [0, 1, 1],
            [1, 0, 0, 0],
        ]

        # Initial machine
        m1 = MooreDetMachine[int, str]()
        m1.new_state_output("a")
        m1.new_state_output("a")
        m1.new_state_output("b")
        m1.new_transition(0, 0, 1)
        m1.new_transition(0, 1, 0)
        m1.new_transition(1, 0, 2)
        m1.new_transition(1, 1, 1)
        m1.new_transition(2, 0, 0)
        m1.new_transition(2, 1, 0)
        m1.set_initial(0)

        # This should be the same machine
        m1_min = m1.minimize()
        assert m1_min.n_states == 3
        for word in test_words:
            assert m1.process_word(word) == m1_min.process_word(word)

        m1.save_graphviz("outputs/m1")
        m1_min.save_graphviz("outputs/m1_min")

        # Redundant machine
        m2 = MooreDetMachine[int, str]()
        m2.new_state_output("a")
        m2.new_state_output("a")
        m2.new_state_output("b")
        m2.new_state_output("a")
        m2.new_state_output("a")
        m2.new_state_output("b")
        m2.new_transition(0, 0, 1)
        m2.new_transition(0, 1, 0)
        m2.new_transition(1, 0, 2)
        m2.new_transition(1, 1, 1)
        m2.new_transition(2, 0, 3)
        m2.new_transition(2, 1, 3)
        m2.new_transition(3, 0, 4)
        m2.new_transition(3, 1, 3)
        m2.new_transition(4, 0, 5)
        m2.new_transition(4, 1, 4)
        m2.new_transition(5, 0, 0)
        m2.new_transition(5, 1, 0)
        m2.set_initial(0)

        # This should be as m1
        m2_min = m2.minimize()
        assert m2_min.n_states == 3
        for word in test_words:
            assert m2.process_word(word) == m2_min.process_word(word)

        m2.save_graphviz("outputs/m2")
        m2_min.save_graphviz("outputs/m2_min")

        # Very simple redundant machine
        m3 = MooreDetMachine[int, str]()
        m3.new_state_output("a")
        m3.new_state_output("a")
        m3.new_transition(0, 0, 1)
        m3.new_transition(0, 1, 1)
        m3.new_transition(1, 1, 0)
        m3.new_transition(1, 0, 1)
        m3.set_initial(0)

        m3_min = m3.minimize()
        assert m3_min.n_states == 1
        for word in test_words:
            assert m3.process_word(word) == m3_min.process_word(word)

        m3.save_graphviz("outputs/m3")
        m3_min.save_graphviz("outputs/m3_min")
