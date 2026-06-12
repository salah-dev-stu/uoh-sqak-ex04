"""Offline graph-guided query wrappers (FR-GRAPH-006).

``query`` / ``explain`` / ``path`` / ``affected`` operate on ``graph.json`` with
no LLM. They compose a :class:`GraphifyRunner` so the single (metered) subprocess
path lives in ``runner.py``. These are the agent's navigation primitives.
"""

from __future__ import annotations

from typing import Any

from graphguide.constants import KIND_FILE_READ
from graphguide.graphify.runner import GraphifyRunner
from graphguide.shared import config


class GraphQueries:
    def __init__(self, runner: GraphifyRunner, cfg: dict[str, Any] | None = None) -> None:
        self._runner = runner
        self._cfg = cfg or config.get_graphify()

    def _graph_path(self) -> str:
        return f"{self._cfg['out_dir']}/graph.json"

    def _cli(self) -> str:
        return self._cfg["cli_path"]

    def query(self, question: str, budget: int | None = None) -> str:
        budget = budget or int(self._cfg.get("query_budget", 2000))
        args = [
            self._cli(),
            "query",
            question,
            "--budget",
            str(budget),
            "--graph",
            self._graph_path(),
        ]
        return _stdout(self._runner.run_cli(args, kind=KIND_FILE_READ, units_read=budget))

    def explain(self, node: str) -> str:
        args = [self._cli(), "explain", node, "--graph", self._graph_path()]
        return _stdout(self._runner.run_cli(args, kind=KIND_FILE_READ, units_read=1))

    def path(self, source: str, target: str) -> str:
        args = [self._cli(), "path", source, target, "--graph", self._graph_path()]
        return _stdout(self._runner.run_cli(args, kind=KIND_FILE_READ, units_read=1))

    def affected(self, node: str) -> str:
        args = [self._cli(), "affected", node, "--graph", self._graph_path()]
        return _stdout(self._runner.run_cli(args, kind=KIND_FILE_READ, units_read=1))


def _stdout(result: Any) -> str:
    return getattr(result, "stdout", "") or ""
