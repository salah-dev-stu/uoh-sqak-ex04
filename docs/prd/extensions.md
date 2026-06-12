# Per-Mechanism PRD — Original Extensions (`src/graphguide/extensions/`)

> **Parent** `prd.md` §5.7 (FR-EXT-101/102/201/301) · **Plan** `Plan.md` §8, §13 (Phase P8, T491–T540)
> **Package** `graphguide` · **Module** `src/graphguide/extensions/` · **Course** 203.3763 · **Group** `uoh-sqak`
> **Spec mapping** §5.6 (≥1 original extension per part) · **Gate** H10 (original extensions) — this PRD ships **two**.
> **Status** Gate-2 companion · appends its tasks to the global `Todo.md`.

This PRD specifies the two original extensions that satisfy spec §5.6 / gate H10. Both are **read-only over the committed graph + vault** (they never mutate the target repo), both are **metered through the Gatekeeper** like every other capability, and both are exercised by **mock-LLM / fixture tests** so the grader sees them without an API key (grader Path D). Each extension exists not as a decorative add-on but because it **measurably reduces or clarifies work** and **feeds the two graded stories**: token-savings (§5.5 / H6) and code+knowledge before/after (§5.4 / H9).

---

## 1. Overview & Motivation

The base build already converts luigi into a Graphify graph and an Obsidian vault, then drives a graph-guided LangGraph agent. The two extensions sharpen the *start* and the *end* of that pipeline:

- **E1 — Suspect-ranking by proximity to failing test** sharpens the **start**: instead of letting the agent discover the prime suspect by trial, it seeds the agent's first move with a ranked suspect list, fusing graph centrality with graph-distance to the failing test. Fewer iterations, fewer raw-code reads → directly improves the token-savings story.
- **E2 — Knowledge before/after auto-diff** sharpens the **end**: instead of hand-writing "what we learned," it diffs the vault + graph before vs after the investigation and emits a reproducible artifact (`reports/knowledge_diff.md`) — auto-manufacturing the H9 knowledge-level before/after deliverable.

Both are original relative to the off-the-shelf tooling (see §3 for the originality argument).

---

## 2. Scope

**In scope**
- `extensions/suspect_ranker.py` — centrality × test-proximity ranking, output to `vault/suspects/` and as an agent seed.
- `extensions/knowledge_diff.py` — vault/graph before-vs-after diff → `reports/knowledge_diff.md`.
- Config-driven weights/paths; Gatekeeper metering; mock/fixture tests; README documentation block.

**Out of scope (v1)**
- Learned/ML ranking models — ranking is a transparent, configurable formula.
- Re-running Graphify or the live agent inside the diff — the diff consumes committed snapshots only.
- A third extension — two is sufficient for H10; further mechanisms are listed under README "Future work" (RQ8).

---

## 3. Why These Are Original (the H10 / spec-§5.6 argument)

**E1 vs Graphify's built-in centrality.** Graphify (and our `graphify/centrality.py`) already ranks nodes by **degree / betweenness centrality** — i.e. *structural importance in the abstract*. That answers "which node is a God Node," **not** "which node is likely to contain *this* bug." A God Node (e.g. luigi's `Task`) is central regardless of which test is failing. E1's contribution is to **fuse** that structural signal with a **failure-specific signal** — the NetworkX shortest-path graph-distance from the *failing test's node* to each candidate — so the ranking is **conditioned on the actual symptom**:

```
score = w1 · centrality_norm + w2 · (1 / (1 + dist_to_failing_test))
```

`centrality_norm` is the min-max-normalised centrality from `graphify/centrality.py`; `dist_to_failing_test` is the shortest-path hop count from the failing test node to the candidate node over `graph.json` (∞ → distance term contributes 0). `w1`, `w2` come from config (`config/agents.json` or `extensions` block), never code (R10). The result: a node that is both broadly central **and** topologically close to the failing test ranks highest — exactly the bug's locus (`Task.to_str_params`). Plain centrality alone would float every God Node to the top regardless of the symptom; plain distance alone would float trivial helper nodes adjacent to the test. The **fusion** is the original mechanism.

