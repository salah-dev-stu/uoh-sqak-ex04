# EX04 — Graph-Guided, Token-Efficient Reverse Engineering & Debugging

[![CI](https://github.com/salah-dev-stu/uoh-sqak-ex04/actions/workflows/ci.yml/badge.svg)](https://github.com/salah-dev-stu/uoh-sqak-ex04/actions/workflows/ci.yml)

> Course 203.3763 "Orchestration of AI Agents" · University of Haifa · Group `uoh-sqak` (Salah Qadah + Andalus Kalash).

Turn an unfamiliar buggy Python codebase (`spotify/luigi`) into a navigable **Graphify** knowledge graph + **Obsidian** vault, drive a **graph-guided LangGraph agent** that consults the graph/vault before raw code, fix a real bug, and **prove the token savings** versus naive raw-file reading.

_Full README (architecture, diagrams, walkthrough, token comparison, run instructions) is authored in Phase 15 — see `prd.md`, `Plan.md`, `Todo.md`._

## Quick start (uv only)

```bash
uv sync
uv run pytest          # mock LLM — no API key needed
uv run graphguide version
```
