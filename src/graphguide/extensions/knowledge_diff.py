"""Extension 2 — knowledge before/after auto-diff (FR-EXT-201, H9).

Diffs the vault before vs after the investigation (pages added/changed, wikilinks
added) and emits the H9 knowledge-level before/after as a reproducible artifact.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_WIKILINK = re.compile(r"\[\[([^\]|]+)")


def _md_map(directory: str | Path) -> dict[str, str]:
    base = Path(directory)
    return {str(p.relative_to(base)): p.read_text(encoding="utf-8") for p in base.rglob("*.md")}


def _all_links(texts: dict[str, str]) -> set[str]:
    return {link for text in texts.values() for link in _WIKILINK.findall(text)}


def knowledge_diff(before_dir: str | Path, after_dir: str | Path) -> dict[str, Any]:
    before, after = _md_map(before_dir), _md_map(after_dir)
    shared = set(before) & set(after)
    return {
        "pages_added": sorted(set(after) - set(before)),
        "pages_removed": sorted(set(before) - set(after)),
        "pages_changed": sorted(k for k in shared if before[k] != after[k]),
        "links_added": sorted(_all_links(after) - _all_links(before)),
    }


def knowledge_diff_markdown(diff: dict[str, Any]) -> str:
    def fmt(items: list[str]) -> str:
        return ", ".join(f"`{i}`" for i in items) if items else "_none_"

    return (
        "# Knowledge-Level Before/After (H9)\n\n"
        "Auto-diff of the vault: `reports/vault_before/` -> `reports/vault_after/`.\n\n"
        f"**Pages added ({len(diff['pages_added'])}):** {fmt(diff['pages_added'])}\n\n"
        f"**Pages changed ({len(diff['pages_changed'])}):** {fmt(diff['pages_changed'])}\n\n"
        f"**Links added ({len(diff['links_added'])}):** {fmt(diff['links_added'])}\n"
    )
