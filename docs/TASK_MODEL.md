# Task Model

## Purpose

This document defines the data model for tasks within the AutoForge AI execution architecture. The task model is the fundamental unit of work — every action performed by an AI agent, every tool invocation, and every decision point is represented as a task with a well-defined schema.

## Scope

This document covers the task data model, its fields, states, and lifecycle. It does not cover how tasks are scheduled, executed, or recovered — those concerns are addressed in their respective architecture documents.

---

## Task Data Model

Each task in the system is represented by the following fields:

| Field | Type | Description |
|---|---|---|
| `taskId` | UUID | Globally unique identifier for the task |
| `projectId` | UUID | Identifier of the parent project |
| `workflowId` | UUID | Identifier of the parent workflow execution |
| `title` | String | Human-readable short description |
| `description` | Text | Detailed description of the work to be performed |
| `owner` | String | The AI agent service responsible for execution (e.g., `planner`, `backend`) |
| `department` | String | The logical group the task belongs to (e.g., `planning`, `generation`, `testing`) |
| `priority` | Enum | `critical`, `high`, `medium`, `low` |
| `status` | Enum | Current state in the task lifecycle |
| `dependencies` | List[UUID] | Task IDs that must complete before this task can start |
| `estimatedCost` | Float | Estimated token cost in USD |
| `actualCost` | Float | Actual token cost after execution |
| `estimatedDuration` | Duration | Estimated wall-clock time for execution |
| `actualDuration` | Duration | Actual wall-clock time after execution |
| `maxRetries` | Integer | Maximum number of retry attempts |
| `retryCount` | Integer | Current retry attempt number |
| `confidence` | Float | Confidence score (0.0–1.0) from the agent on output quality |
| `checkpointId` | UUID | Reference to the last saved checkpoint for this task |
| `input` | JSON | Structured input data conforming to the service contract |
| `output` | JSON | Structured output data produced by the agent |
| `artifacts` | List[ArtifactRef] | References to files or objects produced by this task |
| `events` | List[EventRef] | References to events emitted during this task's lifecycle |
| `auditTrail` | List[AuditEntry] | Immutable log of all state transitions and decisions |
| `metadata` | JSON | Flexible metadata for service-specific data |
| `createdAt` | Timestamp | When the task was created |
| `updatedAt` | Timestamp | When the task was last modified |
| `startedAt` | Timestamp | When execution began |
| `completedAt` | Timestamp | When execution completed or failed |

## Task States

The task lifecycle consists of the following states:

```
                    ┌──────────┐
                    │ Created  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Queued  │
                    └────┬─────┘
                         │
                    ┌────▼──────┐
                    │  Assigned │
                    └────┬──────┘
                         │
                    ┌────▼─────┐
              ┌─────│  Running │─────┐
              │     └────┬─────┘     │
              │          │           │
     ┌────────▼───┐ ┌────▼─────┐ ┌───▼────────┐
     │  Waiting   │ │ Blocked  │ │  Review     │
     │ (Approval) │ │ (Dep.)   │ │ (Human)     │
     └────────┬───┘ └────┬─────┘ └───┬────────┘
              │          │           │
              └──────────┼───────────┘
                         │
              ┌──────────▼──────────┐
              │     Completed       │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
         ┌────│       Failed        │────┐
         │    └──────────┬──────────┘    │
         │               │               │
    ┌────▼─────┐   ┌────▼─────┐    ┌────▼──────┐
    │ Retrying │   │Cancelled │    │  Archived │
    └────┬─────┘   └──────────┘    └───────────┘
         │
         └─────────▶ Running (re-dispatch)
```

### State Descriptions

| State | Description |
|---|---|
| **Created** | Task has been defined and added to the task graph. No execution has occurred. |
| **Queued** | Task is ready for execution but has not yet been assigned to an agent. |
| **Assigned** | Task has been assigned to an AI agent service but execution has not started. |
| **Running** | Task is actively being executed by an AI agent. |
| **Waiting** | Task is paused waiting for external input (human approval, API response, user feedback). |
| **Blocked** | Task cannot proceed because one or more dependencies have failed or are incomplete. |
| **Review** | Task execution is complete and awaiting human review before proceeding. |
| **Completed** | Task executed successfully and produced valid output. |
| **Failed** | Task failed with a non-recoverable error after exhausting retries. |
| **Retrying** | Task failed with a recoverable error and is being retried. |
| **Cancelled** | Task was cancelled by user or system before completion. |
| **Archived** | Task has been archived for long-term storage and audit. |

## State Transition Rules

- A task can only transition to `Running` from `Assigned` or `Retrying`.
- A task can only transition to `Retrying` from `Failed` if `retryCount < maxRetries`.
- A task can only transition to `Blocked` from `Running` or `Waiting`.
- A task in `Completed`, `Failed`, `Cancelled`, or `Archived` is terminal — no further transitions are allowed.
- Human intervention is required to transition from `Waiting` or `Review` to `Running`.

## Audit Trail

Every state transition produces an audit entry with:

| Field | Description |
|---|---|
| `timestamp` | When the transition occurred |
| `fromState` | Previous state |
| `toState` | New state |
| `trigger` | What caused the transition (system, agent, human, timeout) |
| `reason` | Human-readable explanation |
| `actor` | Who or what performed the transition |

## Future Implementation Notes

- The task model should be versioned to support schema evolution
- Task IDs should be sortable (e.g., ULID) to enable chronological ordering without timestamps
- The audit trail should be append-only and immutable
- Task metadata should support indexing for efficient querying

## Open Questions

- Should tasks support sub-tasks (hierarchical decomposition), or should all tasks be flat with dependencies?
- How should partial task output be represented when a task completes with warnings but no errors?
- Should the confidence score be required or optional? What threshold triggers human review?
- How should the system handle tasks that produce no output (e.g., validation tasks)?