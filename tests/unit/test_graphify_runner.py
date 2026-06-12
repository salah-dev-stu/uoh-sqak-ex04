"""FR-GRAPH-001..004 — runner builds commands, routes via gatekeeper, collects outputs."""

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


def _fake_runner(calls):
    def run(args, **kw):
        calls.append(args)
        return FakeResult("OUT: " + " ".join(args))

    return run


def _runner(calls):
    gk = ApiGatekeeper(mode="graph", limits=LIMITS)
    return GraphifyRunner(gk, cfg=CFG, runner=_fake_runner(calls)), gk


def test_build_command_ast():
    runner, _ = _runner([])
    assert runner.build_command("ast") == ["graphify", "update", "target_repo/luigi"]


def test_build_command_deep():
    runner, _ = _runner([])
    assert runner.build_command("deep") == ["graphify", "target_repo/luigi", "--mode", "deep"]


def test_extract_routes_through_gatekeeper():
    calls: list = []
    runner, gk = _runner(calls)
    runner.extract("ast")
    assert calls == [["graphify", "update", "target_repo/luigi"]]
    assert gk.meter.totals("graph")["calls"] == 1


def test_collect_outputs(tmp_path):
    src = tmp_path / "graphify-out"
    src.mkdir()
    (src / "graph.json").write_text("{}")
    (src / "GRAPH_REPORT.md").write_text("# report")
    runner, _ = _runner([])
    copied = runner.collect_outputs(src, tmp_path / "dest")
    assert set(copied) == {"graph.json", "GRAPH_REPORT.md"}
    assert (tmp_path / "dest" / "graph.json").exists()
