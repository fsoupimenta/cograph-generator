from __future__ import annotations

import os
from typing import List, Tuple, Dict

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

matplotlib.use("Agg")


def generate_cotree_filename(
        leaf_count: int,
        output_dir: str,
) -> str:
    """
    Generate a sequential filename for a cotree image.

    Parameters
    ----------
    leaf_count : int
        Number of leaves in the cotree.
    output_dir : str
        Directory where the image will be saved.

    Returns
    -------
    str
        Deterministic sequential file-base name.
    """
    existing = [
        f for f in os.listdir(output_dir)
        if f.startswith(f"cotree_n{leaf_count}_") and f.endswith(".jpg")
    ]
    index = len(existing) + 1
    return f"cotree_n{leaf_count}_{index}"


def parse_cotree(
        serialized: str,
) -> Tuple[List[Tuple[int, int]], Dict[int, str], Dict[int, bool]]:
    """
    Parse a serialized cotree expression into edges and node labels.

    Parameters
    ----------
    serialized : str
        Serialized cotree expression.

    Returns
    -------
    edges : list[tuple[int,int]]
        Edge list as (parent, child).
    labels : dict[int,str]
        Mapping node_id → label (internal nodes only).
    is_leaf : dict[int,bool]
        Mapping node_id → True if leaf.
    """

    node_id = 1
    edges: List[Tuple[int, int]] = []
    labels: Dict[int, str] = {}
    is_leaf: Dict[int, bool] = {}

    def _split_args(s: str) -> List[str]:
        result, balance, current = [], 0, ""
        for ch in s:
            if ch == "," and balance == 0:
                result.append(current)
                current = ""
            else:
                current += ch
                if ch == "(":
                    balance += 1
                elif ch == ")":
                    balance -= 1
        result.append(current)
        return result

    def _parse(expr: str, parent: int | None = None) -> int:
        nonlocal node_id
        current = node_id
        node_id += 1

        if expr == "a":
            is_leaf[current] = True
            if parent is not None:
                edges.append((parent, current))
            return 1

        operator = expr[0]
        inside = expr[2:-1]
        parts = _split_args(inside)

        leaf_counts = []
        for subexpr in parts:
            count = _parse(subexpr, current)
            leaf_counts.append(count)

        total_leaves = sum(leaf_counts)
        labels[current] = f"{operator} ({total_leaves})"
        is_leaf[current] = False

        if parent is not None:
            edges.append((parent, current))

        return total_leaves

    _parse(serialized)
    return edges, labels, is_leaf


def hierarchy_layout(
        graph: nx.Graph,
        root: int = 1,
        x_center: float = 0.5,
        y_top: float = 1.0,
        level_gap: float = 0.1,
) -> Dict[int, Tuple[float, float]]:
    """
    Compute hierarchical top-down coordinates for tree drawing.

    Parameters
    ----------
    graph : networkx.Graph
        Tree-like graph.
    root : int, optional
        Root node. Default is 1.
    x_center : float, optional
        Horizontal center of the root.
    y_top : float, optional
        Vertical position of the root.
    level_gap : float, optional
        Vertical spacing between levels.

    Returns
    -------
    dict[int, tuple[float,float]]
        Mapping node_id → (x, y).
    """

    positions: Dict[int, Tuple[float, float]] = {}
    parent: Dict[int, int] = {}

    def _dfs(node: int, depth: int, x_left: float = 0.0) -> float:
        children = list(graph.neighbors(node))
        if node in parent:
            children.remove(parent[node])

        y = y_top - depth * level_gap

        if not children:
            positions[node] = (x_left + 0.5, y)
            return 1.0

        total_width = 0.0
        child_positions = []

        for child in children:
            parent[child] = node
            w = _dfs(child, depth + 1, x_left + total_width)
            child_positions.append((child, total_width, w))
            total_width += w

        for child, offset, w in child_positions:
            positions[child] = (
                x_left + offset + w / 2,
                y_top - (depth + 1) * level_gap
            )

        positions[node] = (x_left + total_width / 2, y)
        return total_width

    _dfs(root, 0, 0.0)
    return positions


def render_cotree_jpg(
        serialized: str,
        leaf_count: int,
        output_dir: str = "cotree_images",
        dpi: int = 150,
) -> str:
    """
    Render a cotree into a JPG image using Matplotlib.

    Parameters
    ----------
    serialized : str
        Serialized cotree representation.
    leaf_count : int
        Number of leaves in the cotree.
    output_dir : str, optional
        Output directory.
    dpi : int, optional
        Image resolution.

    Returns
    -------
    str
        Full path to the generated JPEG file.
    """

    edges, labels, is_leaf = parse_cotree(serialized)

    graph = nx.Graph()
    for parent, child in edges:
        graph.add_edge(parent, child)

    pos = hierarchy_layout(graph, root=1)

    internal_nodes = [n for n, leaf in is_leaf.items() if not leaf]
    leaf_nodes = [n for n, leaf in is_leaf.items() if leaf]

    plt.figure(figsize=(8, 5))

    nx.draw_networkx_edges(
        graph,
        pos,
        width=1.2,
        edge_color="#555555"
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=internal_nodes,
        node_size=1400,
        node_color="#c9e6ff",
        linewidths=1.4,
        edgecolors="#333333"
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=leaf_nodes,
        node_size=500,
        node_color="#eeeeee",
        linewidths=1.0,
        edgecolors="#777777"
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_size=9,
        font_weight="bold"
    )

    images_dir = os.path.join(output_dir, f"cotree_images_{leaf_count}")
    os.makedirs(images_dir, exist_ok=True)

    filename = generate_cotree_filename(leaf_count, images_dir)
    path = os.path.join(images_dir, f"{filename}.jpg")

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", dpi=dpi)
    plt.close()

    return path
