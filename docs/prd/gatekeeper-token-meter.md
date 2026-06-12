# PRD — Gatekeeper + Token Meter

> Per-mechanism PRD for `prd.md` §5.9 (Gatekeeper) + §5.6 (Token Meter).
> **Component**: `src/graphguide/shared/gatekeeper.py` + `src/graphguide/shared/token_meter.py`
> **Package** `graphguide` · **Version** 1.00 · **Course** 203.3763 — University of Haifa · Dr. Yoram Segal
> **Group** `uoh-sqak` — Salah Qadah (323039974) + Andalus Kalash (211435797)
> **Traceability** FR-GATE-001..003, FR-TOKEN-001 · **Rubric** R3, R4, R10 · **Gates** H6
> Tasks for this mechanism append to the global `Todo.md` (P1 Shared/Gatekeeper, T061–T120).

---

## 1. Overview

`ApiGatekeeper` is the single chokepoint through which **every** external call in the system
passes: LLM completions (Claude / MockLLM), the `graphify` CLI subprocess, and the agent's
budgeted file reads. There is exactly one entry method —
`ApiGatekeeper.call(kind, fn, *, est_tokens=…)` — and nothing in `src/` may perform a raw
`subprocess.*`, raw `anthropic`/LLM-client, or unbudgeted file read outside it.

This is deliberately wired for real, not decorative. The **HW3 audit lesson** was that a
Gatekeeper which only fed `get_spend_report()` (a cosmetic accounting wrapper, while the real
calls happened elsewhere) does not satisfy R3. Here the Gatekeeper is the *only* code path, and
a `test_no_bypass` greps `src/` to prove it.

The **Token Meter** (`token_meter.py`) is the recording half of the same mechanism: each
mediated call produces a `TokenRecord`, and `get_spend_report()` aggregates those records
**per mode** (`naive` vs `graph`). That aggregate is the measurement instrument for the §5.5
token-savings proof (FR-TOKEN-002..006) — the numbers in `reports/token_comparison.md` come
out of this meter, not by hand.

---

## 2. Inputs / Outputs

| Field | Type | Description |
|---|---|---|
| **Input** `kind` | `CallKind` (enum: `LLM`, `GRAPHIFY`, `FILE_READ`) | Selects rate-limit/budget bucket + how tokens are accounted |
| **Input** `fn` | `Callable[..., T]` | The actual I/O to invoke (LLM client, `subprocess.run`, file read) |
| **Input** `est_tokens` | `int` (keyword-only) | Pre-call token estimate (tiktoken / unit count) for the budget pre-check |
| **Input** `mode` | `str` (`"naive"` \| `"graph"`) | Active run mode; stamped onto the `TokenRecord` |
| **Output** | `T` | Return value of `fn`, unchanged |
| **Side-effect** | `TokenRecord` | Appended to the in-memory ledger and to `reports/metrics/<mode>.json` |
| **Side-effect** | Log line | Structured JSON via `logging_config.py` (`kind`, `mode`, `total`, `latency_ms`) |

### TokenRecord schema (consumed by the §5.5 report)

```json
{
  "mode": "graph",
  "call_type": "LLM",
  "prompt_tokens": 1840,
  "completion_tokens": 260,
  "total": 2100,
  "files_read": 0,
  "units_read": 0,
  "ts": "2026-06-13T10:22:41Z"
}
```

---

## 3. Functional Requirements

### Gatekeeper (FR-GATE-*)

1. **FR-GATE-001** — One `ApiGatekeeper.call(kind, fn, *, est_tokens=…)` is the **only** path
   for every external call: LLM completions, the `graphify` subprocess, and agent file reads.
   No subpackage (`graphify/`, `agent/`, `extensions/`, `vault_builder/`) may invoke
   `subprocess.*`, an LLM client, or an unbudgeted file read directly — they go through
   `call()`. This is enforced mechanically (see FR-GATE-003 / `test_no_bypass`).

2. **FR-GATE-002** — `call()` enforces limits **before** dispatch and records **after** dispatch:
   - **Pre-call**: read the per-`kind` rate limit (sliding-window RPM) and the remaining
     token budget for the active mode from `config/rate_limits.json`; if `est_tokens` would
     cross the configured hard cap, raise `BudgetExceededError` *before* spending; if the RPM
     window is full, block up to `max_wait_seconds` then raise `RateLimitError`. No numeric
     limit is hardcoded in `gatekeeper.py` (R4, R10).
   - **Post-call**: derive the real cost per `kind` (see FR-TOKEN-001), build a `TokenRecord`,
     append it to the ledger, persist it, and update the per-mode cumulative counters.

3. **FR-GATE-003** — `get_spend_report()` returns aggregated usage per mode
   (`{mode: {calls, prompt, completion, total, files_read, units_read}}`). A
   `test_no_bypass` greps `src/` (excluding `gatekeeper.py` itself) and asserts there are
   **zero** raw `subprocess.`, `anthropic`, or direct LLM-client call sites — proving nothing
   bypasses the Gatekeeper. This guards against the HW3 decorative-gatekeeper regression.

