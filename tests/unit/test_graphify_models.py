"""FR-GRAPH-005 — typed node/edge models + confidence enum."""

from graphguide.graphify.models import Confidence, Edge, Node


def test_confidence_from_str():
    assert Confidence.from_str("inferred") is Confidence.INFERRED
    assert Confidence.from_str("EXTRACTED") is Confidence.EXTRACTED


def test_node_from_dict():
    n = Node.from_dict({"id": "task", "label": "Task", "source_file": "luigi/task.py"})
    assert n.id == "task" and n.label == "Task"


def test_edge_from_dict_defaults_confidence():
    e = Edge.from_dict({"source": "a", "target": "b"})
    assert e.confidence is Confidence.EXTRACTED and e.weight == 1.0


def test_edge_from_dict_parses_confidence():
    e = Edge.from_dict({"source": "a", "target": "b", "confidence": "AMBIGUOUS"})
    assert e.confidence is Confidence.AMBIGUOUS
