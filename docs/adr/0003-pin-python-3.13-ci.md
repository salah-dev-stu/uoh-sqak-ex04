# ADR 0003 — Pin GitHub Actions CI to Python 3.13

> **Project** `graphguide` (EX04) · **Course** 203.3763 · **Group** `uoh-sqak`
> **Relates to** `prd.md` NFR-CI-001 (R13) · `Plan.md` §11 (CI / Tooling), §15 (ADRs)
> **Companion ADRs** 0001-use-real-graphify-tool · 0002-langgraph-over-crewai · 0004-ast-fallback · 0005-gatekeeper-wraps-all-calls

## Status

**Accepted.**

## Context

HW3 (same pair, CrewAI + LaTeX) shipped a GitHub Actions workflow that broke on the runner's **default Python**: CrewAI bundled a **pydantic-v1** lineage that failed to build/import on the runner's then-default **Python 3.14**, turning the CI red even though the project itself was correct. A red CI fails NFR-CI-001 / R13 outright ("CI on GitHub must be GREEN"), and an unpinned `actions/setup-python` silently tracks whatever the GitHub runner image promotes to default — a moving target outside our control.

For EX04 we moved to **LangGraph** (ADR 0002), which removes the CrewAI/pydantic-v1 pain point specifically. However, the broader **langchain / langgraph / pydantic** ecosystem still has wheels and resolution behavior that are **safest and best-tested on Python 3.13**, and the project deliberately pins **`requires-python = ">=3.13,<3.14"`** in `pyproject.toml`. Letting CI run on an arbitrary newer interpreter (e.g. a runner-default 3.14) risks dependency-resolution and wheel-availability surprises that have nothing to do with our code — exactly the class of failure HW3 hit.

CI must execute: `uv sync` → `ruff check` → `python scripts/check_file_lines.py` → `pytest --cov` (`fail_under = 85`), all GREEN, with no network and a mock LLM (grader Path D, NFR-TEST-002/003).

## Decision

**Pin the GitHub Actions CI matrix to Python 3.13 via `actions/setup-python@v5`**, matching the project's `requires-python = ">=3.13,<3.14"`.

- Use `actions/setup-python@v5` with `python-version: "3.13"` (single, explicit version — not a range, not the runner default).
- Keep the pin **consistent across every CI job** and aligned with `pyproject.toml` and the ruff target (`py313`).
- The CI pipeline runs the full green gate: `uv sync` → `ruff check` → `scripts/check_file_lines.py` (≤150 logical lines) → `pytest --cov` (`fail_under = 85`), offline with a mock LLM.
- Do **not** run luigi's full suite in CI (NG4); only our package's tests against committed fixtures.

## Consequences

**Positive**
- **Reproducible, GREEN CI** — the interpreter is fixed, so CI behavior does not drift when GitHub bumps the runner's default Python. Satisfies NFR-CI-001 / R13.
- **No runner-default surprises** — the langchain/pydantic dependency stack resolves on the interpreter it is tested against; we avoid the HW3 failure mode pre-emptively even though the specific CrewAI trigger is gone.
- **Single source of truth for the interpreter** — `pyproject.toml` `requires-python`, the ruff `target-version = py313`, and the CI `python-version` all agree, so a contributor cannot accidentally develop against an unsupported interpreter.

**Negative / trade-offs**
- **No multi-version matrix** — we do not prove 3.14+ compatibility in CI. Acceptable: the project explicitly scopes `requires-python` to `<3.14`, and HW4 targets a fixed deliverable, not a broadly-distributed library.
- **Manual bump required** — when the ecosystem is verified on a newer Python, the pin (and `requires-python`) must be updated deliberately. This is a feature, not a bug: the upgrade becomes an intentional, reviewed change rather than a silent runner-driven break.

**Revisit when** the langchain/langgraph/pydantic stack is confirmed green on Python 3.14+, at which point `requires-python` and the CI pin can be widened together in a single reviewed change (with a version bump per R5).
