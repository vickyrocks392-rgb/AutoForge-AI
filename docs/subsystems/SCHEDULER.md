# Scheduler

## Purpose

This document defines the scheduler — the component responsible for determining which tasks to execute, when to execute them, and with what resources. The scheduler is the decision-making engine that translates the static task graph into a dynamic execution plan.

## Scope

This document covers scheduling strategies, queue management, resource allocation, and priority handling. It does not cover task execution or state management — those concerns are addressed in their respective documents.

---

## Overview

The scheduler sits between the task graph and the execution engine. It receives the task graph, determines which tasks are ready to run, assigns them to available resources, and manages the execution queue. It is responsible for maximizing throughput while respecting dependencies, priorities, and resource constraints.

```
                    ┌──────────────┐
                    │  Task Graph  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Scheduler   │
                    │              │
            ┌───────┤  ┌────────┐  ├───────┐
            │       │  │ Queues │  │       │
            │       │  └────────┘  │       │
            │       └──────┬───────┘       │
            │              │               │
     ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │  FIFO Queue │ │  Priority  │ │  Retry      │
     │             │ │  Queue     │ │  Queue      │
     └─────────────┘ └────────────┘ └─────────────┘
                           │
                    ┌──────▼───────┐
                    │   Worker     │
                    │   Pool       │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Execution   │
                    │  Engine      │
                    └──────────────┘
```

## Scheduling Strategies

### FIFO (First-In, First-Out)
Tasks are executed in the order they become ready. Simple and predictable, but does not account for priority or resource constraints.

**Use case:** Simple projects with few tasks and no priority differentiation.

### Priority-Based Scheduling
Tasks are assigned a priority level (critical, high, medium, low). Higher-priority tasks are scheduled before lower-priority tasks, regardless of when they became ready.

**Use case:** Projects where certain tasks (e.g., architecture decisions) must complete before others can begin.

### Dependency-Aware Scheduling
The scheduler uses the task graph's topological order to determine execution sequence. A task is only scheduled when all its dependencies are met.

**Use case:** All projects. This is the default scheduling mode.

### Deadline-Aware Scheduling
Tasks with approaching deadlines are prioritized. The scheduler uses estimated duration and critical path analysis to ensure tasks complete before their deadlines.

**Use case:** Projects with time-sensitive deliverables or external dependencies.

### Cost-Optimized Scheduling
The scheduler considers token cost when assigning tasks to models. Cheaper models are preferred for simple tasks; expensive models are reserved for complex tasks.

**Use case:** Cost-sensitive projects or when operating under a token budget.

## Queue Architecture

The scheduler maintains multiple queues to handle different task states:

### Ready Queue
Tasks whose dependencies are all met and are ready for execution. This is the primary queue the scheduler draws from.

### Priority Queue
A subset of the ready queue, sorted by priority. When priority scheduling is active, the scheduler draws from this queue instead of the FIFO ready queue.

### Retry Queue
Tasks that failed with recoverable errors and are waiting for retry. Tasks in the retry queue have a backoff timer before they can be re-dispatched.

### Blocked Queue
Tasks that cannot proceed due to dependency failures or missing inputs. These tasks are not scheduled until their blocking condition is resolved.

### Human Approval Queue
Tasks that have completed execution and are awaiting human review. These tasks are not scheduled for downstream execution until approved.

## Worker Pool

The scheduler manages a pool of worker slots that represent concurrent execution capacity:

- **Max Workers** — The maximum number of tasks that can execute concurrently
- **Available Workers** — The number of idle worker slots
- **Worker Assignment** — When a task is scheduled, it consumes a worker slot. When the task completes, the slot is released.

Worker slots are allocated based on:
- **Task priority** — Higher priority tasks get worker slots first
- **Task cost** — Expensive tasks may be limited to prevent budget overruns
- **Model availability** — Tasks requiring specific models wait for those models to be available

## Scheduling Algorithm

The scheduling algorithm operates in a continuous loop:

1. **Evaluate** — Examine the task graph for tasks whose dependencies are all met
2. **Filter** — Remove tasks that are blocked, waiting, or in review
3. **Prioritize** — Sort ready tasks by priority (and optionally by deadline or cost)
4. **Allocate** — Assign tasks to available worker slots, respecting resource constraints
5. **Dispatch** — Send assigned tasks to the execution engine
6. **Monitor** — Listen for task completion events and release worker slots
7. **Repeat** — Return to step 1

## Backpressure

The scheduler implements backpressure to prevent overloading the execution engine:

- **Worker limit** — Hard limit on concurrent task execution
- **Queue depth** — Maximum number of tasks in the ready queue before new tasks are deferred
- **Rate limiting** — Maximum number of tasks dispatched per unit time

## Future Implementation Notes

- The scheduler should support dynamic worker pool scaling based on system load
- Scheduling decisions should be logged for audit and optimization
- The scheduler should expose metrics (queue depth, wait times, worker utilization) for monitoring
- Custom scheduling strategies should be pluggable via a strategy interface

## Open Questions

- Should the scheduler support preemption — where a higher-priority task can interrupt a running lower-priority task?
- How should the scheduler handle tasks with no estimated duration (unknown cost)?
- Should the scheduler support gang scheduling — where a group of related tasks must be scheduled together?
- How should the scheduler balance between maximizing throughput and minimizing cost?
- Should the scheduler support affinity scheduling — where certain tasks prefer to run on specific workers or models?