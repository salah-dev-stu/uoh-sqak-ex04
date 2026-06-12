"""FR-VAULT-001/007 — builder writes pages; link-integrity check works."""

from graphguide.vault_builder.builder import VaultBuilder, check_links


def test_build_writes_core_pages(tmp_path):
    vb = VaultBuilder(tmp_path)
    written = vb.build(["Task", "Parameter"])
    assert set(written) == {"index.md", "hot.md", "log.md"}
    assert (tmp_path / "index.md").exists()


def test_write_component(tmp_path):
    vb = VaultBuilder(tmp_path)
    rel = vb.write_component("Task", "The central class.")
    assert rel == "components/Task.md"
    assert "The central class." in (tmp_path / "components/Task.md").read_text()


def test_check_links_clean(tmp_path):
    vb = VaultBuilder(tmp_path)
    vb.build(["Task", "Parameter"])
    vb.write_component("Task", "body")
    vb.write_component("Parameter", "body")
    vb.write_page("tests/test_task_to_str_to_task.md", "Failing test", "body")
    assert check_links(tmp_path) == []


def test_check_links_detects_dangling(tmp_path):
    vb = VaultBuilder(tmp_path)
    vb.write_page("a.md", "A", "see [[ghost]] here")
    assert ("a.md", "ghost") in check_links(tmp_path)
