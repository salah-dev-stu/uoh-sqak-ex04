---
node: luigi_task_config
label: Config
tags: [community/6]
---

# Config

Graph node `luigi_task_config`.

## Neighbours
- [[luigi_init]]
- [[luigi_scheduler]]
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_scheduler_simpletaskstate]]
- [[luigi_task]]
- [[luigi_task_register_register]]
- [[luigi_task_register_taskclassexception]]
- [[luigi_task_task]]
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
    luigi_task_config --> luigi_init
    luigi_task_config --> luigi_scheduler
    luigi_task_config --> luigi_scheduler_centralplannerscheduler
    luigi_task_config --> luigi_scheduler_simpletaskstate
    luigi_task_config --> luigi_task
    luigi_task_config --> luigi_task_register_register
    luigi_task_config --> luigi_task_register_taskclassexception
    luigi_task_config --> luigi_task_task
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
