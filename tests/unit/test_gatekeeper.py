"""R3 / FR-GATE — every external call is guarded and metered."""

import pytest

from graphguide.shared.gatekeeper import (
    ApiGatekeeper,
    BudgetExceededError,
    RateLimitExceededError,
)
from graphguide.shared.token_meter import TokenRecord, record_from_cost_json

LIMITS = {"requests_per_minute": 60, "token_budget": {"graph": 1000, "naive": 5000}}


def _gk(**over):
    limits = {**LIMITS, **over}
    return ApiGatekeeper(mode="graph", limits=limits)


def test_call_returns_result_and_records():
    gk = _gk()
    out = gk.call("file_read", lambda: 7, files_read=1, units_read=20)
    assert out == 7
    assert gk.meter.totals("graph")["calls"] == 1
    assert gk.meter.totals("graph")["files_read"] == 1


def test_budget_exceeded_raises():
    gk = _gk(token_budget={"graph": 50, "naive": 50})
    with pytest.raises(BudgetExceededError):
        gk.call("llm", lambda: None, est_tokens=200)


def test_rate_limit_raises():
    gk = _gk(requests_per_minute=2)
    gk.call("file_read", lambda: 1)
    gk.call("file_read", lambda: 1)
    with pytest.raises(RateLimitExceededError):
        gk.call("file_read", lambda: 1)


def test_record_from_result_llm_usage():
    gk = _gk()
    gk.call(
        "llm",
        lambda: {"usage": {"input_tokens": 100, "output_tokens": 40}},
        record_from_result=lambda res: TokenRecord(
            mode="graph",
            call_type="llm",
            prompt_tokens=res["usage"]["input_tokens"],
            completion_tokens=res["usage"]["output_tokens"],
        ),
    )
    assert gk.meter.totals("graph")["tokens"] == 140


def test_subprocess_cost_ingested(tmp_path):
    gk = _gk()
    cost = tmp_path / "cost.json"
    cost.write_text('{"total_tokens": 300}')
    gk.call(
        "subprocess",
        lambda: 0,
        record_from_result=lambda _r: record_from_cost_json(cost, mode="graph"),
    )
    assert gk.meter.totals("graph")["tokens"] == 300


def test_spend_report_aggregates():
    gk = _gk()
    gk.call("file_read", lambda: 1, files_read=1)
    gk.call("file_read", lambda: 1, files_read=1)
    report = gk.get_spend_report()
    assert report["graph"]["file_read"]["calls"] == 2
    assert report["graph"]["file_read"]["files_read"] == 2
