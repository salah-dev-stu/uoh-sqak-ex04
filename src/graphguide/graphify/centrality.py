"""Centrality + God-Node detection over the code graph (FR-GRAPH-007/008).

God Nodes = bottlenecks: high degree or high betweenness centrality. Tiers
``CRITICAL``/``WARNING`` follow the lecture's degree/betweenness thresholds.
"""

from __future__ import annotations

from typing import Any

import networkx as nx


def degree_centrality(graph: nx.DiGraph) -> dict[str, float]:
    return nx.degree_centrality(graph)


def betweenness_centrality(graph: nx.DiGraph) -> dict[str, float]:
    return nx.betweenness_centrality(graph)


def centrality_table(graph: nx.DiGraph) -> list[dict[str, Any]]:
    """Per-node centrality rows, sorted most-central first."""
    deg = nx.degree_centrality(graph)
    bet = nx.betweenness_centrality(graph)
    rows = [
        {
            "node": n,
            "degree": round(deg[n], 4),
            "betweenness": round(bet[n], 4),
            "degree_count": graph.degree(n),
        }
        for n in graph.nodes
    ]
    rows.sort(key=lambda r: (r["betweenness"], r["degree"]), reverse=True)
    return rows


def god_nodes(
    graph: nx.DiGraph,
    *,
    degree_warning: int,
    degree_critical: int,
    betweenness_warning: float,
    betweenness_critical: float,
) -> list[dict[str, Any]]:
    """Flag bottleneck nodes with a ``CRITICAL``/``WARNING`` tier."""
    bet = nx.betweenness_centrality(graph)
    flagged: list[dict[str, Any]] = []
    for n in graph.nodes:
        deg = graph.degree(n)
        b = bet[n]
        if deg >= degree_critical or b >= betweenness_critical:
            tier = "CRITICAL"
        elif deg >= degree_warning or b >= betweenness_warning:
            tier = "WARNING"
        else:
            continue
        flagged.append({"node": n, "degree": deg, "betweenness": round(b, 4), "tier": tier})
    flagged.sort(key=lambda r: (r["betweenness"], r["degree"]), reverse=True)
    return flagged
