---
title: Parameter
type: component
tags: [component]
---

# Parameter

`Parameter` (luigi/parameter.py) is a descriptor attached to a [[components/Task|Task]]. Key attribute `significant`: whether the parameter affects task identity. `serialize()` / `parse_from_input()` convert values to/from strings. Subclasses: IntParameter, DateParameter, TupleParameter, etc.

Bug link: `to_str_params` skips params with `significant=False`, yet they are still expected when deserializing.
