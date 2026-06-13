# Real-LLM Graph-Guided Run (Upgrade 3, FR-UPG3)

One genuine run of the graph-guided agent against the **real Claude CLI** (`claude -p`, routed through the Gatekeeper — no API key, uses the CLI login). The mock proves the token *reduction* deterministically; this confirms the model **genuinely finds the bug** from the graph-selected focused context.

- **Path (nodes navigated):** `index.md`, `hot.md`, `luigi_task_task`
- **Files read:** `luigi/task.py`
- **Iterations (rounds):** 1
- **Real tokens (Gatekeeper meter):** 7922
- **Found the bug:** True

## Model's root cause

> The failing test (`test_task_to_str_to_task`) breaks on the serialization round-trip because `Task.to_str_params` and `Task.from_str_params` disagree about which parameters are present. `to_str_params` builds its `str→str` dict selectively — it omits insignificant (`significant=False`) parameters — whereas `from_str_params` does the opposite: it loops over *every* declared parameter from `cls.get_params()` and reads each one with a direct, unguarded dictionary lookup (`params_str[param_name]`). So when a task carries an insignificant parameter, that key never makes it into the serialized dict, and reconstructing the task raises a `KeyError` on the missing name. The root cause is this asymmetry in the (de)serialization contract — one side skips parameters the other side unconditionally requires — not anything in the parameter parsing or the test itself.
