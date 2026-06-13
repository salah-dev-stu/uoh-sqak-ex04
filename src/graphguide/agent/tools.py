"""Budgeted, metered code reader (FR-AGENT-007).

Reads only requested files (never the whole repo), routes through the Gatekeeper,
records token cost (so file context counts toward the token comparison), and caps
the number of files per the mode's ``max_files`` budget.
"""

from __future__ import annotations

from pathlib import Path

from graphguide.constants import KIND_FILE_READ
from graphguide.shared.gatekeeper import ApiGatekeeper
from graphguide.shared.token_meter import TokenRecord, estimate_tokens


class FileBudgetExceededError(RuntimeError):
    """Raised when more than ``max_files`` reads are attempted."""


class CodeReader:
    def __init__(
        self, gatekeeper: ApiGatekeeper, root: str, max_files: int, read_chars: int = 4000
    ) -> None:
        self._gk = gatekeeper
        self._root = Path(root)
        self._max = int(max_files)
        self._read_chars = int(read_chars)
        self._count = 0
        self._cache: dict[str, str] = {}

    @property
    def count(self) -> int:
        return self._count

    def read(self, rel_path: str, max_chars: int | None = None) -> str:
        max_chars = max_chars or self._read_chars
        if rel_path in self._cache:
            return self._cache[rel_path]  # already paid for; no re-meter, no budget hit
        if self._count >= self._max:
            raise FileBudgetExceededError(f"file budget {self._max} exhausted")
        path = self._root / rel_path

        def _run() -> str:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]

        text = self._gk.call(
            KIND_FILE_READ,
            _run,
            record_from_result=lambda t: TokenRecord(
                mode=self._gk.mode,
                call_type=KIND_FILE_READ,
                prompt_tokens=estimate_tokens(t),
                files_read=1,
                units_read=len(t),
            ),
        )
        self._count += 1
        self._cache[rel_path] = text
        return text
