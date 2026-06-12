"""Token-savings comparison (FR-TOKEN-003/004) — naive vs graph-guided.

Pure functions over two trace dicts (from ``agent.trace.build_trace``) so the
report regenerates from committed ``reports/metrics/*.json`` with no live run.
"""

from __future__ import annotations

from typing import Any


def efficiency_pct(naive: float, graph: float) -> float:
    return round((naive - graph) / naive * 100, 1) if naive else 0.0


def comparison(graph_trace: dict[str, Any], naive_trace: dict[str, Any]) -> dict[str, Any]:
    return {
        "graph": graph_trace,
        "naive": naive_trace,
        "token_savings_pct": efficiency_pct(naive_trace["tokens"], graph_trace["tokens"]),
        "file_savings_pct": efficiency_pct(naive_trace["files_count"], graph_trace["files_count"]),
    }


def comparison_markdown(graph_trace: dict[str, Any], naive_trace: dict[str, Any]) -> str:
    c = comparison(graph_trace, naive_trace)
    rows = [
        ("Tokens consumed", naive_trace["tokens"], graph_trace["tokens"]),
        ("Files / text-units read", naive_trace["files_count"], graph_trace["files_count"]),
        ("Iterations", naive_trace["iterations"], graph_trace["iterations"]),
        ("Graph/vault nodes navigated", 0, len(graph_trace.get("nodes_visited", []))),
        ("Found the bug (quality)", naive_trace["found_bug"], graph_trace["found_bug"]),
    ]
    lines = [
        "# Token-Savings Proof — naive vs graph-guided (H6, §5.5)",
        "",
        f"**Token savings: {c['token_savings_pct']}%** · "
        f"file-read savings: {c['file_savings_pct']}%.",
        "",
        "| Metric | Naive (baseline) | Graph-guided |",
        "| --- | ---: | ---: |",
    ]
    for name, naive_v, graph_v in rows:
        lines.append(f"| {name} | {naive_v} | {graph_v} |")
    lines += [
        "",
        "**Why:** the graph routes the agent from `index.md` -> `hot.md` -> the bug node's "
        "neighbourhood, so it reads only that neighbourhood instead of scanning many files. This "
        "avoids 'Lost in the Middle' — the focused context keeps the signal where the model "
        "attends. Time-to-root-cause is proxied by iterations + files read.",
        "",
        "Numbers come from the Gatekeeper token meter; reproducible from "
        "`reports/metrics/naive.json` + `reports/metrics/graph.json`.",
    ]
    return "\n".join(lines) + "\n"
