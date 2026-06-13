"""FR-UPG1-007/008 — dense vault generates >=30 interlinked notes from the real graph."""

import re
from pathlib import Path

import pytest

from graphguide.graphify.loader import GraphLoader
from graphguide.vault_builder.graph_pages import generate

REAL_GRAPH = Path("reports/graph/graph.json")
LINK = re.compile(r"\[\[([^\]]+)\]\]")


@pytest.mark.skipif(not REAL_GRAPH.exists(), reason="real graph not committed")
def test_generate_30plus_interlinked_no_dangling(tmp_path):
    g = GraphLoader.load(REAL_GRAPH)
    written = generate(
        g,
        tmp_path,
        bug_node="luigi_task_task_to_str_params",
        top_n=40,
        hops=2,
        cap=120,
        god=set(),
        suspects=set(),
    )
    assert len(written) >= 30
    stems = {w[:-3] for w in written}
    total_links = 0
    for w in written:
        for target in LINK.findall((tmp_path / w).read_text()):
            assert target in stems  # every wikilink resolves
            total_links += 1
    assert total_links >= 30  # genuinely interlinked, not isolated notes
