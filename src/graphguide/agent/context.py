"""AgentContext (FR-AGENT) — dependencies + graph helpers shared by the nodes.

Holds the LLM, the budgeted reader, the loaded graph, prompt templates, and the
frontier-expansion helpers (seed nodes, BFS frontier, proximity ranking) that
drive the genuinely-iterative graph-guided loop (FR-UPG2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from graphguide.graphify.loader import CodeGraph


@dataclass
class AgentContext:
    llm: Any
    reader: Any
    vault_dir: str
    graph: CodeGraph
    failing_test_node: str
    max_files: int
    prompts: dict[str, str]
    seed_nodes: list[str] = field(default_factory=list)
    max_iterations: int = 8
    max_rounds: int = 5
    _nx: Any = field(init=False, default=None)
    _und: Any = field(init=False, default=None)
    _files: dict[str, str] = field(init=False, default_factory=dict)
    _deg: dict[str, float] = field(init=False, default_factory=dict)
    _dist: dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._nx = self.graph.to_networkx()
        self._und = self._nx.to_undirected()
        self._files = {n.id: n.source_file for n in self.graph.nodes if n.source_file}
        self._deg = nx.degree_centrality(self._nx) if self._nx.number_of_nodes() else {}
        self._dist = (
            nx.single_source_shortest_path_length(self._und, self.failing_test_node)
            if self.failing_test_node in self._und
            else {}
        )

    def neighbors(self, node_id: str) -> list[str]:
        if node_id not in self._nx:
            return []
        return sorted(set(self._nx.predecessors(node_id)) | set(self._nx.successors(node_id)))

    def frontier(self, cutoff: int) -> list[str]:
        """All nodes within ``cutoff`` hops of any seed node (round 0 = seeds only)."""
        reached: set[str] = set()
        for seed in self.seed_nodes:
            if seed in self._und:
                reached |= set(
                    nx.single_source_shortest_path_length(self._und, seed, cutoff=cutoff)
                )
        return sorted(reached)

    def rank(self, candidates: list[str]) -> list[str]:
        """Rank candidate nodes by centrality + proximity to the failing-test node."""

        def score(nid: str) -> float:
            prox = 1.0 / (1.0 + self._dist.get(nid, 999))
            return 0.5 * self._deg.get(nid, 0.0) + 0.5 * prox

        return sorted(candidates, key=score, reverse=True)

    def source_files(self, node_ids: list[str]) -> list[str]:
        files: list[str] = []
        for nid in node_ids:
            src = self._files.get(nid)
            if src and src not in files:
                files.append(src)
        return files

    def source_file(self, node_id: str) -> str | None:
        return self._files.get(node_id)

    def prompt(self, key: str, **kw: Any) -> str:
        return self.prompts[key].format(**kw)
