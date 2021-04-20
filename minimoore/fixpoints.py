"""Implementation of fixpoint algorithms for functions on sets."""

from typing import AbstractSet, Callable, Generic, Optional, Set, TypeVar

# Types
ElementType = TypeVar("ElementType")
FunctionType = Callable[[Set[ElementType]], Set[ElementType]]
AFunctionType = Callable[[AbstractSet[ElementType]], AbstractSet[ElementType]]
StopConditionType = Callable[[AbstractSet[ElementType]], bool]


def reach_fixpoint(
    fn: FunctionType[ElementType],
    start: Set[ElementType],
    stop_cond: Optional[StopConditionType[ElementType]] = None,
) -> Set[ElementType]:
    """Return a fixpoint from a staring set.

    :param fn: a monotone input function on sets. Its domain must be
        finite, and the function must be monotone. This won't terminate
        otherwise. Side effects on the input set are preferred for efficiency.
    :param start: the initial set of states.
    :param stop_cond: the algorithm is stopped as soon as this returns True.
    :return: A fixpoint, or the set reached at the stop condition.
    """
    # Init
    x = start
    x_len = -1

    # Iterate
    while len(x) != x_len:
        # Stop?
        if stop_cond is not None and stop_cond(x):
            break

        # Do
        x_len = len(x)
        x = fn(x)

    return x


def least_fixpoint(
    fn: FunctionType[ElementType],
    start: Optional[Set[ElementType]] = None,
    stop_cond: Optional[StopConditionType[ElementType]] = None,
) -> Set[ElementType]:
    """Returns the least fixpoint for the input function.

    :param fn: a *monotone* function on sets. Side effects on the input set
        are allowed.
    :param start: the initial set. This may be useful if the initialization
        is special, and we don't want to complicate fn.
    :param stop_cond: the algorithm is stopped as soon as this returns True.
    :return: the least fixpoint for fn, or the set reached at stop condition.
    """
    if start is None:
        start = set()
    return reach_fixpoint(fn, start, stop_cond)


def greatest_fixpoint(
    fn: FunctionType[ElementType],
    universe: Set[ElementType],
    stop_cond: Optional[StopConditionType[ElementType]] = None,
) -> Set[ElementType]:
    """Returns the greatest fixpoint for the input function.

    :param fn: a *monotone* function on sets. Side effects on the input set
        are allowed.
    :param universe: the entire set of elements.
    :param stop_cond: the algorithm is stopped as soon as this returns True.
    :return: the greatest fixpoint set of fn, or the set reached at stop condition.
    """
    return reach_fixpoint(fn, universe, stop_cond)


class Union(Generic[ElementType]):
    """Function wrapper: union.

    Any element that is returned by the input function is added to the set.
    This can be passed to fixpoint methods.
    The input function shouln't have side-effects on the set.
    """

    def __init__(self, fn: AFunctionType[ElementType]):
        """Initialize; see class docstring."""
        self.fn = fn

    def __call__(self, x: Set[ElementType]) -> Set[ElementType]:
        """Modify the input set."""
        elements = self.fn(x)
        x.update(elements)
        return x


class Intersection(Generic[ElementType]):
    """Function wrapper: intersection.

    The output set will be the intersection of the original element and the
    elements returned from the function. This can be passed to fixpoint
    methods.  The input function shouln't have side-effects on the set.
    """

    def __init__(self, fn: AFunctionType[ElementType]):
        """Initialize; see class docstring."""
        self.fn = fn

    def __call__(self, x: Set[ElementType]) -> Set[ElementType]:
        """Modify the input set."""
        elements = self.fn(x)
        x.intersection_update(elements)
        return x


class Difference(Generic[ElementType]):
    """Function wrapper: difference.

    Any element that is returned by the input function is removed from the set,
    if present. This can be passed to fixpoint methods.
    The input function shouln't have side-effects on the set.
    """

    def __init__(self, fn: AFunctionType[ElementType]):
        """Initialize; see class docstring."""
        self.fn = fn

    def __call__(self, x: Set[ElementType]) -> Set[ElementType]:
        """Modify the input set."""
        elements = self.fn(x)
        x.difference_update(elements)
        return x
