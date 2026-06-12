# Per-Mechanism PRD — Obsidian Vault Layer (`vault_builder/` → `vault/`)

> **Parent** `prd.md` §5.2 (FR-VAULT-001..007) · `Plan.md` §1 (`src/graphguide/vault_builder/`), §7 (Vault Workflow)
> **Course** 203.3763 "Orchestration of AI Agents" · University of Haifa · Spring 2026 · Dr. Yoram Segal
> **Group** `uoh-sqak` — Salah Qadah (323039974) + Andalus Kalash (211435797)
> **Package** `graphguide` · **Mechanism owner** `src/graphguide/vault_builder/` (`builder.py`, `pages.py`)
> **Target system** `spotify/luigi` (≈21.7k LOC, 82 files) · **Bug** BugsInPy bug 20 — `Task.to_str_params`
> **Spec gates** H3 (vault: `index.md` + `hot.md` + linked pages), H9 (knowledge-level before/after)
> **Appends tasks to** `Todo.md` (P3 range T201–T260, per the per-feature workflow)

This per-mechanism PRD expands the master PRD's §5.2 into the design contract for the Obsidian vault layer. It defines the mechanism that turns Graphify's raw `obsidian/` export into a **curated, navigable knowledge space** the graph-guided agent reads *before* touching raw code.

---

## 1. Purpose — why a vault, not a folder of notes

The vault is the **knowledge surface** of this project: a real Obsidian knowledge space, **not a file dump**. Its job is to let a developer (or our agent, persona P2) reach the root cause of bug 20 without reading 82 files. Two lecture themes govern its shape:

- **Active Knowledge.** The vault is not passive documentation. Pages are *operational*: `index.md` is the agent's mandatory first read; `hot.md` is the working focus that is *rewritten during* the investigation; `log.md` is an append-only decision trace. Knowledge is produced and consumed inside the loop, not filed away afterward.
- **"Lost in the Middle."** Long unfocused context decays — mid-context information is effectively ignored. The vault counters this by keeping **strong information at the start and end** of every page and a **deliberately small, focused middle**. `index.md` puts the navigation hub up front; `hot.md` holds only the bug-critical neighborhood (the `Task`/`Parameter` serialization area) so the agent never carries the whole codebase in-window. Short, linked pages beat one long page every time.

The vault is therefore the bridge from Graphify's graph (`graph.json`, §5.1) to the agent's disciplined reading order (§5.3): **index → hot → graph query → only-then code**.

## 2. Scope & ownership

- **In scope:** generation of the base vault from Graphify output; curation into `vault/`; the required pages (`index.md`, `hot.md`, `log.md`); the linked page tree (`components/`, `tests/`, `findings/`, `suspects/`, `fix/`); wikilink + tag conventions; link-integrity checking; before/after vault snapshots feeding H9.
- **Owned modules:** `src/graphguide/vault_builder/builder.py` (curate Graphify `obsidian/` → `vault/`), `src/graphguide/vault_builder/pages.py` (page templates: `hot.md` / `log.md` / suspects / fix).
- **Out of scope (owned elsewhere):** Graphify extraction and `graph.json` (§5.1, `graphify/`); suspect *ranking* logic (§5.6, `extensions/suspect_ranker.py` — the vault only *renders* the ranked list into `suspects/`); the knowledge *diff* engine (§5.6, `extensions/knowledge_diff.py` — the vault only *provides* the before/after snapshots it consumes); the agent's reading loop (§5.3).

## 3. How the vault is produced

### 3.1 Base vault from Graphify
Graphify, when run over `target_repo/luigi/`, emits an `obsidian/` directory alongside `graph.json`: an `index.md` plus **per-community and per-node notes** (a note per file/class/function cluster, with wikilinks tracking the extracted call/import/inheritance edges). This is the raw substrate — accurate but unfocused, with no notion of *which* nodes matter for our bug. Per `Plan.md` §6, Graphify's `obsidian/` is copied into `reports/graph/`/base output as the pre-curation snapshot.

### 3.2 Curation by `builder.py`
`builder.py` curates that base export into `vault/`:
- Promotes Graphify's `index.md` into a true **navigation hub** (§4.1) — system structure + the Portfolio→Domains→Components paths — rather than a flat node listing.
- Selects the bug-critical neighborhood (the `Task`/`Parameter` serialization nodes, identified via `graph.json` + centrality) and seeds `hot.md`.
- Lays down the linked-page tree skeleton (`components/`, `tests/`, `findings/`, `suspects/`, `fix/`).
- Preserves real wikilinks from Graphify's extracted edges so navigation mirrors actual code relationships.

