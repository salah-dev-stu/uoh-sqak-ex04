---
title: Investigation log
type: log
tags: [decision]
---

# Investigation log

Query → finding → action trace.

- query: neighbours of `luigi_task_task_to_str_params` -> Task, Parameter
- read: luigi/task.py, luigi/parameter.py (2 files; naive read 40)
- finding: `to_str_params` skips `significant=False` params; `from_str_params` expects all -> KeyError
- action: removed the `significant` guard (`reports/fix.diff`); regression test FAIL -> PASS