**E2 vs hand-written before/after.** Spec §5.4 / H9 demand a knowledge-level before/after. The naive way is to write two prose paragraphs by hand — unverifiable and non-reproducible. E2 makes it a **mechanical artifact**: it captures a vault+graph snapshot **before** investigation and **after** the fix, then computes the set differences (`nodes_added`, `links_added`, `pages_added`, `insights`) and renders `reports/knowledge_diff.md`. The deliverable becomes a reproducible, test-asserted output rather than a claim — which is exactly the rigor the rubric rewards.

---

## 4. Functional Requirements

### 4.1 Extension 1 — Suspect-ranking by proximity to failing test (`suspect_ranker.py`)
- **FR-EXT-101** Rank candidate buggy nodes by `score = w1·centrality_norm + w2·(1/(1+dist_to_failing_test))`, where `dist_to_failing_test` is the NetworkX shortest-path graph-distance from the failing test's node to the candidate, and `w1`/`w2` are loaded from config (not hardcoded). Produces a ranked `list[SuspectRank]` (`{node_id, label, centrality, dist_to_failing_test, score, rank}`, per `Plan.md` §3).
- **FR-EXT-101a** `centrality_norm` reuses `graphify/centrality.py` output (no duplicate centrality computation — R2/no-duplication); the ranker only *fuses* it with distance.
- **FR-EXT-101b** Unreachable candidates (no path to the failing-test node) get `dist_to_failing_test = ∞`, so the proximity term is `0` and the node ranks on centrality alone — never excluded, never crashing.
- **FR-EXT-102** The ranked list is written to `vault/suspects/` as linked Markdown (wikilinks + `#suspect` tag) **and** returned as the **seed for the agent's first move** so the graph-guided agent jumps to the prime suspect instead of discovering it — measurably **reducing agent iterations** (the reduction is recorded in the trace and surfaced in `reports/token_comparison.md`).

### 4.2 Extension 2 — Knowledge before/after auto-diff (`knowledge_diff.py`)
- **FR-EXT-201** Diff the vault **and** graph **before** investigation vs **after** the fix, computing `KnowledgeDiff` = `{nodes_added[], links_added[], pages_added[], insights[]}` (per `Plan.md` §3), and emit the H9 knowledge-level before/after artifact at **`reports/knowledge_diff.md`**.
- **FR-EXT-201a** Consumes the **before** snapshot (post-Graphify, pre-investigation — `FR-VAULT-006`) and the **after** snapshot (post-fix — `FR-VAULT-006`); it does not re-run Graphify or the agent.
- **FR-EXT-201b** `insights[]` are sourced from the agent's investigation trace / `vault/findings/` (e.g. "serialize/deserialize asymmetry in `Task`"), so the diff captures *understanding gained*, not just file churn.
- **FR-EXT-201c** `reports/knowledge_diff.md` is a **committed, reproducible** artifact regenerated deterministically from the two committed snapshots (grader Path D — no live run, no API key).

### 4.3 Cross-cutting
- **FR-EXT-301** Both extensions are documented in **README** with rationale (§3 of this PRD, condensed) + **example output** (a sample ranked-suspect table and a sample knowledge-diff excerpt), answering spec-§4 **RQ8** ("what further mechanisms?") with shipped proof.
- **FR-EXT-302** Both run **only through the SDK façade** (`GraphGuide.rank_suspects()`, `GraphGuide.knowledge_diff()` — `FR-SDK-001`); CLI exposes `suspects` and `knowledge-diff` (`FR-CLI-001`). No business logic in CLI/tests (R1).
- **FR-EXT-303** Both route any external/file access through the **Gatekeeper** (`FR-GATE-001`) and are **metered** (file/text units counted) so their cost is itself visible in the spend report (R3).
- **FR-EXT-304** All tunables (weights, snapshot paths, output paths, suspect-list size) live in **config** under an `extensions` block (`config/agents.json` or dedicated keys) — zero hardcoded values (R10).

---

## 5. Data Schemas (consumed / produced)

- **SuspectRank** (produced by E1): `{node_id, label, centrality, dist_to_failing_test, score, rank}` — matches `prd.md` §8 / `Plan.md` §3.
- **KnowledgeDiff** (produced by E2): `{nodes_added[], links_added[], pages_added[], insights[]}` — matches `Plan.md` §3.
- **Inputs**: `reports/graph/graph.json` (via `GraphLoader`), `graphify/centrality.py` output, failing-test node id, before/after vault+graph snapshots.

---

