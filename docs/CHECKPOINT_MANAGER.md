# Checkpoint Manager

## Purpose

This document defines the checkpoint manager — the component responsible for persisting execution state at strategic points to enable recovery from failures, crashes, and interruptions. The checkpoint manager is the foundation of the platform's fault tolerance and recoverability.

## Scope

This document covers checkpoint strategies, storage, versioning, and restoration. It does not cover the state model itself (see STATE_MANAGER.md) or failure recovery strategies (see FAILURE_RECOVERY.md).

---

## Overview

The checkpoint manager periodically captures the complete state of the execution system — task statuses, agent contexts, intermediate results, and queue states — and persists them to durable storage. When a failure occurs, the system can restore from the most recent checkpoint and resume execution with minimal data loss.

```
                    ┌──────────────┐
                    │  Execution   │
                    │  Components  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Checkpoint  │
                    │   Manager    │
                    │              │
            ┌───────┤  ┌────────┐  ├───────┐
            │       │  │ Policy │  │       │
            │       │  │ Engine │  │       │
            │       │  └────────┘  │       │
            │       └──────┬───────┘       │
            │              │               │
     ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │  Checkpoint │ │  Checkpoint│ │  Checkpoint │
     │  Store      │ │  Index     │ │  Validator  │
     └─────────────┘ └────────────┘ └─────────────┘
```

## Checkpoint Model

Each checkpoint captures the following state:

| Component | State Captured |
|---|---|
| **Task Graph** | Current graph version, all task definitions and dependencies |
| **Task States** | Status, input, output, artifacts, audit trail for every task |
| **Agent Contexts** | Conversation history, tool results, intermediate outputs for running tasks |
| **Queue States** | Contents of ready, priority, retry, blocked, and approval queues |
| **Worker States** | Status and assignment of all worker slots |
| **Project State** | Progress, timing, configuration |
| **Event Log Offset** | Position in the event log for replay |

## Checkpoint Structure

| Field | Description |
|---|---|
| `checkpointId` | UUID | Globally unique identifier |
| `projectId` | UUID | The project this checkpoint belongs to |
| `timestamp` | Timestamp | When the checkpoint was created |
| `version` | Integer | Checkpoint schema version |
| `stateHash` | String | Hash of the captured state for integrity verification |
| `parentCheckpointId` | UUID | Previous checkpoint in the chain |
| `taskCount` | Integer | Number of tasks in the checkpoint |
| `runningTaskCount` | Integer | Number of tasks that were running at checkpoint time |
| `data` | JSON | The serialized state data |
| `size` | Integer | Size of the checkpoint data in bytes |
| `duration` | Duration | How long it took to create this checkpoint |

## Checkpoint Strategies

### Time-Based Checkpointing
Checkpoints are created at regular time intervals (e.g., every 5 minutes). Simple and predictable, but may capture unnecessary intermediate states.

**Use case:** Default strategy for most projects.

### Task-Based Checkpointing
Checkpoints are created after specific task completions (e.g., after every task, or after every N tasks). More targeted but may miss long-running tasks.

**Use case:** Projects with heterogeneous task durations.

### Hybrid Checkpointing
Checkpoints are created on a time interval AND after significant task completions. Provides the best coverage.

**Use case:** Long-running projects where both time and task boundaries matter.

### Manual Checkpointing
Checkpoints are created on demand by a human operator or by specific system events (e.g., before a high-risk task).

**Use case:** Before human approval checkpoints or high-cost operations.

## Checkpoint Storage

### Storage Format
Checkpoints are serialized as compressed JSON and stored in durable object storage.

### Storage Layout
```
checkpoints/
  {projectId}/
    {checkpointId}.json.gz
    index.json
```

### Retention Policy
- **Active projects** — Keep all checkpoints for the duration of execution
- **Completed projects** — Keep the final checkpoint and hourly snapshots for 30 days
- **Archived projects** — Keep only the final checkpoint indefinitely

## Checkpoint Lifecycle

### Creation
1. Checkpoint manager receives a checkpoint trigger (time, task completion, manual)
2. Manager freezes the current state snapshot
3. Manager serializes and compresses the state
4. Manager computes a hash of the serialized state
5. Manager writes the checkpoint to storage
6. Manager updates the checkpoint index
7. Manager publishes `checkpoint.saved` event
8. Manager releases the frozen state

### Restoration
1. System detects failure or receives a restore request
2. Manager identifies the most recent valid checkpoint
3. Manager loads and decompresses the checkpoint data
4. Manager verifies the state hash for integrity
5. Manager restores state to the state manager
6. Manager restores queue states to the scheduler
7. Manager publishes `checkpoint.restored` event
8. System resumes execution from the restored state

### Validation
Each checkpoint is validated on creation:
- **Integrity check** — State hash matches the serialized data
- **Consistency check** — All referenced entities exist and are in valid states
- **Completeness check** — All required fields are present

## Checkpoint Index

The checkpoint index maintains a lightweight catalog of all checkpoints for a project:

| Field | Description |
|---|---|
| `checkpointId` | Unique identifier |
| `timestamp` | When the checkpoint was created |
| `trigger` | What triggered the checkpoint (time, task, manual) |
| `taskCount` | Number of tasks in the checkpoint |
| `runningTaskCount` | Number of running tasks |
| `size` | Size of the checkpoint data |
| `valid` | Whether the checkpoint passed validation |

## Future Implementation Notes

- Checkpoint creation should be asynchronous to avoid blocking execution
- Large checkpoints should support incremental snapshots (only store changes since last checkpoint)
- Checkpoint storage should support configurable compression levels
- The checkpoint manager should expose metrics (checkpoint size, duration, frequency) for monitoring

## Open Questions

- What is the optimal checkpoint frequency for 10-hour execution sessions?
- Should checkpoints support partial restoration (restore only a subset of tasks)?
- How should the system handle checkpoint corruption — should it fall back to the previous checkpoint automatically?
- Should checkpoints be encrypted at rest?
- How should the system handle checkpoints that are too large to restore quickly?