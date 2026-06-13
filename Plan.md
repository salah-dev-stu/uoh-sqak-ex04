# Plan — EX04 Graphify + Obsidian + Token-Efficient Graph-Guided Agent

> Implementation & architecture plan for `prd.md`. Package `graphguide`. uv-only, Python 3.13, ruff-clean, ≤150 logical lines/file, pytest ≥85%, version single-source, mock-LLM tests, Python-3.13-pinned CI. Per-mechanism PRDs in `docs/prd/`, ADRs in `docs/adr/`. Tasks live in `Todo.md`.

## 1. Project Structure (target tree)

```
README.md  prd.md  Plan.md  Todo.md
pyproject.toml  uv.lock  .env-example  .pre-commit-config.yaml  .gitignore
.github/workflows/ci.yml
src/graphguide/
  __init__.py            # exposes VERSION (imported from shared/version.py)
  constants.py           # non-config literals (enum names, keys) — no tunables
  main.py                # CLI entry (delegates to SDK only)
  sdk/
    __init__.py
    facade.py            # GraphGuide — single public entry
  graphify/
    __init__.py
    models.py            # Node, Edge, Confidence(enum) dataclasses
    runner.py            # GraphifyRunner — graphify CLI subprocess (via Gatekeeper)
    loader.py            # GraphLoader — graph.json -> models
    queries.py           # query/explain/path/affected wrappers (offline, metered)
    centrality.py        # NetworkX degree/betweenness + Hub-Node detection
  vault_builder/
    __init__.py
    builder.py           # curate graphify obsidian/ -> vault/
    pages.py             # hot.md / log.md / suspects / fix page templates
  agent/
    __init__.py
    state.py             # AgentState (LangGraph state schema)
    llm.py               # LLM client behind Gatekeeper; mock-injectable
    tools.py             # budgeted file reader + graph-query tool
    nodes.py             # LangGraph node fns: read_index, read_hot, query_graph, read_code, diagnose
    graph_guided.py      # graph-guided StateGraph assembly
    naive.py             # naive-mode runner (raw files, capped)
    trace.py             # InvestigationTrace recorder
  extensions/
    __init__.py
    suspect_ranker.py    # centrality + distance-to-failing-test ranking
    knowledge_diff.py    # vault/graph before-after diff -> knowledge_diff.md
  shared/
    __init__.py
    version.py           # VERSION = "1.00" (single source)
    config.py            # JSON config loader + typed accessors
    gatekeeper.py        # ApiGatekeeper — wraps+meters EVERY external call
    token_meter.py       # TokenRecord + aggregation
    logging_config.py    # logging from config/logging.json
vault/  index.md hot.md log.md  components/ tests/ findings/ suspects/ fix/
reports/  GRAPH_REPORT.md  graph/{graph.json,graph.html,cost.json}  bug_analysis.md
          token_comparison.md  architecture.md  knowledge_diff.md  metrics/*.json
diagrams/  block_diagram.{mmd,svg,png}  oop_diagram.{mmd,svg,png}
docs/  prd/*.md  adr/*.md  PROMPTS.md
tests/  conftest.py  unit/*  integration/*  fixtures/*
config/  agents.json tasks.json rate_limits.json logging.json graphify.json
target_repo/  luigi/...(vendored buggy + regression test)  PROVENANCE.md
scripts/  check_file_lines.py  fill_submission_pdf.py
```

