# Per-Mechanism PRD — Graph-Guided Agent (`src/graphguide/agent/`)

> **Parent** `prd.md` §5.4 (FR-AGENT-001..009) · **Plan** `Plan.md` §5 (Agent Design) · **Spec** 5.3 · **Gate** H4
> **Framework** LangGraph `StateGraph` (explicit state machine) · **Package** `graphguide` · **Version** starts `1.00`
> **Status** Gate-2 companion (per-mechanism PRD) · ADR: `docs/adr/0002-langgraph-over-crewai.md`

This PRD specifies the graph-guided investigation agent — the mechanism that satisfies spec 5.3 and gate H4. It refines, but does not contradict, the master PRD's FR-AGENT-001..009. Its tasks are appended to the global `Todo.md` (phase **P5**, T301–T400) per the per-feature workflow.

---

## 1. Overview & Problem Statement

A naive LLM debugging loop dumps many raw files into the context window, wasting tokens and triggering **"Lost in the Middle"** — the buggy lines, buried mid-context, get ignored. This mechanism replaces that loop with a **disciplined LangGraph state machine** whose central rule is: **consult the graph and the Obsidian vault FIRST, and read raw code ONLY for the few nodes the graph identifies.** That ordering is the context-reduction mechanism the whole project is built to prove.

The same machine exposes a **naive baseline** behind the identical `investigate()` interface so that the two modes can be compared on an honest, shared success bar (the token report, FR-TOKEN-*).

**Target bug (the success criterion):** luigi `Task.to_str_params` silently drops parameters declared `significant=False`, while `Task.from_str_params` indexes *all* declared params — so a `task → str → task` round-trip raises `KeyError: 'insignificant_param'`. The agent must **locate** `Task.to_str_params`, **explain** the serialize/deserialize asymmetry as root cause, and **propose** the 3-line fix (drop the `significant` guard). In tests this is verified against the known answer via a deterministic **MockLLM** — no API key required (grader Path D).

## 2. Goals / Non-Goals

**Goals**
- AG1 An explicit LangGraph `StateGraph` with an **enforced node order** (no skipping the graph/vault to reach code).
- AG2 Two modes — **naive** and **graph-guided** — behind one `investigate(mode=…)` interface, sharing `state`, `tools`, and `trace` for a fair comparison.
- AG3 Hard **iteration / token / file budgets** from config; graceful stop on exceed.
- AG4 Every LLM call routed through the **Gatekeeper** (token meter + rate-limit + budget).
- AG5 A **budgeted file-reader** that returns only a requested node's source span, never whole files/repo.
- AG6 A structured **`InvestigationTrace`** (steps, nodes visited, files read, tokens/step) that feeds `reports/token_comparison.md`.
- AG7 A **MockLLM** injected in tests → deterministic, offline, no API key.
- AG8 Each node's role and its context-reduction mechanism documented (spec 5.3).

**Non-Goals**
- NAG1 Not a chatty multi-agent crew — one disciplined state machine (master NG2).
- NAG2 Not re-running luigi's full suite — the one regression test stands alone (master NG4).
- NAG3 Not inventing graph data — the agent reads Graphify outputs + vault, it does not build them.
- NAG4 No web UI, no streaming UI; the trace is the observable surface.

## 3. State Machine Design

The agent is a LangGraph `StateGraph` over a single `AgentState`:

```
AgentState = {
  task, mode, phase,
  nodes_visited[], files_read[], budget_remaining{tokens,files,iters},
  suspects[], findings, fix_proposal, trace[]
}
```

### 3.1 Graph-guided node order (enforced)

```
        ┌──────────────────────────── conditional loop ───────────────────────────┐
        ▼                                                                           │
read_index → read_hot → rank_suspects → query_graph → read_code → diagnose ─┐  not confident /
 (vault)      (vault)    (extension)     (graph,      (budgeted,   (LLM)     │  budget left
                                          offline)     suspects                       │
                                          metered)     only)                          │
                                                                            confident │
                                                                                ▼     │
                                                                          propose_fix ┘
```

