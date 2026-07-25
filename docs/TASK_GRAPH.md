# Task Graph

## Purpose

This document defines the task graph — the directed acyclic graph (DAG) that represents the complete set of work items for a project and their dependency relationships. The task graph is the blueprint that the scheduler and executor use to determine what to run, in what order, and in parallel.

## Scope

This document covers the structure, construction, and properties of the task graph. It does not cover how tasks are scheduled or executed — those concerns are addressed in the Scheduler and Execution Lifecycle documents.

---

## Overview

The task graph is a DAG where:

- **Nodes** represent individual tasks (as defined in the Task Model)
- **Edges** represent dependencies between tasks
- **Direction** flows from dependency to dependent (a → b means "a must complete before b can start")

The task graph is produced by the Planner service from the user's request and project configuration. It is the complete, materialized plan of all work required to complete the project.

```
Example Task Graph (Simplified):

    ┌──────────────┐
    │  Research    │
    │  Dependencies│
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Requirements│
    │  Specification│
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Architecture│
    │  Design      │
    └──────┬───────┘
           │
    ┌──────▼───────┐          ┌──────────────┐
    │  Backend     │          │  Frontend    │
    │  Generation  │          │  Generation  │
    └──────┬───────┘          └──────┬───────┘
           │                         │
           └──────────┬──────────────┘
                      │
               ┌──────▼───────┐
               │  Integration │
               │  Testing     │
               └──────┬───────┘
                      │
               ┌──────▼───────┐
               │  Deployment  │
               │  Config      │
               └──────┬───────┘
                      │
               ┌──────▼───────┐
               │  Documentation│
               └──────────────┘
```

## Graph Properties

### Acyclicity
The task graph must always be acyclic. Cycles represent circular dependencies that cannot be resolved. The Planner service is responsible for ensuring acyclicity during graph construction.

### Connectivity
The task graph may have multiple root nodes (tasks with no dependencies) and multiple leaf nodes (tasks with no dependents). All nodes must be reachable from at least one root.

### Layering
Tasks can be grouped into layers based on their depth from root nodes. Layers enable the scheduler to reason about parallelism — tasks in the same layer with no interdependencies can execute in parallel.

### Granularity
Each node represents a single, atomic unit of work that can be assigned to one AI agent service. Nodes should be coarse enough to avoid excessive orchestration overhead but fine enough to enable meaningful parallelism and checkpointing.

## Graph Construction

The task graph is constructed in three phases:

### Phase 1: Decomposition
The Planner service decomposes the user request into a set of high-level work items. Each work item corresponds to a phase of the SDLC (research, requirements, architecture, etc.).

### Phase 2: Refinement
Each work item is refined into one or more tasks. Refinement considers:
- The complexity and scope of the work item
- The capabilities of the target AI agent service
- The need for human review checkpoints
- The expected duration and cost of each task

### Phase 3: Dependency Resolution
Dependencies between tasks are identified and encoded as edges. Dependencies arise from:
- **Data dependencies** — Task B requires output from Task A
- **Sequential dependencies** — Task B must logically follow Task A
- **Resource dependencies** — Task B requires resources produced by Task A
- **Review dependencies** — Task B requires human approval of Task A's output

## Graph Operations

### Topological Sort
Produces a linear ordering of tasks that respects all dependencies. Used by the scheduler to determine execution order.

### Parallel Set Identification
Identifies sets of tasks that can execute in parallel (tasks with no transitive dependencies between them). Used by the scheduler to maximize throughput.

### Critical Path Analysis
Identifies the longest path through the graph — the sequence of tasks that determines the minimum project duration. Used for progress estimation and bottleneck identification.

### Subgraph Extraction
Extracts a subset of the graph for focused execution or re-execution. Used during recovery to re-run only the affected portion of the graph.

## Graph Versioning

The task graph is versioned. Each modification (re-planning, recovery, human intervention) produces a new graph version. The version history enables:

- **Audit** — Tracking how the plan evolved over time
- **Recovery** — Reverting to a previous graph version if re-planning introduces errors
- **Comparison** — Diffing graph versions to understand what changed

## Future Implementation Notes

- The task graph should be stored as a materialized data structure, not computed on the fly
- Graph operations (topological sort, parallel set identification) should be cached and invalidated on graph changes
- Large graphs (1000+ nodes) should support lazy loading of subgraphs
- The graph should be serializable to JSON for storage, transmission, and debugging

## Open Questions

- Should the task graph support dynamic expansion — where a running task can spawn new sub-tasks that are added to the graph?
- How should the system handle diamond dependencies (multiple paths to the same task)?
- Should the graph support conditional edges (edges that are only active if a condition is met)?
- What is the maximum practical size of a task graph before performance degrades?
- Should the graph support weighted edges for cost and duration estimation?