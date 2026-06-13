"""R1 / FR-SDK — the GraphGuide façade orchestrates every feature (mock LLM)."""

from pathlib import Path

import pytest

from graphguide.agent.llm import MockLLM
from graphguide.sdk.facade import GraphGuide

REAL_GRAPH = Path("reports/graph/graph.json")


def _reply(prompt: str) -> str:
    return "FIX" if prompt.startswith("f ") else "ROOTCAUSE: significant guard"


def test_version():
    assert GraphGuide.version() == "1.04"


def test_build_llm_backend_selection():
    from graphguide.agent.llm import CliLLMClient, LLMClient
    from graphguide.shared.gatekeeper import ApiGatekeeper

    gk = ApiGatekeeper("graph")
    assert isinstance(GraphGuide()._build_llm(gk), LLMClient)
    assert isinstance(GraphGuide(llm_kind="cli")._build_llm(gk), CliLLMClient)


def test_graphify_invokes_runner():
    calls: list = []

    def fake_run(args, **kw):
        calls.append(args)
        return type("R", (), {"stdout": ""})()

    result = GraphGuide(subprocess_runner=fake_run).graphify("ast")
    assert calls and calls[0][:2] == ["graphify", "update"]
    assert isinstance(result, list)


def test_build_vault_to_tmp(tmp_path):
    written = GraphGuide().build_vault(vault_dir=str(tmp_path))
    assert set(written) == {"index.md", "hot.md", "log.md"}
    assert (tmp_path / "index.md").exists()


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed")
def test_investigate_graph_beats_naive():
    gg = GraphGuide(llm=MockLLM(_reply))
    graph = gg.investigate("graph")
    naive = gg.investigate("naive")
    assert graph["found_bug"] and naive["found_bug"]
    assert naive["files_count"] > graph["files_count"]


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed")
def test_build_graph_vault_dense(tmp_path):
    written = GraphGuide().build_graph_vault(nodes_dir=str(tmp_path))
    assert len(written) >= 30  # dense, generated from the real graph


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed")
def test_build_html_graph_offline(tmp_path):
    out = GraphGuide().build_html_graph(out_path=str(tmp_path / "g.html"))
    html = Path(out).read_text(encoding="utf-8")
    assert "luigi_task_task_to_str_params" in html  # the bug node is in the graph
    assert "<script" in html and len(html) > 50_000  # vis-network inlined (renders offline)


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed")
def test_rank_suspects_surfaces_bug_node():
    rows = GraphGuide().rank_suspects(top=5)
    assert any("to_str_params" in r["node"] for r in rows)


def test_knowledge_diff_and_token_report():
    if not Path("reports/vault_after").exists():
        pytest.skip("snapshots not present")
    gg = GraphGuide()
    assert gg.knowledge_diff()["pages_added"]
    assert "Token-Savings Proof" in gg.token_report()
