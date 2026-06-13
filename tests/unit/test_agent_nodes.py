"""FR-AGENT-002 / FR-UPG2 — iterative node behaviour + the frontier-expansion router."""

from graphguide.agent import nodes
from graphguide.agent.state import initial_state


def test_read_index_and_hot_seeds_frontier(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    idx = nodes.read_index(ctx, st)
    assert idx["nodes_visited"] == ["index.md"] and idx["context"][0]
    hot = nodes.read_hot(ctx, st)
    assert hot["nodes_visited"] == ["hot.md"]
    assert hot["frontier"] == ["task", "parameter"] and hot["round"] == 0


def test_query_graph_round0_is_seeds_only(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    out = nodes.query_graph(ctx, st)  # round 0
    assert set(out["frontier"]) <= {"task", "parameter"}
    assert out["suspects"] and "to_str_params" not in out["frontier"]


def test_query_graph_round1_reaches_bug(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    st["round"] = 1
    st["read_nodes"] = ["task"]
    out = nodes.query_graph(ctx, st)
    assert "to_str_params" in out["frontier"]  # one-hop expansion reaches the bug node
    assert out["suspects"][0] == "to_str_params"  # ranked top (proximity 0)


def test_read_code_reads_one_node_with_marker(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    st["suspects"] = ["to_str_params"]
    out = nodes.read_code(ctx, st)
    assert out["read_nodes"] == ["to_str_params"]
    assert out["files_read"] == ["luigi/task.py"]
    assert "[node:to_str_params]" in out["context"][0]


def test_read_code_same_file_not_double_counted(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    st["suspects"] = ["to_str_params"]
    st["files_read"] = ["luigi/task.py"]  # already read this file
    out = nodes.read_code(ctx, st)
    assert out["files_read"] == []  # not recounted
    assert "[node:to_str_params]" in out["context"][0]  # but marker still surfaced


def test_read_code_no_suspects(make_ctx):
    ctx, _ = make_ctx()
    assert nodes.read_code(ctx, initial_state("t", "graph")) == {"phase": "read_code"}


def test_read_code_budget_exhausted(make_ctx):
    ctx, _ = make_ctx(max_files=0)  # reader cannot read any file
    st = initial_state("t", "graph")
    st["suspects"] = ["to_str_params"]
    out = nodes.read_code(ctx, st)
    assert out["files_read"] == [] and out["read_nodes"] == ["to_str_params"]


def test_diagnose_sets_measured_iterations(make_ctx):
    ctx, _ = make_ctx()
    st = initial_state("t", "graph")
    st["round"] = 1
    st["context"] = ["[node:to_str_params] from luigi/task.py\n..."]
    out = nodes.diagnose(ctx, st)
    assert out["iterations"] == 2 and "ROOTCAUSE" in out["root_cause"]


def test_router_expands_until_conclusive_or_capped(make_ctx):
    ctx, _ = make_ctx()
    assert (
        nodes.route_after_diagnose(ctx, {"root_cause": "ROOTCAUSE x", "round": 1}) == "propose_fix"
    )
    assert nodes.route_after_diagnose(ctx, {"root_cause": "INCONCLUSIVE", "round": 0}) == "expand"
    assert (
        nodes.route_after_diagnose(ctx, {"root_cause": "INCONCLUSIVE", "round": 99})
        == "propose_fix"
    )
