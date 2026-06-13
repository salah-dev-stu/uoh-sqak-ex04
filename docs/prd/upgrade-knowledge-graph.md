# PRD — Upgrade: "Strong → Standout" (post-audit enhancement)

> Per-feature PRD for the upgrades in [`UPGRADE-SPEC.md`](../../UPGRADE-SPEC.md). The submission already
> passes every gate; this adds the *superior* visual + proof layer **without scope creep** (lecturer's
> warning: don't make it a final project). Same standards: TDD, ruff-clean, pytest ≥85% green,
> ≤150 logical lines/file, Gatekeeper-wired for any external call, honest reporting, GitHub CI green,
> continuous commits, all existing tests still passing. Tasks append to the global `Todo.md`.
> **Approval gates apply; STOP after Upgrade 1 for user review.** Version bumps +0.01 per upgrade.

## Goals
- G1 Make Obsidian's **Graph View render the real luigi architecture** from a dense, auto-generated,
  data-faithful vault (hubs, communities, the scheduler/Task God Nodes, the bug + suspects).
- G2 Recover **iterations** as a genuinely-measured, favorable metric via a real frontier-expansion loop.
- G3 Add a **real-LLM demonstration run** proving the model finds the bug graph-guided (beyond the mock).
- G4 Ship an **interactive `graph.html`** the grader can click through.
- G5 (optional) Demonstrate **"Lost in the Middle"** with our own data.

## Non-goals
No new bugs, frameworks, or agents. No change to the grader path (tests stay on MockLLM, no key needed).
The real run + screenshots are committed artifacts, never CI dependencies.

---

## Upgrade 1 (HEADLINE) — Dense auto-generated Obsidian knowledge graph + real screenshots
`src/graphguide/vault_builder/graph_pages.py`

- **FR-UPG1-001** Auto-generate one Markdown note per **selected** graph node into `vault/nodes/<node_id>.md`,
  generated entirely from `graph.json` (no hand-faked edges; idempotent/deterministic).
- **FR-UPG1-002** Selection set `S` = **top-N by centrality ∪ all nodes within K hops of the bug node**
  (N, K, and a hard `max_notes` cap from config). Rich but bounded — no 2253-node noise.
- **FR-UPG1-003** Each note emits `[[wikilinks]]` mirroring its graph edges, **restricted to neighbors that
  are also in S** — guarantees zero dangling links while staying faithful to the real subgraph.
- **FR-UPG1-004** Each note carries tags: `#god-node` (if flagged in the God-Node report), `#suspect` (top
  suspect-rank), `#bug` (the bug node), `#fixed` (post-fix), `#community/<id>` (from `graph.json`).
- **FR-UPG1-005** Each note embeds a small **Mermaid neighborhood diagram** + one **Dataview** query
  (e.g. list nodes in the same community / within 2 hops of the bug).
- **FR-UPG1-006** `index.md` and `hot.md` remain curated hubs and now link **into** the dense graph.
- **FR-UPG1-007** `vault/` has **≥30 interlinked generated notes**; a test asserts the count and that the
  wikilinks match `graph.json` edges (restricted to S).
- **FR-UPG1-008** A test verifies **no dangling wikilinks** across the whole vault.
- **FR-UPG1-009** Capture **3 real Obsidian Graph View screenshots** into `assets/`: (a) full graph showing
  clusters + the highlighted God Node, (b) local graph centered on the bug node with suspects highlighted,
  (c) **before vs after** the investigation (sparse base → dense + investigation layer).
- **FR-UPG1-010** README §4/§7 embed the 3 screenshots; the visuals *show*, not tell.

**Acceptance (U1):** ≥30 generated notes; wikilinks ↔ edges test green; no-dangling test green; 3 Obsidian
screenshots committed + embedded; all prior tests still pass; ruff clean; ≤150-line files; version → 1.01.

## Upgrade 2 — Genuinely iterative graph-guided agent
- **FR-UPG2-001** `run_graph_guided` performs hop-by-hop **frontier expansion**: seed at `hot.md` nodes →
  read top suspect → if inconclusive, expand frontier 1 hop, re-rank, repeat; stop on confidence or
  `max_rounds` (config).
- **FR-UPG2-002** Record **real** `iterations` (rounds taken) in the trace/meter — no literal constant.
- **FR-UPG2-003** Naive stays single-bulk-read (its honest baseline).
- **FR-UPG2-004** A test asserts graph-guided converges in 2–3 rounds (mock scripted), naive in 1; restore
  the **Iterations** row in `token_comparison.md` (remove the "omitted" note) — now genuinely measured.

## Upgrade 3 — One real-LLM demonstration run
- **FR-UPG3-001** `scripts/real_run_demo.py` runs the graph-guided agent once against the real LLM,
  routed through the **Gatekeeper** (metered), and writes `reports/real_run.md` + raw trace JSON.
- **FR-UPG3-002** LLM access: prefer a Claude-CLI-backed client (shell out via Gatekeeper, no API key
  required) so it uses the user's login; fall back to `ANTHROPIC_API_KEY` if present. **Decided at U3.**
- **FR-UPG3-003** Tests/CI stay on MockLLM (grader Path D unchanged). The real run is a committed artifact.
- **FR-UPG3-004** `reports/real_run.md` shows the real path (nodes visited), real token count, correct root
  cause; README links it; `token_comparison.md` note updated (mock proves reduction; real run confirms success).

## Upgrade 4 — Interactive `graph.html`
- **FR-UPG4-001** Emit an interactive `graph.html` (pyvis/vis-network from `graph.json`): node size =
  centrality, color = community, God Nodes marked, bug node highlighted.
- **FR-UPG4-002** Screenshot via headless **Playwright** into `assets/`; embed/link in README ("open this file").
- **FR-UPG4-003** Renders offline; a test asserts the HTML is produced and contains the node/edge data.

## Upgrade 5 (OPTIONAL) — "Lost in the Middle," demonstrated
- **FR-UPG5-001** Bury bug-relevant code mid-context in the naive dump; show the model misses/degrades vs
  the focused graph-guided context where it succeeds. Write `reports/lost_in_the_middle.md`. Skip if it
  risks the core 4.

## Rubric / standards traceability
U1→H3 (vault) + H7/H8 visuals + H9 (before/after grows) · U2→H6 (iterations metric) · U3→H6/H5 (real proof) ·
U4→H2 (graph artifact). All keep R3 (Gatekeeper), R6–R9 (tests/ruff/lines/cov), R13 (CI), honest reporting.

## Definition of done
All prior gates green; new tests green; vault graph renders with real Obsidian screenshots committed;
iterations measured; real run recorded; `graph.html` present; README visually rich. Self-grade may honestly
move toward ~88. Continuous commits; push to `origin`.
