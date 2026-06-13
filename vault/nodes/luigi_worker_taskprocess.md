---
node: luigi_worker_taskprocess
label: TaskProcess
tags: [community/6]
---

# TaskProcess

Graph node `luigi_worker_taskprocess`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_taskprocess --> luigi_scheduler_centralplannerscheduler
    luigi_worker_taskprocess --> luigi_task_config
    luigi_worker_taskprocess --> luigi_task_task
    luigi_worker_taskprocess --> luigi_worker
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
