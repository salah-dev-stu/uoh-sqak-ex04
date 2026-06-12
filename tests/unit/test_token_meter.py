"""FR-TOKEN-001 — token meter records, aggregates, persists, estimates."""

from pathlib import Path

from graphguide.shared.token_meter import (
    TokenMeter,
    TokenRecord,
    estimate_tokens,
    record_from_cost_json,
    record_from_usage,
)

FIXTURE = Path("tests/fixtures/cost_sample.json")


def test_record_auto_total():
    r = TokenRecord(mode="graph", call_type="llm", prompt_tokens=10, completion_tokens=5)
    assert r.total == 15


def test_meter_add_and_totals():
    m = TokenMeter()
    m.add(TokenRecord(mode="graph", call_type="llm", total=100, files_read=2))
    m.add(TokenRecord(mode="naive", call_type="llm", total=400, files_read=10))
    assert m.totals("graph")["tokens"] == 100
    assert m.totals("graph")["files_read"] == 2
    assert m.totals()["tokens"] == 500
    assert m.totals()["calls"] == 2


def test_to_from_json_roundtrip(tmp_path):
    m = TokenMeter()
    m.add(TokenRecord(mode="graph", call_type="llm", total=42, units_read=3))
    out = tmp_path / "m.json"
    m.to_json(out)
    loaded = TokenMeter.from_json(out)
    assert loaded.totals()["tokens"] == 42
    assert loaded.records[0].units_read == 3


def test_estimate_tokens_positive():
    assert estimate_tokens("hello world, this is a test") > 0


def test_record_from_usage_dict_and_obj():
    r1 = record_from_usage({"input_tokens": 30, "output_tokens": 7}, mode="graph")
    assert r1.total == 37 and r1.call_type == "llm"

    class U:
        input_tokens = 5
        output_tokens = 2

    r2 = record_from_usage(U(), mode="naive")
    assert r2.total == 7


def test_record_from_cost_json():
    r = record_from_cost_json(FIXTURE, mode="graph")
    assert r.total == 2000 and r.call_type == "subprocess"
