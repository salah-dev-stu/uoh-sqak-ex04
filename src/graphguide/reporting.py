"""Token-savings comparison (FR-TOKEN-003/004) — naive vs graph-guided.

Pure functions over two trace dicts (from ``agent.trace.build_trace``) so the
report regenerates from committed ``reports/metrics/*.json`` with no live run.
"""

from __future__ import annotations

from typing import Any


def efficiency_pct(naive: float, graph: float) -> float:
    return round((naive - graph) / naive * 100, 1) if naive else 0.0


def identifies_root_cause(text: str) -> bool:
    """True if the model's answer names the serialize/deserialize asymmetry root cause."""
    t = text.lower()
    return "significant" in t and any(
        k in t for k in ("from_str_params", "asymmetr", "keyerror", "insignificant")
    )


def lim_markdown(results: list[dict[str, Any]], verdict: str) -> str:
    """Render the 'Lost in the Middle' experiment report (FR-UPG5)."""
    lines = [
        "# Lost in the Middle — demonstrated (Upgrade 5, FR-UPG5)",
        "",
        "Does burying the bug-relevant code in the **middle** of a large naive context degrade the "
        "model's diagnosis, versus the small **focused** graph-guided context? Real run "
        "(`claude -p`, routed through the Gatekeeper).",
        "",
        "| Condition | Context tokens | Bug position | Found root cause? |",
        "| --- | ---: | --- | :---: |",
    ]
    for r in results:
        mark = "yes" if r["found"] else "NO"
        lines.append(f"| {r['condition']} | {r['tokens']} | {r['position']} | {mark} |")
    lines += ["", "## Verdict", "", verdict, "", "## What each run answered"]
    for r in results:
        excerpt = " ".join(r["excerpt"].split())[:400]
        lines += ["", f"**{r['condition']}:**", "", f"> {excerpt}"]
    return "\n".join(lines) + "\n"


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
        ("Code tokens read", naive_trace["tokens"], graph_trace["tokens"]),
        ("Code files read", naive_trace["files_count"], graph_trace["files_count"]),
        ("Iterations (rounds)", naive_trace["iterations"], graph_trace["iterations"]),
        ("Graph/vault nodes navigated", 0, len(graph_trace.get("nodes_visited", []))),
        ("Found the bug", naive_trace["found_bug"], graph_trace["found_bug"]),
    ]
    lines = [
        "# Token-Savings Proof — naive vs graph-guided (H6, §5.5)",
        "",
        f"**Code-token savings: {c['token_savings_pct']}%** "
        f"({naive_trace['tokens']} -> {graph_trace['tokens']}) · "
        f"file-read savings: {c['file_savings_pct']}%.",
        "",
        "| Metric | Naive (baseline) | Graph-guided |",
        "| --- | ---: | ---: |",
    ]
    for name, naive_v, graph_v in rows:
        lines.append(f"| {name} | {naive_v} | {graph_v} |")
    lines += [
        "",
        "## What this measures (and what it does not)",
        "- **Metric = code tokens actually read into the agent's context** (the spec's target: "
        "'cut needless code reads'). The Obsidian vault (`index.md`/`hot.md`) is the cheap "
        "*navigation layer* that replaces expensive code reading; it is not counted as code cost.",
        "- **Both modes use a deterministic mock LLM**, so 'found the bug' is true by construction. "
        "This experiment isolates and proves the **context/token reduction** the graph enables — not "
        "a claim that graph-guidance raises the model's success rate.",
        "- **Iterations are measured**, not hardcoded: graph-guided runs a real frontier-expansion "
        "loop (seed at `hot.md` nodes -> expand one hop per round -> read the top-ranked node) and "
        "converges in a few targeted rounds, each reading a single node; naive is one bulk pass over "
        "many files. So graph-guided trades a few cheap rounds for a fraction of the tokens.",
        "- **Baseline fairness:** naive reads every top-level `luigi/*.py` module (capped at "
        "`max_files`) — an unfocused read of the package, not a strawman. The tokens charged equal "
        "the code it ingests (no read-then-discard).",
        "",
        "## Why graph-guided wins",
        "The graph routes the agent `index.md` -> `hot.md` -> the failing-test node's neighbourhood, "
        "so it reads only that neighbourhood. Focused context also avoids 'Lost in the Middle'.",
        "",
        "Numbers come from the Gatekeeper token meter; reproducible from "
        "`reports/metrics/naive.json` + `reports/metrics/graph.json`.",
        "",
        "A **real-LLM run** (no mock, `claude -p` via the Gatekeeper) confirms the model genuinely "
        "finds this bug graph-guided — see `reports/real_run.md`.",
    ]
    return "\n".join(lines) + "\n"
