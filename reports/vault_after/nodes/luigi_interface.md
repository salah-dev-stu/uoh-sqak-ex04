---
node: luigi_interface
label: interface.py
tags: [community/19]
---

# interface.py

Graph node `luigi_interface`.

## Neighbours
- [[luigi_configuration]]
- [[luigi_init]]
- [[luigi_parameter]]
- [[luigi_scheduler]]
- [[luigi_task]]
- [[luigi_task_register_register]]
- [[luigi_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_interface --> luigi_configuration
    luigi_interface --> luigi_init
    luigi_interface --> luigi_parameter
    luigi_interface --> luigi_scheduler
    luigi_interface --> luigi_task
    luigi_interface --> luigi_task_register_register
    luigi_interface --> luigi_worker
```

## Related (Dataview)

```dataview
LIST FROM #community/19
```
