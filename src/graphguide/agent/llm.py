"""LLM clients (FR-AGENT-003) — real Anthropic client (via Gatekeeper) + MockLLM.

The agent depends only on a ``.complete(prompt) -> str`` interface, so tests
inject :class:`MockLLM` and need no API key (grader Path D).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from graphguide.constants import KIND_LLM
from graphguide.shared import config
from graphguide.shared.gatekeeper import ApiGatekeeper
from graphguide.shared.token_meter import record_from_usage


def _default_anthropic() -> Any:  # pragma: no cover - needs network + API key
    import anthropic

    return anthropic.Anthropic()


class LLMClient:
    def __init__(
        self,
        gatekeeper: ApiGatekeeper,
        cfg: dict[str, Any] | None = None,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._gk = gatekeeper
        self._cfg = cfg or config.get_agents()
        self._factory = client_factory or _default_anthropic

    def complete(self, prompt: str) -> str:
        client = self._factory()

        def _run() -> Any:
            return client.messages.create(
                model=self._cfg["model_id"],
                max_tokens=int(self._cfg["max_tokens"]),
                messages=[{"role": "user", "content": prompt}],
            )

        resp = self._gk.call(
            KIND_LLM,
            _run,
            record_from_result=lambda r: record_from_usage(r.usage, self._gk.mode),
        )
        return _text(resp)


def _text(resp: Any) -> str:
    return "".join(getattr(b, "text", "") for b in getattr(resp, "content", []))


class MockLLM:
    """Deterministic LLM for tests: scripted dict (substr -> reply) or a callable."""

    def __init__(self, scripted: dict[str, str] | Callable[[str], str]) -> None:
        self._scripted = scripted

    def complete(self, prompt: str) -> str:
        if callable(self._scripted):
            return self._scripted(prompt)
        for key, value in self._scripted.items():
            if key in prompt:
                return value
        return "no scripted response"
