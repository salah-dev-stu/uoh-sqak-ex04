"""FR-AGENT-002/004 — node behaviour + the bounded-loop router."""

from graphguide.agent import nodes
from graphguide.agent.state import initial_state


def test_read_index_and_hot(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    idx = nodes.read_index(ctx, st)
    assert idx["nodes_visited"] == ["index.md"] and idx["context"][0]
    hot = nodes.read_hot(ctx, st)
    assert hot["nodes_visited"] == ["hot.md"] and "Task" in hot["context"][0]


def test_query_graph_picks_suspects_from_graph(make_ctx):
    ctx, _ = make_ctx()
    out = nodes.query_graph(ctx, initial_state("t", "graph"))
    assert "luigi/task.py" in out["suspects"]
    assert "luigi/parameter.py" in out["suspects"]
    assert "to_str_params" in out["nodes_visited"]


def test_read_code_reads_only_suspects(make_ctx):
    ctx, gk = make_ctx()
    st = initial_state("t", "graph")
    st["suspects"] = ["luigi/task.py", "luigi/parameter.py"]
    out = nodes.read_code(ctx, st)
    assert out["files_read"] == ["luigi/task.py", "luigi/parameter.py"]
    assert all(out["context"])  # non-empty snippets read from the suspect files


def test_read_code_respects_file_budget(make_ctx):
    ctx, _ = make_ctx(max_files=1)
    st = initial_state("t", "graph")
    st["suspects"] = ["luigi/task.py", "luigi/parameter.py"]
    out = nodes.read_code(ctx, st)
    assert out["files_read"] == ["luigi/task.py"]  # reader budget stopped after 1


def test_diagnose_and_fix(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    st["context"] = ["some focused context"]
    diag = nodes.diagnose(ctx, st)
    assert "ROOTCAUSE" in diag["root_cause"] and diag["iterations"] == 1
    st["root_cause"] = diag["root_cause"]
    assert "FIX" in nodes.propose_fix(ctx, st)["fix"]


def test_router_bounds_iterations(make_ctx):
    ctx, _ = make_ctx()
    assert nodes.route_after_diagnose(ctx, {"root_cause": "x", "iterations": 1}) == "propose_fix"
    assert nodes.route_after_diagnose(ctx, {"root_cause": "", "iterations": 1}) == "query_graph"
    assert nodes.route_after_diagnose(ctx, {"root_cause": "", "iterations": 99}) == "propose_fix"