## 2. Module Boundaries (each unit: what it does / how used / depends on)
- **sdk/facade.py** — orchestration only; the one public API. Depends on every subpackage; nothing depends back on CLI.
- **graphify/** — owns all interaction with `graph.json` and the `graphify` CLI. `runner` (writes), `loader`+`queries`+`centrality` (read). No LLM here except deep extraction (metered).
- **agent/** — pure decision flow; gets graph data via `graphify` queries and code via budgeted `tools`. LLM only via `agent/llm.py` → Gatekeeper. Naive vs graph-guided share `state`, `tools`, `trace`.
- **extensions/** — read-only over graph + vault; produce ranked suspects + knowledge diff.
- **shared/** — cross-cutting: version, config, gatekeeper, meter, logging. No upward deps.
- **vault_builder/** — turns graphify output + findings into curated `vault/` pages.

Keep every file ≤150 logical lines → split when a file does two jobs (e.g., `nodes.py` vs `graph_guided.py`).

## 3. Key Schemas
- **graph.json** (Graphify, consumed): node `{id,label,file_type,source_file,...}`; edge `{source,target,relation,confidence∈{EXTRACTED,INFERRED,AMBIGUOUS},weight,source_file}`.
- **TokenRecord**: `{mode,call_type,prompt_tokens,completion_tokens,total,files_read,units_read,ts}`.
- **AgentState**: `{task, phase, nodes_visited[], files_read[], budget_remaining, findings, trace[]}`.
- **SuspectRank**: `{node_id,label,centrality,dist_to_failing_test,score,rank}`.
- **KnowledgeDiff**: `{nodes_added[],links_added[],pages_added[],insights[]}`.

## 4. Gatekeeper & Token Meter (R3 + §5.5 engine)
- `ApiGatekeeper.call(kind, fn, *, est_tokens=…)` is the ONLY path for: LLM completion, `graphify` subprocess, agent file read.
- Pre-call: check rate limit + remaining budget (config). Post-call: record a `TokenRecord` (LLM tokens from API/usage or tiktoken estimate; subprocess tokens from graphify `cost.json`; file reads counted as units).
- `get_spend_report()` aggregates per mode. A test greps `src/` to assert no raw `subprocess.`/LLM client calls outside the gatekeeper.

## 5. Agent Design (LangGraph) (§5.3)
- **State machine nodes**: `read_index` → `read_hot` → `rank_suspects` (ext) → `query_graph` (query/explain/path/affected, budgeted) → `read_code` (only top suspects, budgeted) → `diagnose` → `propose_fix`. Conditional edge: if confident → `diagnose`; else loop `query_graph`/`read_code` until budget/iteration cap.
- **Naive runner**: linear `read_code` over many files (capped by config), then `diagnose`. No index/hot/graph. Same success bar.
- **Determinism for grading**: `agent/llm.py` accepts an injected client; tests inject a **MockLLM** that returns scripted answers keyed to prompts → CI needs no API key.
- Each node updates `trace` with tokens + files; the trace feeds the token report.

## 6. Graphify Workflow (§5.1)
1. Vendor luigi → `target_repo/luigi`.
2. `GraphifyRunner.extract(mode)` runs `graphify update target_repo/luigi` (AST, offline) and, once, deep mode (LLM, metered) — both via Gatekeeper.
3. Copy outputs → `reports/graph/` + base `obsidian/`.
4. `centrality.py` loads graph.json (NetworkX), computes degree+betweenness, flags Hub Nodes (`[CRITICAL]`/`[WARNING]`), writes `reports/graph_report_annotated.md`.
5. ADR documents the AST-only fallback (real tool is primary).

## 7. Vault Workflow (§5.1)
- `builder.py` curates graphify `obsidian/` → `vault/` with `index.md` (nav hub), `hot.md` (Task/Parameter serialization focus), `log.md`.
- `pages.py` emits `suspects/`, `tests/`, `findings/`, `fix/` from agent findings + suspect ranker.
- Snapshot vault **before** (post-graphify, pre-investigation) and **after** (post-fix) → knowledge diff.

## 8. Extensions (§5.6)
- **suspect_ranker**: `score = w1·centrality_norm + w2·(1/(1+dist_to_failing_test))` (weights in config). Output ranked list → `vault/suspects/` + agent seed.
- **knowledge_diff**: diff before/after vault + graph → `reports/knowledge_diff.md` (H9 artifact).

## 9. Config (R4, R10)
- `graphify.json`: cli path, mode, output dirs, deep-run toggle.
- `rate_limits.json`: rpm, token budgets per mode, max_iterations, max_files.
- `agents.json` / `tasks.json`: model id, temperature, prompts ref, success criteria.
- `logging.json`: handlers/levels. **No tunable appears in code.**

## 10. Testing Strategy (R6, R9, grader Path D)
- **Unit**: models, loader, centrality (fixture graph.json), gatekeeper (limits+meter), config, version, suspect_ranker, knowledge_diff, vault link-integrity, file-line guard.
- **Integration**: full `investigate()` in both modes with MockLLM over a committed fixture graph → asserts graph-mode reads fewer files/tokens than naive; asserts bug located.
- **Fixtures**: small committed `graph.json`, scripted MockLLM, vendored luigi slice for the fix test.
- Coverage ≥85%; everything offline.

## 11. CI / Tooling (R8, R13)
- `.github/workflows/ci.yml`: setup-python@v5 **pinned 3.13** → `uv sync` → `ruff check` → `python scripts/check_file_lines.py` → `pytest --cov` (fail_under 85). Badge in README.
- `.pre-commit-config.yaml`: ruff, ruff-format, file-lines, trailing-whitespace, end-of-file.

## 12. Versioning (R5)
`shared/version.py: VERSION="1.00"`; `__init__.py` imports it; `config` mirrors via a generated/asserted value; `test_version.py` asserts code==config. Bump +0.01 per change.

## 13. Implementation Phases (→ Todo.md task ranges)
- **P0 Scaffold** (T001–T060): repo init, pyproject/uv, gitignore/env, pre-commit, CI, version, config skeleton, constants, logging, check_file_lines.
- **P1 Shared/Gatekeeper** (T061–T120): config loader, gatekeeper, token_meter, tests (TDD).
- **P2 Graphify layer** (T121–T200): models, runner, loader, queries, centrality, Hub-Node report, tests; vendor luigi; run extraction; commit artifacts.
- **P3 Vault** (T201–T260): builder, pages, index/hot/log, linked pages, link-integrity test, before snapshot.
- **P4 Reverse-eng diagrams** (T261–T300): block + OOP diagrams (source+render), architecture.md.
- **P5 Agent** (T301–T400): state, llm+mock, tools (budgeted reader, graph tool), nodes, graph_guided, naive, trace, tests.
- **P6 Bug fix** (T401–T440): reproduce (fail), apply fix, verify (pass), bug_analysis.md, after snapshot, fix test.
- **P7 Token proof** (T441–T490): run both modes, persist metrics, token_comparison.md, chart.
- **P8 Extensions** (T491–T540): suspect_ranker, knowledge_diff, tests, vault/suspects, knowledge_diff.md.
- **P9 SDK + CLI** (T541–T580): facade wiring all features, main.py CLI, e2e smoke.
- **P10 Docs/README** (T581–T660): README (§8 list + visuals), per-mechanism PRDs, ADRs, PROMPTS.md, research-Q answers, reports finalize.
- **P11 Quality gate** (T661–T720): ruff, file-lines, coverage ≥85, CI green, version sync, gatekeeper-bypass grep test.
- **P12 Submission** (T721–T760): self-grade, submission PDF, final commits, push public, verify access.

## 14. Risks & Mitigations
- Deep Graphify cost → run once on luigi-core only; commit artifacts (OQ1 approved).
- Naive strawman → cap naive reads at a config ceiling, document the bar (OQ2 approved).
- luigi old-commit env → only the one regression test needs running; vendored + pinned; CI doesn't run luigi suite.
- LangGraph learning curve → minimal linear StateGraph; no over-engineering.
- File-line limit → split modules proactively (nodes vs assembly).

## 15. Per-Mechanism PRDs & ADRs (Gate-2 companions)
- `docs/prd/`: graphify.md, vault.md, agent.md, gatekeeper-token-meter.md, extensions.md.
- `docs/adr/`: 0001-use-real-graphify-tool.md, 0002-langgraph-over-crewai.md, 0003-pin-python-3.13-ci.md, 0004-ast-fallback.md, 0005-gatekeeper-wraps-all-calls.md.

## 16. Upgrades ("Strong → Standout") — see docs/prd/upgrade-knowledge-graph.md
Post-audit enhancements (U1–U4, U5 optional). Same standards; STOP after U1 for review.

- **U1 dense vault** — new `vault_builder/graph_pages.py`: `select_nodes(graph, bug, top_n, hops, cap)`
  (top-N centrality ∪ K-hop-of-bug) → `render_note(node, in_set_neighbors, tags, community)` (wikilinks
  to in-set neighbors only → no dangling; tags; Mermaid neighborhood; Dataview query) → `generate()`
  writes `vault/nodes/*.md`. Config `config/vault.json` (top_n, hops, max_notes). SDK `build_graph_vault()`.
  Real **Obsidian app** opened to capture Graph View screenshots → `assets/` (full / bug-local / before-after).
- **U2 iterative agent** — frontier loop in `graph_guided` (reuse the `route_after_diagnose` back-edge):
  `state["round"]`, expand 1 hop/round in `query_graph`, re-rank, stop on confidence or `max_rounds`
  (config). Real iterations in trace; restore the Iterations row in `reporting.py` + `token_comparison.md`.
- **U3 real run** — `scripts/real_run_demo.py`; a Claude-CLI-backed `LLMClient` variant (shell out via the
  Gatekeeper, tokens via tiktoken) so no key is needed; writes `reports/real_run.md` + trace json.
- **U4 graph.html** — pyvis graph from `graph.json` (size=centrality, color=community, Hub/bug highlighted);
  Playwright headless screenshot → `assets/`; test asserts HTML produced with node/edge data.
- **Versioning:** U1→1.01, U2→1.02, U3→1.03, U4→1.04 (single-source `version.py` + config mirror).
- **Risks:** Obsidian GUI automation flakiness → settle layout before capture, retry; node-cap to keep
  Graph View readable; keep generated notes out of coverage-sensitive paths (they're data, tested via the
  generator).
