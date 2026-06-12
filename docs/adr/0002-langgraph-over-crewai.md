# ADR 0002 — LangGraph over CrewAI for the Graph-Guided Agent

> **Course** 203.3763 · **Project** `uoh-sqak-ex04` · **Relates to** `prd.md` §5.4 (FR-AGENT-*), `docs/prd/agent.md`, `Plan.md` §5
> **Date** 2026-06-13 · **Deciders** Salah Qadah, Andalus Kalash

## Status

**Accepted.**

## Context

Spec 5.3 (gate H4) requires a **graph-guided AI agent built in CrewAI *or* LangGraph** that consults the Graphify graph and the Obsidian vault **before** reading raw code, under hard step/token/file budgets, and whose run is measured for token savings (spec 5.5, FR-TOKEN-*). The grader does not run our live agent and pays no tokens (grader Path D), so whatever framework we pick must also be drivable by a deterministic mock with no API key.

Two constraints shape the decision:

1. **The lecturer leans LangGraph.** Lecture 07 and the HW4 brief explicitly suggest LangGraph for limited/free-tier accounts because it makes it **easy to cap LLM calls and steps**. Its **explicit graph-state traversal** is a natural fit for our central requirement — "consult the graph before the code" maps directly onto an enforced node order in a `StateGraph`, where there is simply *no edge* from the vault nodes to the code-reading node until the graph has been queried.
2. **CrewAI is what we already know (HW3).** Reusing it would save ramp-up time. But CrewAI is **role/agent-and-task oriented and chattier by design** — bounding total LLM calls and step counts is harder, which works against the very thing we must measure (token savings) and against free-tier call control. CrewAI also pins **pydantic v1**, which is exactly the **Python-3.13 CI trap** we hit in HW3 (see ADR 0003): keeping that runner green cost real effort.

## Decision

Build the graph-guided agent (`src/graphguide/agent/`) as a **LangGraph `StateGraph`** — an explicit state machine with the enforced node order `read_index → read_hot → rank_suspects → query_graph → read_code → diagnose → propose_fix` and a budget-bounded conditional loop (see `docs/prd/agent.md` §3). LLM calls go through `agent/llm.py` → the Gatekeeper; tests inject a MockLLM.

We do **not** use CrewAI for this homework's agent.

## Consequences

**Positive**
- The "graph/vault before raw code" rule becomes a **topological invariant** of the state graph, not a convention — directly testable (no edge reaches `read_code` before the graph/vault nodes) and aligned with spec 5.3.
- **Easy, explicit caps** on iterations/steps/tokens/files (FR-AGENT-004) fit LangGraph's conditional edges and our `config/rate_limits.json`, giving honest, bounded runs for the token comparison (FR-TOKEN-*) and safe free-tier behavior.
- A linear `StateGraph` is **minimal and deterministic** — no multi-agent chatter (master NG2) — so the MockLLM can script answers by prompt key and the grader needs **no API key** (Path D).
- We **sidestep the pydantic-v1 / Python-3.13 CI trap**: LangGraph runs cleanly on the pinned Python 3.13 runner, keeping CI green (R13).

**Negative / Tradeoff**
- **New framework for us** — LangGraph wasn't used in HW3, so there is a learning cost. We mitigate by keeping the graph minimal (a near-linear state machine with one bounded loop) and avoiding over-engineering (Plan §14).
- We give up CrewAI's higher-level role abstractions, but this task wants tight control over a single disciplined flow, not a crew — so that abstraction was a poor fit anyway.

## Alternatives Considered

- **CrewAI (HW3 stack).** Rejected: chattier and harder to bound for a fair token measurement, weaker free-tier call control, and the pydantic-v1/Python-3.13 CI risk.
- **A hand-rolled Python loop (no framework).** Rejected: spec 5.3 names CrewAI/LangGraph specifically, and a bespoke loop would not demonstrate the required agentic framework nor give us LangGraph's clean, testable state/edge model.

## Related

- `docs/prd/agent.md` — the agent's per-mechanism PRD (FR-AGENT-001..009).
- ADR `0003-pin-python-3.13-ci.md` — the CI pin this choice keeps simple.
- ADR `0005-gatekeeper-wraps-all-calls.md` — every LLM call (incl. the agent's) routes through the Gatekeeper.
