---
title: Hot — bug-critical context
type: focus
tags: [hot]
---

# Hot — bug-critical context

**Active focus:** Task.to_str_params serialization

The bug lives where `Task` serializes parameters. Read these first, in order:

- [[components/Task|Task]] — `to_str_params` / `from_str_params`
- [[components/Parameter|Parameter]] — `significant` flag, `serialize`/`parse`

Hypothesis: `to_str_params` skips `significant=False` params; `from_str_params` expects all.
