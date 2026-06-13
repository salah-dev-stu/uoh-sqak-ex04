---
node: luigi_task_wrappertask
label: WrapperTask
tags: [community/7]
---

# WrapperTask

Graph node `luigi_task_wrappertask`.

## Neighbours
- [[luigi_init]]
- [[luigi_task]]
- [[luigi_task_register_register]]
- [[luigi_task_register_taskclassexception]]
- [[luigi_task_task]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_task_wrappertask --> luigi_init
    luigi_task_wrappertask --> luigi_task
    luigi_task_wrappertask --> luigi_task_register_register
    luigi_task_wrappertask --> luigi_task_register_taskclassexception
    luigi_task_wrappertask --> luigi_task_task
```

## Related (Dataview)

```dataview
LIST FROM #community/7
```
