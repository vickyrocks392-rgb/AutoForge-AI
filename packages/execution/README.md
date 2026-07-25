# Execution Engine

## Purpose

The Execution Engine is the operational heart of AutoForge AI. It is the runtime that receives plans from the workflow engine, dispatches work to AI agent services, monitors execution, manages state, and ensures completion. While the workflow engine defines *what* to do and *when*, the Execution Engine determines *how* it actually happens — managing resources, retries, timeouts, and the physical act of running agent tasks.

## Responsibility

- **Work Dispatch** — Receive executable units from the workflow engine and dispatch them to the appropriate AI agent services.
- **Resource Management** — Allocate and manage computational resources (LLM calls, tool executions, context windows) for each agent task.
- **Execution Monitoring** — Track the lifecycle of every dispatched task from submission through completion or failure.
- **Error Recovery** — Implement retry logic, fallback strategies, and graceful degradation when agent tasks fail.
- **State Coordination** — Maintain execution state across distributed agent runs, ensuring consistency and auditability.
- **Lifecycle Management** — Handle agent startup, shutdown, health checks, and resource cleanup.

## Relationship with AI Employees

The Execution Engine is the employer and operator of the AI agent workforce. Each service (planner, researcher, architect, etc.) is an "AI employee" that the Execution Engine manages:

- **Hiring** — The engine instantiates and configures agent services with the appropriate context and tools.
- **Tasking** — The engine assigns work units to agents, providing clear inputs and expected outputs.
- **Supervision** — The engine monitors agent progress, collects results, and intervenes on failure.
- **Compensation** — The engine manages token budgets, rate limits, and resource allocation for each agent.
- **Termination** — The engine cleans up agent contexts and releases resources when work is complete.

## Why the Execution Engine is the Heart of AutoForge AI

1. **It is the only component that touches every agent task.** Every piece of work flows through the Execution Engine.
2. **It defines reliability.** The engine's retry policies, timeout handling, and error recovery determine whether the platform is robust or fragile.
3. **It controls resource economics.** Token usage, LLM call costs, and execution time are all governed by the engine.
4. **It enables observability.** Without the engine, there is no single source of truth for what happened, when, and why.
5. **It is the platform's backbone for scaling.** Adding more agents, more tools, or more concurrent work all depend on the engine's architecture.

## Future Components

- **Task Dispatcher** — Routes executable units to the correct agent service with proper context.
- **Execution Context Manager** — Maintains per-task context including conversation history, tool state, and intermediate results.
- **Retry & Circuit Breaker** — Configurable retry policies with exponential backoff, circuit breaker patterns, and dead-letter handling.
- **Resource Governor** — Manages token budgets, rate limits, and concurrent execution slots.
- **Execution Log** — Immutable log of every execution event for audit, debugging, and replay.
- **Agent Lifecycle Manager** — Handles agent instantiation, health checking, and graceful shutdown.
- **Result Collector** — Aggregates outputs from parallel agent executions and resolves dependencies.