The conditional edge out of `diagnose`: **confident → `propose_fix`** (terminal); **not confident AND budget remains → loop back to `query_graph`/`read_code`**; **budget exhausted → graceful stop** with the best partial finding recorded in the trace. The order is **enforced in graph topology**, not by convention: there is no edge from `read_index`/`read_hot` directly to `read_code`. Raw code is reachable only *after* the graph/vault nodes — this is the hard rule of AG1 and the project's core context-reduction mechanism.

### 3.2 Per-node role + context-reduction mechanism (FR-AGENT-009 / AG8)

| Node | Role | Context-reduction mechanism |
|---|---|---|
| `read_index` | Read `vault/index.md` — system structure + main navigation paths. The agent's first and cheapest orientation. | One small curated page replaces scanning 82 files for structure. |
| `read_hot` | Read `vault/hot.md` — focused context on the bug-critical area (`Task`/`Parameter` serialization). | Pre-narrowed to the suspect region; no broad reading to "find where to look". |
| `rank_suspects` | Seed from the **suspect-ranking extension** (FR-EXT-101): rank candidate nodes by centrality + graph-distance to the failing test's node. | Produces a short ordered suspect list so the agent jumps to the prime suspect instead of breadth-first reading. |
| `query_graph` | Offline graph operations via the SDK: `query --budget N`, `explain`, `path`, `affected`. All metered, no LLM, no file I/O. | Answers "who calls this / what breaks / shortest path" from `graph.json` — structural facts without reading source. |
| `read_code` | The **only** node that touches source, via the **budgeted file-reader**: returns the source span of **top-ranked suspect nodes only**, capped by `max_files`. | Reads a few function bodies, not whole files/repo; each read is metered and counted as a unit. |
| `diagnose` | LLM call (via Gatekeeper) over the assembled compact context → root-cause hypothesis + confidence. | Operates on a small, relevant context (vault + graph facts + a few spans), avoiding "Lost in the Middle". |
| `propose_fix` | LLM call → the concrete change (drop the `significant` guard in `to_str_params`) + verification note. | Final, single focused call; terminal. |

### 3.3 Naive baseline (same interface, same success bar)

The naive runner shares `state`, `tools`, and `trace` but uses a different topology: **`read_code` (linear over many raw files, capped by `naive_max_files` from config) → `diagnose` → `propose_fix`** — with **no** `read_index`/`read_hot`/`rank_suspects`/`query_graph`. It must reach the *same* success criterion (locate + explain + fix the same bug) so the token comparison is honest, not a strawman. The file cap (OQ2) keeps the baseline realistic rather than unbounded.

## 4. Functional Requirements (refines FR-AGENT-001..009)

- **FR-AGENT-001** Implemented as an explicit LangGraph `StateGraph` (state machine), not an ad-hoc loop.
- **FR-AGENT-002** Enforced order: `read_index → read_hot → rank_suspects → query_graph → read_code → diagnose → propose_fix`. No topological path reaches `read_code` before the graph/vault nodes (graph-guided mode).
- **FR-AGENT-003** Every LLM call (`diagnose`, `propose_fix`) routes through `ApiGatekeeper` (token meter + rate-limit + budget). A grep test asserts no LLM client is constructed/called outside `agent/llm.py` → Gatekeeper.
- **FR-AGENT-004** Hard caps from `config/rate_limits.json`: `max_iterations`, `max_tokens` (per mode), `max_files`. Exceeding any → graceful stop with partial result + reason in trace; never an unbounded run.
- **FR-AGENT-005** Two modes behind one `investigate(mode={naive,graph})` interface, sharing state/tools/trace and the same success criterion.
- **FR-AGENT-006** Emits a structured `InvestigationTrace`: ordered steps each with `{node, mode, nodes_visited, files_read, prompt_tokens, completion_tokens, total_tokens}`; consumed by the token report (FR-TOKEN-*).
- **FR-AGENT-007** A **budgeted file-reader tool**: input = node id (or file + source span); returns only that span; metered; refuses reads beyond `max_files`. Never reads the whole repo.
- **FR-AGENT-008** Agent goal = locate the buggy function + explain root cause + propose the fix; verifiable against the known answer in tests via the **MockLLM** (deterministic, scripted by prompt key).
- **FR-AGENT-009** Each node/step's role + its context-reduction mechanism documented (§3.2 above; mirrored in README + `vault/`).

