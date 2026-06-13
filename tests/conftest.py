"""Shared test fixtures — a deterministic AgentContext factory (no API key)."""

import pytest

from graphguide.agent.context import AgentContext
from graphguide.agent.llm import MockLLM
from graphguide.agent.tools import CodeReader
from graphguide.graphify.loader import GraphLoader
from graphguide.shared.gatekeeper import ApiGatekeeper

LIMITS = {
    "requests_per_minute": 1000,
    "token_budget": {"graph": 10_000_000, "naive": 10_000_000},
}


def _reply(prompt: str) -> str:
    # 'f ' = fix prompt; else diagnose. Conclusive only once the bug node has been read.
    if prompt.startswith("f "):
        return "FIX: remove the significant guard so all params serialize"
    # graph-guided is conclusive once it reads the bug node; naive once it reads the bug's file.
    if "[node:to_str_params]" in prompt or "[file:luigi/task.py]" in prompt:
        return "ROOTCAUSE: to_str_params skips significant=False params -> KeyError on round-trip"
    return "INCONCLUSIVE: expand the frontier"


@pytest.fixture
def make_ctx():
    def _make(mode="graph", max_files=8, reader_root="target_repo/luigi"):
        gk = ApiGatekeeper(mode=mode, limits=LIMITS)
        graph = GraphLoader.load("tests/fixtures/graph_sample.json")
        reader = CodeReader(gk, reader_root, max_files=max_files)
        ctx = AgentContext(
            llm=MockLLM(_reply),
            reader=reader,
            vault_dir="vault",
            graph=graph,
            failing_test_node="to_str_params",
            max_files=max_files,
            prompts={"diagnose": "d {context}", "fix": "f {root_cause}"},
            seed_nodes=["task", "parameter"],
            max_rounds=5,
        )
        return ctx, gk

    return _make
