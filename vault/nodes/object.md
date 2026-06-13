---
node: object
label: object
tags: [hub, suspect, community/53]
---

# object

Graph node `object`.

## Neighbours
- [[luigi_date_interval_dateinterval]]
- [[luigi_parameter_parameter]]
- [[luigi_scheduler_simpletaskstate]]
- [[luigi_task_task]]
- [[luigi_worker_singleprocesspool]]
- [[luigi_worker_tracebackwrapper]]
- [[luigi_worker_worker]]

## Neighbourhood

```mermaid
flowchart LR
    object --> luigi_date_interval_dateinterval
    object --> luigi_parameter_parameter
    object --> luigi_scheduler_simpletaskstate
    object --> luigi_task_task
    object --> luigi_worker_singleprocesspool
    object --> luigi_worker_tracebackwrapper
    object --> luigi_worker_worker
```

## Related (Dataview)

```dataview
LIST FROM #community/53
```
