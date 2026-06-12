# HW4 — Vibe Input (feed into Plan Mode to generate the PRD)

> This is the distilled "idea" prompt for the Vibe Coding Lifecycle. Read `CLAUDE.md` and `RULES.md` first. The raw spec text is in `IDEA-raw.txt`; the authoritative source PDF is `../materials/hw4-spec-ex04-graphify-obsidian-reverse-engineering.pdf` (10 pages). Lecture digests: `CONTEXT-lec07-pdfs.md` (+ `CONTEXT-lecture-07.md` when added).

## Mission (one sentence)
Build a Python project + a **graph-guided AI agent** that reverse-engineers an unfamiliar buggy Python codebase using **Graphify** (code→graph) and an **Obsidian** knowledge vault, finds → explains → fixes a real bug, and **proves it consumed fewer tokens** than naive raw-code reading.

## Title (spec cover)
**EX04 — Reverse Engineering, Debugging and Token-Efficient Agentic AI with Graphify and Obsidian** · Lecture L07 · ד"ר יורם סגל · June 2026 · spec v1.0.
Keywords (spec): Graphify, Obsidian, Reverse Engineering, Debugging, Token Efficiency, Agentic AI, CrewAI, LangGraph, graphical code representation, Knowledge Graph, God Nodes, **Lost in the Middle**, Context Window, `index.md`, `hot.md`, `graph.json`, OOP schema, architectural block schema, knowledge-based navigation, BugsInPy.

## Evaluation lens (spec §1, §8, + lecturer's standing dictum)
The grade centers on **the GitHub repo + README + the reports + the Obsidian vault** — proof of *process*, not just a working fix. The check is technical and runs on what you committed (tests with mock LLM; the grader does not run your live agent). README is graded heavily and must be rich with visuals.

## The 6 core tasks (spec §5) — verbatim intent
- **5.1 Graphify + Obsidian** — produce a graph representation of the codebase via Graphify; build a *real* Obsidian vault (active knowledge space, not a file dump). MUST include `index.md` (central entry: system structure + main navigation paths), `hot.md` (focused context for the bug-critical area), plus linked pages documenting key components, tests, findings, prime suspects, the fix.
- **5.2 Reverse-engineer unfamiliar code** — extract architectural insight; present **≥2 illustrations**: an **architectural block diagram** (main parts + flow) and an **OOP diagram** (classes, usage/composition/inheritance/wrappers/patterns). Folder listing ≠ acceptable.
- **5.3 Graph-guided AI agent** — build + run an agent in **CrewAI or LangGraph**. It MUST be graph-guided: rely on Graphify outputs + Obsidian pages first, request raw code snippets only afterward. Explain the workflow, each step/agent's role, and the context-reduction mechanisms you built.
- **5.4 Real fix** — actually fix the code; show problem, why it happened, the change, how success was verified; plus knowledge-level before/after (which Obsidian pages/nodes/links/insights were added).
- **5.5 Token-savings proof** — compare **naive mode** (agent/workflow over many raw files, unfocused) vs **graph-guided mode** (via Graphify, `index.md`, `hot.md`, Obsidian). Report at minimum: tokens consumed · files/text-units read · iterations/investigation rounds · quality/speed to root-cause + fix.
- **5.6 Original extensions** — ≥1 original extension/analysis/improvement per part. Examples the spec gives: rank suspect nodes by **centrality** or **proximity to failing tests**; generate a **dynamic `hot.md` from `git diff` + `graph.json`**; detect orphan components + auto-document them; spot vague coupling / mixed responsibility and propose refactoring; before/after architecture comparison; an **impact report** ("what breaks if I change this class/function").

## Base repository (spec §2) — pick one, justify in README
- **`soarsmu/BugsInPy`** — real bugs in real Python projects (most realistic; isolate in venv/Docker).
- **`martinpeck/broken-python`** — buggy Python snippets for debugging practice.
- **`andela/buggy-python`** — buggy scripts.
- **OR your own repo** — allowed only if substantial: **~10,000+ LOC, ≥70 code files** (stated in the submission box). Justify fit.

