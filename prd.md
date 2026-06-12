# PRD — EX04: Reverse Engineering, Debugging & Token-Efficient Agentic AI with Graphify + Obsidian

> **Course** 203.3763 "Orchestration of AI Agents" · University of Haifa · Spring 2026 · Dr. Yoram Segal
> **Group** `uoh-sqak` — Salah Qadah (323039974) + Andalus Kalash (211435797)
> **Repo** https://github.com/salah-dev-stu/uoh-sqak-ex04 (public) · **Deadline** Fri 2026-06-19 23:59 (−5/24h late)
> **Package** `graphguide` (importable name; `src/graphguide/`) · **Version** starts `1.00`
> **Status** Gate-1 draft for approval · **Self-grade target** 85

This is the master PRD. Per-mechanism PRDs (one per major component) live under `docs/prd/` and append their tasks to the global `Todo.md` (per the project's per-feature workflow). All requirements carry stable IDs (`FR-<AREA>-NNN`, `NFR-<CAT>-NNN`) so `Todo.md` coverage can be verified mechanically.

---

## 1. Overview & Problem Statement

Large codebases overflow an LLM's context window. Dumping raw files wastes tokens and triggers **"Lost in the Middle"** — information buried mid-context is effectively ignored. This project proves a better way: convert an **unfamiliar buggy Python codebase** into a navigable **knowledge graph** (via the real **Graphify** tool) plus an **Obsidian** knowledge vault, then drive a **graph-guided LangGraph agent** that consults the graph/vault *first* and reads raw code *only* for the few nodes that matter — and we **measure** that this consumes far fewer tokens than naive raw-file reading.

**The concrete vehicle:** `spotify/luigi` (≈21.7k LOC, 82 files) carrying BugsInPy **bug 20** — `Task.to_str_params` silently drops parameters declared `significant=False`, while `Task.from_str_params` indexes *all* params, so a `task → str → task` round-trip raises `KeyError: 'insignificant_param'`. A 3-line fix in the central `Task` class. Small bug, rich architecture — ideal for reverse engineering, God-Node analysis, and a clean before/after.

**Validated before this PRD:** Graphify (`graphifyy`, MIT) installs and runs AST extraction offline; the luigi bug reproduces (failing test) and the fix passes — both confirmed in an isolated uv venv (Python 3.8.3).

## 2. Goals / Non-Goals

**Goals**
- G1 Represent luigi as a Graphify graph (`graph.json` + `GRAPH_REPORT.md` + `graph.html`) with God Nodes flagged.
- G2 Build a real Obsidian vault (`index.md`, `hot.md`, `log.md`, linked component/test/suspect/finding/fix pages).
- G3 Reverse-engineer luigi into an **architectural block diagram** + an **OOP/class diagram**.
- G4 Build a **graph-guided LangGraph agent** that consults graph/vault before raw code, with hard step/token budgets.
- G5 Find → explain → **fix** bug 20 for real; show code-level **and** knowledge-level before/after.
- G6 **Prove token savings**: naive vs graph-guided, measured (tokens, files read, iterations, time-to-root-cause).
- G7 Ship ≥2 original extensions: suspect-ranking by proximity-to-failing-test, and knowledge before/after auto-diff.
- G8 Meet all engineering standards (R1–R13) and ship a rich README + green GitHub CI.

**Non-Goals (v1)**
- NG1 Not fixing multiple bugs or the whole project — exactly one small bug.
- NG2 Not a chatty multi-agent crew — one disciplined graph-guided agent/state machine.
- NG3 Not re-implementing Graphify — we use the real tool and wrap it.
- NG4 Not running luigi's full test suite in CI — only the one regression test, reproduced/documented offline; CI runs our package's tests with a mock LLM.
- NG5 The grader does not run our live agent or pay tokens — committed artifacts + mock-LLM tests stand alone.

## 3. Target Users / Personas

- **P1 The grader / Dr. Segal** — runs `uv run pytest` (no API key), reads README + reports + vault + diagrams, checks H1–H12 & R1–R13 on the committed repo. Primary audience.
- **P2 A developer dropped into unfamiliar code** — the persona the *product* serves: uses index.md/hot.md + graph queries to reach root cause without reading 80 files.
- **P3 The pair (us)** — reproduce, run the agent live (with Claude access), regenerate artifacts.

## 4. Background — Lecture Themes the Build Must Embody (spec §4 research questions)
- **RQ1** What is luigi's *actual* architecture and what's non-obvious? → README + `reports/architecture.md` + diagrams + vault.
- **RQ2** Which components/classes/functions are most central? → God Nodes in `GRAPH_REPORT.md` + centrality table.
- **RQ3** Where are complexity hotspots / mixed responsibilities / **God Nodes**? → graph metrics + report.
- **RQ4** How to extract block + OOP schemas from thin docs? → reverse-engineering walkthrough.
- **RQ5** How was the bug found, root cause, the steps? → `reports/bug_analysis.md` + agent trace.
- **RQ6** Advantage of graph + Obsidian vs linear reading? → token report + narrative.
- **RQ7** How did graph-guided AI save tokens? → `reports/token_comparison.md` (measured).
- **RQ8** What further agent mechanisms would we add? → README "Future work" + the 2 extensions as proof.

---

## 5. Functional Requirements

### 5.1 Graphify integration — `src/graphguide/graphify/` (spec 5.1 · H2)
- **FR-GRAPH-001** Provide a `GraphifyRunner` that invokes the real `graphify` CLI as a subprocess to extract the graph of `target_repo/luigi/`.
- **FR-GRAPH-002** Support **offline AST mode** (`graphify update <path>`, no LLM) and **deep/semantic mode** (LLM); mode selectable via config, not code.
- **FR-GRAPH-003** Every `graphify` subprocess call routes through the **Gatekeeper** (FR-GATE-*), which records command, duration, exit code, and token cost (from graphify's `cost.json`).
- **FR-GRAPH-004** Persist Graphify outputs into the repo: `reports/graph/graph.json`, `reports/GRAPH_REPORT.md`, `reports/graph/graph.html`, `reports/graph/cost.json` (committed artifacts).
- **FR-GRAPH-005** Provide a typed `GraphLoader` that reads `graph.json` into Python objects (nodes, edges with `confidence ∈ {EXTRACTED, INFERRED, AMBIGUOUS}`) for the agent and extensions.
- **FR-GRAPH-006** Provide graph-query wrappers (`query --budget N`, `explain`, `path`, `affected`) exposed through the SDK, all offline, all metered.
- **FR-GRAPH-007** `GRAPH_REPORT.md` (or our augmentation `reports/graph_report_annotated.md`) must flag **God Nodes** with degree/betweenness centrality, mark `[CRITICAL]`/`[WARNING]`, and for each give why-it's-a-bottleneck + risk + fix option.
- **FR-GRAPH-008** Compute centrality (degree, betweenness) for nodes via NetworkX over `graph.json`; expose as a ranked table.
- **FR-GRAPH-009** Document the AST-only fallback (if the real tool were unavailable) in an ADR — but the real tool is the primary path.

### 5.2 Obsidian vault — `vault/` (spec 5.1 · H3)
- **FR-VAULT-001** Generate the base vault via Graphify (`obsidian/`), then curate it into `vault/`.
- **FR-VAULT-002** `vault/index.md` — central entry: system structure + main navigation paths (Portfolio→Domains→Components), wikilinks to key pages. Agents read this FIRST.
- **FR-VAULT-003** `vault/hot.md` — focused context for the bug-critical area (`Task`/`Parameter` serialization), refreshed during investigation.
- **FR-VAULT-004** `vault/log.md` — decision/investigation log: query → finding → action trace.
- **FR-VAULT-005** Linked pages: `components/` (key classes), `tests/` (the failing test), `findings/`, `suspects/` (prime suspects), `fix/` (the fix). Real wikilinks + tags (`#suspect`, `#fix`, `#decision`), not a file dump.
- **FR-VAULT-006** Capture a **before** snapshot of the vault (pre-investigation) and an **after** snapshot (post-fix) to power the knowledge-level before/after (FR-FIX-005, FR-EXT-201).
- **FR-VAULT-007** A link-integrity check (no dangling wikilinks) runs in tests.

### 5.3 Reverse-engineering illustrations — `diagrams/` (spec 5.2 · H7, H8)
- **FR-REV-001** **Architectural block diagram** of luigi (main parts: CLI/interface, Task/Register, Scheduler, Worker, Target/FileSystem, Parameter) + data flow. Source committed (Mermaid/draw.io/matplotlib).
- **FR-REV-002** **OOP/class diagram** — `Task`, `Parameter` hierarchy, `Scheduler`, `Worker`, `Target` with inheritance/composition/patterns. Source committed.
- **FR-REV-003** Both diagrams rendered (PNG/SVG) and embedded in README + vault. Folder listing ≠ acceptable.
- **FR-REV-004** A `reports/architecture.md` walkthrough explaining how the diagrams were extracted from the graph (not from docs).

### 5.4 Graph-guided agent — `src/graphguide/agent/` (spec 5.3 · H4)
- **FR-AGENT-001** Implemented in **LangGraph** as an explicit state machine.
- **FR-AGENT-002** Workflow order is enforced: read `index.md` → read `hot.md` → graph `query`/`explain`/`path`/`affected` → **only then** request raw code snippets for the few identified nodes.
- **FR-AGENT-003** Every LLM call routes through the **Gatekeeper** (token meter + rate-limit + budget enforcement).
- **FR-AGENT-004** Hard caps from config: max iterations/steps, max tokens, max files read. Exceeding → graceful stop.
- **FR-AGENT-005** Two run modes behind one interface: **naive mode** (reads many raw files, no graph) and **graph-guided mode** (graph/vault first). Same task, same success criterion.
- **FR-AGENT-006** The agent emits a structured **investigation trace** (steps, nodes visited, files read, tokens per step) consumed by the token report.
- **FR-AGENT-007** A **budgeted file-reader tool** (reads only requested node's source span, never whole repo) — metered.
- **FR-AGENT-008** Agent goal: locate the buggy function, explain root cause, propose the fix — verifiable against the known answer in tests via a **mock LLM** (deterministic).
- **FR-AGENT-009** Document each node/step's role + the context-reduction mechanisms (spec 5.3 requirement).

### 5.5 The bug fix — `target_repo/` + `reports/bug_analysis.md` (spec 5.4 · H5, H9)
- **FR-FIX-001** Vendor luigi at the buggy commit `b958140…` as `target_repo/luigi/` (pinned + provenance file), with the regression test from the fixed commit applied (the BugsInPy-exposing test).
- **FR-FIX-002** Reproduce the failure: `test_task_to_str_to_task` → `KeyError: 'insignificant_param'` (logged to `reports/`).
- **FR-FIX-003** Apply the 3-line fix to `Task.to_str_params` (remove the `significant` guard).
- **FR-FIX-004** Verify: the test passes after the fix (logged). Provide the unified diff.
- **FR-FIX-005** `reports/bug_analysis.md`: problem, root cause (serialize/deserialize asymmetry), investigation path, change, verification — **plus knowledge-level before/after** (which vault pages/nodes/links/insights were added).
- **FR-FIX-006** A test in our suite asserts the fix's behavior (round-trip preserves insignificant params) using vendored luigi or a minimal extracted reproduction.

### 5.6 Token-savings proof — `reports/token_comparison.md` (spec 5.5 · H6)
- **FR-TOKEN-001** A **token meter** in the Gatekeeper records, per call: prompt tokens, completion tokens, total, files/text-units read, timestamp, mode.
- **FR-TOKEN-002** Run the agent in **naive** and **graph-guided** modes on the same bug; collect both runs' metrics.
- **FR-TOKEN-003** Report ≥4 metrics side by side: **tokens consumed · files/text-units read · iterations/rounds · quality+speed to root-cause**.
- **FR-TOKEN-004** Compute and report efficiency `= (T_naive − T_graph)/T_naive × 100%`; state honestly if savings are below target with reasons.
- **FR-TOKEN-005** Numbers come from the instrumented meter (persisted JSON in `reports/metrics/`), not hand-waving; a chart is embedded in README.
- **FR-TOKEN-006** Metrics are reproducible from committed JSON so the grader sees them without running the live agent.

### 5.7 Original extensions — `src/graphguide/extensions/` (spec 5.6 · H10)
- **FR-EXT-101** **Suspect-ranking by proximity to failing test**: rank candidate nodes by combining centrality with graph-distance from the failing test's node; output a ranked suspect list the agent uses to jump to the prime suspect.
- **FR-EXT-102** The ranking is surfaced in `vault/suspects/` and measurably reduces agent iterations (tie into token report).
- **FR-EXT-201** **Knowledge before/after auto-diff**: a tool that diffs the vault (and graph) before vs after investigation — nodes/links/pages added — and emits the H9 knowledge-level before/after artifact (`reports/knowledge_diff.md`).
- **FR-EXT-301** Both extensions documented in README with rationale + example output.

### 5.8 SDK layer — `src/graphguide/sdk/` (R1)
- **FR-SDK-001** A single public façade (`GraphGuide`) is the only entry to business logic: `graphify()`, `build_vault()`, `investigate(mode=…)`, `rank_suspects()`, `knowledge_diff()`, `token_report()`.
- **FR-SDK-002** `main.py` / CLI calls only the SDK; no business logic in CLI or tests directly.
- **FR-SDK-003** SDK methods are typed and documented.

### 5.9 Gatekeeper — `src/graphguide/shared/gatekeeper.py` (R3)
- **FR-GATE-001** One `ApiGatekeeper` wraps **every** external call: LLM calls, `graphify` subprocess, agent file reads.
- **FR-GATE-002** It enforces rate limits + token budgets (from config) and **records** every call (the token meter) — wired for real, not decorative.
- **FR-GATE-003** `get_spend_report()` returns aggregated usage; a grep test asserts no raw `subprocess`/LLM calls bypass it.

### 5.10 Config, version, logging — `src/graphguide/shared/`, `config/` (R4, R5, R10)
- **FR-CONFIG-001** All tunables in JSON under `config/`: `agents.json`, `tasks.json`, `rate_limits.json`, `logging.json`, `graphify.json`. Zero hardcoded models/timeouts/paths/budgets.
- **FR-VERSION-001** `shared/version.py` holds `VERSION = "1.00"`; `__init__.py` imports it; config mirrors it; a test asserts all agree (single source of truth).
- **FR-LOG-001** Structured logging configured from `config/logging.json`.

### 5.11 CLI / entry — `src/graphguide/main.py`, `constants.py` (R1)
- **FR-CLI-001** `uv run graphguide <command>` exposes: `graphify`, `vault`, `investigate --mode {naive,graph}`, `suspects`, `knowledge-diff`, `token-report`, `version` — each delegating to the SDK.

### 5.12 Documentation deliverables — `README.md`, `reports/`, `docs/` (spec §7,§8 · H11, H12)
- **FR-DOC-001** README contains the full spec-§8 list: repo+why, the bug, research questions (§4), extracted architecture, agent workflow, Graphify+Obsidian usage, reverse-engineering walkthrough, bug+root-cause+fix, before/after, token-efficiency, extensions, run instructions.
- **FR-DOC-002** README embeds visuals: block diagram, OOP diagram, graph.html screenshot, token chart, vault screenshot.
- **FR-DOC-003** `docs/` holds: this PRD, `PLAN.md`, `Todo.md`, per-mechanism PRDs, ADRs (incl. the Graphify-tool ADR + LangGraph ADR + Python-3.13-CI ADR), `PROMPTS.md`.
- **FR-DOC-004** All §4 research questions answered explicitly in README + reports + vault.
- **FR-DOC-005** Submission PDF `uoh-sqak-ex04.pdf` produced via `scripts/fill_submission_pdf.py`; self-grade 85.

---

## 6. Non-Functional Requirements

- **NFR-QUALITY-001** `ruff check` = 0 failures (line-length 100, py313, E/F/W/I/N/UP/B/C4/SIM, ignore E501). [R8]
- **NFR-QUALITY-002** ≤150 logical lines per Python file, enforced by `scripts/check_file_lines.py`. [R7]
- **NFR-QUALITY-003** `pytest --cov` ≥ 85% (`fail_under = 85`). [R9]
- **NFR-TEST-001** TDD: red→green→refactor; suite GREEN. [R6]
- **NFR-TEST-002** A **mock LLM** drives all agent tests so the grader needs no API key (grader Path D); the 4 auth paths (CLI login, `claude --login`, `ANTHROPIC_API_KEY`, mock) all work. [grader]
- **NFR-TEST-003** Tests run against committed fixtures (graph.json, metrics JSON, vendored luigi) — no network, no live agent.
- **NFR-CI-001** GitHub Actions CI (ruff + file-lines + pytest+cov) **GREEN**, **pinned to Python 3.13** via `actions/setup-python@v5`. [R13]
- **NFR-PKG-001** `uv` only; `pyproject.toml` + `uv.lock` tracked; no pip/venv/requirements.txt. [R12]
- **NFR-SEC-001** Zero secrets; `.env-example` + `os.environ.get`; `.env` gitignored. [R11]
- **NFR-SEC-002** Skill/superpower artifacts (`.blender-toolkit/`, `.claude/`, `SKILL.md`) gitignored; `prd.md`/`Plan.md`/`Todo.md`/`README.md`/`docs/`/`reports/`/`vault/`/`diagrams/` tracked.
- **NFR-REPRO-001** Target repo vendored at a pinned commit with provenance; Graphify outputs committed; everything reproducible without an API key.
- **NFR-VCS-001** Continuous, meaningful commits — no single big-bang push. [R13]
- **NFR-PERF-001** Agent honors token/step/file budgets from config; naive vs graph modes share the same success bar for a fair comparison.
- **NFR-OOP-001** OOP, no duplication (base classes/mixins/Template Method); class diagram submitted. [R2]

---

## 7. Technical Architecture (overview)

```
CLI (main.py) ─► SDK façade (GraphGuide)
                     │
   ┌─────────────────┼───────────────────────────────────┐
   ▼                 ▼                 ▼                   ▼
graphify/        agent/ (LangGraph)  extensions/        shared/
 GraphifyRunner   state machine:      suspect_ranker     gatekeeper (meter+limits)
 GraphLoader      index→hot→query→     knowledge_diff     config loader
 query wrappers   code (budgeted)                         version / logging
   │                 │                                       ▲
   ▼                 ▼                                       │
graphify CLI ──► reports/graph/*  vault/*  ◄── all external calls routed here
(subprocess)     (committed artifacts)
```

Data flow: `target_repo/luigi` → Graphify (metered) → `graph.json` + base `obsidian/` → curated `vault/` → agent (naive | graph-guided) reads vault/graph then budgeted code → finding + fix → token metrics → reports + README. Extensions read `graph.json` + vault to rank suspects and diff knowledge.

## 8. Key Data Schemas (consumed, not invented)
- **graph.json** (Graphify): nodes `{id,label,file_type,source_file,…}`; edges `{source,target,relation,confidence∈{EXTRACTED,INFERRED,AMBIGUOUS},weight,source_file}`.
- **TokenRecord** (ours): `{mode,call_type,prompt_tokens,completion_tokens,total,files_read,units_read,ts}` → `reports/metrics/*.json`.
- **AgentState** (LangGraph): `{task, phase, nodes_visited, files_read, budget_remaining, findings, trace[]}`.
- **SuspectRank**: `{node_id, centrality, dist_to_failing_test, score, rank}`.

## 9. Rubric Traceability (every gate has an FR/NFR home)
- **Spec 5.1**→FR-GRAPH-\*, FR-VAULT-\* · **5.2**→FR-REV-\* · **5.3**→FR-AGENT-\* · **5.4**→FR-FIX-\* · **5.5**→FR-TOKEN-\* · **5.6**→FR-EXT-\*
- **H1**→FR-FIX-001 · **H2**→FR-GRAPH-004/007 · **H3**→FR-VAULT-\* · **H4**→FR-AGENT-\* · **H5**→FR-FIX-\* · **H6**→FR-TOKEN-\* · **H7**→FR-REV-001 · **H8**→FR-REV-002 · **H9**→FR-FIX-005+FR-EXT-201 · **H10**→FR-EXT-\* · **H11**→FR-DOC-001/002 · **H12**→FR-DOC-004
- **R1**→FR-SDK-\* · **R2**→NFR-OOP-001 · **R3**→FR-GATE-\* · **R4**→FR-CONFIG-001 · **R5**→FR-VERSION-001 · **R6**→NFR-TEST-001 · **R7**→NFR-QUALITY-002 · **R8**→NFR-QUALITY-001 · **R9**→NFR-QUALITY-003 · **R10**→FR-CONFIG-001 · **R11**→NFR-SEC-001 · **R12**→NFR-PKG-001 · **R13**→NFR-CI-001+NFR-VCS-001
- **RQ1–RQ8**→FR-DOC-004 (+ reports/vault as noted in §4).

## 10. Out of Scope (v1)
Multiple bugs; non-luigi targets; re-implementing Graphify; live-graded agent runs; a web UI; Neo4j push; languages other than Python in the target.

## 11. Approval Gates (the workflow)
- **Gate 1 (this doc)** — approve the PRD before any further docs.
- **Gate 2** — approve the full docs package (`Plan.md` + `Todo.md` ≥300 tasks + per-mechanism PRDs + ADRs + class-diagram plan) before writing code.
- Then: execute `Todo.md` one-by-one (marking `[x]`), README, run, push public — with continuous commits.

## 12. Open Questions
- OQ1 Deep (LLM) Graphify run: we run it once with Claude access and commit artifacts; confirm budget acceptable (it's small — luigi core only).
- OQ2 Naive-mode fairness: cap naive file reads at a realistic ceiling (config) so the comparison is honest, not strawmanned.
