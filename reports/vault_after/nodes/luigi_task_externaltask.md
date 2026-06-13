---
node: luigi_task_externaltask
label: ExternalTask
tags: [community/0]
---

# ExternalTask

Graph node `luigi_task_externaltask`.

## Neighbours
- [[luigi_init]]
- [[luigi_s3]]
- [[luigi_s3_s3client]]
- [[luigi_task]]
- [[luigi_task_register_register]]
- [[luigi_task_register_taskclassexception]]
- [[luigi_task_task]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_task_externaltask --> luigi_init
    luigi_task_externaltask --> luigi_s3
    luigi_task_externaltask --> luigi_s3_s3client
    luigi_task_externaltask --> luigi_task
    luigi_task_externaltask --> luigi_task_register_register
    luigi_task_externaltask --> luigi_task_register_taskclassexception
    luigi_task_externaltask --> luigi_task_task
```

## Related (Dataview)

```dataview
LIST FROM #community/0
```