### 3.3 Page emission by `pages.py`
`pages.py` holds the page **templates** and emits living pages from agent findings + the suspect ranker:
- `hot.md` (refreshed during investigation), `log.md` (appended per decision).
- `suspects/` pages from the ranked suspect list (extension output).
- `tests/`, `findings/`, `fix/` pages as the investigation produces them.

This split keeps `builder.py` (structure/curation) and `pages.py` (content templates) each within the ≤150-logical-line limit (R7); split further if either takes on two jobs.

## 4. Required pages (the H3 contract)

### 4.1 `vault/index.md` — central navigation hub  *(FR-VAULT-002)*
- The agent reads this **FIRST** (enforced by the agent state machine, FR-AGENT-002).
- Content, strong-info-first: a compact statement of luigi's **system structure** (CLI/interface · Task/Register · Scheduler · Worker · Target/FileSystem · Parameter) and the **main navigation paths** organized **Portfolio → Domains → Components**, with wikilinks to the key pages.
- It is a hub, not an encyclopedia: it points outward (links to `components/`, `hot.md`, `suspects/`) and stays short so the navigation map sits at the high-attention top of context.

### 4.2 `vault/hot.md` — focused bug context  *(FR-VAULT-003)*
- The **focused context page for the bug-critical area**: the `Task`/`Parameter` **serialization** neighborhood — `Task.to_str_params`, `Task.from_str_params`, the `Parameter` hierarchy, and the serialize/deserialize asymmetry at the heart of bug 20.
- **Refreshed during investigation**: as the agent queries the graph and reads code, `hot.md` is rewritten to hold the *current* working set only — embodying the focused-middle principle so the window never bloats.
- Deliberately small: only the nodes/links/snippets the agent needs right now; everything else lives one wikilink away.

### 4.3 `vault/log.md` — decision / investigation trace  *(FR-VAULT-004)*
- Append-only **query → finding → action** trace of the investigation: each step records what was asked of the graph/vault, what was learned, and what was done next.
- Tagged with `#decision` so the reasoning path is reconstructable and feeds the bug-analysis investigation-path narrative (FR-FIX-005).

### 4.4 Linked pages  *(FR-VAULT-005)*
Under `vault/`, a real linked tree (wikilinks + tags, not a dump):
- `components/` — key classes: **Task**, **Parameter**, **Scheduler**, **Worker**, **Target** (one page each, cross-linked to the graph nodes).
- `tests/` — the failing regression test (`test_task_to_str_to_task`).
- `findings/` — investigation findings as they accrue.
- `suspects/` — the prime-suspect pages rendered from the suspect ranker (`#suspect`).
- `fix/` — the root cause + the applied fix (`#fix`).

## 5. Wikilink & tag conventions

- **Wikilinks:** `[[Target]]` for page references; `[[components/Task|Task]]` with display alias where a path is needed. Links mirror real extracted edges (call/import/inheritance) so navigation = code reality.
- **Tags:** a small controlled vocabulary —
  - `#suspect` — a node under suspicion (lives in `suspects/`, also tagged in `hot.md`/`findings/`).
  - `#fix` — the fix and its verification (`fix/`).
  - `#decision` — an investigation decision/turn (`log.md`).
  - (supporting, consistent use): `#component`, `#test`, `#finding`, `#godnode`.
- **Page front-matter (optional, consistent):** lightweight YAML (`title`, `tags`) where it aids Obsidian graph view; never a substitute for inline links.
- Strong-info-first within every page: a one-line "what this is / where to go next" header and a "links" footer, focused middle between.

## 6. Link-integrity check  *(FR-VAULT-007)*

A test asserts **no dangling wikilinks**: every `[[…]]` target resolves to an existing page (or section) in `vault/`. Implementation: scan all `vault/**/*.md`, extract wikilink targets, resolve against the set of pages, fail on any unresolved target. Runs in the unit suite (`Plan.md` §10), offline, no API key. This is what keeps the vault a *coherent knowledge space* rather than a pile of half-linked notes.

## 7. Before/after snapshots → knowledge-level before/after  *(FR-VAULT-006, feeds H9)*

