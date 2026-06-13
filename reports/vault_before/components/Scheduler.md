---
title: Scheduler
type: component
tags: [component]
---

# Scheduler

`CentralPlannerScheduler` (luigi/scheduler.py) is a Hub Node (degree 55). It tracks the global task graph and each task's state (PENDING/RUNNING/DONE/FAILED) and hands runnable tasks to [[components/Worker|Worker]]s.
