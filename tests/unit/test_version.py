"""R5 — version is single-source and config mirrors code."""

import graphguide
from graphguide.shared import config, version


def test_code_version_is_1_00():
    assert graphguide.VERSION == "1.00"


def test_dunder_matches_version():
    assert version.__version__ == version.VERSION == "1.00"


def test_config_mirrors_code_version():
    assert config.config_version() == graphguide.VERSION
