"""Naive investigator (FR-AGENT-005) — the baseline for the token comparison.

Reads many raw files (capped by ``max_files``) with no graph/vault narrowing,
then diagnoses. Same success bar as graph-guided, deliberately unfocused.
"""

from __future__ import annotations

from graphguide.agent.context import AgentContext
from graphguide.agent.state import AgentState, initial_state
from graphguide.agent.tools import FileBudgetExceededError


def run_naive(ctx: AgentContext, task: str, files: list[str]) -> AgentState:
    state = initial_state(task, "naive")
    read: list[str] = []
    snippets: list[str] = []
    for path in files:
        try:
            snippets.append(ctx.reader.read(path))
            read.append(path)
        except FileBudgetExceededError:
            break
    context = "\n".join(snippets)[:6000]
    state["files_read"] = read
    state["context"] = snippets
    state["root_cause"] = ctx.llm.complete(ctx.prompt("diagnose", context=context))
    state["phase"] = "diagnose"
    state["iterations"] = 1
    return state
