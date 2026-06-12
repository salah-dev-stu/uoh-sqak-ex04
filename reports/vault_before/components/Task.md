---
title: Task
type: component
tags: [component]
---

# Task

`Task` (luigi/task.py) is the **central abstraction** and the graph's top code God Node (degree 43). Built via the `Register` metaclass; declares work through `requires()`/`output()`/`run()`; parameterised by [[components/Parameter|Parameter]] descriptors.

Serialization round-trip:
- `to_str_params()` -> dict of param name -> serialized string
- `from_str_params()` -> rebuilds a Task from that dict

The bug under study lives in `to_str_params` (see [[hot|hot.md]]).
