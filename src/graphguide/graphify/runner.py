"""GraphifyRunner (FR-GRAPH-001..004) — runs the real ``graphify`` CLI.

The ONLY module that touches ``subprocess``; every invocation is wrapped by the
Gatekeeper (metered). AST mode (``graphify update``) is offline/free; deep mode
adds the semantic layer. Outputs are collected into ``reports/graph/``.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from graphguide.constants import COST_JSON, GRAPH_HTML, GRAPH_JSON, GRAPH_REPORT, KIND_SUBPROCESS
from graphguide.shared import config
from graphguide.shared.gatekeeper import ApiGatekeeper

_ARTIFACTS = (GRAPH_JSON, GRAPH_REPORT, GRAPH_HTML, COST_JSON)


class GraphifyRunner:
    def __init__(
        self,
        gatekeeper: ApiGatekeeper,
        cfg: dict[str, Any] | None = None,
        runner: Callable[..., Any] = subprocess.run,
    ) -> None:
        self._gk = gatekeeper
        self._cfg = cfg or config.get_graphify()
        self._run = runner

    def run_cli(self, args: list[str], *, kind: str = KIND_SUBPROCESS, **meter: Any) -> Any:
        """Run a graphify CLI invocation through the gatekeeper."""
        return self._gk.call(
            kind, lambda: self._run(list(args), capture_output=True, text=True), **meter
        )

    def build_command(self, mode: str, target: str | None = None) -> list[str]:
        target = target or self._cfg["target_path"]
        cli = self._cfg["cli_path"]
        if mode == "ast":
            return [cli, "update", target]
        return [cli, target, "--mode", "deep"]

    def extract(self, mode: str = "ast", target: str | None = None, **meter: Any) -> Any:
        return self.run_cli(self.build_command(mode, target), **meter)

    def collect_outputs(self, src_dir: str | Path, dest_dir: str | Path | None = None) -> list[str]:
        dest = Path(dest_dir or self._cfg["out_dir"])
        dest.mkdir(parents=True, exist_ok=True)
        copied: list[str] = []
        for name in _ARTIFACTS:
            artifact = Path(src_dir) / name
            if artifact.exists():
                shutil.copy2(artifact, dest / name)
                copied.append(name)
        return copied
