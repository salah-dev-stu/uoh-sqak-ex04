"""FR-UPG1-* — dense vault generator: selection, tags, rendering, no dangling."""

import re

from graphguide.graphify.loader import GraphLoader
from graphguide.vault_builder.graph_pages import (
    generate,
    node_tags,
    render_note,
    select_nodes,
    slug,
)

LINK = re.compile(r"\[\[([^\]]+)\]\]")


def _g():
    return GraphLoader.load("tests/fixtures/graph_sample.json")


def test_slug_is_filename_safe():
    assert slug("luigi/task.py::x") == "luigi_task_py__x"


def test_select_empty_graph():
    from graphguide.graphify.loader import CodeGraph

    assert select_nodes(CodeGraph([], []), "x", top_n=5, hops=2, cap=10) == []


def test_select_includes_bug_first_and_caps():
    sel = select_nodes(_g(), "to_str_params", top_n=3, hops=1, cap=5)
    assert sel[0] == "to_str_params"
    assert len(sel) <= 5


def test_select_khop_of_bug():
    sel = select_nodes(_g(), "to_str_params", top_n=0, hops=1, cap=99)
    assert "task" in sel and "parameter" in sel  # 1-hop neighbours of the bug node


def test_node_tags():
    assert set(node_tags("to_str_params", "to_str_params", {"task"}, set())) == {"bug", "fixed"}
    assert "hub" in node_tags("task", "to_str_params", {"task"}, set())
    assert "suspect" in node_tags("parameter", "to_str_params", set(), {"parameter"})


def test_render_note_links_tags_mermaid_dataview():
    md = render_note("task", "Task", ["parameter", "to_str_params"], ["hub"], 6)
    assert "[[parameter]]" in md and "[[to_str_params]]" in md
    assert "hub" in md and "community/6" in md
    assert "```mermaid" in md and "```dataview" in md


def test_generate_no_dangling_and_links_mirror_edges(tmp_path):
    g = _g()
    written = generate(
        g,
        tmp_path,
        bug_node="to_str_params",
        top_n=9,
        hops=2,
        cap=99,
        hub={"task"},
        suspects={"parameter"},
    )
    assert len(written) >= 5
    stems = {w[:-3] for w in written}
    for w in written:
        for target in LINK.findall((tmp_path / w).read_text()):
            assert target in stems  # no dangling
    # links mirror real graph edges (restricted to the selected set)
    nxg = g.to_networkx().to_undirected()
    task_note = (tmp_path / "task.md").read_text()
    for neighbour in nxg.neighbors("task"):
        if f"{neighbour}.md" in written:
            assert f"[[{neighbour}]]" in task_note
