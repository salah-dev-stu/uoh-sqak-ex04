"""Load ``graph.json`` into typed models + a NetworkX view (FR-GRAPH-005)."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from graphguide.graphify.models import RANK, Confidence, Edge, Node


class CodeGraph:
    """A loaded graph: typed nodes/edges + on-demand NetworkX projection."""

    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def filter_edges(self, min_confidence: Confidence) -> list[Edge]:
        threshold = RANK[min_confidence]
        return [e for e in self.edges if RANK[e.confidence] >= threshold]

    def to_networkx(self, min_confidence: Confidence | None = None) -> nx.DiGraph:
        graph: nx.DiGraph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.id, label=node.label, file_type=node.file_type)
        edges = self.filter_edges(min_confidence) if min_confidence else self.edges
        for edge in edges:
            graph.add_edge(
                edge.source,
                edge.target,
                relation=edge.relation,
                confidence=edge.confidence.value,
                weight=edge.weight,
            )
        return graph


class GraphLoader:
    @staticmethod
    def load(path: str | Path) -> CodeGraph:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        nodes = [Node.from_dict(d) for d in data.get("nodes", [])]
        edges = [Edge.from_dict(d) for d in data.get("edges", [])]
        return CodeGraph(nodes, edges)