- **Before snapshot:** captured **post-Graphify, pre-investigation** — the base curated vault before the agent learns anything.
- **After snapshot:** captured **post-fix** — the vault enriched with findings, suspects, the root cause, the fix, and the new links/insights the investigation produced.
- The vault layer's responsibility ends at producing two faithful snapshots; `extensions/knowledge_diff.py` (FR-EXT-201) consumes them to emit `reports/knowledge_diff.md` — the **H9 knowledge-level before/after** artifact (nodes/links/pages/insights added). This pairs with the code-level before/after (FR-FIX-005) to satisfy H9 end-to-end.

## 8. Functional Requirements (traceability)

| FR | Requirement | Owned by |
|----|-------------|----------|
| **FR-VAULT-001** | Generate the base vault via Graphify (`obsidian/`), then curate it into `vault/`. | `builder.py` (consumes Graphify output) |
| **FR-VAULT-002** | `index.md` — central entry: system structure + main navigation paths (Portfolio→Domains→Components), wikilinks to key pages. Agents read this FIRST. | `builder.py` |
| **FR-VAULT-003** | `hot.md` — focused context for the bug-critical area (`Task`/`Parameter` serialization), refreshed during investigation. | `pages.py` |
| **FR-VAULT-004** | `log.md` — decision/investigation log: query → finding → action trace. | `pages.py` |
| **FR-VAULT-005** | Linked pages: `components/`, `tests/`, `findings/`, `suspects/`, `fix/` with real wikilinks + tags (`#suspect`/`#fix`/`#decision`). | `builder.py` (tree) + `pages.py` (content) |
| **FR-VAULT-006** | Before (pre-investigation) + after (post-fix) vault snapshots powering the knowledge-level before/after. | `builder.py` |
| **FR-VAULT-007** | Link-integrity check (no dangling wikilinks) runs in tests. | test suite over `builder.py` output |

Upstream/downstream: consumes `graphify/` outputs (§5.1); fed by `extensions/suspect_ranker` (suspects rendering) and `agent/trace` (findings/log); produces snapshots for `extensions/knowledge_diff` (§5.6); wired through the SDK via `GraphGuide.build_vault()` (FR-SDK-001).

## 9. Acceptance Criteria

1. **AC-1 (FR-VAULT-001):** Running `GraphGuide.build_vault()` after a Graphify run produces a populated `vault/` curated from Graphify's `obsidian/` export — verifiable from committed artifacts, no live LLM.
2. **AC-2 (FR-VAULT-002):** `vault/index.md` exists, opens with luigi's system structure, and presents the Portfolio→Domains→Components navigation with resolving wikilinks to `components/`, `hot.md`, and `suspects/`.
3. **AC-3 (FR-VAULT-003):** `vault/hot.md` exists and is scoped to the `Task`/`Parameter` serialization neighborhood (names `Task.to_str_params` and `from_str_params`); a test confirms it is regenerated/refreshable from current findings.
4. **AC-4 (FR-VAULT-004):** `vault/log.md` exists as an append-only query→finding→action trace, entries tagged `#decision`.
5. **AC-5 (FR-VAULT-005):** `components/{Task,Parameter,Scheduler,Worker,Target}.md`, plus `tests/`, `findings/`, `suspects/`, `fix/` pages exist with real wikilinks and the `#suspect`/`#fix`/`#decision` tags applied where due.
6. **AC-6 (FR-VAULT-007):** The link-integrity test passes — zero dangling wikilinks across `vault/**/*.md` — and fails loudly if a target is removed.
7. **AC-7 (FR-VAULT-006 → H9):** A before snapshot (pre-investigation) and an after snapshot (post-fix) are produced and committed; `knowledge_diff.py` can diff them into `reports/knowledge_diff.md`.
8. **AC-8 (quality):** `builder.py` and `pages.py` each ≤150 logical lines (R7), ruff-clean (R8), covered by tests counting toward ≥85% (R9); no hardcoded paths/values — vault/output locations come from config (R10).

## 10. Open Questions

- **OQ-V1:** Snapshot mechanism — copy `vault/` to `vault_snapshots/{before,after}/` vs. git-tag the tree. Default: directory copies committed under `reports/` so the grader sees both without git archaeology (aligns with NFR-REPRO-001).
- **OQ-V2:** How much of Graphify's per-node `obsidian/` to carry into `components/` vs. summarize — default to summarized, bug-relevant components to keep the focused-middle small.
