# ADR 0001 — Use the Real Graphify Tool

> Status: **Accepted** · Context: `prd.md` §5.1 (FR-GRAPH-001..009) · `Plan.md` §6 · Companion PRD: `docs/prd/graphify.md`

## Context

Spec 5.1 (H2) requires a **graph representation of the code** — nodes for files/classes/functions, edges for calls/imports/inheritance — produced as `graph.json` + `GRAPH_REPORT.md`. The lecturer states explicitly that **Graphify is a real, downloadable tool**, not something we are meant to re-implement. We confirmed the tool exists, installs, and runs:

| Fact | Value |
|---|---|
| PyPI package | `graphifyy` |
| CLI command | `graphify` |
| Version | `0.8.39` |
| License | **MIT** |
| Python requirement | `>= 3.10` |
| Install | `uv tool install graphifyy` |

Validated before deciding: `uv tool install graphifyy` succeeds and `graphify update <path>` performs **offline AST extraction** (no LLM, no API key) on `target_repo/luigi/`, emitting the graph artifacts.

The alternative would be to hand-roll an AST→graph builder ourselves.

## Decision

**Use the real `graphify` tool (`graphifyy`, v0.8.39) as the primary and only graph-extraction engine.** We wrap it in `src/graphguide/graphify/` (`GraphifyRunner` runs the CLI subprocess via the Gatekeeper; `GraphLoader`/`queries`/`centrality` consume its output). We do **not** hand-roll a parser for the primary path.

Reasons:
- The lecturer designated Graphify as the intended real tool; using it is faithful to the assignment.
- It is **MIT-licensed**, so depending on it is legally safe.
- It runs **AST extraction offline**, so the core graph is reproducible with no API key.
- Re-implementing it would be wasted effort (NG3: "Not re-implementing Graphify"), and worse, would not be "the real tool."

Installation is via `uv tool install graphifyy` only (R12: uv-only, no pip/requirements.txt).

## Consequences

**Positive**
- Faithful to the lecturer's instruction; the graph is produced by the designated tool.
- MIT license removes any dependency-licensing risk.
- Offline AST mode means the core `graph.json` needs no API key.
- **Outputs are committed** to the repo (`reports/graph/graph.json`, `reports/GRAPH_REPORT.md`, `reports/graph/graph.html`, `reports/graph/cost.json`) so the **grader reproduces everything without installing the tool, paying tokens, or holding a key** (grader Path D / NFR-REPRO-001).

**Negative / mitigations**
- External CLI dependency → pinned to `0.8.39`; every call routed through the Gatekeeper and metered; outputs committed so a tool/version drift never blocks the grader.
- Deep/semantic mode needs a Claude key → run **once by us** and the result committed; the default and graded path is offline AST mode.
- Risk the tool is unavailable in some environment → a self-contained AST fallback is **documented** (and reproduces the same schema) in `docs/adr/0004-ast-fallback.md`, but is **not** the primary path.
