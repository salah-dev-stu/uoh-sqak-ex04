# HW4 Upgrade Spec — "Strong → Standout"

> Post-audit enhancement plan. The submission already passes every gate (real bug+fix, 96.1% token proof, wired Gatekeeper, 100% cov, green CI, honest reporting). This spec adds the *superior* layer that makes a grader take notice — **without scope creep**. Execute under the same standards: TDD, ruff-clean, pytest ≥85% green, ≤150-line files, Gatekeeper-wired, honest reporting, GitHub CI green, continuous commits. Keep all existing tests passing.
>
> **Scope discipline (lecturer's explicit warning — don't make it a final project):** Do the 4 core upgrades below, deeply. The "Lost in the Middle" experiment is OPTIONAL (only if the 4 land cleanly with time to spare). Do NOT add more bugs, more frameworks, or more agents.

---

## Upgrade 1 (HEADLINE) — Rich, complex Obsidian knowledge graph + visuals
**Goal:** turn the sparse curated vault into a dense, auto-generated knowledge graph so Obsidian's Graph View renders the real luigi architecture (hubs, clusters, the scheduler God Node). This is the visual centerpiece the assignment is about.

**Build:**
- Extend `VaultBuilder` (or a new `vault_builder/graph_pages.py`) to **auto-generate one Markdown note per node in `graph.json`** (module / class / key function). Each note:
  - has `[[wikilinks]]` to its graph neighbors (mirror every edge — calls/imports/inheritance),
  - carries tags: `#god-node` (degree/centrality threshold from GRAPH_REPORT), `#suspect` (top suspect-rank), `#bug`, `#fixed`, and `#community/<id>` per detected community,
  - embeds a small Mermaid neighborhood diagram + one Dataview query (e.g. "nodes within 2 hops of the bug").
- Keep `index.md` and `hot.md` as the curated entry/hub pages; they now link into the dense graph.
- Idempotent + generated-from-data (no hand-faking edges). Cap note count sensibly (e.g. top-N by centrality + everything within K hops of the bug) so the graph is rich but not noise.

**Acceptance:**
- `vault/` has ≥30 interlinked notes generated from `graph.json` (assert count + that wikilinks match graph edges in a test).
- 3 README screenshots committed to `assets/`: (a) full Graph View showing clusters + the highlighted God Node, (b) **local graph centered on the bug node** with suspects highlighted, (c) graph **before vs after** the investigation (knowledge grew).
- A test verifies every generated wikilink target exists (no dangling links).

## Upgrade 2 — Genuinely iterative graph-guided agent (recover "iterations" honestly)
**Goal:** replace the single-pass runner with a real frontier-expansion loop, so iteration count becomes a *measured, favorable* metric (we honestly dropped it before because it was hardcoded).

**Build:**
- `run_graph_guided` does hop-by-hop expansion: start at `hot.md` seed nodes → read top suspect → if not conclusive, expand frontier by 1 hop, re-rank, repeat; stop on confidence or a `max_rounds` cap (from config).
- Record real `iterations` (rounds actually taken) in the meter/trace — no literal constant.
- Naive stays single-bulk-read (its honest baseline); the contrast is now rounds AND tokens AND files.

**Acceptance:**
- `iterations` is computed from the loop, asserted in a test (mock scripted so graph-guided converges in 2–3 rounds, naive in 1 bulk pass) — and the comparison table restores the **Iterations** row, now genuinely measured. Update `token_comparison.md` text accordingly (remove the "omitted" note).

## Upgrade 3 — One real-LLM demonstration run (proof beyond the mock)
**Goal:** convert the proof from "context reduction (mock)" to "context reduction **and** the model genuinely finds the bug graph-guided."

**Build:**
- A `scripts/real_run_demo.py` (or `make demo-real`) that runs the graph-guided agent once against the real Claude CLI/API, captures the trace + token usage from the Gatekeeper meter, and writes `reports/real_run.md` (+ raw trace json).
- Tests/CI stay on the MockLLM (grader Path D unchanged — no key needed). The real run is a committed artifact, not a CI dependency.

**Acceptance:**
- `reports/real_run.md` shows the real agent's path (nodes visited), the real token count, and the correct root cause. README links it. `token_comparison.md`'s "what this measures" note is updated: the mock proves reduction deterministically; the real run confirms genuine success.

## Upgrade 4 — Interactive `graph.html` (a navigable artifact, not just JSON)
**Goal:** a browser-openable interactive graph the grader can click through.

**Build:**
- Have the Graphify runner also emit `graph.html` (pyvis/vis-network or d3 from `graph.json`) — nodes sized by centrality, colored by community, God Nodes marked, the bug node highlighted.
- Screenshot into `assets/`, embed/link in README.

**Acceptance:** `graphify-out/graph.html` exists and renders the graph offline; README has the screenshot + a "open this file" pointer.

---

## Upgrade 5 (OPTIONAL — only if 1–4 land with time) — "Lost in the Middle," demonstrated
Show the lecture's core thesis with your own data: bury the bug-relevant code mid-context in the naive 22 K-token dump and show the model misses/degrades, vs the focused graph-guided context where it succeeds. Write `reports/lost_in_the_middle.md` with the experiment + result. This is the "original thinking" flex — but skip it if it risks the core 4.

---

## README integration (where the "wow" lands)
The visuals are graded — make §4 (architecture) and §7 (Obsidian) and §10 (token efficiency) of the README *show*, not tell:
- Obsidian Graph View screenshots (full + bug-centered + before/after)
- `graph.html` screenshot
- the token-savings bar chart (already have the numbers)
- block + OOP diagrams rendered
One coherent story: *"unfamiliar codebase → navigable visual knowledge graph → agent traverses it to the bug in few rounds on a fraction of the tokens → here's the picture, the real run, and the proof."*

## Definition of done
All existing gates still green (ruff, pytest ≥85%, CI), all new tests green, vault graph renders with screenshots committed, iterations measured, real run recorded, graph.html present, README visually rich. Self-grade can then honestly move to ~88. Continuous commits, push to `origin`.
