"""R4/R10 — config loads, has required keys, and no tunables are hardcoded in src."""

import re
from pathlib import Path

from graphguide.shared import config

SRC = Path("src/graphguide")


def test_each_config_loads():
    for name in ["graphify", "rate_limits", "agents", "tasks", "logging"]:
        assert isinstance(config.load(name), dict)


def test_required_keys_present():
    assert "cli_path" in config.get_graphify()
    rl = config.get_rate_limits()
    assert "token_budget" in rl and "max_files" in rl
    assert "model_id" in config.get_agents()
    assert "suspect_weights" in config.get_tasks()


def test_no_hardcoded_model_id_in_src():
    pattern = re.compile(r"claude-[a-z0-9-]+")
    offenders = [str(p) for p in SRC.rglob("*.py") if pattern.search(p.read_text(encoding="utf-8"))]
    assert not offenders, f"model id hardcoded in: {offenders}"
