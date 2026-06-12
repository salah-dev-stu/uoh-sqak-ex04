"""Investigation trace (FR-AGENT-006) — per-run metrics for the token report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from graphguide.agent.state import AgentState
from graphguide.shared.gatekeeper import ApiGatekeeper


def build_trace(state: AgentState, gatekeeper: ApiGatekeeper) -> dict[str, Any]:
    mode = state.get("mode", gatekeeper.mode)
    totals = gatekeeper.meter.totals(mode)
    return {
        "mode": mode,
        "nodes_visited": state.get("nodes_visited", []),
        "files_read": state.get("files_read", []),
        "files_count": len(state.get("files_read", [])),
        "iterations": state.get("iterations", 0),
        "tokens": totals["tokens"],
        "metered_files": totals["files_read"],
        "root_cause": state.get("root_cause", ""),
        "found_bug": bool(state.get("root_cause")),
    }


def save_trace(trace: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(trace, indent=2), encoding="utf-8")
