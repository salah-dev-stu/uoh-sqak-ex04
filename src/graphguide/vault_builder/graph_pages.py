"""Dense vault generator (FR-UPG1-*) — one note per selected graph node.

Generated entirely from ``graph.json``: selection = top-N by centrality UNION
everything within K hops of the bug node (capped). Wikilinks mirror real edges
but only to neighbours that are also selected -> rich subgraph, zero dangling.
"""

from __future__ import annotations

import re
from pathlib import Path

import networkx as nx

from graphguide.graphify.centrality import degree_centrality
from graphguide.graphify.loader import CodeGraph


def slug(node_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", node_id)


def select_nodes(graph: CodeGraph, bug_node: str, top_n: int, hops: int, cap: int) -> list[str]:
    g = graph.to_networkx()
    if not g.number_of_nodes():
        return []
    deg = degree_centrality(g)
    top = sorted(deg, key=lambda n: deg[n], reverse=True)[:top_n]
    near: list[str] = []
    if bug_node in g:
        reach = nx.single_source_shortest_path_length(g.to_undirected(), bug_node, cutoff=hops)
        near = list(reach)
    ordered = [n for n in dict.fromkeys([bug_node, *near, *top]) if n in g]
    return ordered[:cap]


def node_tags(node_id: str, bug_node: str, hub: set[str], suspects: set[str]) -> list[str]:
    tags: list[str] = []
    if node_id == bug_node:
        tags += ["bug", "fixed"]
    if node_id in hub:
        tags.append("hub")
    if node_id in suspects:
        tags.append("suspect")
    return tags


def render_note(
    node_id: str, label: str, neighbours: list[str], tags: list[str], community: int | None
) -> str:
    all_tags = list(tags)
    if community is not None:
        all_tags.append(f"community/{community}")
    head = ["---", f"node: {node_id}", f"label: {label}"]
    if all_tags:
        head.append("tags: [" + ", ".join(all_tags) + "]")
    head += ["---", "", f"# {label}", "", f"Graph node `{node_id}`.", "", "## Neighbours"]
    body = [f"- [[{slug(n)}]]" for n in neighbours] or ["- _(leaf node)_"]
    mer = ["", "## Neighbourhood", "", "```mermaid", "flowchart LR"]
    s = slug(node_id)
    mer += [f"    {s} --> {slug(n)}" for n in neighbours[:8]] or [f"    {s}"]
    mer.append("```")
    comm = f"community/{community}" if community is not None else "hub"
    dv = ["", "## Related (Dataview)", "", "```dataview", f"LIST FROM #{comm}", "```"]
    return "\n".join([*head, *body, *mer, *dv]) + "\n"


def generate(
    graph: CodeGraph,
    out_dir,
    *,
    bug_node: str,
    top_n: int,
    hops: int,
    cap: int,
    hub: set[str],
    suspects: set[str],
) -> list[str]:
    selected = select_nodes(graph, bug_node, top_n, hops, cap)
    chosen = set(selected)
    g = graph.to_networkx().to_undirected()
    labels = {n.id: (n.label or n.id) for n in graph.nodes}
    communities = {n.id: n.community for n in graph.nodes}
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for node_id in selected:
        neighbours = sorted(n for n in g.neighbors(node_id) if n in chosen) if node_id in g else []
        note = render_note(
            node_id,
            labels.get(node_id, node_id),
            neighbours,
            node_tags(node_id, bug_node, hub, suspects),
            communities.get(node_id),
        )
        (dest / f"{slug(node_id)}.md").write_text(note, encoding="utf-8")
        written.append(f"{slug(node_id)}.md")
    return written
