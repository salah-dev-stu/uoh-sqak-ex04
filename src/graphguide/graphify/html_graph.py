"""Interactive graph.html generator (FR-UPG4) — pyvis from graph.json.

Nodes sized by degree centrality, coloured by community, God Nodes + suspects + the
bug node highlighted. Self-contained (in-line vis-network) so it renders offline.
"""

from __future__ import annotations

from pathlib import Path

from pyvis.network import Network

from graphguide.graphify.centrality import degree_centrality
from graphguide.graphify.loader import CodeGraph

_PALETTE = [
    "#4e79a7",
    "#f28e2b",
    "#59a14f",
    "#76b7b2",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ac",
    "#86bcb6",
]


def build_interactive_html(
    graph: CodeGraph,
    out_path: str | Path,
    *,
    selected: list[str],
    god: set[str],
    suspects: set[str],
    bug_node: str,
) -> str:
    g = graph.to_networkx()
    deg = degree_centrality(g)
    labels = {n.id: (n.label or n.id) for n in graph.nodes}
    community = {n.id: n.community for n in graph.nodes}
    chosen = set(selected)

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#111418",
        font_color="#e8e8e8",
        directed=True,
        cdn_resources="in_line",
    )
    for nid in selected:
        size = 12 + 70 * deg.get(nid, 0.0)
        color = _PALETTE[(community.get(nid) or 0) % len(_PALETTE)]
        if nid == bug_node:
            color = "#ff3b30"  # bug = red
        elif nid in suspects:
            color = "#ff9500"  # suspect = orange
        elif nid in god:
            color = "#af52de"  # god node = purple
        border = 5 if (nid == bug_node or nid in god) else 1
        net.add_node(
            nid,
            label=labels.get(nid, nid),
            size=size,
            color=color,
            borderWidth=border,
            title=f"{labels.get(nid, nid)} — degree {round(deg.get(nid, 0.0), 3)}",
        )
    for source, target in g.edges():
        if source in chosen and target in chosen:
            net.add_edge(source, target)

    net.toggle_physics(True)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    net.save_graph(str(out))
    return str(out)
