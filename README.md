# CographGenerator

CographGenerator is a high-performance Python library for generating and manipulating cographs, with canonical structure parsing and Graph6 encoding.
The library focuses on generating all cographs of a given size and exporting them in graph6 (g6) format, suitable for graph-theoretical applications and combinatorial research.

---

## Installation

You can install the library via pip:

pip install cographgenerator

Note: This library depends on NumPy, which will be installed automatically.

---

## Quick Start

The main function exposed by the library is generate_cographs_final_g6, which generates all cographs for a given number of vertices and saves them to a file in graph6 format.

from cographgenerator import generate_cographs_final_g6

# Generate all cographs with 3 vertices
output_file = generate_cographs_final_g6(node_count=3, output_filename="cographs_3.g6")

print(f"Cographs generated and saved in: {output_file}")

This will create a file named cographs_3.g6 containing all canonical cographs with 3 vertices encoded in graph6 format.

---

## Parameters

Parameter          | Type   | Default          | Description
------------------ | ------ | ---------------- | -----------------------------------------------------------------------------
node_count         | int    | —                | Number of vertices in the cographs to generate.
output_filename    | str    | "cographs_g6.txt"| Destination filename for the final graph6 output.
batch_size         | int    | 50000            | Number of structures to convert per batch in phase 2.
num_processes      | int    | 8                | Number of worker processes used during graph6 conversion.

---

## How it Works

1. Generate canonical cotree structures: Recursively constructs all canonical string representations of cographs of a given size.
2. Convert structures to adjacency matrices: Each canonical structure is converted into a square adjacency matrix.
3. Encode in Graph6 format: The adjacency matrices are transformed into compact graph6 strings and written to the output file.

> The library internally optimizes memory usage by streaming the structures and processing them in batches, making it suitable for large graphs.

---

## License

This project is licensed under the MIT License.

---

## References

- Graph6 Format: https://users.cecs.anu.edu.au/~bdm/nauty/manual.pdf
- Cographs on Wikipedia: https://en.wikipedia.org/wiki/Cograph
