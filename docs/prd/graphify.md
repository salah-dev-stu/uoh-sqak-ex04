# Per-Mechanism PRD — Graphify Integration Layer (`src/graphguide/graphify/`)

> Companion to `prd.md` §5.1 (FR-GRAPH-001..009) and `Plan.md` §2/§6. Package `graphguide`.
> Implements the **graph representation of code** deliverable (spec 5.1 · H2) by wrapping the **real Graphify tool**, not a hand-rolled parser.
> All tasks for this mechanism append to the global `Todo.md` (P2: T121–T200).

---

## 1. Purpose

Turn the unfamiliar buggy target codebase (`target_repo/luigi/`) into a navigable **knowledge graph** (`graph.json` + `GRAPH_REPORT.md` + `graph.html`) so the agent and the reverse-engineering work consult the graph *first* and read raw code *only* for the few nodes that matter. This layer owns **every** interaction with the `graphify` CLI and with `graph.json`: it runs extraction, loads the graph into typed Python objects, exposes offline query primitives, computes centrality, and flags **Hub Nodes**. It is the engine behind RQ2 (most central components), RQ3 (complexity hotspots / Hub Nodes), and RQ6/RQ7 (graph navigation saves tokens vs linear reading).

This mechanism does **not** make decisions about the bug (that is `agent/`) and does **not** curate the vault (that is `vault_builder/`). It produces the graph substrate they both consume.

## 2. The Real Tool (validated, not invented)

| Fact | Value |
|---|---|
| PyPI package | `graphifyy` |
| CLI command | `graphify` |
| Version | `0.8.39` |
| License | **MIT** (safe to depend on — see ADR `docs/adr/0001-use-real-graphify-tool.md`) |
| Python requirement | `>= 3.10` |
| Install | `uv tool install graphifyy` |

The lecturer states Graphify is a **real, downloadable tool**; we therefore use it directly. Validated before this PRD: `graphifyy` installs via `uv tool install graphifyy` and runs AST extraction **offline** (no LLM, no API key) on `target_repo/luigi/`.

### 2.1 Extraction Modes
- **Offline AST mode** — `graphify update <path>`. Pure static analysis (imports, calls, inheritance, definitions). **No LLM, no key, deterministic, free.** This is the default mode and the one the grader can reproduce.
- **Deep / semantic mode** — adds LLM-inferred edges/labels. **Requires a Claude key.** Run **once by us** with Claude access and the outputs **committed** to the repo; the grader never re-runs it. Mode is selectable via `config/graphify.json`, not code (FR-GRAPH-002 / R4).

Both invocations go through the **Gatekeeper** (FR-GRAPH-003); deep-mode cost is read from graphify's emitted `cost.json` and recorded by the token meter.

## 3. Components (`src/graphguide/graphify/`)

Each file ≤150 logical lines (R7); split when a file does two jobs.

| File | Responsibility |
|---|---|
| `models.py` | `Node`, `Edge`, `Confidence(enum)` dataclasses — the typed shape of `graph.json`. |
| `runner.py` | **`GraphifyRunner`** — invokes the `graphify` CLI as a subprocess (offline AST or deep mode) **via the Gatekeeper**; copies outputs into `reports/graph/`. |
| `loader.py` | **`GraphLoader`** — reads `graph.json` into `Node`/`Edge` objects for the agent and extensions. |
| `queries.py` | **Query primitives** — `query`, `explain`, `path`, `affected` wrappers; offline, budgeted, metered. |
| `centrality.py` | **NetworkX** degree + betweenness over `graph.json`; **Hub-Node detection** with `[CRITICAL]`/`[WARNING]` tiers; emits the annotated report. |

Dependency direction: `runner` writes; `loader` + `queries` + `centrality` read. Nothing in `graphify/` depends on `agent/` or the CLI. The only LLM use is deep extraction, and it is metered.

## 4. `graph.json` Schema (consumed, not invented)

```jsonc
{
  "nodes": [
    { "id": "...", "label": "...", "file_type": "...", "source_file": "...", ... }
  ],
  "edges": [
    {
      "source": "...", "target": "...",
      "relation": "calls | imports | inherits | ...",
      "confidence": "EXTRACTED | INFERRED | AMBIGUOUS",
      "weight": 1.0,
      "source_file": "..."
    }
  ]
}
```

- **Nodes** = files / classes / functions (`id`, `label`, `file_type`, `source_file`, …).
- **Edges** = calls / imports / inheritance, each carrying a **confidence**:
  - `EXTRACTED` — directly observed by static AST analysis (highest trust).
  - `INFERRED` — derived by the deep/semantic pass.
  - `AMBIGUOUS` — uncertain; surfaced but treated cautiously by the agent.

`GraphLoader` maps `confidence` onto the `Confidence` enum in `models.py` so downstream code never string-compares.

## 5. Hub-Node Detection

`centrality.py` loads `graph.json` into a NetworkX graph and computes:
- **degree centrality** — how many things connect to a node (fan-in + fan-out).
- **betweenness centrality** — how often a node sits on shortest paths between other nodes (a bottleneck / broker).

