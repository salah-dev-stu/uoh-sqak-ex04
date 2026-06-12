# Token-Savings Proof — naive vs graph-guided (H6, §5.5)

**Code-token savings: 96.1%** (22923 -> 897) · file-read savings: 97.1%.

| Metric | Naive (baseline) | Graph-guided |
| --- | ---: | ---: |
| Code tokens read | 22923 | 897 |
| Code files read | 35 | 1 |
| Graph/vault nodes navigated | 0 | 6 |
| Found the bug | True | True |

## What this measures (and what it does not)
- **Metric = code tokens actually read into the agent's context** (the spec's target: 'cut needless code reads'). The Obsidian vault (`index.md`/`hot.md`) is the cheap *navigation layer* that replaces expensive code reading; it is not counted as code cost.
- **Both modes use a deterministic mock LLM**, so 'found the bug' is true by construction. This experiment isolates and proves the **context/token reduction** the graph enables — not a claim that graph-guidance raises the model's success rate.
- **Both runs are single-pass** (root cause found on the first diagnosis), so iteration count is not a differentiator here and is omitted; the token/file reduction is the result.
- **Baseline fairness:** naive reads every top-level `luigi/*.py` module (capped at `max_files`) — an unfocused read of the package, not a strawman. The tokens charged equal the code it ingests (no read-then-discard).

## Why graph-guided wins
The graph routes the agent `index.md` -> `hot.md` -> the failing-test node's neighbourhood, so it reads only that neighbourhood. Focused context also avoids 'Lost in the Middle'.

Numbers come from the Gatekeeper token meter; reproducible from `reports/metrics/naive.json` + `reports/metrics/graph.json`.
