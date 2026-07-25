# Failure Recovery

## Purpose

This document defines the failure recovery architecture for the AutoForge AI execution system. It describes how the platform detects, classifies, and recovers from failures across all components — from individual LLM call failures to complete system crashes.

## Scope

This document covers failure classification, retry policies, circuit breakers, fallback strategies, and recovery procedures. It does not cover checkpointing (see CHECKPOINT_MANAGER.md) or state management (see STATE_MANAGER.md).

---

## Overview

Failure recovery is a first-class concern in the execution architecture. Given the long-running nature of projects (8–10+ hours) and the inherent non-determinism of LLM-based agents, failures are expected and must be handled gracefully. The system is designed to detect failures quickly, classify them correctly, and apply the appropriate recovery strategy — from automatic retry to human intervention.

```
                    ┌──────────────┐
                    │   Failure    │
                    │   Detected   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Classify    │
                    │  Failure     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───┐ ┌─────▼─────┐ ┌────▼────────┐
     │ Recoverable│ │Non-Recov. │ │  Unknown    │
     │            │ │           │ │             │
     └────────┬───┘ └─────┬─────┘ └────┬────────┘
              │           │            │
     ┌────────▼───┐ ┌─────▼─────┐ ┌────▼────────┐
     │  Retry     │ │  Human    │ │  Escalate   │
     │  Policy    │ │  Notify   │ │  to Human   │
     └────────┬───┘ └───────────┘ └─────────────┘
              │
     ┌────────▼───┐
     │  Backoff   │
     │  Strategy  │
     └────────┬───┘
              │
     ┌────────▼───┐
     │  Re-dispatch│
     └────────────┘
```

## Failure Classification

Failures are classified along three dimensions:

### By Source

| Source | Examples |
|---|---|
| **LLM Failure** | Model timeout, rate limit exceeded, content filter triggered, context window exceeded |
| **Tool Failure** | File system error, network timeout, API rate limit, command execution failure |
| **Agent Failure** | Invalid output format, hallucinated response, circular reasoning, task not completed |
| **Infrastructure Failure** | Database connection lost, message queue unavailable, storage full, network partition |
| **External Failure** | Git push rejected, package install failed, test suite timeout, deployment target unreachable |
| **Human Failure** | Approval timeout, invalid review feedback, cancellation request |

### By Severity

| Severity | Description | Example |
|---|---|---|
| **Warning** | Non-critical issue, execution can continue | LLM response slightly malformed but fixable |
| **Error** | Task failed but can be retried | Tool timeout, rate limit exceeded |
| **Critical** | Task failed, system may be degraded | Database connection lost, checkpoint save failed |
| **Fatal** | System cannot continue without intervention | Corrupt state, unrecoverable data loss |

### By Recoverability

| Category | Description | Recovery Strategy |
|---|---|---|
| **Recoverable** | Failure can be resolved by retrying | Automatic retry with backoff |
| **Non-Recoverable** | Failure cannot be resolved by retrying | Human notification, task cancellation |
| **Unknown** | System cannot determine recoverability | Escalate to human operator |

## Retry Policies

### Exponential Backoff
The default retry strategy. Wait time increases exponentially with each retry attempt.

```
retry_delay = base_delay * (backoff_factor ^ retry_count) + jitter
```

- `base_delay`: 1 second
- `backoff_factor`: 2
- `max_delay`: 60 seconds
- `jitter`: random 0–100ms

### Constant Backoff
Fixed wait time between retries. Used for rate-limited operations where the rate limit window is known.

```
retry_delay = 30 seconds (constant)
```

### Immediate Retry
No wait time. Used for transient failures that are likely to succeed immediately on retry (e.g., network timeouts).

```
retry_delay = 0 seconds
```

### No Retry
Task is failed immediately. Used for non-recoverable failures (e.g., invalid input, corrupt state).

## Circuit Breaker

The circuit breaker prevents repeated retries against a failing component, allowing it time to recover.

### States
- **Closed** — Normal operation. Requests pass through.
- **Open** — Failure threshold exceeded. Requests are immediately failed without attempting.
- **Half-Open** — After cooldown period, a single test request is allowed. If it succeeds, the circuit closes. If it fails, the circuit re-opens.

### Configuration
- **Failure threshold**: 5 consecutive failures
- **Cooldown period**: 30 seconds
- **Half-open max requests**: 1

## Fallback Strategies

### Model Fallback
When a task fails with one LLM model, retry with a different model:

1. Primary model fails → retry with secondary model
2. Secondary model fails → retry with fallback model
3. All models fail → task fails

### Service Fallback
When an AI agent service is unavailable, attempt to use an alternative service:

1. Primary service fails → retry with degraded service (reduced capabilities)
2. Degraded service fails → task fails, human notified

### Partial Output
When a task produces partial output before failing, the partial output is preserved and made available to dependent tasks. Dependent tasks can proceed with reduced functionality.

## Recovery Procedures

### LLM Failure Recovery
1. Classify failure (timeout, rate limit, content filter, etc.)
2. If rate limit: apply constant backoff, retry
3. If timeout: apply exponential backoff, retry
4. If content filter: reduce response scope, retry with stricter constraints
5. If context window exceeded: truncate context, retry
6. After max retries: apply model fallback
7. After all models exhausted: task fails, human notified

### Tool Failure Recovery
1. Classify failure (timeout, network, permission, etc.)
2. If timeout: retry with longer timeout
3. If network: retry with exponential backoff
4. If permission: notify human, task waits
5. If tool unavailable: attempt alternative tool, task fails if no alternative

### Agent Failure Recovery
1. Validate agent output against expected schema
2. If schema violation: provide error feedback to agent, retry with corrected prompt
3. If hallucination detected: reduce agent scope, retry with stricter constraints
4. If circular reasoning detected: reset agent context, retry with fresh state
5. After max retries: task fails, human notified

### Infrastructure Failure Recovery
1. Detect failure via heartbeat timeout or error signal
2. If database failure: attempt reconnection with backoff
3. If message queue failure: buffer events locally, replay on reconnection
4. If storage failure: switch to secondary storage, alert operator
5. If unrecoverable: restore from last checkpoint on a different infrastructure

### Human Interruption Recovery
1. Pause execution at the next safe point (task boundary)
2. Preserve all running task contexts as checkpoints
3. Present current state to human operator
4. On resume: restore from checkpoint, continue execution

### Unexpected Shutdown Recovery
1. On startup, check for incomplete executions
2. Load the most recent checkpoint
3. Verify checkpoint integrity
4. Restore state to state manager
5. Re-dispatch tasks that were running at checkpoint time
6. Mark tasks that completed after checkpoint as completed
7. Resume scheduling from restored queue state

## Future Implementation Notes

- Retry policies should be configurable per task type and per service
- Circuit breaker state should be persisted to survive restarts
- Failure metrics should be collected for trend analysis and early warning
- The system should support automated canary testing of recovery procedures

## Open Questions

- How should the system handle cascading failures where one task failure causes multiple dependent tasks to fail?
- Should the system support automated rollback of completed tasks when a downstream task fails?
- How should the system handle failures that occur during checkpoint creation?
- Should the system support predictive failure detection based on metrics trends?
- How should the system handle failures that require coordination between multiple recovery strategies?