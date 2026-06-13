"""Annotated Hub-Node report generator (FR-GRAPH-007).

Renders a Markdown report flagging bottleneck nodes (degree/betweenness) with a
``CRITICAL``/``WARNING`` tier, plus a top-centrality table. Thresholds come from
``config/graphify.json``.
"""

from __future__ import annotations

from typing import Any

import networkx as nx

from graphguide.graphify.centrality import centrality_table, hub_nodes
from graphguide.shared import config


def hub_node_report(
    graph: nx.DiGraph, thresholds: dict[str, Any] | None = None, top: int = 15
) -> str:
    th = thresholds or config.get_graphify()["hub_nodes"]
    flagged = hub_nodes(
        graph,
        degree_warning=int(th["degree_warning"]),
        degree_critical=int(th["degree_critical"]),
        betweenness_warning=float(th["betweenness_warning"]),
        betweenness_critical=float(th["betweenness_critical"]),
    )
    table = centrality_table(graph)[:top]
    lines = [
        "# Annotated Graph Report — Hub Nodes & Centrality",
        "",
        f"Graph: **{graph.number_of_nodes()} nodes**, **{graph.number_of_edges()} edges**.",
        "",
        "## Hub Nodes (bottlenecks)",
        "",
        f"Flagged **{len(flagged)}** node(s) "
        f"(degree >= {th['degree_critical']} or betweenness >= {th['betweenness_critical']} = CRITICAL).",
        "",
        "| Tier | Node | Degree | Betweenness | Risk |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for f in flagged[:top]:
        risk = "single point of failure / mutation target — consider splitting responsibilities"
        lines.append(
            f"| `{f['tier']}` | `{f['node']}` | {f['degree']} | {f['betweenness']} | {risk} |"
        )
    lines += [
        "",
        "## Top centrality",
        "",
        "| Node | Degree | Betweenness | Degree count |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in table:
        lines.append(
            f"| `{row['node']}` | {row['degree']} | {row['betweenness']} | {row['degree_count']} |"
        )
    return "\n".join(lines) + "\n"
