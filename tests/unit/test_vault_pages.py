"""FR-VAULT-002..005 — page renderers produce front-matter, links, tags."""

from graphguide.vault_builder.pages import hot_md, index_md, log_md, render_page, wikilink


def test_render_page_frontmatter_and_tags():
    page = render_page("Title", "Body text", tags=["a", "b"], page_type="note")
    assert page.startswith("---")
    assert "title: Title" in page and "tags: [a, b]" in page
    assert "# Title" in page and "Body text" in page


def test_wikilink():
    assert wikilink("Task") == "[[Task]]"
    assert wikilink("components/Task", "Task") == "[[components/Task|Task]]"


def test_index_lists_components_and_hot():
    page = index_md(["Task", "Parameter"])
    assert "[[components/Task|Task]]" in page
    assert "[[hot|hot.md (bug-critical area)]]" in page


def test_index_extra_links_appended():
    page = index_md(["Task"], extra_links=[("fix/x", "the fix")])
    assert "[[fix/x|the fix]]" in page


def test_hot_focuses_on_task_parameter():
    page = hot_md()
    assert "Task" in page and "Parameter" in page and "significant" in page


def test_log_renders():
    assert "Investigation log" in log_md()
