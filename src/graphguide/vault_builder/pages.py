"""Markdown page renderers for the Obsidian vault (FR-VAULT-002..005).

One base renderer (``render_page``) writes front-matter + wikilinks + tags so the
pages share a single rendering path (R2, no duplication). Specific pages compose it.
"""

from __future__ import annotations

from collections.abc import Iterable


def render_page(title: str, body: str, *, tags: Iterable[str] = (), page_type: str = "note") -> str:
    front = ["---", f"title: {title}", f"type: {page_type}"]
    if tags:
        front.append("tags: [" + ", ".join(tags) + "]")
    front.append("---")
    return "\n".join(front) + f"\n\n# {title}\n\n{body}\n"


def wikilink(name: str, label: str | None = None) -> str:
    return f"[[{name}|{label}]]" if label else f"[[{name}]]"


def index_md(components: list[str], extra_links: list[tuple[str, str]] | None = None) -> str:
    """Central nav hub. ``extra_links`` (path, label) are appended after the
    investigation discovers suspects/findings/fix — that growth is the H9 knowledge diff."""
    nav = "\n".join(f"- {wikilink(f'components/{c}', c)}" for c in components)
    invest = [
        f"- {wikilink('tests/test_task_to_str_to_task', 'failing test')}",
        f"- {wikilink('log', 'investigation log')}",
    ]
    invest += [f"- {wikilink(path, label)}" for path, label in (extra_links or [])]
    body = (
        "System map for the **luigi** codebase (reverse-engineered from the Graphify graph).\n\n"
        "## Navigation paths\n"
        "1. Start here → 2. "
        + wikilink("hot", "hot.md (bug-critical area)")
        + " → 3. component pages → 4. investigation.\n\n"
        "## Key components\n" + nav + "\n\n"
        "## Investigation\n" + "\n".join(invest) + "\n"
    )
    return render_page("Index — luigi system map", body, tags=["index"], page_type="hub")


def hot_md(focus: str = "Task.to_str_params serialization") -> str:
    body = (
        f"**Active focus:** {focus}\n\n"
        "The bug lives where `Task` serializes parameters. Read these first, in order:\n\n"
        f"- {wikilink('components/Task', 'Task')} — `to_str_params` / `from_str_params`\n"
        f"- {wikilink('components/Parameter', 'Parameter')} — `significant` flag, `serialize`/`parse`\n\n"
        "Hypothesis: `to_str_params` skips `significant=False` params; `from_str_params` expects all.\n"
    )
    return render_page("Hot — bug-critical context", body, tags=["hot"], page_type="focus")


def log_md(entries: list[str] | None = None) -> str:
    rows = entries or ["_Investigation starts here._"]
    body = "Query → finding → action trace.\n\n" + "\n".join(f"- {e}" for e in rows)
    return render_page("Investigation log", body, tags=["decision"], page_type="log")
