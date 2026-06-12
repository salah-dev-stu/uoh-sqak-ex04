# ADR 0004 — AST→Graph Fallback Builder (Documented, Not Used)

> Status: **Accepted** (fallback, not primary) · Context: `prd.md` §5.1 (FR-GRAPH-009) · `Plan.md` §6 step 5 · Companion: `docs/adr/0001-use-real-graphify-tool.md`, `docs/prd/graphify.md`

## Context

ADR 0001 commits us to the **real** Graphify tool (`graphifyy` v0.8.39) as the primary graph-extraction engine. FR-GRAPH-009 requires that we also **document an AST-only fallback** in case the real tool were ever unavailable (e.g., an environment that cannot install `graphifyy`, a PyPI outage, or a version that breaks). The grader must always be able to obtain a `graph.json` of the target.

## Decision

**Document — but do not activate — a self-contained AST→graph builder inside `src/graphguide/graphify/`** that, *if the real tool were unavailable*, would reproduce the **same `graph.json` / `GRAPH_REPORT.md` schema** the rest of the system already consumes.

The fallback would:
- Walk `target_repo/luigi/` with Python's standard-library `ast` module (offline, no LLM, no key).
- Emit **nodes** for files / classes / functions (`id`, `label`, `file_type`, `source_file`, …) and **edges** for `imports`, `calls`, and `inherits` — identical field shapes to graphify's output.
- Mark every fallback-produced edge with `confidence = EXTRACTED` (pure static analysis; it cannot produce `INFERRED`/`AMBIGUOUS` semantic edges — that is deep-mode territory only the real tool has).
- Write to the **same paths** (`reports/graph/graph.json`, `reports/GRAPH_REPORT.md`) so `GraphLoader`, `queries`, `centrality`, the agent, and the extensions need **zero changes** — they cannot tell which engine produced the file.

This keeps a single downstream contract: the schema, not the tool, is the interface.

## Consequences

**Positive**
- Guarantees a reproducible `graph.json` even in a degraded environment — removes single-point-of-failure risk on an external CLI.
- Schema-compatible, so no downstream code branches on which engine ran.
- Pure-stdlib `ast`, so the fallback itself needs no third-party install and no API key.

**Negative**
- A fallback path that ships but is not exercised in the primary flow is dead-ish code; mitigated by keeping it documented-and-minimal and the real-tool outputs committed.
- It cannot reproduce deep/semantic (`INFERRED`/`AMBIGUOUS`) edges — only `EXTRACTED` ones. Acceptable, since the graded path is offline AST anyway and those edges are committed from our one deep run.

## Why it is not used

The real tool installed cleanly via `uv tool install graphifyy` and **runs AST extraction offline**, producing the graph we need with no API key. Because the primary path works and its outputs are committed, the fallback stays **documented as a contingency only** and is not the engine on the graded path.
