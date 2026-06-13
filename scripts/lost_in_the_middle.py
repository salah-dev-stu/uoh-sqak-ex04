"""Upgrade 5 (FR-UPG5) — 'Lost in the Middle', demonstrated with our own data.

Buries the bug-relevant code (Task.to_str_params / from_str_params) at the start,
middle, and end of a large naive context dump, and asks the REAL Claude CLI to find
the root cause each time — versus the small focused graph-guided context. Routed
through the Gatekeeper (real tokens). Writes reports/lost_in_the_middle.md.

Tests/CI stay on the mock; this is a committed artifact. Run:
  uv run python scripts/lost_in_the_middle.py
"""

from __future__ import annotations

from pathlib import Path

from graphguide.agent.llm import CliLLMClient
from graphguide.reporting import identifies_root_cause, lim_markdown
from graphguide.shared.gatekeeper import ApiGatekeeper
from graphguide.shared.token_meter import estimate_tokens

LUIGI = Path("target_repo/luigi/luigi")
QUESTION = (
    "You are debugging luigi. The test `test_task_to_str_to_task` fails with "
    "`KeyError` on a parameter declared `significant=False`. Read the source below and, "
    "in 2-3 sentences, state the precise root cause (which method(s) and why).\n\nSOURCE:\n\n"
)


def bug_snippet() -> str:
    code = (LUIGI / "task.py").read_text(encoding="utf-8", errors="ignore")
    i = code.find("def from_str_params")
    j = code.find("def clone", i)
    return code[i:j] if 0 <= i < j else code[:1600]


def filler(target_tokens: int) -> str:
    parts: list[str] = []
    total = 0
    for path in sorted(LUIGI.glob("*.py")):
        if path.name == "task.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        parts.append(f"# ==== FILE: luigi/{path.name} ====\n{text}")
        total += estimate_tokens(text)
        if total >= target_tokens:
            break
    return "\n\n".join(parts)


def assemble(fill: str, snippet: str, position: str) -> str:
    if position == "start":
        return snippet + "\n\n" + fill
    if position == "end":
        return fill + "\n\n" + snippet
    half = len(fill) // 2
    return fill[:half] + "\n\n" + snippet + "\n\n" + fill[half:]


def run_condition(condition: str, position: str, context: str) -> dict:
    gk = ApiGatekeeper(
        mode="graph", limits={"requests_per_minute": 100, "token_budget": {"graph": 99_000_000}}
    )
    answer = CliLLMClient(gk).complete(QUESTION + context)
    return {
        "condition": condition,
        "position": position,
        "tokens": gk.meter.totals("graph")["tokens"],
        "found": identifies_root_cause(answer),
        "excerpt": answer,
    }


def main() -> int:
    snippet = bug_snippet()
    big = filler(45_000)
    results = [
        run_condition("focused (graph-guided)", "n/a", snippet),
        run_condition("naive buried — start", "start", assemble(big, snippet, "start")),
        run_condition("naive buried — middle", "middle", assemble(big, snippet, "middle")),
        run_condition("naive buried — end", "end", assemble(big, snippet, "end")),
    ]
    found = {r["position"]: r["found"] for r in results}
    focused_tok = results[0]["tokens"] or 1
    middle_tok = next(r["tokens"] for r in results if r["position"] == "middle")
    ratio = round(middle_tok / focused_tok)
    if found.get("middle") is False and (
        found.get("n/a") or found.get("start") or found.get("end")
    ):
        verdict = (
            "**Lost in the Middle confirmed.** The model identified the root cause from the focused "
            "context (and/or when the code sat at the start/end), but **missed it when the same code "
            "was buried in the middle** of the large naive dump — exactly the lecture's thesis, and "
            "why graph-guided focusing (which also uses a fraction of the tokens) is the right design."
        )
    elif all(r["found"] for r in results):
        verdict = (
            "At this context size the model was robust — it found the root cause in every position, "
            "including buried-in-the-middle. The 'Lost in the Middle' degradation is scale-dependent "
            "(it sharpens at much longer contexts); the **practical** win here is unchanged and stark: "
            f"the focused graph-guided context reached the *same* correct diagnosis on **{focused_tok} "
            f"vs ~{middle_tok} tokens — about {ratio}x fewer**. Focusing is the right design whether or "
            "not the model degrades."
        )
    else:
        verdict = (
            "Mixed result (see the table). Position affected the diagnosis, supporting the value of "
            "the focused graph-guided context over an unfocused dump."
        )
    Path("reports/lost_in_the_middle.md").write_text(
        lim_markdown(results, verdict), encoding="utf-8"
    )
    for r in results:
        print(f"{r['condition']:28} tokens={r['tokens']:>6} found={r['found']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
