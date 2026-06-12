---
title: Fix: drop the significant guard
type: fix
tags: [fix]
---

# Fix: drop the significant guard

Remove the `significant` guard in [[components/Task|Task]] `to_str_params` so every parameter serializes (matching `from_str_params`).

```diff
-            if params[param_name].significant:
-                params_str[param_name] = params[param_name].serialize(param_value)
+            params_str[param_name] = params[param_name].serialize(param_value)
```
Verified: regression test FAIL -> PASS (`reports/repro_fail.txt` / `reports/repro_pass.txt`).
