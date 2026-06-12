# Bug Analysis — luigi `Task.to_str_params` (BugsInPy luigi #20)

## Problem
`test/task_test.py::TaskTest::test_task_to_str_to_task` round-trips a Task:
`DummyTask.from_str_params(original.to_str_params())`. With a parameter declared
`significant=False`, the round-trip raises **`KeyError: 'insignificant_param'`**
(`luigi/task.py:314`, in `from_str_params`).

Reproduction (vendored copy, Python 3.8.3): see `reports/repro_fail.txt` (FAIL) and
`reports/repro_pass.txt` (PASS after fix).

## Root cause — a serialize/deserialize asymmetry
`Task.to_str_params` only serialized **significant** parameters:

```python
for param_name, param_value in six.iteritems(self.param_kwargs):
    if params[param_name].significant:          # <-- the bug
        params_str[param_name] = params[param_name].serialize(param_value)
```

But `Task.from_str_params` iterates **all** declared parameters and indexes the dict
directly:

```python
for param_name, param in cls.get_params():
    value = param.parse_from_input(param_name, params_str[param_name])  # KeyError here
```

So any `significant=False` parameter is dropped on the way out and then **missing** on
the way back in → `KeyError`. The two methods disagree on which params they handle.

## Investigation path (graph-guided)
1. `vault/index.md` → `vault/hot.md` pointed at the `Task`/`Parameter` serialization area.
2. Graph query from the failing-test node `luigi_task_task_to_str_params` → its graph
   neighbours resolve to `luigi/task.py` and `luigi/parameter.py` (the only files read).
3. Reading just those two files (vs. 40 in naive mode) surfaced the `significant` guard.
   See `reports/token_comparison.md` for the measured savings.

## The change (3 → 2 lines)
Remove the guard so **all** parameters serialize (matching `from_str_params`):

```diff
-            if params[param_name].significant:
-                params_str[param_name] = params[param_name].serialize(param_value)
+            params_str[param_name] = params[param_name].serialize(param_value)
```
Full diff: `reports/fix.diff`.

## Verification
- Vendored regression test: **FAIL → PASS** (`reports/repro_fail.txt` / `reports/repro_pass.txt`).
- Our suite: `tests/unit/test_fix_behavior.py` reproduces the asymmetry minimally and asserts the
  fixed logic round-trips (runs on Python 3.13, no luigi install — grader Path D).

## Before / after — code level
- **Before:** `to_str_params` drops `significant=False` params → round-trip `KeyError`.
- **After:** `to_str_params` serializes every param → `from_str_params` finds them all.

## Before / after — knowledge level (H9)
- **Added vault pages:** `findings/serialization-asymmetry.md`, `fix/to_str_params-fix.md`.
- **Added links:** `index.md` now links to the finding + fix (was: only the failing test).
- **Updated:** `hot.md` hypothesis → confirmed; `log.md` records the query→finding→fix trace.
- Captured as snapshots `reports/vault_before/` vs `reports/vault_after/`, diffed in
  `reports/knowledge_diff.md` (Phase 13 extension).
