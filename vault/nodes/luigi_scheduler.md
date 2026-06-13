---
node: luigi_scheduler
label: scheduler.py
tags: [community/7]
---

# scheduler.py

Graph node `luigi_scheduler`.

## Neighbours
- [[luigi_configuration]]
- [[luigi_interface]]
- [[luigi_parameter]]
- [[luigi_scheduler_centralplannerscheduler]]
- [[luigi_scheduler_simpletaskstate]]
- [[luigi_server]]
- [[luigi_six]]
- [[luigi_task]]
- [[luigi_task_config]]
- [[luigi_worker]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_scheduler --> luigi_configuration
    luigi_scheduler --> luigi_interface
    luigi_scheduler --> luigi_parameter
    luigi_scheduler --> luigi_scheduler_centralplannerscheduler
    luigi_scheduler --> luigi_scheduler_simpletaskstate
    luigi_scheduler --> luigi_server
    luigi_scheduler --> luigi_six
    luigi_scheduler --> luigi_task
```

## Related (Dataview)

```dataview
LIST FROM #community/7
```
