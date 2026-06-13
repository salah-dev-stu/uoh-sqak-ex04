# Lost in the Middle — demonstrated (Upgrade 5, FR-UPG5)

Does burying the bug-relevant code in the **middle** of a large naive context degrade the model's diagnosis, versus the small **focused** graph-guided context? Real run (`claude -p`, routed through the Gatekeeper).

| Condition | Context tokens | Bug position | Found root cause? |
| --- | ---: | --- | :---: |
| focused (graph-guided) | 375 | n/a | yes |
| naive buried — start | 50026 | start | yes |
| naive buried — middle | 50026 | middle | yes |
| naive buried — end | 50019 | end | yes |

## Verdict

At this context size the model was robust — it found the root cause in every position, including buried-in-the-middle. The 'Lost in the Middle' degradation is scale-dependent (it sharpens at much longer contexts); the **practical** win here is unchanged and stark: the focused graph-guided context reached the *same* correct diagnosis on **375 vs ~50,026 tokens — about 133x fewer**. Focusing is the right design whether or not the model degrades.

## What each run answered

**focused (graph-guided):**

> **Root cause:** The two methods are asymmetric about which parameters they handle. `to_str_params` only serializes the parameters present in `self.param_kwargs`, so an insignificant parameter (`significant=False`) gets omitted from the resulting dict, while `from_str_params` loops over the *full* set from `cls.get_params()` and unconditionally indexes `params_str[param_name]` for every one of them

**naive buried — start:**

> The root cause is an asymmetry between the two serialization methods. `to_str_params` builds its output dict by iterating only over `self.param_kwargs` (the parameters actually set on the instance), so a parameter that isn't materialized there — e.g. an insignificant one — never gets a key in the resulting `str→str` hash. `from_str_params`, however, loops over **every** parameter from `cls.get_par

**naive buried — middle:**

> **Root cause:** The break is a mismatch between `Task.to_str_params` and `Task.from_str_params`. `to_str_params` only serializes parameters present in `self.param_kwargs` (the values actually set on the instance), so a parameter that wasn't explicitly passed — e.g. the `significant=False` param relying on its default — never makes it into the returned dict. `from_str_params` then iterates over *ev

**naive buried — end:**

> The root cause is in the `to_str_params`/`from_str_params` round-trip pair (the `Task` methods shown at the end). `from_str_params` unconditionally indexes `params_str[param_name]` for *every* parameter returned by `cls.get_params()`, assuming each one is present in the serialized dict — but `to_str_params` only emits keys for params it actually serializes (driven by `self.param_kwargs`), so the `