### Token Meter (FR-TOKEN-*)

4. **FR-TOKEN-001** — The token meter records, per mediated call, a `TokenRecord` with
   `{mode, call_type, prompt_tokens, completion_tokens, total, files_read, units_read, ts}`.
   Cost derivation **per `kind`**:
   - **`LLM`** — read `prompt_tokens` / `completion_tokens` from the API `usage` object when
     present; otherwise fall back to a **tiktoken** estimate over prompt+completion text.
   - **`GRAPHIFY`** — ingest the subprocess's reported cost from graphify's `cost.json`
     (written by the `graphify` run into `reports/graph/cost.json`); record it as the call's
     token total (`call_type="GRAPHIFY"`).
   - **`FILE_READ`** — count the read as a **unit** (`units_read += 1`, `files_read += 1`);
     `total` reflects the tiktoken estimate of the bytes actually read (the budgeted span,
     never the whole repo).

---

## 4. Non-Functional Requirements

- **NFR-GTM-01 Real wiring, not decorative** — every external call site in `src/` resolves to
  exactly one `ApiGatekeeper.call(...)`; `test_no_bypass` is part of the suite, not optional.
- **NFR-GTM-02 Config-driven** — all RPM, token budgets (per mode), and wait/cap values live
  in `config/rate_limits.json`; `gatekeeper.py` contains no tunable literals (R4, R10).
- **NFR-GTM-03 Reproducible metrics** — `TokenRecord`s persist to `reports/metrics/<mode>.json`
  so the grader reconstructs the §5.5 numbers from committed artifacts, without an API key
  and without running the live agent (grader Path D).
- **NFR-GTM-04 Determinism under MockLLM** — when the injected client is `MockLLM`,
  token counts are derived from the scripted response's `usage` (or tiktoken on its text), so
  the meter is fully deterministic in CI.
- **NFR-GTM-05 File-size + lint** — `gatekeeper.py` and `token_meter.py` each ≤150 logical
  lines (R7); `ruff check` = 0 (R8). Split accounting helpers into `token_meter.py` to stay
  under the cap.

---

## 5. Configuration

| Key | File | Description |
|---|---|---|
| `kinds.LLM.requests_per_minute` | `config/rate_limits.json` | Sliding-window RPM for LLM calls |
| `kinds.LLM.tokens_per_mode` | `config/rate_limits.json` | Per-mode token budget (naive vs graph) |
| `kinds.GRAPHIFY.requests_per_minute` | `config/rate_limits.json` | RPM for `graphify` subprocess calls |
| `kinds.FILE_READ.max_files` | `config/rate_limits.json` | Max budgeted file reads per run |
| `kinds.*.warn_at_percent` | `config/rate_limits.json` | WARNING threshold (% of budget) |
| `kinds.*.hard_cap_percent` | `config/rate_limits.json` | `BudgetExceededError` threshold |
| `kinds.*.max_wait_seconds` | `config/rate_limits.json` | Max rate-limit block before `RateLimitError` |
| `metrics_dir` | `config/rate_limits.json` | Where `<mode>.json` ledgers are written |

---

## 6. Acceptance Criteria

- [ ] `ApiGatekeeper.call(CallKind.LLM, fn, est_tokens=100)` with a `MockLLM` returning
      `usage.total_tokens = 100` appends a `TokenRecord` whose `total == 100`.
- [ ] A `GRAPHIFY` call ingests `reports/graph/cost.json` and records its reported cost as the
      call's token total.
- [ ] A `FILE_READ` call increments `files_read` and `units_read` by exactly 1 and records the
      budgeted-span token estimate (not the whole file).
- [ ] Pre-call: when `est_tokens` crosses `hard_cap_percent` of the mode budget,
      `BudgetExceededError` is raised **before** `fn` runs (asserted: `fn` not called).
- [ ] Pre-call: when the RPM window is full, the call blocks then raises `RateLimitError` past
      `max_wait_seconds`.
- [ ] `get_spend_report()` returns per-mode aggregates with keys
      `{calls, prompt, completion, total, files_read, units_read}` for both `naive` and `graph`.
- [ ] `test_no_bypass` greps `src/` and finds **zero** raw `subprocess.`/`anthropic`/LLM-client
      call sites outside `gatekeeper.py` (the HW3 regression guard).
- [ ] Per-mode ledgers exist at `reports/metrics/naive.json` and `reports/metrics/graph.json`
      and reproduce the token-comparison numbers without a live run.
- [ ] No numeric limit is hardcoded in `gatekeeper.py`; all come from `config/rate_limits.json`.
- [ ] `ruff check` = 0; both files ≤150 logical lines.
