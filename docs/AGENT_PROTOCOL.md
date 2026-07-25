# Agent Protocol

## Purpose

This document defines the communication protocol that governs interactions between the Execution Engine and AI agent services within the AutoForge AI platform. It establishes the contract for how work is requested, executed, and reported.

## Scope

This document covers the conceptual protocol design, message types, lifecycle states, and error handling patterns. Implementation details are deferred to the `packages/shared` and individual service packages.

---

## Overview

The Agent Protocol is the standardized interface through which the Execution Engine communicates with all AI agent services. Every service — regardless of its specific role — adheres to this protocol, ensuring uniform handling of task dispatch, execution, result reporting, and error recovery.

## Protocol Principles

- **Uniform Interface** — Every agent service exposes the same protocol surface, regardless of its internal implementation.
- **Structured Messages** — All communication uses typed, validated messages with well-defined schemas.
- **Stateless Agents** — Agents do not maintain state between invocations. All context is provided in the request.
- **Synchronous Execution** — Agents execute a single task per invocation and return a result. Long-running tasks are handled by the Execution Engine.
- **Deterministic Error Reporting** — Errors are reported using a standardized schema with codes, messages, and recovery hints.

## Message Types

### Request
Sent from the Execution Engine to an agent service:
- `taskId` — Unique identifier for the task
- `workflowId` — Identifier for the parent workflow
- `input` — Structured input data conforming to the service's contract
- `context` — Execution context including conversation history, tool results, and metadata
- `config` — Service-specific configuration (model, temperature, max tokens, etc.)

### Response
Sent from an agent service back to the Execution Engine:
- `taskId` — Echo of the task identifier
- `status` — One of: `completed`, `failed`, `partial`
- `output` — Structured output data conforming to the service's contract
- `artifacts` — Any files or artifacts produced during execution
- `metadata` — Execution metadata (token usage, duration, model used)

### Error
Sent when an agent service encounters a failure:
- `taskId` — Echo of the task identifier
- `errorCode` — Machine-readable error code
- `errorMessage` — Human-readable error description
- `recoverable` — Boolean indicating whether the task can be retried
- `retryHint` — Suggested retry strategy (immediate, backoff, no retry)

## Lifecycle States

| State | Description |
|---|---|
| `pending` | Task created but not yet dispatched |
| `dispatched` | Task sent to agent service |
| `running` | Agent service is actively processing |
| `completed` | Agent service returned a successful result |
| `failed` | Agent service returned an error |
| `partial` | Agent service returned partial results before interruption |
| `retrying` | Execution Engine is retrying after a recoverable failure |
| `cancelled` | Task was cancelled before completion |

## Future Topics

- Streaming responses for long-running agent tasks
- Bidirectional communication for agent-to-engine feedback
- Protocol versioning and backward compatibility
- Timeout and deadline propagation
- Priority and preemption signaling
- Agent capability discovery and negotiation
- Secure communication and authentication between engine and agents