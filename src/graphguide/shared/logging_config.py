"""Configure logging from ``config/logging.json`` (FR-LOG-001)."""

from __future__ import annotations

import logging
import logging.config

from graphguide.shared import config


def configure() -> None:
    """Apply the logging configuration declared in ``config/logging.json``."""
    logging.config.dictConfig(config.load("logging"))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
