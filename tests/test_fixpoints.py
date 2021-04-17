"""Test fixpoints module."""

from typing import Set

from minimoore import fixpoints


class TestFixpoints:
    """Tests."""

    @staticmethod
    def f1(x: Set[str]) -> Set[str]:
        """Monotone function: add one prefix."""
        for elem in x:
            prefix = elem[:-1] if len(elem) > 0 else ""
            if prefix not in x:
                x.add(prefix)
                break
        return x

    def test_least(self):
        """Test the least fixpoint."""
        start = {
            "testing"
        }
        lfp = fixpoints.least_fixpoint(self.f1, start)
        assert lfp == {"testing", "testin", "testi", "test", "tes", "te", "t", ""}

        start = {
            "ciao",
            "cia",
            "ok",
        }
        lfp = fixpoints.least_fixpoint(self.f1, start)
        assert lfp == {"ciao", "cia", "ci", "c", "", "ok", "o"}

    # TODO: test greatest