## Research questions (spec §4) — must be answered in README, reports, and Obsidian
Actual architecture & surprises · most-central components · complexity hotspots / mixed responsibility / **God Nodes** · how to extract block + OOP schemas from thin docs · how the bug was found + root cause + steps · advantage of graph representation + Obsidian vs linear reading · how graph-guided AI saved tokens · what further agent mechanisms you'd add.

## Open decisions (resolve with the user, then lock in PRD)
| # | Decision | Default / lean | Notes |
|---|---|---|---|
| 1 | Base repo | **BugsInPy** (one isolated bug) — or a small `broken-python` case if Python-env risk is a concern | Pick ONE small/medium bug (spec §6 Do). Don't over-scope. |
| 2 | Agent framework | **LangGraph** | Spec §6: easier to cap calls/steps on a free/limited account. CrewAI also allowed (HW3 reuse). |
| 3 | LLM provider | **Claude CLI login** | Same as HW3; keep Gatekeeper + budget enforcement. |
| 4 | Graphify source | **FIRST: locate & install the real Graphify tool** — the lecturer is explicit it's a free, downloadable CLI/Python tool that "each of you downloads" (transcript L280–288), producing `graph.json`/`graph.html`/`GRAPH_REPORT.md` with evidence layers (EXTRACTED/INFERRED/AMBIGUOUS) + confidence + God Nodes. The materials give NO install link → **task #1 is to find the exact tool** (search PyPI/GitHub for the one matching those outputs/evidence-layers; check the lecture slides/Moodle for a link; if unfindable, ask the lecturer). Use it via CLI and/or wrap from Python behind the Gatekeeper. **Fallback ONLY if the real tool is genuinely unavailable:** a self-contained `src/graphify/` AST→graph builder that reproduces the same `graph.json`/`GRAPH_REPORT.md` schema — document this choice in an ADR for reproducibility. Do NOT default to hand-rolling without first trying the real tool. |
| 5 | Token meter | Implement a token counter around every LLM call (via Gatekeeper) | Needed for §5.5 proof; log per-mode totals. |
| 6 | Repo placement | The target buggy repo as `target_repo/` (vendored or pinned commit) so the grader can reproduce | Reproducibility (lecturer's standing rule). |

## What you MUST do (non-negotiable)
- Build `graph.json` + `GRAPH_REPORT.md`; build the Obsidian vault with `index.md` + `hot.md` + linked pages.
- Graph-guided agent (graph/Obsidian consulted BEFORE raw code).
- Real bug fix + root-cause report + before/after (code & knowledge).
- Token-comparison report with the 4 metrics.
- Architectural block diagram + OOP diagram (in repo AND surfaced in README).
- ≥1 original extension.
- Rich README per spec §8 + visuals (screenshots, graphs, diagrams).
- Our engineering standards: SDK + **Gatekeeper wrapping every LLM call** + uv + ruff-clean + pytest ≥85% green + ≤150-line files + version single-source + **GitHub CI green (pin Python 3.13)** + continuous commits + ≥500-task TODO + two approval gates.

## What you must NOT do (spec §6.2 + our lessons)
- Don't over-scope (many bugs / huge project / final-project creep).
- Don't dump the whole codebase into the LLM at once — that's the anti-pattern the assignment exists to beat.
- Don't build a chatty multi-agent workflow with too many rounds.
- Don't start with BugsInPy if shaky on Python envs/deps.
- Don't skip docs — without strong README + screenshots + diagrams + tidy Obsidian you can't *prove* the process.
- Don't leave the Gatekeeper decorative (HW3 audit caught this — wire it to the real calls).
- Don't desync the version (HW3 lesson: `__init__` import from a single `version.py`).
- Don't let CI go red (HW3 lesson: CrewAI's bundled pydantic-v1 breaks on Python 3.14 — pin the runner to 3.13).
