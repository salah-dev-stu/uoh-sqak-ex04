---
node: luigi_worker_taskexception
label: TaskException
tags: [community/6]
---

# TaskException

Graph node `luigi_worker_taskexception`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_taskexception --> luigi_scheduler_centralplannerscheduler
    luigi_worker_taskexception --> luigi_task_config
    luigi_worker_taskexception --> luigi_task_task
    luigi_worker_taskexception --> luigi_worker
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
