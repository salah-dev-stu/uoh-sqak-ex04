# Token-Savings Proof — naive vs graph-guided (H6, §5.5)

**Code-token savings: 96.1%** (22923 -> 897) · file-read savings: 97.1%.

| Metric | Naive (baseline) | Graph-guided |
| --- | ---: | ---: |
| Code tokens read | 22923 | 897 |
| Code files read | 35 | 1 |
| Iterations (rounds) | 1 | 2 |
| Graph/vault nodes navigated | 0 | 4 |
| Found the bug | True | True |

## What this measures (and what it does not)
- **Metric = code tokens actually read into the agent's context** (the spec's target: 'cut needless code reads'). The Obsidian vault (`index.md`/`hot.md`) is the cheap *navigation layer* that replaces expensive code reading; it is not counted as code cost.
- **Both modes use a deterministic mock LLM**, so 'found the bug' is true by construction. This experiment isolates and proves the **context/token reduction** the graph enables — not a claim that graph-guidance raises the model's success rate.
- **Iterations are measured**, not hardcoded: graph-guided runs a real frontier-expansion loop (seed at `hot.md` nodes -> expand one hop per round -> read the top-ranked node) and converges in a few targeted rounds, each reading a single node; naive is one bulk pass over many files. So graph-guided trades a few cheap rounds for a fraction of the tokens.
  - *Reconciling with the real run:* this harness reads **one node per round** (a small window) to exercise and measure the loop, so it takes **2 rounds**. The real run (`reports/real_run.md`) reads the bug node's **full file** in round 1, so the strong model concludes in **1 round**. Both are honest — iteration count depends on the per-round read window and the model's confidence, not on a fixed constant.
- **Baseline fairness:** naive reads every top-level `luigi/*.py` module (capped at `max_files`) — an unfocused read of the package, not a strawman. The tokens charged equal the code it ingests (no read-then-discard).

## Why graph-guided wins
The graph routes the agent `index.md` -> `hot.md` -> the failing-test node's neighbourhood, so it reads only that neighbourhood. Focused context also avoids 'Lost in the Middle'.

Numbers come from the Gatekeeper token meter; reproducible from `reports/metrics/naive.json` + `reports/metrics/graph.json`.

A **real-LLM run** (no mock, `claude -p` via the Gatekeeper) confirms the model genuinely finds this bug graph-guided — see `reports/real_run.md`.