## 5. Determinism & Test Strategy (grader Path D)

- `agent/llm.py` accepts an **injected client**. Production injects the Gatekeeper-wrapped Claude client; tests inject a **MockLLM** returning **scripted answers keyed to prompt content** (e.g., a prompt containing `to_str_params` → the canned root-cause + fix). No network, no API key.
- **Unit**: state transitions, the budgeted reader's span/cap behavior, conditional-edge logic (confident vs loop vs budget-stop), trace accumulation.
- **Integration**: full `investigate()` in **both** modes over a committed fixture `graph.json` + vendored luigi slice → asserts (a) the bug is located (`Task.to_str_params`), (b) graph-mode reads **fewer files and fewer tokens** than naive, (c) both meet the success bar.
- All fixtures committed; coverage ≥85%; suite GREEN (R6, R9).

## 6. Interfaces & Dependencies

- **Entry**: `GraphGuide.investigate(mode=…)` (SDK façade) → `agent/graph_guided.py` or `agent/naive.py`, both building a `StateGraph` over shared `agent/state.py`.
- **Reads (graph)**: `graphify` query wrappers (FR-GRAPH-006) — offline, metered.
- **Reads (code)**: `tools/file_reader.py` (budgeted) — metered.
- **Reads (vault)**: `vault/index.md`, `vault/hot.md`.
- **Seeds**: `extensions/suspect_ranker.py` (FR-EXT-101) for `rank_suspects`.
- **All external calls**: through `shared/gatekeeper.py` (FR-GATE-*) — LLM and file reads alike.
- **Config**: `config/agents.json` (model, temperature, prompt refs, success criterion), `config/rate_limits.json` (budgets/caps). No tunable in code (R4, R10).
- File-size discipline: split `agent/nodes.py` (node functions) from `agent/graph_guided.py` (assembly) to stay ≤150 logical lines (R7).

## 7. Acceptance Criteria

- **AC1** A LangGraph `StateGraph` exists with the §3.1 nodes and edges; a test asserts no edge reaches `read_code` before the graph/vault nodes in graph mode.
- **AC2** `investigate(mode="graph")` and `investigate(mode="naive")` both run end-to-end with the MockLLM and both **locate `Task.to_str_params`** and **propose dropping the `significant` guard**.
- **AC3** Graph mode's recorded totals (files read AND total tokens) are **strictly less** than naive mode's on the same bug (asserted in the integration test).
- **AC4** Budgets from config are honored: a test that sets `max_files`/`max_tokens`/`max_iterations` low triggers a **graceful stop** with a partial finding + reason in the trace (no crash, no unbounded run).
- **AC5** A grep test confirms every LLM call and file read goes through the Gatekeeper (no bypass).
- **AC6** The emitted `InvestigationTrace` contains per-step tokens + files for both modes and is consumed by `reports/token_comparison.md` (FR-TOKEN-002/003).
- **AC7** No API key is needed for any test (Path D); suite GREEN; coverage ≥85%; ruff clean; every file ≤150 logical lines.
- **AC8** §3.2 (per-node role + context-reduction) is reproduced in README and `vault/` (FR-AGENT-009, FR-DOC-001).

## 8. Traceability

- **Spec 5.3 / H4** → this PRD (FR-AGENT-001..009).
- **FR-AGENT-003/007** → **FR-GATE-001..003** (Gatekeeper wraps LLM + file reads).
- **FR-AGENT-006** → **FR-TOKEN-001..006** (trace feeds the token report).
- **rank_suspects** → **FR-EXT-101/102** (suspect-ranking extension).
- **R1** → SDK entry `investigate()`; **R6/R9** → §5; **R7** → §6 split; **R3/R4/R10** → §6 config + Gatekeeper.
- ADR **0002-langgraph-over-crewai** records the framework choice this PRD assumes.
