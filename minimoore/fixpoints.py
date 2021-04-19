"""Implementation of fixpoint algorithms for functions on sets."""

from typing import TypeVar, Callable, Set, Optional


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
