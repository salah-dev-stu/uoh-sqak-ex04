---
title: Target
type: component
tags: [component]
---

# Target

`Target` (luigi/target.py) abstracts a task's output existence check (e.g. `LocalTarget`). A [[components/Task|Task]] is complete when its `output()` Target `exists()`.
