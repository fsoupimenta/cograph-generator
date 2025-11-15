import os
import tempfile
import multiprocessing as mp
from typing import List, Iterator

from cograph_generator.adjacency_g6 import _structure_to_g6_optimized_worker
from cograph_generator.utils import _generate_all_unique_integer_partitions, _generate_ordered_cartesian_product, \
    _apply_cograph_operator_structure


def generate_all_cotree_structures(node_count: int, depth: int) -> Iterator[str]:
    """
    Generate cotree canonical string structures for a cograph of a given size,
    streaming results via a generator instead of storing them in memory.

    This function alternates the cograph operator between 'J' (join) and 'U'
    (union) based on the recursion depth. For each integer partition of
    ``node_count`` (excluding the trivial one), it recursively generates child
    structures and yields all valid combinations using an ordered,
    redundancy-free Cartesian product.

    Parameters
    ----------
    node_count : int
        Number of nodes in the current cotree.
    depth : int
        Recursion depth, used to determine the operator ('J' for even levels,
        'U' for odd levels).

    Yields
    ------
    str
        A canonical string representation of the cotree structure, such as
        ``"J(U(a,a),a)"``.

    Notes
    -----
    - This generator never accumulates full lists in RAM.
    - The operator alternates deterministically:
        depth % 2 == 0 → 'J'
        depth % 2 == 1 → 'U'
    - Trivial partitions (like (n,)) are ignored.
    """

    operator = "J" if (depth % 2 == 0) else "U"

    if node_count == 1:
        yield "a"
        return

    for partition in _generate_all_unique_integer_partitions(node_count):
        if len(partition) == 1:
            continue

        child_streams: List[List[str]] = []
        for part_size in partition:
            child_streams.append(
                list(generate_all_cotree_structures(part_size, depth + 1))
            )

        for combination in _generate_ordered_cartesian_product(child_streams):
            yield _apply_cograph_operator_structure(operator, list(combination))

def generate_cographs_final_g6(
    node_count: int,
    output_filename: str = "cographs_g6.txt",
    batch_size: int = 50_000,
    num_processes: int = 8
) -> str:
    """
    Generate all cographs with ``node_count`` vertices and save them in graph6 format.

    This function performs two phases:
    1. Generate all canonical cograph structures and write them directly to a temporary file.
    2. Convert the structures to graph6 representation in batches using multiprocessing.

    Parameters
    ----------
    node_count : int
        Number of vertices in the cographs to generate.
    output_filename : str, optional
        Destination filename for the final graph6 output. Default is ``"cographs_g6.txt"``.
    batch_size : int, optional
        Number of structures to convert per batch in phase 2. Default is ``50_000``.
    num_processes : int, optional
        Number of worker processes to use during graph6 conversion. Default is ``8``.

    Returns
    -------
    str
        Path of the output file containing graph6 strings.
    """

    total_structures = 0
    total_graph6 = 0

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_filename = temp.name

        for structure in generate_all_cotree_structures(node_count, 0):
            temp.write(structure + "\n")
            total_structures += 1

    with open(temp_filename, "r") as f_in, open(output_filename, "w") as f_out:

        while True:
            batch = [line.strip() for line in (f_in.readline() for _ in range(batch_size))]
            batch = [s for s in batch if s]

            if not batch:
                break

            with mp.Pool(num_processes) as pool:
                graph6_results = pool.map(_structure_to_g6_optimized_worker, batch)

            for g6 in graph6_results:
                f_out.write(g6 + "\n")

            total_graph6 += len(graph6_results)

    os.remove(temp_filename)

    return output_filename
