---
title: Finding: serialize/deserialize asymmetry
type: finding
tags: [finding]
---

# Finding: serialize/deserialize asymmetry

The bug is a **serialize/deserialize asymmetry** in [[components/Task|Task]].

`to_str_params()` skipped parameters with `significant=False`; `from_str_params()` iterates **all** [[components/Parameter|Parameter]]s and indexes the serialized dict directly, so a dropped param raises `KeyError`.

Evidence: the failing [[tests/test_task_to_str_to_task|test]] adds `insignificant_param = Parameter(significant=False)`.
