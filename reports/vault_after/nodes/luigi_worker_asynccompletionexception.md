---
node: luigi_worker_asynccompletionexception
label: AsyncCompletionException
tags: [community/6]
---

# AsyncCompletionException

Graph node `luigi_worker_asynccompletionexception`.

## Neighbours
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_task_config]]
- [[luigi_task_task]]
- [[luigi_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_worker_asynccompletionexception --> luigi_scheduler_centralplannerscheduler
    luigi_worker_asynccompletionexception --> luigi_task_config
    luigi_worker_asynccompletionexception --> luigi_task_task
    luigi_worker_asynccompletionexception --> luigi_worker
```

## Related (Dataview)

```dataview
LIST FROM #community/6
```
