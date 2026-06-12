"""AgentContext (FR-AGENT) — dependencies + graph helpers shared by the nodes.

Holds the LLM, the budgeted reader, the loaded graph, and prompt templates.
The graph itself drives suspect selection (which files to read), which is the
core context-reduction mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
    max_iterations: int = 8
    _nx: Any = field(init=False, default=None)
    _files: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._nx = self.graph.to_networkx()
        self._files = {n.id: n.source_file for n in self.graph.nodes if n.source_file}

    def neighbors(self, node_id: str) -> list[str]:
        if node_id not in self._nx:
            return []
        return sorted(set(self._nx.predecessors(node_id)) | set(self._nx.successors(node_id)))

    def source_files(self, node_ids: list[str]) -> list[str]:
        files: list[str] = []
        for nid in node_ids:
            src = self._files.get(nid)
            if src and src not in files:
                files.append(src)
        return files

    def prompt(self, key: str, **kw: Any) -> str:
        return self.prompts[key].format(**kw)
