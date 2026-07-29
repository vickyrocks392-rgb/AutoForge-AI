# Execution Architecture

> **Note:** This document describes the execution subsystem in terms consistent with Architecture v1.0 (`architecture/ARCHITECTURE.md`). The canonical architecture describes the Execution Engine as a Platform Engine responsible for executing units of work dispatched by the Workflow Engine, managing engineering loops, coordinating engineering workers, and producing artifacts.

## Purpose

This document defines the overall execution architecture for AutoForge AI — the system that transforms a user request into a completed software engineering project through autonomous, long-running, fault-tolerant execution. It describes how the platform orchestrates engineering workers, manages state, handles failures, and ensures traceability across multi-hour execution sessions.

## Scope

This document covers the high-level architecture of the execution subsystem, its major components, their interactions, and the design principles that govern them. It does not cover implementation details of individual components, which are documented in their respective architecture documents. The canonical architecture specification is `architecture/ARCHITECTURE.md`.

---

## Architecture Overview

The execution architecture is designed around a **directed acyclic graph (DAG) execution model** with **event-driven orchestration**, **checkpoint-based recovery**, and **multi-tier state management**. It is built to support execution sessions lasting 8–10+ hours across multiple AI agents, LLM providers, and infrastructure targets.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Execution Architecture                        │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   Scheduler  │───▶│  Task Graph  │───▶│   State Manager     │  │
│  │              │    │  Executor    │    │                      │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────────┘  │
│         │                   │                                        │
│         │         ┌─────────▼─────────┐                              │
│         │         │  Checkpoint       │                              │
│         └────────▶│  Manager          │                              │
│                   └─────────┬─────────┘                              │
│                             │                                        │
│  ┌──────────────┐    ┌──────▼───────┐    ┌──────────────────────┐  │
│  │  Event Bus   │◀──▶│ Model Router │───▶│   AI Agent Services  │  │
│  │              │    │              │    │   (Planner, Backend, │  │
│  └──────────────┘    └──────────────┘    │   Testing, etc.)     │  │
│                                          └──────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Failure Recovery Engine                      │  │
│  │  (Retry Policies | Circuit Breakers | Fallback Strategies)    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Crash-Only Recovery
The system is designed to be killed at any point and resume from the last checkpoint. There is no graceful shutdown protocol — only checkpoint persistence and recovery.

### 2. Deterministic Task Graphs
Given the same inputs and the same checkpoint state, the task graph executor must produce the same sequence of task executions. This enables replay debugging and audit.

### 3. Eventual Consistency with Observability
State is eventually consistent across components. The event bus provides the single source of truth for what happened, and the state manager provides the current authoritative state.

### 4. Isolation of Concerns
Each component in the execution architecture has a single responsibility. The scheduler does not execute tasks. The state manager does not route models. The checkpoint manager does not handle retries.

### 5. Graceful Degradation
When a component fails, the system degrades to a known safe state rather than crashing or producing incorrect output. Partial results are preserved, and the system can resume from the last valid checkpoint.

## Major Components

| Component | Document | Primary Responsibility |
|---|---|---|
| **Task Graph** | `TASK_GRAPH.md` | Defines the DAG of work items and their dependencies |
| **Task Model** | `TASK_MODEL.md` | Defines the data model for individual tasks |
| **Scheduler** | `SCHEDULER.md` | Determines which tasks to execute and when |
| **State Manager** | `STATE_MANAGER.md` | Maintains authoritative state of all execution entities |
| **Checkpoint Manager** | `CHECKPOINT_MANAGER.md` | Persists execution state for recovery |
| **Event Bus** | `EVENT_BUS.md` | Provides event-driven communication between components |
| **Model Router** | `MODEL_ROUTER.md` | Routes tasks to appropriate LLM providers and models |
| **Failure Recovery** | `FAILURE_RECOVERY.md` | Handles retries, fallbacks, and error recovery |
| **Execution Lifecycle** | `EXECUTION_LIFECYCLE.md` | Describes the end-to-end execution flow |

## Inputs

- **User Request** — A high-level description of the software engineering task
- **Project Configuration** — Language, framework, deployment target, coding standards
- **Context** — Existing codebase, dependencies, reference materials

## Outputs

- **Completed Project** — Generated code, tests, documentation, deployment configuration
- **Execution Trace** — Complete audit log of every task, decision, and state transition
- **Artifacts** — All generated files, logs, and reports

## Interactions

The execution architecture interacts with:

- **Workflow Engine** (`packages/workflows`) — Receives the workflow DAG definition; reports execution progress and results
- **Memory Engine** (`packages/memory`) — Persists state, checkpoints, and artifacts
- **AI Agent Services** (`services/*`) — Dispatches tasks to agent services and collects results
- **LLM Providers** — Routes model requests through the Model Router
- **External Tools** — Git, package managers, test runners, deployment targets

## Future Implementation Notes

- The execution architecture should be implemented as a set of coordinated services, not a monolithic engine
- Each major component should be independently testable and deployable
- The event bus should be pluggable (in-memory for development, NATS/RabbitMQ for production)
- Checkpoint frequency should be configurable per task type and duration
- The scheduler should support dynamic priority adjustment based on execution progress

## Open Questions

- Should the task graph be fully materialized before execution begins, or should it be expanded dynamically as tasks complete?
- How should human approval checkpoints interact with the scheduler — should they pause the entire graph or only block dependent paths?
- What is the optimal checkpoint granularity for 10-hour execution sessions?
- Should the model router support cost-optimized routing (e.g., use cheaper models for simple tasks)?
- How should the system handle LLM context window limits during long-running agent sessions?