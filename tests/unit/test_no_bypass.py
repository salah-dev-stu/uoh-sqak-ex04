"""FR-GATE-003 — no external call bypasses the gatekeeper.

Heuristic: only designated wrapper modules may reference the raw subprocess or
Anthropic client APIs, and those wrappers must route through the gatekeeper.
"""

from pathlib import Path

SRC = Path("src/graphguide")
ALLOWED_WRAPPERS = {"runner.py", "llm.py"}
EXTERNAL_MARKERS = ("subprocess.run", "subprocess.Popen", "Anthropic(", "anthropic.Anthropic")


def test_no_external_call_bypasses_gatekeeper():
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in EXTERNAL_MARKERS):
            assert path.name in ALLOWED_WRAPPERS, (
                f"{path} makes a raw external call but is not an allowed wrapper"
            )
            assert "gatekeeper" in text.lower() or "Gatekeeper" in text, (
                f"{path} touches an external API without routing through the gatekeeper"
            )
