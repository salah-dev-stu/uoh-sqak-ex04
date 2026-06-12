"""FR-AGENT-001/005 — graph-guided StateGraph + naive runner + trace."""

from graphguide.agent.graph_guided import run_graph_guided
from graphguide.agent.naive import run_naive
from graphguide.agent.trace import build_trace, save_trace

NAIVE_FILES = [
    "luigi/task.py",
    "luigi/worker.py",
    "luigi/scheduler.py",
    "luigi/parameter.py",
    "luigi/target.py",
    "luigi/interface.py",
]


def test_graph_guided_runs_in_order(make_ctx):
    ctx, gk = make_ctx(mode="graph", max_files=8)
    final = run_graph_guided(ctx, "find the bug")
    assert final["nodes_visited"][:2] == ["index.md", "hot.md"]  # vault before code
    assert "to_str_params" in final["nodes_visited"]
    assert "ROOTCAUSE" in final["root_cause"] and "FIX" in final["fix"]
    assert len(final["files_read"]) <= 3  # only graph-selected suspects


def test_naive_reads_many_files_no_graph(make_ctx):
    ctx, gk = make_ctx(mode="naive", max_files=5)
    final = run_naive(ctx, "find the bug", NAIVE_FILES)
    assert len(final["files_read"]) == 5  # capped, unfocused
    assert final["nodes_visited"] == []  # no graph/vault navigation
    assert "ROOTCAUSE" in final["root_cause"]


def test_graph_mode_cheaper_than_naive(make_ctx):
    g_ctx, g_gk = make_ctx(mode="graph", max_files=8)
    run_graph_guided(g_ctx, "find the bug")
    n_ctx, n_gk = make_ctx(mode="naive", max_files=5)
    run_naive(n_ctx, "find the bug", NAIVE_FILES)
    assert n_gk.meter.totals("naive")["files_read"] > g_gk.meter.totals("graph")["files_read"]


def test_trace_build_and_save(make_ctx, tmp_path):
    ctx, gk = make_ctx(mode="graph")
    final = run_graph_guided(ctx, "find the bug")
    trace = build_trace(final, gk)
    assert trace["found_bug"] is True and trace["tokens"] > 0
    out = tmp_path / "trace.json"
    save_trace(trace, out)
    assert out.exists() and '"mode": "graph"' in out.read_text()
