# Ranked Suspects — centrality + proximity to failing test

Seeded from failing-test node `luigi_task_task_to_str_params`. score = w_c*centrality + w_p*(1/(1+distance)).

| Rank | Node | Centrality | Distance | Score |
| ---: | --- | ---: | ---: | ---: |
| 1 | `luigi_task_task_to_str_params` | 0.0013 | 0 | 0.5007 |
| 2 | `luigi_task_task` | 0.0191 | 1 | 0.2595 |
| 3 | `luigi_task_task_get_params` | 0.0027 | 1 | 0.2513 |
| 4 | `luigi_task_rationale_303` | 0.0004 | 1 | 0.2502 |
| 5 | `object` | 0.0226 | 2 | 0.178 |
| 6 | `luigi_init` | 0.0155 | 2 | 0.1744 |
| 7 | `luigi_worker_worker` | 0.0155 | 2 | 0.1744 |
| 8 | `luigi_task` | 0.0142 | 2 | 0.1738 |
| 9 | `luigi_worker` | 0.0133 | 2 | 0.1733 |
| 10 | `luigi_task_register_register` | 0.0124 | 2 | 0.1729 |
