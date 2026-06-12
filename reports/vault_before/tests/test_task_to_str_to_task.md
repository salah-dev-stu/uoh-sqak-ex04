---
title: Failing test: test_task_to_str_to_task
type: note
tags: [test]
---

# Failing test: test_task_to_str_to_task

`test/task_test.py::TaskTest::test_task_to_str_to_task` round-trips a Task through `to_str_params()` -> `from_str_params()`. The regression test (from the fixed commit) adds `insignificant_param = luigi.Parameter(significant=False)`. On the buggy source it raises `KeyError: 'insignificant_param'`. See [[components/Task|Task]] and [[components/Parameter|Parameter]].