Nodes are flagged as **Hub Nodes** when degree **and/or** betweenness exceed configured thresholds (thresholds in `config/graphify.json`, R10):
- **`[CRITICAL]`** — top tier; very high centrality, a true architectural bottleneck (expected: luigi's central `Task` class).
- **`[WARNING]`** — elevated centrality; mixed responsibilities worth noting.

For each flagged node the annotated report states **why it's a bottleneck**, the **risk** it carries, and a **fix option** (refactor direction). Output: `reports/graph_report_annotated.md` (augmenting graphify's own `GRAPH_REPORT.md`). This directly answers RQ2 and RQ3 and feeds the suspect ranker (`FR-EXT-101`).

## 6. Gatekeeper Routing & Metering (R3 · FR-GRAPH-003)

Every `graphify` subprocess call routes through the **`ApiGatekeeper`** (`shared/gatekeeper.py`). The Gatekeeper:
- pre-call: checks rate limit + remaining budget from `config/rate_limits.json`;
- runs the subprocess;
- post-call: records a `TokenRecord` — command, duration, exit code, and **token cost read from graphify's emitted `cost.json`** (offline AST mode has zero LLM cost; deep mode carries the real cost).

A grep test asserts **no** raw `subprocess.` call to `graphify` bypasses the Gatekeeper (FR-GATE-003). This is wired for real, not decorative (HW3 audit lesson).

## 7. Offline Query Primitives (FR-GRAPH-006)

Exposed through the SDK, all offline (read `graph.json`, no LLM), all metered as text-units:

| Primitive | Meaning |
|---|---|
| `query <selector> --budget N` | Return up to **N** matching nodes/edges (budget caps the result size so context stays small). |
| `explain <node>` | Summarize a node's role, neighbors, and incident edges. |
| `path <a> <b>` | Shortest path(s) between two nodes (how does X reach Y?). |
| `affected <node>` | Impact set — what depends on / is reachable from a node ("what breaks if I change this"). |

`--budget` keeps every query inside the agent's token/file budget (NFR-PERF-001) and makes naive-vs-graph comparison honest.

## 8. Committed Artifacts (`reports/graph/`)

So the grader reproduces everything **without** an API key or a live tool run (NFR-REPRO-001, grader Path D):

```
reports/GRAPH_REPORT.md            # graphify's own report
reports/graph_report_annotated.md  # our Hub-Node augmentation (centrality + tiers)
reports/graph/graph.json           # the graph (committed)
reports/graph/graph.html           # interactive view (screenshot embedded in README)
reports/graph/cost.json            # graphify cost emission (deep run)
```

## 9. FR Traceability

| FR | Covered by |
|---|---|
| **FR-GRAPH-001** | `runner.py` `GraphifyRunner` invokes `graphify` as a subprocess on `target_repo/luigi/`. |
| **FR-GRAPH-002** | Offline AST mode + deep mode, mode selected via `config/graphify.json` (not code). |
| **FR-GRAPH-003** | Every `graphify` call routes through the Gatekeeper; cost recorded from `cost.json`. |
| **FR-GRAPH-004** | Outputs persisted to `reports/graph/{graph.json,graph.html,cost.json}` + `reports/GRAPH_REPORT.md`. |
| **FR-GRAPH-005** | `loader.py` `GraphLoader` → typed `Node`/`Edge` with `Confidence ∈ {EXTRACTED,INFERRED,AMBIGUOUS}`. |
| **FR-GRAPH-006** | `queries.py` `query --budget` / `explain` / `path` / `affected`, offline + metered, via SDK. |
| **FR-GRAPH-007** | `graph_report_annotated.md` flags Hub Nodes with degree/betweenness + `[CRITICAL]`/`[WARNING]` + why/risk/fix. |
| **FR-GRAPH-008** | `centrality.py` computes degree + betweenness via NetworkX; ranked centrality table. |
| **FR-GRAPH-009** | AST-only fallback documented in `docs/adr/0004-ast-fallback.md` (real tool is primary). |

## 10. Acceptance Criteria

- AC1 `uv tool install graphifyy` succeeds; `graphify --version` reports `0.8.39`.
- AC2 `GraphifyRunner` produces `reports/graph/graph.json` for `target_repo/luigi/` in **offline AST mode with no API key**.
- AC3 `GraphLoader` parses the committed `graph.json` into typed `Node`/`Edge`; every edge's `confidence` maps onto the `Confidence` enum; unit-tested against a committed fixture graph.
- AC4 `centrality.py` flags ≥1 `[CRITICAL]` Hub Node (expected: `Task`) with degree + betweenness values and a why/risk/fix note in `reports/graph_report_annotated.md`.
- AC5 `query/explain/path/affected` run offline against the fixture graph; `query --budget N` returns ≤ N items.
- AC6 A grep test confirms no raw `subprocess.` invocation of `graphify` bypasses the Gatekeeper.
- AC7 All five committed artifacts (§8) are present in the repo and consumed by tests without a live tool run.
- AC8 `ruff check` clean, every file ≤150 logical lines, this layer's tests GREEN and counted toward ≥85% coverage.
