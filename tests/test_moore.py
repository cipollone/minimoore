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

        # TODO: missing arc?

        ret = m.process_word(["in1", "in2", "in3", "in3", "in3"])
        ret = " ".join(ret)
        assert ret == "a long word word word"
