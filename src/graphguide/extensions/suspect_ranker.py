"""Extension 1 — suspect ranking by proximity to the failing test (FR-EXT-101).

Original vs Graphify's centrality alone: we fuse centrality with graph-distance
to the failing-test node, so the prime suspect (central AND close to the failure)
floats to the top and seeds the agent — fewer iterations, fewer tokens.
score = w_c * centrality + w_p * 1/(1+distance).
"""

from __future__ import annotations

from typing import Any

import networkx as nx

from graphguide.graphify.loader import CodeGraph


class SuspectRanker:
    def __init__(self, graph: CodeGraph, failing_test_node: str, weights: dict[str, float]) -> None:
        self._graph = graph
        self._node = failing_test_node
        self._wc = float(weights.get("centrality", 0.5))
        self._wp = float(weights.get("proximity", 0.5))

    def rank(self, top: int = 10) -> list[dict[str, Any]]:
        g = self._graph.to_networkx()
        if self._node not in g:
            return []
        deg = nx.degree_centrality(g)
        dist = nx.single_source_shortest_path_length(g.to_undirected(), self._node)
        rows = [
            {
                "node": n,
                "centrality": round(deg[n], 4),
                "distance": d,
                "score": round(self._wc * deg[n] + self._wp * (1.0 / (1.0 + d)), 4),
            }
            for n, d in dist.items()
        ]
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows[:top]

    def to_markdown(self, top: int = 10) -> str:
        lines = [
            "# Ranked Suspects — centrality + proximity to failing test",
            "",
            f"Seeded from failing-test node `{self._node}`. "
            "score = w_c*centrality + w_p*(1/(1+distance)).",
            "",
            "| Rank | Node | Centrality | Distance | Score |",
            "| ---: | --- | ---: | ---: | ---: |",
        ]
        for i, r in enumerate(self.rank(top), 1):
            lines.append(
                f"| {i} | `{r['node']}` | {r['centrality']} | {r['distance']} | {r['score']} |"
            )
        return "\n".join(lines) + "\n"
