import itertools
from typing import List, Tuple, Iterator


def _generate_all_unique_integer_partitions(n: int) -> List[Tuple[int, ...]]:
    """
    Generate all unique integer partitions of an integer ``n`` in non-increasing order.

    A partition of ``n`` is a sequence of positive integers that sum to ``n``.
    This function generates partitions in non-increasing order, which ensures
    that each partition is unique.

    Parameters
    ----------
    n : int
        The integer to be partitioned. Must be a non-negative integer.

    Returns
    -------
    List[Tuple[int, ...]]
        A list of tuples, where each tuple represents one integer partition
        of ``n`` in non-increasing order.

    Examples
    --------
    >>> _generate_all_unique_integer_partitions(3)
    [(3,), (2, 1), (1, 1, 1)]

    >>> _generate_all_unique_integer_partitions(4)
    [(4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1)]
    """

    def backtrack(remaining: int, max_allowed: int, current: List[int], output: List[Tuple[int, ...]]):
        if remaining == 0:
            output.append(tuple(current))
            return

        for value in range(1, min(remaining, max_allowed) + 1):
            backtrack(remaining - value, value, current + [value], output)

    partitions: List[Tuple[int, ...]] = []
    backtrack(n, n, [], partitions)
    return partitions


def _generate_ordered_cartesian_product(groups: List[List[str]]) -> Iterator[Tuple[str, ...]]:
    """
    Generate a Cartesian product from a list of groups while collapsing consecutive
    identical groups to avoid redundant combinations.

    When two or more consecutive groups are identical, they are treated as a
    single group that allows repeated selections, using combinations-with-replacement
    to avoid redundant permutations. This is particularly useful when group
    structures are symmetric and repeating them would not contribute new results.

    Parameters
    ----------
    groups : List[List[str]]
        A list of groups (lists) where each inner list contains possible options.
        Consecutive identical groups are collapsed for efficiency.

    Yields
    ------
    Tuple[str, ...]
        Each yielded tuple represents one element of the optimized Cartesian product.

    Examples
    --------
    >>> list(_generate_ordered_cartesian_product([["a", "b"], ["a", "b"]]))
    [('a', 'a'), ('a', 'b'), ('b', 'b')]

    >>> list(_generate_ordered_cartesian_product([["x"], ["y", "z"], ["y", "z"]]))
    [('x', 'y', 'y'), ('x', 'y', 'z'), ('x', 'z', 'z')]
    """

    if not groups:
        return

    optimized_groups: List[List[Tuple[str, ...]]] = []

    current_group = groups[0]
    repeat_count = 1

    for next_group in groups[1:] + [None]:
        if next_group == current_group:
            repeat_count += 1
        else:
            if repeat_count == 1:
                optimized_groups.append([(item,) for item in current_group])
            else:
                optimized_groups.append(
                    list(itertools.combinations_with_replacement(current_group, repeat_count))
                )

            current_group = next_group
            repeat_count = 1

    for combination in itertools.product(*optimized_groups):
        yield tuple(itertools.chain.from_iterable(combination))


def _apply_cograph_operator_structure(operator: str, child_structures: List[str]) -> str:
    """
    Build a string representation of a cograph composition using the given operator.

    The operator should be one of:
    - 'J' for join
    - 'U' for union

    Child structures are combined in the format:
        operator(child1, child2, ..., childN)

    Parameters
    ----------
    operator : str
        The cograph operator. Must be either 'J' (join) or 'U' (union).
    child_structures : List[str]
        A list of string representations of substructures.

    Returns
    -------
    str
        A formatted string representing the cograph operator applied to its child structures.

    Examples
    --------
    >>> _apply_cograph_operator_structure("J", ["a", "b"])
    'J(a,b)'

    >>> _apply_cograph_operator_structure("U", ["X", "Y", "Z"])
    'U(X,Y,Z)'
    """
    return f"{operator}({','.join(child_structures)})"
