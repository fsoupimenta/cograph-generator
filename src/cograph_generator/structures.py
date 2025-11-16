from typing import Iterator, List

from src.cograph_generator.utils import _generate_all_unique_integer_partitions, _generate_ordered_cartesian_product, \
    _apply_cograph_operator_structure


def generate_connected_cotree_structures(node_count: int, depth: int = 0) -> Iterator[str]:
    """
    Generate ONLY connected cotree canonical string structures for a cograph
    of a given size. A cograph is connected iff the root operator is ``J``.

    This generator alternates deterministically between 'J' (join) and 'U'
    (union) based on the recursion depth. Since ``depth == 0`` starts with
    'J', only connected cotrees are produced.

    Parameters
    ----------
    node_count : int
        Number of nodes in the cotree.
    depth : int, optional
        Current recursion depth, used to determine the operator. Defaults to 0.

    Yields
    ------
    str
        A canonical cotree structure such as ``"J(U(a,a),a)"``.

    Notes
    -----
    - This function streams results: no full list of structures is kept in RAM.
    - Root operator (depth 0) = 'J' → produces ONLY connected cographs.
    - Operator alternation:
        depth % 2 == 0 → 'J'
        depth % 2 == 1 → 'U'
    """

    operator = "J" if (depth % 2 == 0) else "U"

    if node_count == 1:
        yield "a"
        return

    for partition in _generate_all_unique_integer_partitions(node_count):
        if len(partition) == 1:
            continue

        child_streams: List[List[str]] = [
            list(generate_connected_cotree_structures(p, depth + 1)) for p in partition
        ]

        for combination in _generate_ordered_cartesian_product(child_streams):
            yield _apply_cograph_operator_structure(operator, list(combination))

def _generate_structures_with_root(node_count: int, root_operator: str) -> Iterator[str]:
    """
    Internal helper that generates cotrees with a FIXED operator at depth 0.
    Used to generate disconnected structures (root = 'U').
    """
    if node_count == 1:
        yield "a"
        return

    operator = root_operator

    for partition in _generate_all_unique_integer_partitions(node_count):
        if len(partition) == 1:
            continue

        child_streams = [
            list(generate_all_cotree_structures(p, 1)) for p in partition
        ]

        for combination in _generate_ordered_cartesian_product(child_streams):
            yield _apply_cograph_operator_structure(operator, list(combination))

def generate_all_cotree_structures(node_count: int, depth: int = 0) -> Iterator[str]:
    """
    Generate ALL cotree canonical string structures (connected AND disconnected)
    for a cograph of a given size.

    This function reuses exactly the same logic as the connected version,
    but the operator at depth 0 is allowed to be either:
        - 'J' → connected cotrees
        - 'U' → disconnected cotrees

    The alternation rule remains deterministic for all deeper levels.

    Parameters
    ----------
    node_count : int
        Number of nodes in the cotree.
    depth : int, optional
        Recursion depth, used to alternate between 'J' and 'U'. Defaults to 0.

    Yields
    ------
    str
        A canonical cotree structure such as ``"U(J(a,a),U(a))"``.

    Notes
    -----
    - This generator NEVER accumulates any complete structure list in RAM.
    - Differences from the connected-only version:
        * At depth 0, both possible root operators are used: 'J' and 'U'.
        * All deeper levels alternate normally.
    - Produces exactly:
        * all connected cotrees (root = 'J')
        * all disconnected cotrees (root = 'U')
    """

    # At depth 0, emit both possibilities: connected(J) and disconnected(U)
    if depth == 0:

        # Stream connected ones (root = J)
        yield from generate_connected_cotree_structures(node_count, depth=0)

        # Stream disconnected ones (root = U)
        yield from _generate_structures_with_root(node_count, root_operator="U")

        return

    # Below depth 0, the connected version already covers the logic.
    # This fallback is used only recursively when root was forced to 'U'.
    operator = "J" if (depth % 2 == 0) else "U"

    if node_count == 1:
        yield "a"
        return

    for partition in _generate_all_unique_integer_partitions(node_count):
        if len(partition) == 1:
            continue

        child_streams = [
            list(generate_all_cotree_structures(p, depth + 1)) for p in partition
        ]

        for combination in _generate_ordered_cartesian_product(child_streams):
            yield _apply_cograph_operator_structure(operator, list(combination))
