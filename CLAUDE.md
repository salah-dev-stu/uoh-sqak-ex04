# HW4 Worker Session — Orchestration of AI Agents (Course 203.3763)

## Who you are
You are the **HW4 worker session**. The orchestrator (in `/Users/salah/Projects/orch-ai-agents/`) read the course materials, pulled everything off Moodle, and scaffolded this directory for you:

- **`CLAUDE.md`** (this file) — orientation, rules, workflow, gotchas
- **`IDEA.md`** — vibe input distilled from the HW4 spec; feed into Plan Mode to generate the PRD
- **`RULES.md`** — grading rubric (R1–R13) + HW4-specific audit gates (H1–Hn)
- **`CONTEXT-lec07-pdfs.md`** — deep digest of the 4 Lecture-07 PDFs (Active Knowledge, Graph Architecture, Graphify, Summary)
- **`CONTEXT-lecture-07.md`** — Lec 07 transcript digest *(added later — the orchestrator is recovering the lecture video; until then, rely on the PDFs)*
- **`IDEA-raw.txt`** — raw text extraction of the HW4 spec PDF (backup for verbatim quoting)

The user runs you in a separate window. When you finish or get blocked, surface a clear summary they can paste back to the orchestrator.

## Course context
- **Course**: 203.3763 — "Orchestration of AI Agents" (אורקסטרציה של סוכני AI), University of Haifa, Spring 2026
- **Lecturer**: Dr. Yoram Reuven Segal — `rmisegal@gmail.com`
- **HW4 deadline**: **Friday, 19 June 2026, 23:59** (Asia/Jerusalem) — Moodle assignment `id=274381`. Opened 5 June 2026.
- **Late penalty**: −5 points per 24h (no special request needed)

## Previous results & calibration
- **HW1**: 85.54/100 (self-graded 90 → over-claim triggered "rigorous lens"). Lessons still apply: rigorous planning docs, config/security portability, extensibility shown, quality automation (pre-commit + CI that is GREEN).
- **HW2**: submitted, not yet graded.
- **HW3** (just completed, same pair): CrewAI + LaTeX. Patterns that worked and you should reuse: SDK layer + Gatekeeper (actually wired, not decorative) + per-mechanism PRDs + ADRs + class diagram + 800+ task TODO + pre-commit + **GitHub Actions CI pinned to Python 3.13 and GREEN** + honest self-grade 85.
- **Self-grade default: 85.** Spec §5: a high self-grade invites a pedantic "elephants in a barrel" check; too-low biases you down. 85 = honest for strong work.

## What HW4 actually is — short version
Build a **Python project + AI agent** that does **graph-guided reverse engineering and debugging** of an **unfamiliar Python codebase**, and **proves token savings** vs naive raw-code reading.

The pipeline:
1. **Pick a buggy Python repo** — `soarsmu/BugsInPy` (real bugs, realistic), `martinpeck/broken-python`, or `andela/buggy-python`. OR bring your own repo **if it's substantial: ~10,000+ LOC, ≥70 code files** (stated in the submission box). Justify the choice in the README.
2. **Graphify** the codebase → produce `graph.json` + `GRAPH_REPORT.md` (graph representation of code: nodes = files/classes/functions, edges = calls/imports/inheritance).
3. **Obsidian vault** — a real knowledge space, not a file dump. MUST include:
   - `index.md` — central entry page: system structure + main navigation paths
   - `hot.md` — focused context page for the critical bug-investigation area
   - additional linked Markdown pages: key components, tests, investigation findings, prime suspects, the fix.
4. **AI agent** (CrewAI **or** LangGraph) that is **graph-guided**: it consults Graphify outputs + Obsidian pages FIRST, and only then requests relevant code snippets. Find → explain → fix a bug.
5. **Fix the bug** for real; show before/after at both code level AND knowledge level (what nodes/links/insights were added to Obsidian).
6. **Prove token savings**: compare **naive mode** (agent reads many raw files unfocused) vs **graph-guided mode** (agent works through Graphify/index.md/hot.md/Obsidian). Report: tokens consumed, files/text-units read, iterations, quality/speed to root-cause.

Underlying lecture themes you must reference: **"Lost in the Middle"** (context decay in long windows), `index.md`/`hot.md` as navigation hubs, **God Nodes**, converting a codebase into a navigable graph knowledge space.

