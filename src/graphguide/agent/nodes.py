"""LangGraph node functions (FR-AGENT-002/009).

Each node is ``(ctx, state) -> partial state``. The enforced order is index ->
hot -> graph query -> budgeted code -> diagnose -> fix: the agent consults the
vault and graph BEFORE reading any raw code (the context-reduction mechanism).
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
    }


def query_graph(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    node = ctx.failing_test_node
    neighbors = ctx.neighbors(node)
    suspects = ctx.source_files([node, *neighbors])
    return {
        "phase": "query_graph",
        "nodes_visited": [node, *neighbors],
        "suspects": suspects,
        "context": [f"graph-guided suspects (from {node}): {suspects}"],
    }


def read_code(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    files: list[str] = []
    snippets: list[str] = []
    for path in state.get("suspects", []):
        try:
            snippets.append(ctx.reader.read(path))
            files.append(path)
        except FileBudgetExceededError:
            break
    return {"phase": "read_code", "files_read": files, "context": snippets}


def diagnose(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    context = "\n".join(state.get("context", []))
    return {
        "phase": "diagnose",
        "root_cause": ctx.llm.complete(ctx.prompt("diagnose", context=context)),
        "iterations": state.get("iterations", 0) + 1,
    }


def propose_fix(ctx: AgentContext, state: AgentState) -> dict[str, Any]:
    return {
        "phase": "propose_fix",
        "fix": ctx.llm.complete(ctx.prompt("fix", root_cause=state.get("root_cause", ""))),
    }


def route_after_diagnose(ctx: AgentContext, state: AgentState) -> str:
    """Bounded loop (FR-AGENT-004): proceed when diagnosed or out of iterations."""
    if state.get("root_cause") or state.get("iterations", 0) >= ctx.max_iterations:
        return "propose_fix"
    return "query_graph"
