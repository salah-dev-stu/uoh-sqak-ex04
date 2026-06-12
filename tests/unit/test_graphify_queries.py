"""FR-GRAPH-006 — offline query wrappers build args, return stdout, are metered."""

from graphguide.graphify.queries import GraphQueries
from graphguide.graphify.runner import GraphifyRunner
from graphguide.shared.gatekeeper import ApiGatekeeper

CFG = {
    "cli_path": "graphify",
    "target_path": "target_repo/luigi",
    "out_dir": "reports/graph",
    "query_budget": 2000,
}
LIMITS = {"requests_per_minute": 60, "token_budget": {"graph": 100000, "naive": 100000}}


class FakeResult:
    def __init__(self, stdout: str) -> None:
        self.stdout = stdout


def _queries(calls):
    def run(args, **kw):
        calls.append(args)
        return FakeResult("OUT: " + " ".join(args))

    gk = ApiGatekeeper(mode="graph", limits=LIMITS)
    runner = GraphifyRunner(gk, cfg=CFG, runner=run)
    return GraphQueries(runner, cfg=CFG), gk


def test_query_builds_args_and_budget():
    calls: list = []
    q, gk = _queries(calls)
    out = q.query("where is the bug?", budget=500)
    assert "query" in calls[0] and "--budget" in calls[0] and "500" in calls[0]
    assert out.startswith("OUT:")
    assert gk.meter.records[0].units_read == 500


def test_query_default_budget():
    calls: list = []
    q, _ = _queries(calls)
    q.query("q")
    assert "2000" in calls[0]


def test_explain_path_affected():
    calls: list = []
    q, _ = _queries(calls)
    assert q.explain("task").startswith("OUT:")
    assert q.path("task", "parameter").startswith("OUT:")
    assert q.affected("task").startswith("OUT:")
    assert [c[1] for c in calls] == ["explain", "path", "affected"]
