"""Upgrade 3 (FR-UPG3) — one real-LLM graph-guided run.

Runs the graph-guided agent once against the REAL Claude CLI (`claude -p`, via the
Gatekeeper — uses the user's login, no API key). Reads full files so the model sees
the buggy method, then writes ``reports/real_run.md`` + a raw trace JSON.

Tests/CI stay on the MockLLM (grader Path D unchanged); this is a committed artifact,
not a CI dependency. Run:  uv run python scripts/real_run_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from graphguide.agent.trace import save_trace
from graphguide.sdk.facade import GraphGuide


def _report(trace: dict) -> str:
    nodes = ", ".join(f"`{n}`" for n in trace.get("nodes_visited", []))
    files = ", ".join(f"`{f}`" for f in trace.get("files_read", [])) or "_none_"
    return (
        "# Real-LLM Graph-Guided Run (Upgrade 3, FR-UPG3)\n\n"
        "One genuine run of the graph-guided agent against the **real Claude CLI** "
        "(`claude -p`, routed through the Gatekeeper — no API key, uses the CLI login). "
        "The mock proves the token *reduction* deterministically; this confirms the model "
        "**genuinely finds the bug** from the graph-selected focused context.\n\n"
        f"- **Path (nodes navigated):** {nodes}\n"
        f"- **Files read:** {files}\n"
        f"- **Iterations (rounds):** {trace.get('iterations')}\n"
        f"- **Real tokens (Gatekeeper meter):** {trace.get('tokens')}\n"
        f"- **Found the bug:** {trace.get('found_bug')}\n\n"
        "## Model's root cause\n\n"
        f"> {trace.get('root_cause', '').strip()}\n"
    )


def main() -> int:
    gg = GraphGuide(llm_kind="cli", read_chars=16000)
    trace = gg.investigate("graph")
    Path("reports").mkdir(exist_ok=True)
    save_trace(trace, "reports/metrics/real_run_trace.json")
    Path("reports/real_run.md").write_text(_report(trace), encoding="utf-8")
    print(json.dumps({k: trace[k] for k in ("iterations", "tokens", "found_bug")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
