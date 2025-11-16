import itertools
from typing import Dict, Tuple, List

import numpy as np

_ADJ_CACHE: Dict[str, Tuple[np.ndarray, int]] = {}

def _structure_to_adjacency_matrix(structure: str) -> List[List[int]]:
    """
    Convert a canonical cograph structure expression into its adjacency matrix.

    A structure is a recursive expression using the operators:
    - ``J`` : join (connect all nodes across substructures)
    - ``U`` : disjoint union (no edges across substructures)

    The atomic graph is represented by the symbol ``a``, corresponding
    to a single isolated vertex.

    Examples
    --------
    >>> _structure_to_adjacency_matrix("a")
    [[0]]

    >>> _structure_to_adjacency_matrix("U(a,a)")
    [[0, 0],
     [0, 0]]

    >>> _structure_to_adjacency_matrix("J(U(a,a),a)")
    [[0, 0, 1],
     [0, 0, 1],
     [1, 1, 0]]

    Parameters
    ----------
    structure : str
        The canonical cograph structure string, e.g. ``"J(U(a,a),a)"``.

    Returns
    -------
    List[List[int]]
        A square adjacency matrix as a nested Python list.
    """

    def _parse(expr: str) -> Tuple[np.ndarray, int]:
        # Cached result?
        if expr in _ADJ_CACHE:
            return _ADJ_CACHE[expr]

        # Base case: atomic vertex
        if expr == "a":
            mat = np.zeros((1, 1), dtype=np.uint8)
            _ADJ_CACHE[expr] = (mat, 1)
            return mat, 1

        # Operator is first char: J or U
        operator = expr[0]

        # Extract content inside parentheses: "x,y,z"
        content = expr[2:-1]

        # Split at top-level commas
        parts = []
        depth = 0
        last_split = 0
        for i, ch in enumerate(content):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(content[last_split:i])
                last_split = i + 1
        parts.append(content[last_split:])

        # Recursively parse substructures
        parsed_subs = [_parse(part) for part in parts]
        sub_matrices = [m for (m, _) in parsed_subs]
        sub_sizes = [s for (_, s) in parsed_subs]

        total_size = sum(sub_sizes)
        matrix = np.zeros((total_size, total_size), dtype=np.uint8)

        ranges = []
        offset = 0
        for mat, size in zip(sub_matrices, sub_sizes):
            end = offset + size
            matrix[offset:end, offset:end] = mat
            ranges.append((offset, end))
            offset = end

        if operator == "J":
            for (a0, a1), (b0, b1) in itertools.combinations(ranges, 2):
                matrix[a0:a1, b0:b1] = 1
                matrix[b0:b1, a0:a1] = 1

        _ADJ_CACHE[expr] = (matrix, total_size)
        return matrix, total_size

    result_matrix, _ = _parse(structure)
    return result_matrix.tolist()

def _adjacency_matrix_to_g6(adjacency_matrix: List[List[int]]) -> str:
    """
    Encode an adjacency matrix into the graph6 (g6) format.

    The graph6 encoding is a compact ASCII representation used for
    graphs in various combinatorial and graph theory tools (e.g., nauty).
    This function assumes the adjacency matrix describes a simple,
    undirected graph with no self-loops.

    Parameters
    ----------
    adjacency_matrix : List[List[int]]
        A square adjacency matrix representing an undirected graph.
        Must contain only 0 or 1 values.

    Returns
    -------
    str
        A string containing the graph encoded in graph6 format.

    Examples
    --------
    >>> _adjacency_matrix_to_g6([[0]])
    '?'

    >>> _adjacency_matrix_to_g6([
    ...     [0, 1],
    ...     [1, 0]
    ... ])
    '@'

    Notes
    -----
    The graph6 format stores the upper triangle of the adjacency matrix
    (i < j) as a stream of bits grouped into 6-bit chunks. Each chunk is
    then converted to an ASCII character offset by 63.
    """

    n = len(adjacency_matrix)
    prefix = chr(n + 63)

    bits = []
    for col in range(1, n):
        for row in range(col):
            bits.append(adjacency_matrix[row][col])

    encoded_chunks = []
    current_chunk = 0
    bit_count = 0

    for bit in bits:
        current_chunk = (current_chunk << 1) | bit
        bit_count += 1

        if bit_count == 6:
            encoded_chunks.append(chr(current_chunk + 63))
            current_chunk = 0
            bit_count = 0

    if bit_count > 0:
        current_chunk <<= (6 - bit_count)
        encoded_chunks.append(chr(current_chunk + 63))

    return prefix + "".join(encoded_chunks)

def _structure_to_g6_optimized_worker(structure: str) -> str:
    """
    Convert a canonical cograph structure into its graph6 representation.

    This is a lightweight helper function meant for multiprocessing.
    It transforms a structure string into a g6-encoded adjacency matrix.

    Parameters
    ----------
    structure : str
        Canonical cograph structure, e.g. ``"J(U(a,a),a)"``.

    Returns
    -------
    str
        The graph6 encoding of the adjacency matrix of the cograph.

    Notes
    -----
    This function is intentionally minimal because it is executed inside
    multiprocessing pools.
    """
    adjacency = _structure_to_adjacency_matrix(structure)
    return _adjacency_matrix_to_g6(adjacency)
