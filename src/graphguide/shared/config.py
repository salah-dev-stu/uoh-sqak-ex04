"""JSON config loader (R4, R10) — every tunable lives in ``config/``, never in code.

Resolution order for the config directory: the ``GRAPHGUIDE_CONFIG_DIR`` env var
if set, else ``<repo-root>/config``. Files are tiny; we read on demand.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "config"


def config_dir() -> Path:
    """Directory holding the JSON config files."""
    return Path(os.environ.get("GRAPHGUIDE_CONFIG_DIR", str(_DEFAULT_DIR)))


def load(name: str) -> dict[str, Any]:
    """Load ``config/<name>.json`` as a dict."""
    path = config_dir() / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_graphify() -> dict[str, Any]:
    return load("graphify")


def get_rate_limits() -> dict[str, Any]:
    return load("rate_limits")


def get_agents() -> dict[str, Any]:
    return load("agents")


def get_tasks() -> dict[str, Any]:
    return load("tasks")


def config_version() -> str:
    """The version mirror held in config (asserted == code VERSION by a test)."""
    return str(load("agents")["version"])
