"""FR-AGENT core — state, LLM clients, budgeted reader, context."""

import pytest

from graphguide.agent.context import AgentContext
from graphguide.agent.llm import LLMClient, MockLLM
from graphguide.agent.state import initial_state
from graphguide.agent.tools import CodeReader, FileBudgetExceededError
from graphguide.graphify.loader import GraphLoader
from graphguide.shared.gatekeeper import ApiGatekeeper

LIMITS = {"requests_per_minute": 1000, "token_budget": {"graph": 10_000_000, "naive": 10_000_000}}


def _gk(mode="graph"):
    return ApiGatekeeper(mode=mode, limits=LIMITS)


# --- state ---
def test_initial_state():
    st = initial_state("find bug", "graph")
    assert st["task"] == "find bug" and st["mode"] == "graph"
    assert st["nodes_visited"] == [] and st["iterations"] == 0


# --- LLM ---
class _Usage:
    input_tokens = 50
    output_tokens = 20


class _Block:
    def __init__(self, text):
        self.text = text


class _Resp:
    content = [_Block("root cause: significant guard drops insignificant param")]
    usage = _Usage()


class _Client:
    def create(self, **kw):
        return _Resp()

    @property
    def messages(self):
        return self


def test_llmclient_completes_and_meters():
    gk = _gk()
    client = LLMClient(gk, cfg={"model_id": "m", "max_tokens": 50}, client_factory=_Client)
    out = client.complete("diagnose this")
    assert "root cause" in out
    assert gk.meter.totals("graph")["tokens"] == 70


def test_mockllm_dict_and_callable():
    m = MockLLM({"diagnose": "the significant guard"})
    assert "significant" in m.complete("please diagnose the bug")
    assert m.complete("unrelated") == "no scripted response"
    assert MockLLM(lambda p: p.upper()).complete("hi") == "HI"


# --- tools ---
def test_reader_reads_and_meters(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n")
    gk = _gk()
    reader = CodeReader(gk, tmp_path, max_files=2)
    text = reader.read("a.py")
    assert "def f" in text and reader.count == 1
    assert gk.meter.totals("graph")["files_read"] == 1
    assert gk.meter.totals("graph")["tokens"] > 0


def test_reader_budget_exceeded(tmp_path):
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "b.py").write_text("y")
    reader = CodeReader(_gk(), tmp_path, max_files=1)
    reader.read("a.py")
    reader.read("a.py")  # cached re-read is free (no budget hit)
    with pytest.raises(FileBudgetExceededError):
        reader.read("b.py")  # a distinct file exceeds the budget


# --- context ---
def _ctx():
    graph = GraphLoader.load("tests/fixtures/graph_sample.json")
    return AgentContext(
        llm=None,
        reader=None,
        vault_dir="vault",
        graph=graph,
        failing_test_node="to_str_params",
        max_files=8,
        prompts={"diagnose": "ctx={context}"},
    )


def test_context_neighbors_and_source_files():
    ctx = _ctx()
    nbrs = ctx.neighbors("to_str_params")
    assert "task" in nbrs and "parameter" in nbrs
    files = ctx.source_files(["to_str_params", "parameter"])
    assert "luigi/task.py" in files and "luigi/parameter.py" in files
    assert ctx.neighbors("nonexistent_node") == []


def test_context_prompt_format():
    assert _ctx().prompt("diagnose", context="X") == "ctx=X"
