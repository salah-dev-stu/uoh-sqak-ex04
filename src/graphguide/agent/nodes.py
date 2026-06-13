"""LangGraph node functions (FR-AGENT-002/009, FR-UPG2).

Genuinely iterative graph-guided flow: read_index -> read_hot (seed frontier) ->
[ query_graph -> read_code -> diagnose -> (expand & repeat | propose_fix) ].
Each round expands the frontier one hop from the seeds, reads the top-ranked
unread node, and re-diagnoses — so the round count is measured, not hardcoded.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graphguide.agent.context import AgentContext
from graphguide.agent.state import AgentState
from graphguide.agent.tools import FileBudgetExceededError


def _read_vault(vault_dir: str, name: str) -> str:
    path = Path(vault_dir) / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_index(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    return {
        "phase": "read_index",
        "nodes_visited": ["index.md"],
        "context": [_read_vault(ctx.vault_dir, "index.md")],
    }


def read_hot(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    return {
        "phase": "read_hot",
        "nodes_visited": ["hot.md"],
        "context": [_read_vault(ctx.vault_dir, "hot.md")],
        "frontier": list(ctx.seed_nodes),
        "round": 0,
    }


def query_graph(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    """Expand the frontier to ``round`` hops from the seeds; pick the top unread node."""
    frontier = ctx.frontier(state.get("round", 0))
    unread = [n for n in frontier if n not in state.get("read_nodes", [])]
    ranked = ctx.rank(unread)
    top = ranked[:1]
    return {"phase": "query_graph", "frontier": frontier, "suspects": top, "nodes_visited": top}


def read_code(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    suspects = state.get("suspects", [])
    if not suspects:
        return {"phase": "read_code"}
    node = suspects[0]
    src = ctx.source_file(node)
    files: list[str] = []
    snippets: list[str] = []
    if src:
        try:
            code = ctx.reader.read(src)  # cached re-reads are free + don't recount
            snippets = [f"[node:{node}] from {src}\n{code}"]
            if src not in state.get("files_read", []):
                files = [src]
        except FileBudgetExceededError:
            pass
    return {"phase": "read_code", "files_read": files, "context": snippets, "read_nodes": [node]}


def diagnose(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    context = "\n".join(state.get("context", []))
    return {
        "phase": "diagnose",
        "root_cause": ctx.llm.complete(ctx.prompt("diagnose", context=context)),
        "iterations": state.get("round", 0) + 1,
    }


def expand(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    return {"phase": "expand", "round": state.get("round", 0) + 1}


def propose_fix(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    return {
        "phase": "propose_fix",
        "fix": ctx.llm.complete(ctx.prompt("fix", root_cause=state.get("root_cause", ""))),
    }


def route_after_diagnose(ctx: AgentContext, state: AgentState) -> str:
    """Conclude when the diagnosis is conclusive or rounds are exhausted; else expand."""
    rc = state.get("root_cause", "")
    conclusive = bool(rc) and not rc.upper().startswith("INCONCLUSIVE")
    if conclusive or state.get("round", 0) + 1 >= ctx.max_rounds:
        return "propose_fix"
    return "expand"
