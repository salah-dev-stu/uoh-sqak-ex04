---
node: luigi_worker
label: worker.py
tags: [hub, suspect, community/6]
---

# worker.py

Graph node `luigi_worker`.

## Neighbours
- [[luigi_interface]]
- [[luigi_parameter]]
- [[luigi_scheduler]]
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_six]]
- [[luigi_target]]
- [[luigi_task]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker_asynccompletionexception]]
- [[luigi_worker_dequequeue]]
- [[luigi_worker_keepalivethread]]
- [[luigi_worker_singleprocesspool]]
- [[luigi_worker_taskexception]]
- [[luigi_worker_taskprocess]]
- [[luigi_worker_tracebackwrapper]]
- [[luigi_worker_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker --> luigi_interface
    luigi_worker --> luigi_parameter
    luigi_worker --> luigi_scheduler
    luigi_worker --> luigi_scheduler_centralplannerscheduler
    luigi_worker --> luigi_six
    luigi_worker --> luigi_target
    luigi_worker --> luigi_task
    luigi_worker --> luigi_task_config
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
