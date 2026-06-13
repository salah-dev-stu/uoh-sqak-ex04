---
node: luigi_scheduler_centralplannerscheduler
label: CentralPlannerScheduler
tags: [god-node, community/42]
---

# CentralPlannerScheduler

Graph node `luigi_scheduler_centralplannerscheduler`.

## Neighbours
- [[luigi_scheduler]]
- [[luigi_server]]
- [[luigi_task_config]]
- [[luigi_worker]]
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
    luigi_scheduler_centralplannerscheduler --> luigi_scheduler
    luigi_scheduler_centralplannerscheduler --> luigi_server
    luigi_scheduler_centralplannerscheduler --> luigi_task_config
    luigi_scheduler_centralplannerscheduler --> luigi_worker
    luigi_scheduler_centralplannerscheduler --> luigi_worker_asynccompletionexception
    luigi_scheduler_centralplannerscheduler --> luigi_worker_dequequeue
    luigi_scheduler_centralplannerscheduler --> luigi_worker_keepalivethread
    luigi_scheduler_centralplannerscheduler --> luigi_worker_singleprocesspool
```

## Related (Dataview)

```dataview
LIST FROM #community/42
```
