---
node: luigi_worker_worker
label: worker
tags: [god-node, suspect, community/10]
---

# worker

Graph node `luigi_worker_worker`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]
- [[object]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_worker --> luigi_scheduler_centralplannerscheduler
    luigi_worker_worker --> luigi_task_config
    luigi_worker_worker --> luigi_task_task
    luigi_worker_worker --> luigi_worker
    luigi_worker_worker --> object
```

## Related (Dataview)

```dataview
LIST FROM #community/10
```