## 6. Acceptance Criteria

**E1 — Suspect ranking**
- **AC-E1-1** Given the committed fixture `graph.json` + a designated failing-test node, `rank_suspects()` returns a non-empty, deterministically-ordered `list[SuspectRank]` with `rank` contiguous from 1.
- **AC-E1-2** The score formula is applied exactly as in FR-EXT-101 with `w1`/`w2` read from config; a unit test asserts the computed score for a known fixture node matches the hand-derived value.
- **AC-E1-3** A node with no graph path to the failing-test node yields `dist_to_failing_test = ∞` and `proximity_term = 0` (no crash), ranking on centrality alone (AC asserts this edge case).
- **AC-E1-4** The prime suspect for bug 20 (`Task.to_str_params` / `Task` serialization) appears in the top suspects of the ranked list on the real luigi graph.
- **AC-E1-5** `vault/suspects/` is generated with valid wikilinks (link-integrity test passes — `FR-VAULT-007`) and `#suspect` tags.
- **AC-E1-6** In the integration test, the graph-guided run **seeded** by the ranker records **fewer iterations / fewer files read** than an unseeded baseline run, and the delta is reflected in `reports/token_comparison.md`.

**E2 — Knowledge before/after auto-diff**
- **AC-E2-1** Given committed before/after snapshots, `knowledge_diff()` returns a `KnowledgeDiff` whose `nodes_added` / `links_added` / `pages_added` equal the set differences between snapshots (unit test asserts against a crafted fixture).
- **AC-E2-2** `reports/knowledge_diff.md` is generated, non-empty, and lists each of the four sections (nodes, links, pages, insights) with the relevant vault pages added during the investigation (e.g. `suspects/`, `findings/`, `fix/`).
- **AC-E2-3** Regenerating the diff from the same committed snapshots is **byte-stable** (deterministic ordering) — a test asserts idempotency.
- **AC-E2-4** `insights[]` includes the root-cause insight (serialize/deserialize asymmetry) sourced from `vault/findings/` — satisfying the *knowledge-level* (not just file-count) requirement of H9.

**Cross-cutting**
- **AC-X-1** Both capabilities are reachable only via the SDK façade and the CLI commands `suspects` / `knowledge-diff`; a grep test asserts no direct business logic in CLI/tests (R1).
- **AC-X-2** Every file/external access in both extensions goes through the Gatekeeper; the bypass-grep test (`FR-GATE-003`) passes (R3).
- **AC-X-3** No tunable is hardcoded — weights/paths/sizes resolve from config (R10); a test loads them from `config/`.
- **AC-X-4** README contains the extensions section with rationale + example ranked-suspect table + knowledge-diff excerpt (FR-EXT-301), and answers RQ8.
- **AC-X-5** Coverage of `extensions/` contributes to the ≥85% suite (R9); all tests GREEN, offline (R6, NFR-TEST-003).

---

## 7. How These Tie Into the Graded Stories

| Extension | Reduces / clarifies work | Feeds graded deliverable |
|---|---|---|
| E1 Suspect ranking | Seeds the agent's first move → fewer iterations, fewer raw-code reads | **Token-savings** (§5.5 / H6): the iteration/file-read delta is part of the naive-vs-graph comparison |
| E2 Knowledge diff | Replaces hand-written before/after with a reproducible artifact | **Before/after at knowledge level** (§5.4 / H9): `reports/knowledge_diff.md` is the H9 artifact |

Both also answer spec-§4 **RQ7** (how graph-guidance saves tokens — E1 makes the saving concrete) and **RQ8** (what further mechanisms — E1/E2 are the shipped answer).

---

## 8. Traceability

- **Spec §5.6 / H10** → FR-EXT-101, FR-EXT-102, FR-EXT-201, FR-EXT-301 (this PRD).
- **H9 (knowledge before/after)** → FR-EXT-201 (+ FR-FIX-005).
- **RQ7 / RQ8** → FR-EXT-102, FR-EXT-301.
- **R1** → FR-EXT-302 · **R3** → FR-EXT-303 · **R10** → FR-EXT-304 · **R2** → FR-EXT-101a · **R9/R6** → AC-X-5.
- **Plan phases** → P8 (T491–T540): `suspect_ranker`, `knowledge_diff`, tests, `vault/suspects/`, `knowledge_diff.md`.
