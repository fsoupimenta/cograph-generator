from __future__ import annotations
import hashlib
import os
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import networkx as nx


def generate_cotree_filename(serialized: str, leaf_count: int) -> str:
    """
    Generate a deterministic and compact filename for a cotree image.

    Parameters
    ----------
    serialized : str
        Serialized cotree representation.
    leaf_count : int
        Number of leaves in the cotree.

    Returns
    -------
    str
        Deterministic file-base name derived from the cotree hash.
    """
    digest = hashlib.md5(serialized.encode()).hexdigest()[:8]
    return f"cotree_n{leaf_count}_{digest}"


def parse_cotree(serialized: str) -> Tuple[List[Tuple[int, int]], Dict[int, str]]:
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
        Mapping node_id → label.
    """

    node_id = 1
    edges: List[Tuple[int, int]] = []
    labels: Dict[int, str] = {}

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
            labels[current] = "a"
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

        if parent is not None:
            edges.append((parent, current))

        return total_leaves

    _parse(serialized)
    return edges, labels


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
        Horizontal center of the root. Default is 0.5.
    y_top : float, optional
        Vertical position of the root. Default is 1.0.
    level_gap : float, optional
        Vertical spacing between levels.

    Returns
    -------
    dict[int, tuple[float,float]]
        Mapping node_id → (x, y).
    """

    positions: Dict[int, Tuple[float, float]] = {}
    parent: Dict[int, int] = {}

    def _dfs(node: int, depth: int, x_mid: float) -> float:
        positions[node] = (x_mid, y_top - depth * level_gap)

        children = list(graph.neighbors(node))
        if node in parent:
            children.remove(parent[node])

        if not children:
            return 1.0

        widths: List[Tuple[int, float]] = []
        total_width = 0.0

        for child in children:
            parent[child] = node
            w = _dfs(child, depth + 1, x_mid)
            widths.append((child, w))
            total_width += w

        x_start = x_mid - total_width / 2
        cur = x_start

        for child, w in widths:
            positions[child] = (cur + w / 2, y_top - (depth + 1) * level_gap)
            cur += w

        return total_width

    _dfs(root, 0, x_center)
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
        Output directory. Default is "cotree_images".
    dpi : int, optional
        Image resolution.

    Returns
    -------
    str
        Full path to the generated JPEG file.
    """

    edges, labels = parse_cotree(serialized)

    graph = nx.Graph()
    for parent, child in edges:
        graph.add_edge(parent, child)

    pos = hierarchy_layout(graph, root=1)

    plt.figure(figsize=(8, 5))
    nx.draw(
        graph,
        pos,
        labels=labels,
        node_size=1500,
        node_color="#c9e6ff",
        linewidths=1.4,
        font_size=9,
        font_weight="bold",
        with_labels=True,
    )

    os.makedirs(output_dir, exist_ok=True)
    filename = generate_cotree_filename(serialized, leaf_count)
    path = os.path.join(output_dir, f"{filename}.jpg")

    plt.savefig(path, bbox_inches="tight", dpi=dpi)
    plt.close()

    return path
