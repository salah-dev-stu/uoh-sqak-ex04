"""FR-EXT-101/201 — suspect ranking + knowledge diff."""

from graphguide.extensions.knowledge_diff import knowledge_diff, knowledge_diff_markdown
from graphguide.extensions.suspect_ranker import SuspectRanker
from graphguide.graphify.loader import GraphLoader

WEIGHTS = {"centrality": 0.5, "proximity": 0.5}


def _graph():
    return GraphLoader.load("tests/fixtures/graph_sample.json")


def test_ranker_fuses_centrality_and_proximity():
    rows = SuspectRanker(_graph(), "to_str_params", WEIGHTS).rank(top=5)
    nodes = {r["node"] for r in rows}
    assert "to_str_params" in nodes  # the seed (distance 0) is included
    assert "task" in nodes  # central, close neighbour surfaces high
    assert any(r["distance"] == 0 for r in rows)
    # fusion: a highly-central neighbour can outrank the seed (not pure proximity)
    assert rows[0]["score"] >= rows[-1]["score"]


def test_ranker_missing_node_returns_empty():
    assert SuspectRanker(_graph(), "ghost", WEIGHTS).rank() == []


def test_ranker_markdown():
    md = SuspectRanker(_graph(), "to_str_params", WEIGHTS).to_markdown(top=3)
    assert "Ranked Suspects" in md and "Score" in md


def test_knowledge_diff(tmp_path):
    before = tmp_path / "before"
    after = tmp_path / "after"
    before.mkdir()
    after.mkdir()
    (before / "index.md").write_text("see [[a]]")
    (after / "index.md").write_text("see [[a]] and [[b]]")
    (after / "fix.md").write_text("the fix")
    diff = knowledge_diff(before, after)
    assert diff["pages_added"] == ["fix.md"]
    assert diff["pages_changed"] == ["index.md"]
    assert "b" in diff["links_added"]
    md = knowledge_diff_markdown(diff)
    assert "Pages added (1)" in md and "fix.md" in md
