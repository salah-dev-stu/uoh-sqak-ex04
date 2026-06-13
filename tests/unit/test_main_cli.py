"""FR-CLI-001 — every subcommand dispatches to the SDK (no side effects, no key)."""

import pytest

from graphguide.main import main


class _FakeGG:
    def version(self):
        return "1.03"

    def graphify(self):
        return ["graph.json"]

    def build_vault(self):
        return ["index.md", "hot.md", "log.md"]

    def build_graph_vault(self):
        return ["nodes/luigi_task_task.md", "nodes/luigi_task_task_to_str_params.md"]

    def investigate(self, mode):
        return {"mode": mode, "found_bug": True, "files_count": 1}

    def rank_suspects(self):
        return [{"node": "luigi_task_task_to_str_params", "score": 0.5}]

    def knowledge_diff(self):
        return {"pages_added": ["fix/to_str_params-fix.md"]}

    def token_report(self):
        return "Token-Savings Proof ..."


@pytest.mark.parametrize(
    "argv",
    [
        ["version"],
        ["graphify"],
        ["vault"],
        ["vault", "--graph"],
        ["investigate", "--mode", "graph"],
        ["investigate", "--mode", "naive"],
        ["suspects"],
        ["knowledge-diff"],
        ["token-report"],
    ],
)
def test_subcommands_dispatch(argv, capsys):
    assert main(argv, gg=_FakeGG()) == 0
    assert capsys.readouterr().out.strip()


def test_version_prints_version(capsys):
    main(["version"], gg=_FakeGG())
    assert "1.03" in capsys.readouterr().out
