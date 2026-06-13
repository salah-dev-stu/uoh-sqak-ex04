# Annotated Graph Report — Hub Nodes & Centrality

Graph: **2253 nodes**, **3957 edges**.

## Hub Nodes (bottlenecks)

Flagged **15** node(s) (degree >= 60 or betweenness >= 0.05 = CRITICAL).

| Tier | Node | Degree | Betweenness | Risk |
| --- | --- | ---: | ---: | --- |
| `WARNING` | `luigi_task_task` | 43 | 0.0013 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_scheduler_centralplannerscheduler` | 55 | 0.0012 | single point of failure / mutation target — consider splitting responsibilities |
| `CRITICAL` | `luigi_six` | 72 | 0.0008 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_worker_worker` | 35 | 0.0008 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_parameter_parameter` | 42 | 0.0007 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_parameter` | 37 | 0.0007 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_task` | 32 | 0.0006 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_s3` | 30 | 0.0003 | single point of failure / mutation target — consider splitting responsibilities |
| `CRITICAL` | `lib_jquery_1_10_0_min` | 60 | 0.0001 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `contrib_spark_sparksubmittask` | 37 | 0.0001 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_worker` | 30 | 0.0001 | single point of failure / mutation target — consider splitting responsibilities |
| `CRITICAL` | `js_dagre_d3` | 195 | 0.0 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `object` | 51 | 0.0 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `luigi_init` | 35 | 0.0 | single point of failure / mutation target — consider splitting responsibilities |
| `WARNING` | `notimplementederror` | 35 | 0.0 | single point of failure / mutation target — consider splitting responsibilities |

## Top centrality

| Node | Degree | Betweenness | Degree count |
| --- | ---: | ---: | ---: |
| `luigi_task_task` | 0.0191 | 0.0013 | 43 |
| `luigi_scheduler_centralplannerscheduler` | 0.0244 | 0.0012 | 55 |
| `luigi_six` | 0.032 | 0.0008 | 72 |
| `luigi_worker_worker` | 0.0155 | 0.0008 | 35 |
| `luigi_parameter_parameter` | 0.0187 | 0.0007 | 42 |
| `luigi_parameter` | 0.0164 | 0.0007 | 37 |
| `luigi_task_register_register` | 0.0124 | 0.0007 | 28 |
| `luigi_task_config` | 0.0098 | 0.0007 | 22 |
| `luigi_s3_s3target` | 0.0075 | 0.0007 | 17 |
| `luigi_worker_worker_add` | 0.0071 | 0.0007 | 16 |
| `luigi_task` | 0.0142 | 0.0006 | 32 |
| `luigi_scheduler` | 0.0107 | 0.0005 | 24 |
| `luigi_task_externaltask` | 0.008 | 0.0005 | 18 |
| `contrib_hadoop_create_packages_archive` | 0.0022 | 0.0005 | 5 |
| `luigi_scheduler_worker` | 0.0062 | 0.0004 | 14 |
