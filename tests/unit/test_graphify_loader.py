"""FR-GRAPH-005 — loader builds typed graph + NetworkX view + confidence filter."""

from pathlib import Path

from graphguide.graphify.loader import GraphLoader
from graphguide.graphify.models import Confidence

FIXTURE = Path("tests/fixtures/graph_sample.json")


def test_load_counts():
    g = GraphLoader.load(FIXTURE)
    assert len(g.nodes) == 9
    assert len(g.edges) == 11


def test_filter_edges_by_confidence():
    g = GraphLoader.load(FIXTURE)
    extracted_only = g.filter_edges(Confidence.EXTRACTED)
    assert all(e.confidence is Confidence.EXTRACTED for e in extracted_only)
    assert len(extracted_only) < len(g.edges)


def test_to_networkx():
    g = GraphLoader.load(FIXTURE)
    nxg = g.to_networkx()
    assert nxg.number_of_nodes() == 9
    assert nxg.number_of_edges() == 11
    assert nxg.has_edge("task", "to_str_params")


def test_to_networkx_filtered_drops_ambiguous():
    g = GraphLoader.load(FIXTURE)
    nxg = g.to_networkx(min_confidence=Confidence.EXTRACTED)
    assert not nxg.has_edge("from_str_params", "parameter")  # AMBIGUOUS dropped


def test_load_nodelink_format():
    """Graphify exports NetworkX node-link JSON ('links', not 'edges')."""
    g = GraphLoader.load(Path("tests/fixtures/graph_nodelink.json"))
    assert len(g.edges) == 1
    assert g.edges[0].confidence is Confidence.INFERRED
    assert g.to_networkx().has_edge("a", "b")