## Core tasks (spec §5)
- **5.1** Graphify representation + Obsidian vault (`index.md`, `hot.md`, linked pages)
- **5.2** Reverse-engineer unfamiliar code → **≥2 illustrations**: an **architectural block diagram** AND an **OOP/class diagram** (real engineering understanding, not a folder listing)
- **5.3** Graph-guided AI agent (CrewAI/LangGraph) to investigate/locate/explain the bug
- **5.4** Real code fix — problem, root cause, change, how verified + knowledge-level before/after
- **5.5** Token-savings proof (baseline vs graph-guided, with the 4 metrics above)
- **5.6** ≥1 original extension per part (e.g. rank suspect nodes by centrality/proximity to failing tests; dynamic `hot.md` from `git diff` + `graph.json`; orphan-component detection; impact report "what breaks if I change this")

## Deliverables (spec §7) — the GitHub repo must contain at least
- Full Python solution code
- Agent workflow in CrewAI or LangGraph
- Graphify outputs: `graph.json`, `GRAPH_REPORT.md` (or equivalents)
- Full Obsidian vault with linked Markdown incl. `index.md` + `hot.md`
- Bug analysis report (problem, root cause, investigation path, fix)
- Token-comparison report (baseline vs graph-guided)
- Architectural block diagram + OOP diagram
- Before/after proof (code + system understanding)
- Documentation of the group's original extensions

## README requirements (spec §8) — README.md is graded heavily; must include
Chosen repo + why · the bug/problem studied · the research questions (§4) · architecture as extracted from code · the agent workflow · how Graphify + Obsidian were used · the reverse-engineering walkthrough · bug + root cause + fix · before/after · token-efficiency comparison · the original extensions · clear run instructions. **Plus visuals**: screenshots, graphs, block diagrams, OOP diagrams, flow diagrams.

## Research questions to answer explicitly (spec §4 — in README, reports, and Obsidian)
- What is the project's *actual* architecture, and what did you discover that wasn't obvious at first glance?
- Which components/modules/classes/functions are most central?
- Where are the complexity hotspots, mixed responsibilities, or "God Nodes"?
- How do you extract a block diagram + OOP schema even when original docs are thin?
- How did you find the bug, what was the root cause, what steps led you there?
- What was the advantage of the graph representation + Obsidian navigation vs linear file reading?
- How did graph-guided AI save tokens / cut needless code reads?
- What further agent mechanisms/extensions would you add?

## Planning & efficiency — the lecturer's Do / Don't (spec §6)
**Do:** pick ONE small/medium bug, not a whole system · start with local Graphify → `graph.json`/`index.md`/`hot.md` FIRST · use Obsidian to build a short work map (problem, suspects, tested, fixed) · invoke the AI only after context is assembled · **prefer LangGraph if on a limited/free account** (easier to cap calls/steps) · measure files read / LLM calls / tokens saved throughout · if BugsInPy, isolate in a venv/Docker.
**Don't:** don't pick too many bugs or too big a project · don't dump the whole codebase into the LLM at once · don't build a chatty workflow with too many agents/rounds · don't start with BugsInPy if you're shaky on Python envs/deps · don't turn this into a final project — small, well-explained, clear before/after wins · don't skip documentation — no strong README/screenshots/diagrams/Obsidian = can't prove the process.

## Recommended repo structure (spec §9, adapt with our standards)
```
README.md
pyproject.toml                 ← uv (NOT requirements.txt/pip)
uv.lock
src/<package>/
  sdk/                         ← single public entry (HW3 pattern)
  graphify/                    ← code→graph builder, graph.json + GRAPH_REPORT.md
  agent/                       ← CrewAI or LangGraph workflow (graph-guided)
  tools/                       ← graph query, file read (budgeted), token meter
  shared/                      ← gatekeeper (wrap every LLM call), config, version, logging
  constants.py
  main.py
vault/                         ← the Obsidian vault: index.md, hot.md, linked pages
reports/
  GRAPH_REPORT.md
  bug_analysis.md
  token_comparison.md
diagrams/                      ← architecture block diagram + OOP/class diagram (+ source)
docs/                          ← PRD.md, PLAN.md, TODO.md, per-mechanism PRDs, ADRs, PROMPTS.md
tests/                         ← unit + integration (mock LLM so grader needs no API key)
config/                        ← agents/tasks/rate_limits/logging JSON
.github/workflows/ci.yml       ← ruff + file-lines + pytest, pinned to Python 3.13, MUST be GREEN
.pre-commit-config.yaml
.env-example                   ← never commit real keys
target_repo/  (or submodule/pointer)  ← the buggy codebase under study
```

