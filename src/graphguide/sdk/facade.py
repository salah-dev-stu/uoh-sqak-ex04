"""GraphGuide — the single public SDK entry (R1).

Composes the graphify, vault, agent, extension, and reporting layers. The CLI and
tests call only this façade; it holds no business logic itself, only orchestration.
Dependencies (LLM, subprocess runner) are injectable so tests need no API key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from graphguide.agent.context import AgentContext
from graphguide.agent.graph_guided import run_graph_guided
from graphguide.agent.llm import CliLLMClient, LLMClient
from graphguide.agent.naive import run_naive
from graphguide.agent.tools import CodeReader
from graphguide.agent.trace import build_trace
from graphguide.constants import GRAPH_JSON, METRICS_DIR, VAULT_DIR
from graphguide.extensions.knowledge_diff import knowledge_diff
from graphguide.extensions.suspect_ranker import SuspectRanker
from graphguide.graphify.centrality import god_nodes
from graphguide.graphify.loader import GraphLoader
from graphguide.graphify.runner import GraphifyRunner
from graphguide.reporting import comparison_markdown
from graphguide.shared import config
from graphguide.shared.gatekeeper import ApiGatekeeper
from graphguide.shared.version import VERSION
from graphguide.vault_builder.builder import VaultBuilder
from graphguide.vault_builder.graph_pages import generate as generate_graph_notes


class GraphGuide:
    def __init__(
        self,
        llm: Any = None,
        subprocess_runner: Any = None,
        read_chars: int | None = None,
        llm_kind: str = "anthropic",
    ) -> None:
        self._llm = llm
        self._sub = subprocess_runner
        self._read_chars = read_chars
        self._llm_kind = llm_kind
        self._gcfg = config.get_graphify()
        self._tasks = config.get_tasks()
        self._agents = config.get_agents()
        self._rl = config.get_rate_limits()

    @staticmethod
    def version() -> str:
        return VERSION

    def graphify(self, mode: str = "ast") -> list[str]:
        gk = ApiGatekeeper("graph", limits=self._rl)
        runner = (
            GraphifyRunner(gk, self._gcfg)
            if self._sub is None
            else GraphifyRunner(gk, self._gcfg, runner=self._sub)
        )
        runner.extract(mode)
        return runner.collect_outputs(f"{self._gcfg['target_path']}/graphify-out")

    def build_vault(
        self, extra_links: list[tuple[str, str]] | None = None, vault_dir: str | None = None
    ) -> list[str]:
        return VaultBuilder(vault_dir or VAULT_DIR).build(self._tasks["components"], extra_links)

    def build_graph_vault(self, nodes_dir: str | None = None) -> list[str]:
        vcfg = config.load("vault")
        graph = self._load_graph()
        th = self._gcfg["god_nodes"]
        god = {
            x["node"]
            for x in god_nodes(
                graph.to_networkx(),
                degree_warning=int(th["degree_warning"]),
                degree_critical=int(th["degree_critical"]),
                betweenness_warning=float(th["betweenness_warning"]),
                betweenness_critical=float(th["betweenness_critical"]),
            )
        }
        suspects = {r["node"] for r in self.rank_suspects(top=10)}
        return generate_graph_notes(
            graph,
            nodes_dir or vcfg["nodes_dir"],
            bug_node=self._tasks["failing_test_node"],
            top_n=int(vcfg["top_n"]),
            hops=int(vcfg["hops"]),
            cap=int(vcfg["max_notes"]),
            god=god,
            suspects=suspects,
        )

    def investigate(self, mode: str = "graph", files: list[str] | None = None) -> dict[str, Any]:
        gk = ApiGatekeeper(mode, limits=self._rl)
        ctx = self._context(mode, gk)
        task = self._tasks["investigation_task"]
        if mode == "naive":
            state = run_naive(ctx, task, files or self._repo_files())
        else:
            state = run_graph_guided(ctx, task)
        return build_trace(state, gk)

    def rank_suspects(self, top: int = 10) -> list[dict[str, Any]]:
        ranker = SuspectRanker(
            self._load_graph(), self._tasks["failing_test_node"], self._tasks["suspect_weights"]
        )
        return ranker.rank(top)

    def knowledge_diff(self) -> dict[str, Any]:
        return knowledge_diff("reports/vault_before", "reports/vault_after")

    def token_report(self) -> str:
        graph = json.loads(Path(METRICS_DIR, "graph.json").read_text(encoding="utf-8"))
        naive = json.loads(Path(METRICS_DIR, "naive.json").read_text(encoding="utf-8"))
        return comparison_markdown(graph, naive)

    # --- internals ---
    def _load_graph(self):
        return GraphLoader.load(f"{self._gcfg['out_dir']}/{GRAPH_JSON}")

    def _context(self, mode: str, gk: ApiGatekeeper) -> AgentContext:
        max_files = int(self._rl["max_files"][mode])
        read_chars = self._read_chars or int(self._rl.get("read_chars", 4000))
        reader = CodeReader(gk, self._gcfg["target_path"], max_files, read_chars=read_chars)
        llm = self._llm or self._build_llm(gk)
        return AgentContext(
            llm=llm,
            reader=reader,
            vault_dir=VAULT_DIR,
            graph=self._load_graph(),
            failing_test_node=self._tasks["failing_test_node"],
            max_files=max_files,
            prompts=self._agents["prompts"],
            seed_nodes=list(self._tasks.get("seed_nodes", [])),
            max_iterations=int(self._rl["max_iterations"]),
            max_rounds=int(self._rl.get("max_rounds", 5)),
        )

    def _build_llm(self, gk: ApiGatekeeper) -> Any:
        if self._llm_kind == "cli":
            return CliLLMClient(gk, self._agents)
        return LLMClient(gk, self._agents)

    def _repo_files(self) -> list[str]:
        root = Path(self._gcfg["target_path"])
        return sorted(str(p.relative_to(root)) for p in (root / "luigi").glob("*.py"))
