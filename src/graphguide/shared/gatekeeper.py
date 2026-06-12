"""ApiGatekeeper (R3) — the single path for EVERY external call.

LLM completions, the ``graphify`` subprocess, and agent file reads all flow
through :meth:`ApiGatekeeper.call`. Pre-call it enforces the rate limit and the
remaining token budget (from ``config/rate_limits.json``); post-call it records
a :class:`TokenRecord` in the meter. Wired for real — not decorative.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from graphguide.shared import config
from graphguide.shared.token_meter import TokenMeter, TokenRecord


class BudgetExceededError(RuntimeError):
    """Raised when a call would exceed the mode's token budget."""


class RateLimitExceededError(RuntimeError):
    """Raised when the per-minute request rate is exceeded."""


class ApiGatekeeper:
    def __init__(
        self,
        mode: str = "graph",
        meter: TokenMeter | None = None,
        limits: dict[str, Any] | None = None,
    ) -> None:
        self.mode = mode
        self.meter = meter or TokenMeter()
        self._limits = limits or config.get_rate_limits()
        self._call_times: list[float] = []

    def _budget(self) -> int:
        return int(self._limits["token_budget"][self.mode])

    def _check_budget(self, est_tokens: int) -> None:
        spent = self.meter.totals(self.mode)["tokens"]
        if spent + est_tokens > self._budget():
            raise BudgetExceededError(
                f"{self.mode}: {spent}+{est_tokens} > budget {self._budget()}"
            )

    def _check_rate(self, now: float) -> None:
        self._call_times = [t for t in self._call_times if now - t < 60.0]
        if len(self._call_times) >= int(self._limits["requests_per_minute"]):
            raise RateLimitExceededError(f"> {self._limits['requests_per_minute']} req/min")

    def call(
        self,
        kind: str,
        fn: Callable[[], Any],
        *,
        record_from_result: Callable[[Any], TokenRecord] | None = None,
        est_tokens: int = 0,
        files_read: int = 0,
        units_read: int = 0,
    ) -> Any:
        """Run ``fn`` under rate/budget guard and record its token cost."""
        now = time.time()
        self._check_rate(now)
        self._check_budget(est_tokens)
        self._call_times.append(now)
        result = fn()
        if record_from_result is not None:
            record = record_from_result(result)
            record.mode = self.mode
        else:
            record = TokenRecord(
                mode=self.mode,
                call_type=kind,
                total=est_tokens,
                files_read=files_read,
                units_read=units_read,
            )
        if record.ts == 0.0:
            record.ts = now
        self.meter.add(record)
        return result

    def get_spend_report(self) -> dict[str, dict[str, dict[str, int]]]:
        report: dict[str, dict[str, dict[str, int]]] = {}
        for r in self.meter.records:
            bucket = report.setdefault(r.mode, {}).setdefault(
                r.call_type, {"tokens": 0, "calls": 0, "files_read": 0}
            )
            bucket["tokens"] += r.total
            bucket["calls"] += 1
            bucket["files_read"] += r.files_read
        return report