## The mandatory workflow (Vibe Coding Lifecycle)
`Idea → PRD → Plan → TODO → Verify → Execute → README → Run → Push`. Use these verbatim phase names. **Two approval gates** (rubric §2.5): STOP after the PRD for user approval, and STOP after the full docs package (PRD + PLAN + TODO + per-mechanism PRDs) before writing code. TODO must have **≥500 tasks** (aim 800). Continuous commits — one big-bang push is penalized.

## Top hard rules (the grading agent enforces; see RULES.md for full list)
| # | Rule |
|---|---|
| R1 | All business logic through an SDK layer |
| R2 | OOP, no duplication; **submit a class diagram** |
| R3 | Every external call (LLM, graph build, file read) routes through a **Gatekeeper** — wire it for real, don't leave it decorative (HW3 audit lesson) |
| R4 | Rate limits + token budgets in JSON config, not code |
| R5 | Versioning starts 1.00, +0.01/change, **single source of truth** in code AND config (HW3 lesson: don't desync `__init__`/`version.py`) |
| R6 | TDD; test suite GREEN — a red suite fails outright |
| R7 | ≤150 logical lines per Python file |
| R8 | `ruff check` zero failures |
| R9 | `pytest --cov` ≥ 85% (`fail_under=85`) |
| R10 | Zero hardcoded values — everything via config |
| R11 | Zero secrets; `.env-example` + `os.environ.get`; `.env` git-ignored |
| R12 | `uv` only — no pip/venv/virtualenv/requirements.txt |
| R13 | Continuous, meaningful commits; CI on GitHub must be GREEN (HW3 lesson: pin Python 3.13 so CrewAI's pydantic-v1 doesn't break the runner) |

## HW4-specific gates (from spec §§5,7,8) — see RULES.md for audit method
H1 Buggy Python repo chosen + justified (or own repo ≥10k LOC / ≥70 files) · H2 `graph.json` + `GRAPH_REPORT.md` present · H3 Obsidian vault with `index.md` + `hot.md` + linked pages · H4 Graph-guided agent in CrewAI **or** LangGraph (graph/Obsidian consulted before raw code) · H5 Real bug fixed with root-cause writeup · H6 Token-comparison report (tokens, units read, iterations, time-to-root-cause) · H7 Architectural block diagram · H8 OOP/class diagram · H9 Before/after at code + knowledge level · H10 ≥1 original extension · H11 Rich README with the §8 list + visuals · H12 Research questions (§4) answered.

## Grader auth paths (carry over from HW3 — keep all 4 working)
A. logged into Claude CLI · B. `claude --login` · C. `ANTHROPIC_API_KEY` env · D. **no AI access → `uv run pytest` with mock LLM exercises the whole workflow.** The grader does NOT run your live agent or pay tokens — design so tests + committed reports stand alone.

## User-specific info (pre-filled — confirm, don't re-ask)
| Field | Value |
|---|---|
| Group code | `uoh-sqak` (semester-long) |
| Pair | Salah Qadah (ID 323039974) + Andalus Kalash (ID 211435797) |
| Repo (suggested) | `https://github.com/salah-dev-stu/uoh-sqak-ex04` (public OR shared with rmisegal@gmail.com — inaccessible = auto-zero) |
| Submission PDF | `uoh-sqak-ex04.pdf` via `scripts/fill_submission_pdf.py` (already adapted) |
| Self-grade placeholder | 85 |

**Ask the user at session start:** (1) which base repo (BugsInPy / broken-python / buggy-python / own 10k+ repo), (2) CrewAI vs LangGraph (lecturer hints LangGraph for free-tier call control), (3) LLM provider (Claude CLI default).

## First action — required reading order
1. `IDEA.md` · 2. `RULES.md` · 3. `CONTEXT-lec07-pdfs.md` · 4. `CONTEXT-lecture-07.md` (when present) · 5. `../hw3/README.md` + `../hw3/docs/PLAN.md` (patterns that worked) · 6. `../hw1/feedback/Detailed_Feedback_Report.pdf` (what to fix).
Then collect the 3 user choices, enter Plan Mode, and begin the lifecycle. **Do not write code until PRD + PLAN + TODO are approved.**
