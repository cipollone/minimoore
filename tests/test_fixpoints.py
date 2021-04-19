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

    @staticmethod
    def f2(x: Set[int]) -> Set[int]:
        """Monotone function: remove one higher than 5."""
        for elem in x:
            if elem >= 5:
                x.remove(elem)
                break
        return x

    def test_least(self):
        """Test the least fixpoint in a very simple case."""
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

    def test_greatest(self):
        """Test the greatest fixpoint in a very simple case."""
        numbers = {i for i in range(2, 8)}
        gfp = fixpoints.greatest_fixpoint(self.f2, numbers)
        assert gfp == {2, 3, 4}

        numbers = {-2, 0, 5, 3}
        gfp = fixpoints.greatest_fixpoint(self.f2, numbers)
        assert gfp == {-2, 0, 3}
