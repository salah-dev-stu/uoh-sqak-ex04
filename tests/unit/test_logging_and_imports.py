"""FR-LOG-001 + import smoke (covers package/subpackage __init__ + constants)."""

import importlib

from graphguide import constants
from graphguide.shared import logging_config


def test_configure_and_log():
    logging_config.configure()
    logging_config.get_logger("graphguide").info("logging configured")


def test_constants_present():
    assert constants.GRAPH_JSON == "graph.json"
    assert constants.MODE_NAIVE == "naive"
    assert constants.MODE_GRAPH == "graph"
    assert constants.KIND_LLM == "llm"


def test_subpackages_import():
    for sub in ["sdk", "graphify", "agent", "extensions", "shared", "vault_builder"]:
        importlib.import_module(f"graphguide.{sub}")
