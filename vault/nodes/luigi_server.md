---
node: luigi_server
label: server.py
tags: [community/18]
---

# server.py

Graph node `luigi_server`.

## Neighbours
- [[luigi_configuration]]
- [[luigi_scheduler]]
- [[luigi_scheduler_centralplannerscheduler]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_server --> luigi_configuration
    luigi_server --> luigi_scheduler
    luigi_server --> luigi_scheduler_centralplannerscheduler
```

## Related (Dataview)

```dataview
LIST FROM #community/18
```
