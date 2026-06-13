---
node: luigi_parameter_parameter
label: Parameter
tags: [god-node, community/14]
---

# Parameter

Graph node `luigi_parameter_parameter`.

## Neighbours
- [[luigi_init]]
- [[luigi_parameter]]
- [[luigi_s3]]
- [[luigi_s3_s3client]]
- [[object]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_parameter_parameter --> luigi_init
    luigi_parameter_parameter --> luigi_parameter
    luigi_parameter_parameter --> luigi_s3
    luigi_parameter_parameter --> luigi_s3_s3client
    luigi_parameter_parameter --> object
```

## Related (Dataview)

```dataview
LIST FROM #community/14
```
