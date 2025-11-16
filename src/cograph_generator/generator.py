import os
import tempfile
import multiprocessing as mp

from src.cograph_generator.adjacency_g6 import _structure_to_g6_optimized_worker
from src.cograph_generator.structures import generate_connected_cotree_structures, generate_all_cotree_structures
from src.cograph_generator.visualization import render_cotree_jpg


def generate_cographs_final_g6(
    node_count: int,
    output_filename: str = "cographs_g6.txt",
    batch_size: int = 50_000,
    num_processes: int = 8,
    connected_only: bool = True,
) -> str:
    """
    Generate cographs with ``node_count`` vertices and save them in graph6 format.

    This function performs two phases:
    1. Generate all canonical cograph structures (connected only or all) and write
       them directly to a temporary file.
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
    connected_only : bool, optional
        If True, generate only connected cographs (root operator 'J').
        If False, generate all cographs (connected + disconnected).

    Returns
    -------
    str
        Path of the output file containing graph6 strings.
    """

    total_structures = 0
    total_graph6 = 0

    if connected_only:
        generator = generate_connected_cotree_structures
    else:
        generator = generate_all_cotree_structures

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_filename = temp.name

        for structure in generator(node_count, 0):
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


def generate_cographs_g6(
    node_count: int,
    connected_only: bool = True,
    num_processes: int = 8
) -> list[str]:
    """
    Generate cographs in graph6 format using parallel processing,
    returning all results in memory (no batching, no temporary files).

    Parameters
    ----------
    node_count : int
        Number of vertices.
    connected_only : bool, optional
        If True, generate only connected cographs.
    num_processes : int, optional
        Number of worker processes.

    Returns
    -------
    list[str]
        All graph6 strings generated.
    """

    if connected_only:
        generator = generate_connected_cotree_structures
    else:
        generator = generate_all_cotree_structures
    results = []

    with mp.Pool(num_processes) as pool:
        for g6 in pool.imap_unordered(_structure_to_g6_optimized_worker, generator(node_count, 0)):
            results.append(g6)

    return results

def generate_cotree_images(
    node_count: int,
    output_dir: str = "cotree_images"
) -> int:
    """
    Generate JPG files for all canonical cotrees with the specified number of leaves.
    Structures are produced by ``generate_all_cotree_structures`` and rendered by
    ``render_cotree_jpg``.

    Parameters
    ----------
    node_count : int
        Number of leaves in the cotrees.
    output_dir : str, optional
        Directory where the JPG files will be saved.

    Returns
    -------
    int
        Total number of images generated.
    """
    total = 0
    for structure in generate_all_cotree_structures(node_count, 0):
        render_cotree_jpg(structure, node_count, output_dir)
        total += 1
    return total
