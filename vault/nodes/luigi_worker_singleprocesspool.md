---
node: luigi_worker_singleprocesspool
label: SingleProcessPool
tags: [community/6]
---

# SingleProcessPool

Graph node `luigi_worker_singleprocesspool`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]
- [[object]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_singleprocesspool --> luigi_scheduler_centralplannerscheduler
    luigi_worker_singleprocesspool --> luigi_task_config
    luigi_worker_singleprocesspool --> luigi_task_task
    luigi_worker_singleprocesspool --> luigi_worker
    luigi_worker_singleprocesspool --> object
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
