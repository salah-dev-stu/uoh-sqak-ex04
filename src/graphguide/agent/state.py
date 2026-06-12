"""LangGraph state schema for the investigation (FR-AGENT)."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict, total=False):
    task: str
    mode: str
    phase: str
    nodes_visited: Annotated[list[str], operator.add]
    files_read: Annotated[list[str], operator.add]
    context: Annotated[list[str], operator.add]
    suspects: list[str]
    root_cause: str
    fix: str
    iterations: int


def initial_state(task: str, mode: str) -> AgentState:
    return {
        "task": task,
        "mode": mode,
        "phase": "start",
        "nodes_visited": [],
        "files_read": [],
        "context": [],
        "suspects": [],
        "root_cause": "",
        "fix": "",
        "iterations": 0,
    }
