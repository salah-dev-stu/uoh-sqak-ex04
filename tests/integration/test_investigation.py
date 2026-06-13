"""FR-AGENT-008 / H4 / H6 — end-to-end on the REAL luigi graph (mock LLM, no key).

Graph-guided mode navigates the real graph to the bug node and reads only its
neighbourhood; naive mode reads many raw files. Asserts graph-guided reads fewer
files and fewer tokens — the measured basis for the token-savings report.
"""

from pathlib import Path

import pytest

from graphguide.agent.context import AgentContext
from graphguide.agent.graph_guided import run_graph_guided
from graphguide.agent.llm import MockLLM
from graphguide.agent.naive import run_naive
from graphguide.agent.tools import CodeReader
from graphguide.graphify.loader import GraphLoader
from graphguide.shared.gatekeeper import ApiGatekeeper

REAL_GRAPH = Path("reports/graph/graph.json")
BUG_NODE = "luigi_task_task_to_str_params"
LIMITS = {"requests_per_minute": 100000, "token_budget": {"graph": 50_000_000, "naive": 50_000_000}}


def _reply(prompt: str) -> str:
    if prompt.startswith("f "):
        return "FIX: remove the significant guard"
    if f"[node:{BUG_NODE}]" in prompt or "[file:luigi/task.py]" in prompt:
        return "ROOTCAUSE: significant guard drops params"
    return "INCONCLUSIVE: expand the frontier"


def _ctx(mode: str, max_files: int):
    gk = ApiGatekeeper(mode=mode, limits=LIMITS)
    graph = GraphLoader.load(REAL_GRAPH)
    reader = CodeReader(gk, "target_repo/luigi", max_files=max_files)
    ctx = AgentContext(
        llm=MockLLM(_reply),
        reader=reader,
        vault_dir="vault",
        graph=graph,
        failing_test_node=BUG_NODE,
        max_files=max_files,
        prompts={"diagnose": "d {context}", "fix": "f {root_cause}"},
        seed_nodes=["luigi_task_task", "luigi_parameter_parameter"],
        max_rounds=6,
    )
    return ctx, gk


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed in this checkout")
def test_graph_guided_beats_naive_on_real_graph():
    g_ctx, g_gk = _ctx("graph", max_files=10)
    g_final = run_graph_guided(g_ctx, "fix the to_str_params round-trip bug")
    assert g_final["root_cause"] and g_final["fix"]
    assert BUG_NODE in g_final["read_nodes"]
    assert g_final["iterations"] >= 2  # genuinely iterated to reach the bug node
    assert g_final["nodes_visited"][:2] == ["index.md", "hot.md"]

    files = sorted(
        str(p.relative_to("target_repo/luigi"))
        for p in Path("target_repo/luigi/luigi").glob("*.py")
    )
    n_ctx, n_gk = _ctx("naive", max_files=40)
    n_final = run_naive(n_ctx, "fix the to_str_params round-trip bug", files)

    g_tokens = g_gk.meter.totals("graph")["tokens"]
    n_tokens = n_gk.meter.totals("naive")["tokens"]
    assert len(g_final["files_read"]) < len(n_final["files_read"])
    assert g_tokens < n_tokens
