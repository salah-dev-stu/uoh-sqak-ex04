"""VaultBuilder (FR-VAULT-001..007) — build & validate the Obsidian vault.

Derives the vault from the Graphify graph (no graphify ``obsidian/`` dir is
produced by AST mode, so we curate directly from ``graph.json``). One write path
keeps pages consistent; ``check_links`` guards against dangling wikilinks.
"""

from __future__ import annotations

import re
from pathlib import Path

from graphguide.vault_builder.pages import hot_md, index_md, log_md, render_page

_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")


class VaultBuilder:
    def __init__(self, vault_dir: str | Path = "vault") -> None:
        self.vault = Path(vault_dir)

    def _write(self, rel: str, text: str) -> str:
        path = self.vault / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def build(
        self, components: list[str], extra_links: list[tuple[str, str]] | None = None
    ) -> list[str]:
        return [
            self._write("index.md", index_md(components, extra_links)),
            self._write("hot.md", hot_md()),
            self._write("log.md", log_md()),
        ]

    def write_component(self, name: str, body: str) -> str:
        return self._write(
            f"components/{name}.md",
            render_page(name, body, tags=["component"], page_type="component"),
        )

    def write_page(self, rel: str, title: str, body: str, tags: list[str] | None = None) -> str:
        return self._write(rel, render_page(title, body, tags=tags or []))


def check_links(vault_dir: str | Path) -> list[tuple[str, str]]:
    """Return (page, target) pairs for wikilinks whose target page is missing."""
    vault = Path(vault_dir)
    md_files = list(vault.rglob("*.md"))
    known = {str(p.relative_to(vault).with_suffix("")) for p in md_files}
    known |= {p.stem for p in md_files}
    dangling: list[tuple[str, str]] = []
    for path in md_files:
        for target in _WIKILINK.findall(path.read_text(encoding="utf-8")):
            if target.strip() not in known:
                dangling.append((str(path.relative_to(vault)), target.strip()))
    return dangling
