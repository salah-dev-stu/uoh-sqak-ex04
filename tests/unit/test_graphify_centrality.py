"""FR-GRAPH-007/008 — centrality table + God-Node detection."""

from pathlib import Path

from graphguide.graphify.centrality import (
    betweenness_centrality,
    centrality_table,
    degree_centrality,
    god_nodes,
)
from graphguide.graphify.loader import GraphLoader

FIXTURE = Path("tests/fixtures/graph_sample.json")


def _graph():
    return GraphLoader.load(FIXTURE).to_networkx()


def test_degree_and_betweenness_keys():
    g = _graph()
    assert set(degree_centrality(g)) == set(g.nodes)
    assert set(betweenness_centrality(g)) == set(g.nodes)


def test_task_is_most_central():
    rows = centrality_table(_graph())
    assert rows[0]["node"] == "task"


def test_god_nodes_flags_task():
    flagged = god_nodes(
        _graph(),
        degree_warning=4,
        degree_critical=6,
        betweenness_warning=0.1,
        betweenness_critical=0.3,
    )
    names = {f["node"] for f in flagged}
    assert "task" in names
    task_row = next(f for f in flagged if f["node"] == "task")
    assert task_row["tier"] in {"CRITICAL", "WARNING"}


def test_god_nodes_warning_tier():
    flagged = god_nodes(
        _graph(),
        degree_warning=2,
        degree_critical=99,
        betweenness_warning=0.99,
        betweenness_critical=1.0,
    )
    assert flagged and all(f["tier"] == "WARNING" for f in flagged)


def test_god_nodes_empty_with_high_thresholds():
    flagged = god_nodes(
        _graph(),
        degree_warning=999,
        degree_critical=9999,
        betweenness_warning=0.99,
        betweenness_critical=1.0,
    )
    assert flagged == []
