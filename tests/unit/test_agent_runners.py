"""FR-AGENT-001/005 + FR-UPG2 — iterative graph-guided run + naive baseline + trace."""

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


def test_graph_guided_iterates_and_converges(make_ctx):
    ctx, _ = make_ctx(mode="graph", max_files=8)
    final = run_graph_guided(ctx, "find the bug")
    assert final["nodes_visited"][:2] == ["index.md", "hot.md"]  # vault before code
    assert "to_str_params" in final["read_nodes"]
    assert "ROOTCAUSE" in final["root_cause"] and "FIX" in final["fix"]
    assert final["iterations"] >= 2  # genuinely iterated (measured, not hardcoded)
    assert len(final["files_read"]) <= 2  # only the few graph-selected files


def test_naive_reads_many_files_single_pass(make_ctx):
    ctx, _ = make_ctx(mode="naive", max_files=5)
    final = run_naive(ctx, "find the bug", NAIVE_FILES)
    assert len(final["files_read"]) == 5  # capped, unfocused
    assert final["nodes_visited"] == []  # no graph/vault navigation
    assert final["iterations"] == 1  # single bulk pass
    assert "ROOTCAUSE" in final["root_cause"]


def test_graph_mode_cheaper_than_naive(make_ctx):
    g_ctx, g_gk = make_ctx(mode="graph", max_files=8)
    run_graph_guided(g_ctx, "find the bug")
    n_ctx, n_gk = make_ctx(mode="naive", max_files=5)
    run_naive(n_ctx, "find the bug", NAIVE_FILES)
    assert n_gk.meter.totals("naive")["files_read"] > g_gk.meter.totals("graph")["files_read"]
    assert n_gk.meter.totals("naive")["tokens"] > g_gk.meter.totals("graph")["tokens"]


def test_trace_build_and_save(make_ctx, tmp_path):
    ctx, gk = make_ctx(mode="graph")
    final = run_graph_guided(ctx, "find the bug")
    trace = build_trace(final, gk)
    assert trace["found_bug"] is True and trace["tokens"] > 0
    assert trace["iterations"] >= 2
    out = tmp_path / "trace.json"
    save_trace(trace, out)
    assert out.exists() and '"mode": "graph"' in out.read_text()
