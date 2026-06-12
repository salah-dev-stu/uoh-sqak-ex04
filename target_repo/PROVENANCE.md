# Vendored Target Repo — Provenance (H1, NFR-REPRO)

| Field | Value |
|---|---|
| Upstream | https://github.com/spotify/luigi |
| Dataset | `soarsmu/BugsInPy` — project `luigi`, bug `20` |
| Buggy commit | `b958140c2ec838e590a5be02dbac7414d5d0bf17` (vendored state) |
| Fixed commit | `c3d685e2b03369aab6f4d86ed1c95169c1c2c217` |
| Python (upstream) | 3.8.3 |
| License | Apache-2.0 (see `luigi/LICENSE`) |

## What is vendored
- `luigi/luigi/` — the full luigi package at the **buggy** commit (source under study).
- `luigi/test/task_test.py` — the regression test taken from the **fixed** commit (it adds
  `insignificant_param = luigi.Parameter(significant=False)`), which exposes the bug against the buggy source.
- `luigi/setup.py`, `luigi/LICENSE` — for provenance/context.

## The bug (BugsInPy luigi #20)
`Task.to_str_params` (luigi/task.py) skips parameters declared `significant=False`:

```python
for param_name, param_value in six.iteritems(self.param_kwargs):
    if params[param_name].significant:               # <-- buggy guard
        params_str[param_name] = params[param_name].serialize(param_value)
```

But `Task.from_str_params` iterates **all** params and indexes `params_str[param_name]`,
so a `task -> str -> task` round-trip raises `KeyError: 'insignificant_param'`.

## Reproduce (isolated)
```bash
python3.8 -m venv .venv && . .venv/bin/activate
pip install -e luigi && pip install pytest
pytest luigi/test/task_test.py::TaskTest::test_task_to_str_to_task   # FAILS on buggy source
```

The fix removes the `significant` guard so all params serialize (3-line change). Verified:
buggy → FAIL (`KeyError`), fixed → PASS, in a uv venv (Python 3.8.3).
