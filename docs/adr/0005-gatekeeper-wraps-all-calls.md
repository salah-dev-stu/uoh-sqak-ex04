# ADR-0005: One Gatekeeper Wraps and Meters Every External Call

**Status:** Accepted
**Date:** 2026-06-13
**Authors:** Salah Qadah, Andalus Kalash (pair `uoh-sqak`)
**Course:** 203.3763 — Orchestration of AI Agents, University of Haifa · Dr. Yoram Segal
**Relates to:** `prd.md` §5.9 (FR-GATE-001..003), §5.6 (FR-TOKEN-001); `Plan.md` §4
**Component:** `src/graphguide/shared/gatekeeper.py` + `src/graphguide/shared/token_meter.py`

---

## Context

Two forces collide on this mechanism:

- **Rubric R3** requires that every external call (LLM, graph build, file read) route through a
  **Gatekeeper**, wired for real and not decorative.
- **The HW3 audit finding**: in HW3 the Gatekeeper existed but was effectively decorative — it
  was wired only as an accounting wrapper feeding `get_spend_report()`, while the *actual*
  external calls were made directly by the tools. The audit flagged this as not satisfying R3.

This project independently *needs* a precise, trustworthy token meter: the §5.5 deliverable is a
**measured** token-savings proof comparing naive raw-file reading against graph-guided
investigation. If LLM calls, the `graphify` subprocess, and file reads are scattered across the
code, there is no single, credible place to count tokens — and the comparison becomes
hand-waving, which the rubric explicitly penalizes (FR-TOKEN-004/005).

So the same design pressure comes from two directions: compliance (R3) and measurement (§5.5).
One mechanism should answer both.

---

## Decision

There is exactly **one** `ApiGatekeeper`, and a single method
`ApiGatekeeper.call(kind, fn, *, est_tokens=…)` is the **only** path for **all** external calls:

1. **LLM completions** (Claude / injected `MockLLM`) — `kind=LLM`.
2. **The `graphify` subprocess** — `kind=GRAPHIFY`.
3. **Agent file reads** (budgeted source spans) — `kind=FILE_READ`.

Every `call()`:

- **Pre-call** enforces, from `config/rate_limits.json`, the per-`kind` rate limit and the
  remaining per-mode token budget; over-budget raises before any spend.
- **Post-call** records a `TokenRecord`
  `{mode, call_type, prompt_tokens, completion_tokens, total, files_read, units_read, ts}`:
  LLM tokens from the API `usage` (or a tiktoken estimate), graphify tokens ingested from
  graphify's `cost.json`, and file reads counted as units.

`get_spend_report()` aggregates the records **per mode** (`naive` vs `graph`). A
`test_no_bypass` greps `src/` and asserts there are zero raw `subprocess.` / `anthropic` /
direct LLM-client call sites outside the Gatekeeper.

---

## Consequences

**Positive**

- **R3 satisfied for real.** Because `call()` is the only path and `test_no_bypass` proves it,
  the gatekeeper cannot regress into the HW3 decorative state without turning the suite red.
- **The token meter doubles as the §5.5 measurement instrument.** Since *every* metered call
  flows through one place, the per-mode aggregates in `get_spend_report()` are exactly the
  numbers reported in `reports/token_comparison.md` (FR-TOKEN-002..006) — measured, not
  estimated. Naive vs graph-guided become directly comparable on tokens, files/units read, and
  iterations.
- **Reproducible without an API key.** `TokenRecord`s persist to `reports/metrics/<mode>.json`,
  so the grader reconstructs the proof from committed artifacts (Path D), no live agent run.
- **Single enforcement point** for rate limits, budgets, and structured logging; budgets stay
  in config (R4, R10), not code.

**Negative / costs**

- One layer of indirection on every external call. Acceptable: these are I/O-bound (network,
  subprocess, disk) where the wrapper overhead is negligible.
- The `est_tokens` pre-check is an estimate; the recorded post-call total is the source of
  truth. Tests assert on the recorded total, not the estimate.

**Guard against regression**

- `test_no_bypass` is a standing grep test. Any future code that calls `subprocess`, an LLM
  client, or an unbudgeted file read directly will fail it — keeping the mechanism wired for
  real for the life of the repo.

---

## Status

Accepted. Implemented in P1 (Shared/Gatekeeper, Todo.md T061–T120); the per-mechanism PRD is
`docs/prd/gatekeeper-token-meter.md`.
