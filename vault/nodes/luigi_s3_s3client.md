---
node: luigi_s3_s3client
label: S3Client
tags: [community/21]
---

# S3Client

Graph node `luigi_s3_s3client`.

## Neighbours
- [[luigi_parameter_parameter]]
- [[luigi_s3]]
- [[luigi_task_externaltask]]

## Neighbourhood

```mermaid
flowchart LR
    luigi_s3_s3client --> luigi_parameter_parameter
    luigi_s3_s3client --> luigi_s3
    luigi_s3_s3client --> luigi_task_externaltask
```

## Related (Dataview)

```dataview
LIST FROM #community/21
```
