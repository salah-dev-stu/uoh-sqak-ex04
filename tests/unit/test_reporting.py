"""FR-TOKEN-003/004/006 — comparison maths + report regenerates from metrics JSON."""

import json
from pathlib import Path

import pytest

from graphguide.reporting import comparison, comparison_markdown, efficiency_pct


def test_efficiency_pct():
    assert efficiency_pct(100, 25) == 75.0
    assert efficiency_pct(0, 0) == 0.0


def test_identifies_root_cause():
    from graphguide.reporting import identifies_root_cause

    assert identifies_root_cause("The significant guard drops it; from_str_params then KeyErrors")
    assert identifies_root_cause("insignificant params are skipped (significant=False)")
    assert not identifies_root_cause("Looks like a parsing issue in the CLI")


def test_lim_markdown():
    from graphguide.reporting import lim_markdown

    results = [
        {
            "condition": "focused",
            "tokens": 900,
            "position": "n/a",
            "found": True,
            "excerpt": "significant guard",
        },
        {
            "condition": "buried-middle",
            "tokens": 50000,
            "position": "middle",
            "found": False,
            "excerpt": "not sure",
        },
    ]
    md = lim_markdown(results, "Middle degraded.")
    assert "Lost in the Middle" in md and "buried-middle" in md and "Middle degraded." in md


def test_comparison_and_markdown():
    g = {
        "tokens": 1000,
        "files_count": 2,
        "iterations": 1,
        "found_bug": True,
        "nodes_visited": ["a", "b"],
    }
    n = {"tokens": 8000, "files_count": 40, "iterations": 1, "found_bug": True}
    c = comparison(g, n)
    assert c["token_savings_pct"] == 87.5
    assert c["file_savings_pct"] == 95.0
    md = comparison_markdown(g, n)
    assert "Token-Savings Proof" in md and "87.5%" in md
    assert "Graph-guided" in md


def test_report_regenerates_from_committed_metrics():
    gm, nm = Path("reports/metrics/graph.json"), Path("reports/metrics/naive.json")
    if not (gm.exists() and nm.exists()):
        pytest.skip("metrics not generated in this checkout")
    md = comparison_markdown(json.loads(gm.read_text()), json.loads(nm.read_text()))
    assert "Token-Savings Proof" in md
