# Execution Engine

## Purpose

This document describes the Execution Engine — the operational runtime that dispatches, monitors, and manages AI agent tasks within the AutoForge AI platform. It is the component that turns plans into action.

## Scope

This document covers the conceptual architecture of the Execution Engine, its responsibilities, and its relationship to other platform components. Implementation details are deferred to the `packages/execution` package.

---

## Overview

The Execution Engine is the bridge between the workflow engine's abstract plans and the concrete execution of AI agent tasks. While the workflow engine defines the DAG of work items, the Execution Engine handles the actual running of those items — managing LLM calls, tool executions, context windows, and agent lifecycles.

## Key Concepts

- **Executable Unit** — A discrete piece of work that can be dispatched to an agent service. The smallest unit of execution.
- **Execution Context** — The state, conversation history, tool results, and metadata associated with a single executable unit.
- **Agent Session** — A managed interaction with an AI agent service, spanning one or more executable units.
- **Execution Plan** — A collection of executable units with dependencies, derived from the workflow engine's output.

## Relationship to Other Components

| Component | Relationship |
|---|---|
| `packages/workflows` | Defines the DAG of work; Execution Engine executes each node |
| `packages/memory` | Provides state persistence for execution contexts |
| `packages/tools` | Provides tool definitions that agents use during execution |
| `packages/prompts` | Provides prompt templates rendered with execution context |
| `services/*` | AI agent services that receive and process executable units |

## Future Topics

- Task dispatch strategies (round-robin, priority-based, affinity-based)
- Execution context serialization and checkpointing
- Parallel execution and dependency resolution
- Token budget management and cost tracking
- Circuit breaker patterns for failing agents
- Execution replay for debugging and audit
- Agent session pooling and reuse