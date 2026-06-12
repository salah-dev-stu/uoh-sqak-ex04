# Token-Savings Proof — naive vs graph-guided (H6, §5.5)

**Token savings: 96.1%** · file-read savings: 97.1%.

| Metric | Naive (baseline) | Graph-guided |
| --- | ---: | ---: |
| Tokens consumed | 22923 | 897 |
| Files / text-units read | 35 | 1 |
| Iterations | 1 | 1 |
| Graph/vault nodes navigated | 0 | 6 |
| Found the bug (quality) | True | True |

**Why:** the graph routes the agent from `index.md` -> `hot.md` -> the bug node's neighbourhood, so it reads only that neighbourhood instead of scanning many files. This avoids 'Lost in the Middle' — the focused context keeps the signal where the model attends. Time-to-root-cause is proxied by iterations + files read.

Numbers come from the Gatekeeper token meter; reproducible from `reports/metrics/naive.json` + `reports/metrics/graph.json`.
