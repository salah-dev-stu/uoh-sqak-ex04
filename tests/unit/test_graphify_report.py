"""FR-GRAPH-007 — annotated Hub-Node report renders."""

from graphguide.graphify.loader import GraphLoader
from graphguide.graphify.report import hub_node_report

LOW = {
    "degree_warning": 2,
    "degree_critical": 99,
    "betweenness_warning": 0.99,
    "betweenness_critical": 1.0,
}


def test_report_renders_sections():
    g = GraphLoader.load("tests/fixtures/graph_sample.json").to_networkx()
    md = hub_node_report(g, thresholds=LOW)
    assert "# Annotated Graph Report" in md
    assert "## Hub Nodes" in md
    assert "## Top centrality" in md
    assert "task" in md
    assert "2253" not in md  # uses the small fixture, not the real graph


def test_report_uses_config_thresholds_by_default():
    g = GraphLoader.load("tests/fixtures/graph_sample.json").to_networkx()
    md = hub_node_report(g)  # thresholds from config/graphify.json
    assert "Hub Nodes" in md
