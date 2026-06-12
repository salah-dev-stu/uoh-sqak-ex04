# Agent Prompts

The graph-guided agent uses two LLM nodes. Templates live in `config/agents.json`
(`prompts`) — never hardcoded (R10). They are formatted with the focused context the
graph/vault assembled, so the prompt stays small (the token-efficiency mechanism).

## `diagnose`
```
Debug luigi. Focused context:
{context}

In one paragraph, state the root cause of the failing test.
```
`{context}` = `index.md` + `hot.md` + the graph-selected suspect file(s) only — **not** the whole repo.

## `fix`
```
Root cause:
{root_cause}

Propose the minimal code change to fix it.
```

## Determinism for grading
Tests inject `MockLLM` (scripted, no API key) so the whole workflow runs in CI without tokens
(grader Path D). The real `LLMClient` calls Anthropic through the Gatekeeper, which records the
token usage that feeds `reports/token_comparison.md`.
