# HW4 — Grading Rules & Audit Gates

> Two layers: the **standing software rubric** (R1–R13, same `software_submission_guidelines` PDF graded in HW1–HW3) and the **HW4-specific gates** (H1–H12, from the EX04 spec §§4,5,7,8). The grading agent runs automated checks on the committed repo (tests use a mock LLM — it does NOT run your live agent). A high self-grade triggers a pedantic pass; 85 is the honest default for strong work. See `../hw3/CONTEXT-rubric-and-pdfs.md` → `../hw2/CONTEXT-rubric-and-pdfs.md` for the full 63K rubric digest (unchanged since HW1).

## Standing software rubric (R1–R13)

| # | Rule | Audit method |
|---|---|---|
| R1 | **SDK layer** — all business logic flows through a single public SDK entry (`src/<pkg>/sdk/`). | Code review |
| R2 | **OOP, no duplication** — extract via base class / mixin / Template Method. **Submit a class diagram.** | Code review + `diagrams/` |
| R3 | **Gatekeeper** — every external call (LLM, graph build subprocess, file read in agent mode) routes through one `ApiGatekeeper`. **Wire it for real** — HW3 audit found it only used for `get_spend_report()`; here it must gate AND record the LLM + tool calls (the token meter for §5.5 lives here). | Code review + grep for raw `subprocess`/`requests`/LLM calls outside the gatekeeper |
| R4 | **Rate limits + token budgets in JSON config**, never in code. | `config/rate_limits.json` inspection |
| R5 | **Versioning** — starts `1.00`, `+0.01` per change, in code AND config, **single source of truth** (`__init__.py` imports `VERSION` from `shared/version.py`; tests assert the same value). | Version module + test |
| R6 | **TDD** — Red→Green→Refactor; suite must be **GREEN**. A failing test fails the rule outright (HW3 lesson: a version desync that reddened 3 tests cost real credit until fixed). | `uv run pytest` |
| R7 | **≤150 logical lines per Python file** (excl. comments/blanks). | `scripts/check_file_lines.py` (copy from HW3) |
| R8 | **`ruff check` = 0 failures** (line-length 100, py313, E/F/W/I/N/UP/B/C4/SIM, ignore E501). | ruff |
| R9 | **`pytest --cov` ≥ 85%** (`fail_under = 85` in pyproject). | pytest-cov |
| R10 | **Zero hardcoded values** — models, timeouts, paths, budgets all via config. | Code review (HW3 lesson: don't hardcode the model id / `timeout=120`) |
| R11 | **Zero secrets** — `.env-example` + `os.environ.get(...)`; `.env` git-ignored. | Auto scan |
| R12 | **`uv` only** — no `pip` / `python -m venv` / `virtualenv` / `requirements.txt`. `uv.lock` tracked. | Auto |
| R13 | **Continuous commits + GREEN GitHub CI.** One big push is penalized. CI must pass on GitHub — **pin Python 3.13** via `actions/setup-python@v5` so CrewAI's bundled pydantic-v1 doesn't break on the runner's default 3.14 (the exact trap HW3 hit). | Git history + Actions badge |

## HW4-specific gates (H1–H12)

| # | Gate | What "pass" means | Audit |
|---|---|---|---|
| H1 | **Base repo chosen + justified** | One of BugsInPy / broken-python / buggy-python, OR own repo **≥10,000 LOC & ≥70 code files**. README explains the choice + fit. Target repo vendored/pinned for reproducibility. | README + repo presence |
| H2 | **Graphify outputs** | `graph.json` (nodes = files/classes/functions; edges = calls/imports/inheritance) **+ `GRAPH_REPORT.md`**. God-Nodes / central nodes / hotspots flagged in the report. | File presence + content review |
| H3 | **Obsidian vault** | A real linked vault (not a dump) with **`index.md`** (system map + nav paths) and **`hot.md`** (focused bug-area context) plus linked pages: components, tests, findings, suspects, fix. | `vault/` inspection + link check |
| H4 | **Graph-guided agent** | Working agent in **CrewAI or LangGraph**. Must consult Graphify/Obsidian **before** requesting raw code. Workflow + each step's role + context-reduction mechanisms documented. | Code + run log/report; mock-LLM test |
| H5 | **Real bug fixed** | Actual code change with **root-cause** writeup: problem, why, change, how verified. | `reports/bug_analysis.md` + diff |
| H6 | **Token-savings proof** | `reports/token_comparison.md`: **naive vs graph-guided** with ≥4 metrics — tokens consumed, files/text-units read, iterations, quality/speed to root-cause. Numbers must come from the instrumented token meter, not hand-waving. | Report + meter code |
| H7 | **Architectural block diagram** | Real block diagram of the target system's parts + flow (TikZ/Mermaid/draw.io/matplotlib — source committed). | `diagrams/` + README embed |
| H8 | **OOP / class diagram** | Classes + usage/composition/inheritance/patterns of the target system. Folder listing ≠ pass. | `diagrams/` + README embed |
| H9 | **Before/after** | At code level (the fix) AND knowledge level (Obsidian pages/nodes/links/insights added). | README + vault diff |
| H10 | **Original extension** | ≥1 genuine extension (centrality-ranked suspects; dynamic `hot.md` from `git diff`+`graph.json`; orphan detection; impact report; before/after architecture). Documented. | README + code |
| H11 | **Rich README (spec §8)** | Contains the full §8 list (repo+why, bug, research questions, extracted architecture, agent workflow, Graphify+Obsidian usage, reverse-eng walkthrough, bug+root-cause+fix, before/after, token-efficiency, extensions, run instructions) **+ visuals** (screenshots, graphs, block/OOP/flow diagrams). | README inspection |
| H12 | **Research questions answered (spec §4)** | All §4 questions addressed in README + reports + Obsidian. | Cross-check |

## Standing submission rules (spec §§1–8, identical to HW1–HW3)
1. **One GitHub link** for both pair members; **public OR shared with `rmisegal@gmail.com`** — inaccessible = automatic zero.
2. Each pair member **submits separately** on Moodle (`id=274381`); timing is per-individual.
3. **Group code** `uoh-sqak` (8 chars, no spaces) — semester-long.
4. Fill the Word template, **don't alter fields**, save as PDF named **`uoh-sqak-ex04.pdf`**. Nothing extra added. (`scripts/fill_submission_pdf.py` is ready.)
5. **Self-grade** honest (default **85**). Too-high → pedantic check; too-low → biased down.
6. **Late** −5/24h, no request needed. Deadline **Fri 2026-06-19 23:59**.
7–8. Reserve-duty exceptions per spec (N/A unless applicable).

## Reuse from HW3 (don't re-discover)
- `scripts/check_file_lines.py`, the pre-commit config, the **Python-3.13-pinned CI workflow**, the Gatekeeper pattern, the SDK façade, the per-mechanism-PRD + ADR + class-diagram docs shape, the 4 grader auth paths, and the mock-LLM integration-test pattern (so the grader needs no API key). Copy and adapt; cite in ADRs.

## ⚠️ Verify before trusting the lecture digest
`CONTEXT-lec07-pdfs.md` (subagent digest of the 4 Lec-07 PDFs) asserts some specifics — e.g. edge **confidence scores** in `graph.json`, a **71.5% token-savings** figure, and "LangGraph over CrewAI." Treat framework choice and exact numbers as *recommendations to confirm against the slides/transcript*, not hard spec requirements, before building the PRD around them. The binding requirements are in this file + the spec PDF.
