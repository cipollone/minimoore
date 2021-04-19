"""Implementation of fixpoint algorithms for functions on sets."""

from typing import Callable, Generic, Optional, Set, TypeVar

# Types
ElementType = TypeVar("ElementType")
FunctionType = Callable[[Set[ElementType]], Set[ElementType]]


def reach_fixpoint(
    fn: FunctionType[ElementType],
    start: Set[ElementType],
) -> Set[ElementType]:
    """Return a fixpoint from a staring set.

    :param fn: a monotone input function on sets. Its domain must be
        finite, and the function must be monotone. This won't terminate
        otherwise. Side effects on the input set are preferred for efficiency.
    :param start: the initial set of states.
    :return: A fixpoint.
    """
    # Init
    x = start
    x_len = -1

    # Iterate
    while len(x) != x_len:
        x_len = len(x)
        x = fn(x)

    return x


def least_fixpoint(
    fn: FunctionType[ElementType],
    start: Optional[Set[ElementType]] = set(),
) -> Set[ElementType]:
    """Returns the least fixpoint for the input function.

    :param fn: a *monotone* function on sets. Side effects on the input set
        are allowed.
    :param start: the initial set. This may be useful if the initialization
        is special, and we don't want to complicate fn.
    :return: the least fixpoint for fn.
    """
    return reach_fixpoint(fn, start if start is not None else set())


def greatest_fixpoint(
    fn: FunctionType[ElementType],
    universe: Set[ElementType],
) -> Set[ElementType]:
    """Returns the greatest fixpoint for the input function.

    :param fn: a *monotone* function on sets. Side effects on the input set
        are allowed.
    :param universe: the entire set of elements.
    :return: the greatest fixpoint set of fn.
    """
    return reach_fixpoint(fn, universe)


class Union(Generic[ElementType]):
    """Function wrapper: union.

    Any element that is returned by the input function is added to the set.
    This can be passed to fixpoint methods.
    The input function shouln't have side-effects on the set.
    """
    def __init__(self, fn: FunctionType[ElementType]):
        """Initialize; see class docstring."""
        self.fn = fn

    def __call__(self, x: Set[ElementType]) -> Set[ElementType]:
        """Modify the input set."""
        elements = self.fn(x)
        x.update(elements)
        return x


class Intersection(Generic[ElementType]):
    """Function wrapper: intersection.

    Any element that is returned by the input function is removed from the set,
    if present. This can be passed to fixpoint methods.
    The input function shouln't have side-effects on the set.
    """
    def __init__(self, fn: FunctionType[ElementType]):
        """Initialize; see class docstring."""
        self.fn = fn

    def __call__(self, x: Set[ElementType]) -> Set[ElementType]:
        """Modify the input set."""
        elements = self.fn(x)
        x.intersection_update(elements)
        return x
