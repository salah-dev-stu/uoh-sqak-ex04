"""Token meter (FR-TOKEN-001) — the measurement instrument behind the §5.5 proof.

Records every metered call as a :class:`TokenRecord`; the gatekeeper feeds it.
Also provides builders that turn an Anthropic usage object or a graphify
``cost.json`` into a record, plus a tiktoken-based estimator.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import tiktoken

from graphguide.shared import config


@dataclass
class TokenRecord:
    mode: str
    call_type: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total: int = 0
    files_read: int = 0
    units_read: int = 0
    ts: float = 0.0

    def __post_init__(self) -> None:
        if not self.total:
            self.total = self.prompt_tokens + self.completion_tokens


class TokenMeter:
    def __init__(self) -> None:
        self._records: list[TokenRecord] = []

    def add(self, record: TokenRecord) -> None:
        self._records.append(record)

    @property
    def records(self) -> list[TokenRecord]:
        return list(self._records)

    def totals(self, mode: str | None = None) -> dict[str, int]:
        recs = [r for r in self._records if mode is None or r.mode == mode]
        return {
            "tokens": sum(r.total for r in recs),
            "files_read": sum(r.files_read for r in recs),
            "units_read": sum(r.units_read for r in recs),
            "calls": len(recs),
        }

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps([asdict(r) for r in self._records], indent=2), encoding="utf-8"
        )

    @classmethod
    def from_json(cls, path: str | Path) -> TokenMeter:
        meter = cls()
        for item in json.loads(Path(path).read_text(encoding="utf-8")):
            meter.add(TokenRecord(**item))
        return meter


def estimate_tokens(text: str) -> int:
    """Estimate tokens for ``text`` using the configured encoding."""
    encoding = config.get_agents().get("token_encoding", "cl100k_base")
    return len(tiktoken.get_encoding(encoding).encode(text))


def record_from_usage(usage: Any, mode: str, ts: float = 0.0) -> TokenRecord:
    """Build a record from an Anthropic-style usage object/dict."""
    prompt = int(_attr(usage, "input_tokens"))
    completion = int(_attr(usage, "output_tokens"))
    return TokenRecord(
        mode=mode, call_type="llm", prompt_tokens=prompt, completion_tokens=completion, ts=ts
    )


def record_from_cost_json(path: str | Path, mode: str, ts: float = 0.0) -> TokenRecord:
    """Build a record from a graphify ``cost.json`` (subprocess token cost)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    total = int(
        data.get("total_tokens") or data.get("input_tokens", 0) + data.get("output_tokens", 0)
    )
    return TokenRecord(mode=mode, call_type="subprocess", total=total, ts=ts)


def _attr(obj: Any, name: str) -> Any:
    return obj.get(name, 0) if isinstance(obj, dict) else getattr(obj, name, 0)
