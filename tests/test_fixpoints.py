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

    @staticmethod
    def f3(x: Set[int]) -> Set[int]:
        """Monotone function: Add +2 (stop at 10)."""
        return {elem + 2 for elem in x if elem < 8}

    @staticmethod
    def f4(x: Set[int]) -> Set[int]:
        """Monotone function: remove if next not here (stop at 5)."""
        return {elem for elem in x if elem + 1 in x or elem < 5}

    @staticmethod
    def f5(x: Set[int]) -> Set[int]:
        """Monotone function: remove if next not here (stop at 5)."""
        return {elem for elem in x if elem + 1 not in x and elem >= 5}

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
        numbers = set(range(2, 8))
        gfp = fixpoints.greatest_fixpoint(self.f2, numbers)
        assert gfp == {2, 3, 4}

        numbers = {-2, 0, 5, 3}
        gfp = fixpoints.greatest_fixpoint(self.f2, numbers)
        assert gfp == {-2, 0, 3}

    def test_least_union(self):
        """Test least fixpoint with union."""
        fn = fixpoints.Union(self.f3)
        lfp = fixpoints.least_fixpoint(fn, {1})
        assert lfp == {1, 3, 5, 7, 9}

    def test_greatest_intersection(self):
        """Test greatest fixpoint with intersection."""
        fn = fixpoints.Intersection(self.f4)
        gfp = fixpoints.greatest_fixpoint(fn, set(range(0, 50)))
        assert gfp == {0, 1, 2, 3, 4}

    def test_greatest_difference(self):
        """Test greatest fixpoint with difference."""
        fn = fixpoints.Difference(self.f5)
        gfp = fixpoints.greatest_fixpoint(fn, set(range(0, 50)))
        assert gfp == {0, 1, 2, 3, 4}

    def test_stop(self):
        """Test stop conditions."""
        fn = fixpoints.Union(self.f3)
        lfp = fixpoints.least_fixpoint(fn, {1}, lambda x: 7 in x)
        assert lfp == {1, 3, 5, 7}

        fn = fixpoints.Intersection(self.f4)
        gfp = fixpoints.greatest_fixpoint(
            fn,
            set(range(0, 50)),
            lambda x: 6 not in x,
        )
        assert gfp == {0, 1, 2, 3, 4, 5}
