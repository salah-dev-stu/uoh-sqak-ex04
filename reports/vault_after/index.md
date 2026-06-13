---
title: Index — luigi system map
type: hub
tags: [index]
---

# Index — luigi system map

System map for the **luigi** codebase (reverse-engineered from the Graphify graph).

## Navigation paths
1. Start here → 2. [[hot|hot.md (bug-critical area)]] → 3. component pages → 4. investigation.

## Key components
- [[components/Task|Task]]
- [[components/Parameter|Parameter]]
- [[components/Scheduler|Scheduler]]
- [[components/Worker|Worker]]
- [[components/Target|Target]]

## Investigation
- [[tests/test_task_to_str_to_task|failing test]]
- [[log|investigation log]]
- [[suspects/ranked|ranked suspects]]
- [[findings/serialization-asymmetry|root-cause finding]]
- [[fix/to_str_params-fix|the fix]]

## Knowledge graph (dense, auto-generated)
77 notes under `nodes/` — one per central / bug-adjacent graph node; wikilinks mirror real `graph.json` edges. Open in Obsidian -> Graph View. Hubs:
- [[luigi_task_task]] — Task (Hub Node)
- [[luigi_scheduler_centralplannerscheduler]] — Scheduler (Hub Node)
- [[luigi_parameter_parameter]] — Parameter
- [[luigi_task_task_to_str_params]] — the bug node (`#bug` `#fixed`)
