"""FR-VAULT-007 (integration) — the committed vault has no dangling wikilinks."""

from pathlib import Path

import pytest

from graphguide.vault_builder.builder import check_links


def test_committed_vault_links_resolve():
    if not Path("vault/index.md").exists():
        pytest.skip("vault not built in this checkout")
    assert check_links("vault") == []
