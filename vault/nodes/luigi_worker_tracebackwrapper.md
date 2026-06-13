---
node: luigi_worker_tracebackwrapper
label: TracebackWrapper
tags: [community/6]
---

# TracebackWrapper

Graph node `luigi_worker_tracebackwrapper`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]
- [[object]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_tracebackwrapper --> luigi_scheduler_centralplannerscheduler
    luigi_worker_tracebackwrapper --> luigi_task_config
    luigi_worker_tracebackwrapper --> luigi_task_task
    luigi_worker_tracebackwrapper --> luigi_worker
    luigi_worker_tracebackwrapper --> object
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
