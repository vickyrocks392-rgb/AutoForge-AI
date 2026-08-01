# Runtime State Manager Specification v1.0

> **Status:** Frozen — Phase 3.1 Deliverable
> **Canonical Reference:** This document is the authoritative specification for the Runtime State Manager subsystem. All implementation must conform to this specification.
> **Architecture Alignment:** This specification is consistent with `architecture/ARCHITECTURE.md` v1.0, `docs/subsystems/kernel/KERNEL_SPECIFICATION.md` v1.0, and all subsystem architecture documents.

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Responsibilities](#2-responsibilities)
3. [Non-Responsibilities](#3-non-responsibilities)
4. [Design Philosophy](#4-design-philosophy)
5. [Architectural Principles](#5-architectural-principles)
6. [Public Interfaces](#6-public-interfaces)
7. [Internal Components](#7-internal-components)
8. [Runtime State Model](#8-runtime-state-model)
9. [Project State Model](#9-project-state-model)
10. [Workflow State Model](#10-workflow-state-model)
11. [Engineering Loop State Model](#11-engineering-loop-state-model)
12. [Worker State Model](#12-worker-state-model)
13. [Task State Model](#13-task-state-model)
14. [Checkpoint Model](#14-checkpoint-model)
15. [Runtime Persistence Model](#15-runtime-persistence-model)
16. [Runtime Lifecycle](#16-runtime-lifecycle)
17. [State Transition Engine](#17-state-transition-engine)
18. [Transition Validation Rules](#18-transition-validation-rules)
19. [Recovery Model](#19-recovery-model)
20. [Runtime Queries](#20-runtime-queries)
21. [Runtime Events](#21-runtime-events)
22. [Event Interactions](#22-event-interactions)
23. [Kernel Interactions](#23-kernel-interactions)
24. [Platform Engine Interactions](#24-platform-engine-interactions)
25. [Shared Platform Service Interactions](#25-shared-platform-service-interactions)
26. [Failure Recovery](#26-failure-recovery)
27. [State Consistency Guarantees](#27-state-consistency-guarantees)
28. [Concurrency Model](#28-concurrency-model)
29. [Sequence Diagrams](#29-sequence-diagrams)
30. [State Diagrams](#30-state-diagrams)
31. [Public API Reference](#31-public-api-reference)
32. [Internal Components Reference](#32-internal-components-reference)
33. [Extension Points](#33-extension-points)
34. [ADR Requirements](#34-adr-requirements)
35. [Glossary](#35-glossary)

---

## 1. Purpose

The Runtime State Manager is the authoritative source of runtime state for the entire AutoForge AI OS. It is the single component responsible for owning, maintaining, and governing all runtime state across the platform.

The Runtime State Manager ensures that every component in the platform has access to consistent, current, and authoritative state information. It owns state transitions, validates transitions, persists state, creates checkpoints, maintains history, and publishes state change events.

### What the Runtime State Manager Is

- The **authoritative source** of runtime state for the entire platform
- The **owner** of all runtime state entities (projects, workflows, loops, workers, tasks, checkpoints)
- The **validator** of all state transitions
- The **persistor** of state to durable storage
- The **publisher** of state change events
- The **recorder** of state history
- The **provider** of runtime query APIs

### What the Runtime State Manager Is Not

- The Runtime State Manager is **NOT** an orchestration engine
- The Runtime State Manager is **NOT** an execution engine
- The Runtime State Manager is **NOT** a planning engine
- The Runtime State Manager is **NOT** an event bus
- The Runtime State Manager is **NOT** a memory store
- The Runtime State Manager is **NOT** a knowledge base
- The Runtime State Manager **NEVER** makes orchestration decisions
- The Runtime State Manager **NEVER** executes work
- The Runtime State Manager **NEVER** performs engineering tasks

---

## 2. Responsibilities

The Runtime State Manager owns the following responsibilities:

### 2.1 Runtime State Ownership

- **Own runtime state** — Maintain the authoritative state of all runtime entities
- **Own project state** — Maintain project lifecycle state (Created, Planning, Running, Reviewing, Paused, Completing, Finished, Failed, Cancelled)
- **Own workflow state** — Maintain workflow execution state
- **Own engineering loop state** — Maintain engineering loop lifecycle state (IDLE, PLAN, EXECUTE, REVIEW, COMPLETE, REMEDIATE, ESCALATE, FAILED)
- **Own worker state** — Maintain worker availability and assignment state
- **Own task state** — Maintain task lifecycle state (Pending, Running, Completed, Failed, Waiting, Blocked, Ready, Retrying)
- **Own execution state** — Maintain execution session state
- **Own checkpoint state** — Maintain checkpoint metadata and lineage
- **Own recovery state** — Maintain recovery operation state
- **Own runtime metadata** — Maintain platform-wide runtime metadata

### 2.2 State Transition Management

- **Validate transitions** — Validate all state transition requests against defined rules
- **Execute transitions** — Execute validated state transitions atomically
- **Reject illegal transitions** — Reject state transitions that violate transition rules
- **Record transitions** — Record all state transitions in audit trail
- **Publish transition events** — Publish events for all state transitions

### 2.3 State Persistence

- **Persist state** — Write state to durable storage
- **Maintain consistency** — Ensure state is consistent across all reads
- **Support recovery** — Enable state restoration from persisted data
- **Manage versions** — Version state for optimistic concurrency control
- **Handle conflicts** — Resolve concurrent state update conflicts

### 2.4 Checkpoint Management

- **Create checkpoints** — Create state snapshots at defined points
- **Maintain checkpoints** — Store and index checkpoints
- **Track lineage** — Maintain checkpoint lineage and relationships
- **Support restoration** — Enable state restoration from checkpoints
- **Manage cleanup** — Clean up obsolete checkpoints according to policy

### 2.5 State History

- **Record history** — Maintain complete history of state changes
- **Enable audit** — Provide audit trail of all state transitions
- **Support replay** — Enable state history replay for debugging and analysis
- **Track lineage** — Maintain entity lineage and relationships

### 2.6 Runtime Queries

- **Provide query APIs** — Expose rich query APIs for runtime state
- **Support filtering** — Filter state by entity type, status, project, time range
- **Support aggregation** — Aggregate state metrics and statistics
- **Enable monitoring** — Provide state information for observability
- **Support dashboards** — Provide state projections for dashboards

### 2.7 Event Publishing

- **Publish state events** — Publish events for all state changes
- **Maintain event consistency** — Ensure events reflect state changes accurately
- **Support event ordering** — Preserve event ordering for state transitions
- **Enable event replay** — Support event replay for state reconstruction

---

## 3. Non-Responsibilities

The Runtime State Manager explicitly does NOT own the following:

### 3.1 Orchestration

- **Orchestration** — The Runtime State Manager does not orchestrate execution
- **Planning** — The Runtime State Manager does not plan work
- **Scheduling** — The Runtime State Manager does not schedule tasks
- **Worker dispatch** — The Runtime State Manager does not dispatch workers
- **Model selection** — The Runtime State Manager does not select AI models
- **Retry logic** — The Runtime State Manager does not implement retry policies
- **Recovery logic** — The Runtime State Manager does not implement recovery strategies

### 3.2 Execution

- **Engineering work** — The Runtime State Manager does not perform engineering tasks
- **Code generation** — The Runtime State Manager does not generate code
- **Research** — The Runtime State Manager does not perform research
- **Review** — The Runtime State Manager does not review artifacts
- **Testing** — The Runtime State Manager does not execute tests
- **Deployment** — The Runtime State Manager does not deploy applications

### 3.3 Infrastructure

- **Event routing** — The Runtime State Manager publishes events but does not implement the Event Bus
- **Memory management** — The Runtime State Manager uses memory but does not implement the Memory Engine
- **Knowledge management** — The Runtime State Manager uses knowledge but does not implement the Knowledge Engine
- **Model execution** — The Runtime State Manager records model assignments but does not execute models
- **Connector management** — The Runtime State Manager uses connectors but does not implement the Connector Layer

### 3.4 Decision Ownership

- **Orchestration decisions** — The Kernel makes orchestration decisions; the Runtime State Manager records them
- **Engineering decisions** — Workers make engineering decisions; the Runtime State Manager records them
- **Quality assessments** — The Review Engine assesses quality; the Runtime State Manager records results
- **Model selection** — The Model Router selects models; the Runtime State Manager records assignments
- **Recovery strategies** — The Execution Continuity Manager determines recovery; the Runtime State Manager records recovery state

### 3.5 What the Runtime State Manager Delegates

| Capability | Owner | Runtime State Manager's Role |
|---|---|---|
| Orchestration | Kernel | Record orchestration state |
| Execution | Execution Engine | Record execution state |
| Planning | Workflow Engine | Record planning state |
| Event routing | Event Bus | Publish state change events |
| Memory operations | Memory Engine | Use memory for state storage |
| Knowledge retrieval | Knowledge Engine | Use knowledge for context |
| Model execution | Model Router | Record model assignments |
| Recovery | Execution Continuity Manager | Record recovery state |
| External access | Connector Layer | Use connectors for persistence |
| Quality evaluation | Review Engine | Record review results |
| Observability | Observability | Provide state metrics |

---

## 4. Design Philosophy

The Runtime State Manager is designed around the following philosophical principles:

### 4.1 State is Authority

The Runtime State Manager is the single source of truth for runtime state. Every component reads from and writes to the Runtime State Manager. There is no alternative source of state information. State in the Runtime State Manager is always the authoritative state.

### 4.2 Nobody Modifies State Directly

No component directly modifies state. Every component requests a state transition. The Runtime State Manager validates the transition, executes it atomically, persists it, publishes events, and records history. This ensures that all state changes are controlled, validated, and auditable.

### 4.3 State-Driven Coordination

The platform coordinates through state, not through imperative control flow. State is the canonical record of progress. Components read state to understand current conditions, transition state to trigger actions, and observe state changes to detect completion. This enables loose coupling, recoverability, and observability.

### 4.4 Event-Driven Communication

The Runtime State Manager communicates state changes through events. It publishes events to signal state transitions and subscribes to events to detect external state changes. This decouples the Runtime State Manager from direct dependencies on other components and enables independent evolution.

### 4.5 First-Class Checkpoints

Checkpoints are first-class citizens in the state model. The Runtime State Manager treats checkpoints as critical state artifacts that enable recovery, replay, and audit. Checkpoints are created automatically, maintained systematically, and restored reliably.

### 4.6 Complete History

Every state transition is recorded in history. The Runtime State Manager maintains a complete, immutable audit trail of all state changes. This enables debugging, audit, compliance, and analysis.

### 4.7 Strong Consistency

The Runtime State Manager provides strong consistency guarantees for state reads and writes. Components can rely on state being consistent and current. The Runtime State Manager uses proven concurrency control mechanisms to ensure consistency.

### 4.8 Interface-First Design

The Runtime State Manager defines explicit interfaces for all interactions. Components depend on interfaces, not implementations. This enables the Runtime State Manager to evolve internally without affecting consumers.

---

## 5. Architectural Principles

The Runtime State Manager adheres to the following architectural principles:

### 5.1 Single Responsibility

The Runtime State Manager has one responsibility: own runtime state. It does not attempt to do anything else. All state-related concerns are concentrated in the Runtime State Manager.

### 5.2 Single Source of Truth

The Runtime State Manager is the single source of truth for runtime state. There is no alternative state store, no cached state that diverges, no shadow state. The Runtime State Manager's state is always authoritative.

### 5.3 Interface First

The Runtime State Manager defines explicit interfaces for all state operations. Consumers depend on interfaces, not implementations. Implementation details are hidden behind contracts.

### 5.4 No Circular Dependencies

The Runtime State Manager may depend on infrastructure services (Event Bus, persistence layer), but no component depends on the internal implementation of the Runtime State Manager. The dependency graph is strictly hierarchical.

### 5.5 Event-Driven Communication

The Runtime State Manager communicates through events, not direct invocations. It publishes events for state changes and subscribes to events for external state changes. This decouples the Runtime State Manager from consumers.

### 5.6 State-Driven Coordination

The Runtime State Manager coordinates through state transitions, not imperative commands. State transitions are the mechanism for coordination. Components observe state changes to detect events and trigger actions.

### 5.7 Loose Coupling

The Runtime State Manager depends on contracts, not implementations. It knows what persistence providers can do, not how they do it. This enables persistence providers to evolve independently.

### 5.8 High Cohesion

All state management logic resides in the Runtime State Manager. There is no state management logic scattered across other components. This makes the state model explicit, inspectable, and maintainable.

### 5.9 Idempotency

All Runtime State Manager operations are idempotent. If an operation is invoked multiple times (due to retry or event replay), the result is the same as if it were invoked once. This enables safe retry and event replay.

### 5.10 Observability

Every Runtime State Manager operation is observable. Every state transition, every validation, every persistence operation is logged and traceable. There are no black boxes.

### 5.11 Thread Safety by Design

The Runtime State Manager is thread-safe by design. All state operations are safe for concurrent access. The Runtime State Manager uses proven concurrency control mechanisms (optimistic concurrency, versioning) to prevent race conditions.

### 5.12 Deterministic

The Runtime State Manager is deterministic. Given the same sequence of state transition requests, the Runtime State Manager produces the same sequence of state changes. This enables testing, debugging, and replay.

---

## 6. Public Interfaces

The Runtime State Manager exposes the following public interfaces:

### 6.1 State Write Interface

**Purpose:** Request state transitions for runtime entities.

**Operations:**

**Create Project**
- Input: `projectData` — Project initialization data
- Output: `projectId` — Unique project identifier
- Behavior:
  1. Validate project data
  2. Create project state with status = Created
  3. Persist state
  4. Publish `project.created` event
  5. Return projectId

**Transition Project State**
- Input: `projectId`, `newStatus`, `metadata` (optional)
- Output: `success` — Boolean indicating transition success
- Behavior:
  1. Validate transition (current status → new status)
  2. If valid: Execute transition
  3. Persist state
  4. Create checkpoint (if required)
  5. Publish state change event
  6. Record in history
  7. Return success
  8. If invalid: Return validation error

**Update Task State**
- Input: `taskId`, `newStatus`, `metadata` (optional)
- Output: `success` — Boolean indicating update success
- Behavior:
  1. Validate transition
  2. If valid: Execute transition
  3. Persist state
  4. Publish state change event
  5. Record in history
  6. Return success

**Create Checkpoint**
- Input: `projectId`, `checkpointType`, `metadata` (optional)
- Output: `checkpointId` — Unique checkpoint identifier
- Behavior:
  1. Capture current state snapshot
  2. Create checkpoint record
  3. Persist checkpoint
  4. Publish `checkpoint.created` event
  5. Return checkpointId

**Restore Checkpoint**
- Input: `checkpointId`, `restoreType` (full/partial)
- Output: `success` — Boolean indicating restoration success
- Behavior:
  1. Validate checkpoint exists and is restorable
  2. Load checkpoint state
  3. Restore state to checkpoint snapshot
  4. Publish `checkpoint.restored` event
  5. Record in history
  6. Return success

### 6.2 State Read Interface

**Purpose:** Query runtime state.

**Operations:**

**Get Project State**
- Input: `projectId`
- Output: `projectState` — Complete project state
- Behavior:
  1. Read project state from persistence
  2. Return current state

**Get Task State**
- Input: `taskId`
- Output: `taskState` — Complete task state
- Behavior:
  1. Read task state from persistence
  2. Return current state

**Get Worker State**
- Input: `workerId`
- Output: `workerState` — Complete worker state
- Behavior:
  1. Read worker state from persistence
  2. Return current state

**Get Checkpoint**
- Input: `checkpointId`
- Output: `checkpoint` — Complete checkpoint data
- Behavior:
  1. Read checkpoint from persistence
  2. Return checkpoint data

### 6.3 Query Interface

**Purpose:** Query runtime state with filters and aggregations.

**Operations:**

**Get Projects by Status**
- Input: `status` — Project status filter
- Output: `List[projectState]` — Projects matching status
- Behavior:
  1. Query projects by status
  2. Return matching projects

**Get Tasks by Project**
- Input: `projectId`
- Output: `List[taskState]` — All tasks in project
- Behavior:
  1. Query tasks by project
  2. Return matching tasks

**Get Tasks by Status**
- Input: `status` — Task status filter
- Output: `List[taskState]` — Tasks matching status
- Behavior:
  1. Query tasks by status
  2. Return matching tasks

**Get Running Workflows**
- Input: None
- Output: `List[workflowState]` — All running workflows
- Behavior:
  1. Query workflows with status = Running
  2. Return matching workflows

**Get Worker Status**
- Input: None
- Output: `List[workerState]` — All worker states
- Behavior:
  1. Query all workers
  2. Return worker states

**Get Execution Progress**
- Input: `projectId`
- Output: `progress` — Execution progress metrics
- Behavior:
  1. Calculate progress from task states
  2. Return progress metrics

**Get Runtime History**
- Input: `entityType`, `entityId`, `timeRange` (optional)
- Output: `List[stateTransition]` — State transition history
- Behavior:
  1. Query state transition history
  2. Filter by entity type and ID
  3. Filter by time range (if provided)
  4. Return history

**Get Checkpoint History**
- Input: `projectId`
- Output: `List[checkpoint]` — All checkpoints for project
- Behavior:
  1. Query checkpoints by project
  2. Return checkpoint list

**Get Failure History**
- Input: `projectId` (optional)
- Output: `List[failureRecord]` — Failure records
- Behavior:
  1. Query failure records
  2. Filter by project (if provided)
  3. Return failure records

### 6.4 Event Subscription Interface

**Purpose:** Subscribe to state change events.

**Operations:**

**Subscribe to State Changes**
- Input: `entityType`, `callback`
- Output: `subscriptionId` — Unique subscription identifier
- Behavior:
  1. Register subscription for entity type
  2. Route state change events to callback
  3. Return subscription ID

**Unsubscribe**
- Input: `subscriptionId`
- Output: `success` — Boolean indicating unsubscription success
- Behavior:
  1. Remove subscription
  2. Return success

---

## 7. Internal Components

The Runtime State Manager consists of the following internal components:

### Architecture Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│              Runtime State Manager                          │
│         (Authoritative State Owner)                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    State Transition Engine                   │
│  (Validates and executes state transitions)                 │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Transition     │  │ Validation     │  │ Concurrency  │  │
│  │ Executor       │  │ Engine         │  │ Controller   │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    State Models                              │
│  (Define the structure and semantics of state entities)      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Project    │  │   Workflow   │  │     Loop     │      │
│  │    State     │  │    State     │  │    State     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Worker    │  │     Task     │  │ Checkpoint   │      │
│  │    State     │  │    State     │  │    State     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Persistence Layer                         │
│  (Persists state to durable storage)                         │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │     Cache      │  │  Persistent    │  │   History    │  │
│  │     Layer      │  │     Store      │  │   Store      │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Checkpoint Manager                        │
│  (Creates and manages checkpoints)                           │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │   Checkpoint   │  │   Checkpoint   │  │   Checkpoint │  │
│  │     Creator    │  │   Restorer     │  │   Cleaner    │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Query Engine                              │
│  (Provides rich query APIs)                                  │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │   Query        │  │  Aggregation   │  │   Filter     │  │
│  │   Parser       │  │   Engine       │  │   Engine     │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Publisher                           │
│  (Publishes state change events)                             │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │   Event        │  │   Event        │  │   Event      │  │
│  │   Formatter    │  │   Router       │  │   Publisher  │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 7.1 State Transition Engine

**Responsibility:** Validate and execute state transitions.

**Sub-components:**

**Transition Executor**
- Executes validated state transitions
- Ensures atomicity of transitions
- Updates state models
- Coordinates with persistence layer

**Validation Engine**
- Validates transition requests against rules
- Checks pre-conditions and post-conditions
- Ensures transition legality
- Returns validation errors

**Concurrency Controller**
- Manages concurrent state access
- Implements optimistic concurrency control
- Handles version conflicts
- Ensures thread safety

**Interactions:**
- Receives transition requests from components
- Validates transitions
- Executes valid transitions
- Rejects invalid transitions
- Publishes state change events

### 7.2 State Models

**Responsibility:** Define the structure and semantics of state entities.

**Sub-components:**

**Project State Model**
- Defines project state structure
- Defines project state transitions
- Defines project state validation rules

**Workflow State Model**
- Defines workflow state structure
- Defines workflow state transitions
- Defines workflow state validation rules

**Engineering Loop State Model**
- Defines loop state structure
- Defines loop state transitions
- Defines loop state validation rules

**Worker State Model**
- Defines worker state structure
- Defines worker state transitions
- Defines worker state validation rules

**Task State Model**
- Defines task state structure
- Defines task state transitions
- Defines task state validation rules

**Checkpoint State Model**
- Defines checkpoint structure
- Defines checkpoint metadata
- Defines checkpoint lineage

**Interactions:**
- Provides state structure definitions
- Provides transition rules
- Provides validation logic
- Used by Transition Engine

### 7.3 Persistence Layer

**Responsibility:** Persist state to durable storage.

**Sub-components:**

**Cache Layer**
- In-memory cache for frequently accessed state
- Provides low-latency reads
- Keeps cache consistent with persistent store
- Implements cache invalidation

**Persistent Store**
- Durable storage for all state
- Supports transactions
- Ensures durability
- Supports backup and restore

**History Store**
- Stores complete state transition history
- Immutable audit trail
- Supports historical queries
- Enables state replay

**Interactions:**
- Receives state write requests from Transition Engine
- Writes state to persistent storage
- Updates cache
- Returns confirmation
- Supports state queries

### 7.4 Checkpoint Manager

**Responsibility:** Create and manage checkpoints.

**Sub-components:**

**Checkpoint Creator**
- Creates checkpoints at defined points
- Captures state snapshots
- Generates checkpoint metadata
- Stores checkpoints

**Checkpoint Restorer**
- Restores state from checkpoints
- Validates checkpoint integrity
- Handles partial and full restoration
- Publishes restoration events

**Checkpoint Cleaner**
- Cleans up obsolete checkpoints
- Enforces checkpoint retention policies
- Manages checkpoint lineage
- Archives old checkpoints

**Interactions:**
- Creates checkpoints on request
- Restores checkpoints on request
- Cleans up checkpoints periodically
- Publishes checkpoint events

### 7.5 Query Engine

**Responsibility:** Provide rich query APIs.

**Sub-components:**

**Query Parser**
- Parses query requests
- Validates query syntax
- Optimizes query execution
- Returns query results

**Aggregation Engine**
- Aggregates state metrics
- Calculates statistics
- Computes progress metrics
- Generates reports

**Filter Engine**
- Filters state by criteria
- Supports complex filters
- Optimizes filter performance
- Returns filtered results

**Interactions:**
- Receives query requests from components
- Parses and validates queries
- Executes queries against state
- Returns query results

### 7.6 Event Publisher

**Responsibility:** Publish state change events.

**Sub-components:**

**Event Formatter**
- Formats state changes as events
- Adds event metadata
- Ensures event schema compliance
- Adds correlation IDs

**Event Router**
- Routes events to appropriate topics
- Ensures event ordering
- Handles event delivery failures
- Retries failed deliveries

**Event Publisher**
- Publishes events to Event Bus
- Confirms event delivery
- Handles publishing errors
- Logs publishing activity

**Interactions:**
- Receives state change notifications from Transition Engine
- Formats state changes as events
- Publishes events to Event Bus
- Confirms delivery

---

## 8. Runtime State Model

The Runtime State Manager maintains state for the following entity types:

### 8.1 Entity Hierarchy

```
Runtime State
    │
    ├── Project State
    │   ├── Workflow State
    │   │   ├── Engineering Loop State
    │   │   │   └── Task State
    │   │   └── Execution State
    │   └── Checkpoint State
    │
    ├── Worker State
    │
    ├── Recovery State
    │
    └── Runtime Metadata
```

### 8.2 State Entity Types

**Project State**
- Top-level container for all project-related state
- Contains workflow state, checkpoint references, and project metadata
- Represents the complete state of a project

**Workflow State**
- Represents the execution state of a workflow
- Contains loop states, task states, and execution metadata
- Represents the current position in workflow execution

**Engineering Loop State**
- Represents the state of an engineering loop
- Contains task states, loop progress, and loop metadata
- Represents the current position in loop lifecycle

**Task State**
- Represents the state of a discrete task
- Contains task status, assignments, and execution metadata
- Represents the current state of task execution

**Worker State**
- Represents the state of a worker
- Contains worker status, current assignment, and capacity
- Represents worker availability and utilization

**Checkpoint State**
- Represents a state snapshot
- Contains checkpoint metadata, state snapshot, and lineage
- Enables recovery and replay

**Recovery State**
- Represents the state of a recovery operation
- Contains recovery status, strategy, and progress
- Tracks recovery operations

**Runtime Metadata**
- Platform-wide runtime metadata
- Contains system state, configuration, and metrics
- Represents the overall platform state

### 8.3 State Relationships

**Project → Workflow**
- A project contains one or more workflows
- Workflow state is scoped to a project
- Project state references current workflow state

**Workflow → Loop**
- A workflow contains one or more engineering loops
- Loop state is scoped to a workflow
- Workflow state references current loop states

**Loop → Task**
- A loop contains one or more tasks
- Task state is scoped to a loop
- Loop state references task states

**Project → Checkpoint**
- A project has zero or more checkpoints
- Checkpoints are scoped to a project
- Project state references current checkpoint

**Worker → Task**
- A worker can be assigned to zero or one task at a time
- Task state references assigned worker
- Worker state references current task

### 8.4 State Identifiers

**Project ID**
- Format: UUID
- Uniquely identifies a project
- Generated at project creation
- Immutable throughout project lifecycle

**Workflow ID**
- Format: UUID
- Uniquely identifies a workflow
- Generated at workflow creation
- Immutable throughout workflow lifecycle

**Loop ID**
- Format: UUID
- Uniquely identifies an engineering loop
- Generated at loop creation
- Immutable throughout loop lifecycle

**Task ID**
- Format: UUID
- Uniquely identifies a task
- Generated at task creation
- Immutable throughout task lifecycle

**Worker ID**
- Format: UUID
- Uniquely identifies a worker
- Generated at worker registration
- Immutable throughout worker lifecycle

**Checkpoint ID**
- Format: UUID
- Uniquely identifies a checkpoint
- Generated at checkpoint creation
- Immutable throughout checkpoint lifecycle

**Execution ID**
- Format: UUID
- Uniquely identifies an execution session
- Generated at execution start
- Immutable throughout execution lifecycle

---

## 9. Project State Model

The project state model defines the structure and lifecycle of project state.

### 9.1 Project State Structure

| Field | Type | Description |
|---|---|---|
| `projectId` | UUID | Unique project identifier |
| `status` | Enum | Current project status (see state machine) |
| `request` | JSON | Original user request |
| `configuration` | JSON | Project configuration |
| `intentAnalysis` | JSON | Intent analysis results |
| `strategicPlan` | JSON | Strategic plan from Strategic Engine |
| `executableWorkflow` | JSON | Executable workflow from Workflow Engine |
| `workflowVersion` | UUID | Current executable workflow version |
| `currentLoop` | String | Currently executing engineering loop |
| `loopState` | JSON | Current loop state |
| `taskGraphId` | UUID | Current task graph version |
| `taskCount` | Integer | Total number of tasks |
| `completedCount` | Integer | Number of completed tasks |
| `failedCount` | Integer | Number of failed tasks |
| `runningCount` | Integer | Number of currently running tasks |
| `progress` | Float | Overall progress percentage (0.0–100.0) |
| `currentCheckpointId` | UUID | Most recent checkpoint |
| `startedAt` | Timestamp | When execution started |
| `estimatedDuration` | Duration | Estimated total duration |
| `actualDuration` | Duration | Actual elapsed duration |
| `estimatedCost` | Float | Estimated cost in USD |
| `actualCost` | Float | Actual cost in USD |
| `acceptanceCriteria` | JSON | Project acceptance criteria |
| `artifacts` | List[UUID] | All produced artifact IDs |
| `approvalHistory` | List[ApprovalRecord] | History of approval decisions |
| `failureHistory` | List[FailureRecord] | History of failures and recoveries |
| `metadata` | JSON | Flexible metadata |
| `version` | Integer | State version for optimistic concurrency |
| `createdAt` | Timestamp | When project was created |
| `updatedAt` | Timestamp | When project was last modified |
| `finishedAt` | Timestamp | When project completed (if finished) |

### 9.2 Project State Transitions

```
┌──────────┐
│  Created │  Project record created, no execution started
└────┬─────┘
     │
     │ start planning
     ▼
┌──────────┐
│ Planning │  Coordinating Strategic Engine and Workflow Engine
└────┬─────┘
     │
     │ plan complete
     ▼
┌──────────┐
│ Running  │  Executing engineering loops
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┬────────┐
│         │        │        │
▼         ▼        ▼        ▼
Reviewing Paused  Completing Failed
           │        │        │
           │        │        │ cancel
           │        │        ▼
           │        │  ┌──────────┐
           │        │  │ Cancelled │
           │        │  └──────────┘
           │        │
           │        │ complete
           │        ▼
           │  ┌──────────┐
           │  │ Finished  │
           │  └──────────┘
           │
           │ resume
           └───────────┤
                       │
                       ▼
                 ┌──────────┐
                 │ Running  │
                 └──────────┘
```

### 9.3 Project State Descriptions

| State | Description | Valid Transitions |
|---|---|---|
| **Created** | Project record created, no execution started | → Planning, → Cancelled |
| **Planning** | Coordinating Strategic Engine and Workflow Engine | → Running, → Failed, → Cancelled |
| **Running** | Executing engineering loops | → Reviewing, → Paused, → Completing, → Failed, → Cancelled |
| **Reviewing** | Awaiting human review | → Running, → Paused, → Failed, → Cancelled |
| **Paused** | Execution paused | → Running, → Cancelled |
| **Completing** | Validating completion, finalizing | → Finished, → Failed |
| **Finished** | Project completed successfully | → (terminal) |
| **Failed** | Project terminated due to unrecoverable error | → (terminal) |
| **Cancelled** | Project cancelled by user | → (terminal) |

### 9.4 Project State Transition Rules

- A project can only transition to Running from Planning or Paused
- A project can only transition to Reviewing from Running
- A project can only transition to Paused from Running or Reviewing
- A project can only transition to Completing from Running
- A project can only transition to Finished from Completing
- A project can only transition to Failed from Planning, Running, Reviewing, or Completing
- A project can only transition to Cancelled from Created, Planning, Running, Reviewing, or Paused
- A project in Finished, Failed, or Cancelled is terminal — no further transitions are allowed
- Human intervention is required to transition from Reviewing to Running (approval decision)

---

## 10. Workflow State Model

The workflow state model defines the structure and lifecycle of workflow state.

### 10.1 Workflow State Structure

| Field | Type | Description |
|---|---|---|
| `workflowId` | UUID | Unique workflow identifier |
| `projectId` | UUID | Parent project identifier |
| `status` | Enum | Current workflow status |
| `version` | UUID | Workflow version |
| `taskGraph` | JSON | Task graph (DAG) structure |
| `taskCount` | Integer | Total number of tasks |
| `completedCount` | Integer | Number of completed tasks |
| `failedCount` | Integer | Number of failed tasks |
| `runningCount` | Integer | Number of currently running tasks |
| `blockedCount` | Integer | Number of blocked tasks |
| `progress` | Float | Overall progress percentage (0.0–100.0) |
| `currentTaskId` | UUID | Currently executing task |
| `queues` | JSON | Task queue states |
| `dependencies` | JSON | Task dependency graph |
| `schedulingPolicy` | JSON | Scheduling configuration |
| `retryPolicy` | JSON | Retry configuration |
| `approvalPolicies` | JSON | Approval gate configuration |
| `startedAt` | Timestamp | When workflow started |
| `estimatedDuration` | Duration | Estimated total duration |
| `actualDuration` | Duration | Actual elapsed duration |
| `version` | Integer | State version for optimistic concurrency |
| `createdAt` | Timestamp | When workflow was created |
| `updatedAt` | Timestamp | When workflow was last modified |

### 10.2 Workflow State Transitions

```
┌──────────┐
│  Created │  Workflow created, not yet started
└────┬─────┘
     │
     │ start
     ▼
┌──────────┐
│ Running  │  Executing tasks
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┬────────┐
│         │        │        │
▼         ▼        ▼        ▼
Paused   Completing Failed  Cancelled
           │        │
           │        │
           │        │
           │        ▼
           │  ┌──────────┐
           │  │ Finished  │
           │  └──────────┘
           │
           │ resume
           └───────────┤
                       │
                       ▼
                 ┌──────────┐
                 │ Running  │
                 └──────────┘
```

### 10.3 Workflow State Descriptions

| State | Description | Valid Transitions |
|---|---|---|
| **Created** | Workflow created, not yet started | → Running, → Cancelled |
| **Running** | Executing tasks | → Paused, → Completing, → Failed, → Cancelled |
| **Paused** | Workflow paused | → Running, → Cancelled |
| **Completing** | Validating completion | → Finished, → Failed |
| **Finished** | Workflow completed successfully | → (terminal) |
| **Failed** | Workflow failed | → (terminal) |
| **Cancelled** | Workflow cancelled | → (terminal) |

---

## 11. Engineering Loop State Model

The engineering loop state model defines the structure and lifecycle of engineering loop state.

### 11.1 Engineering Loop State Structure

| Field | Type | Description |
|---|---|---|
| `loopId` | UUID | Unique loop identifier |
| `workflowId` | UUID | Parent workflow identifier |
| `projectId` | UUID | Parent project identifier |
| `loopType` | Enum | Loop type (Research, Architecture, Coding, Review, Testing, Deployment, Learning) |
| `status` | Enum | Current loop status (see state machine) |
| `iteration` | Integer | Current iteration number (for REMEDIATE cycles) |
| `maxIterations` | Integer | Maximum allowed iterations |
| `inputArtifacts` | List[UUID] | Input artifact IDs |
| `outputArtifacts` | List[UUID] | Output artifact IDs |
| `reviewFindings` | JSON | Review findings (if applicable) |
| `remediationPlan` | JSON | Remediation plan (if applicable) |
| `assignedWorkers` | List[String] | Assigned worker types |
| `assignedModels` | JSON | Model assignments |
| `retryCount` | Integer | Current retry count |
| `maxRetries` | Integer | Maximum retries allowed |
| `startedAt` | Timestamp | When loop started |
| `estimatedDuration` | Duration | Estimated duration |
| `actualDuration` | Duration | Actual elapsed duration |
| `estimatedCost` | Float | Estimated cost |
| `actualCost` | Float | Actual cost |
| `version` | Integer | State version for optimistic concurrency |
| `createdAt` | Timestamp | When loop was created |
| `updatedAt` | Timestamp | When loop was last modified |

### 11.2 Engineering Loop State Transitions

```
┌──────────┐
│   IDLE   │  Loop initialized, not yet started
└────┬─────┘
     │
     │ start
     ▼
┌──────────┐
│   PLAN   │  Loop creating execution plan
└────┬─────┘
     │
     │ plan complete
     ▼
┌──────────┐
│ EXECUTE  │  Loop executing tasks
└────┬─────┘
     │
     │ execute complete
     ▼
┌──────────┐
│  REVIEW  │  Loop reviewing outputs
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┬────────┐
│         │        │        │
▼         ▼        ▼        ▼
COMPLETE  REMEDIATE ESCALATE FAILED
   │         │        │        │
   │         │        │        │ fail
   │         │        │        ▼
   │         │        │  ┌──────────┐
   │         │        │  │  FAILED  │
   │         │        │  └──────────┘
   │         │        │
   │         │        │ escalate
   │         │        ▼
   │         │  ┌──────────┐
   │         │  │ESCALATED │
   │         │  └────┬─────┘
   │         │       │ human decision
   │         │       ▼
   │         │  ┌──────────┐
   │         │  │  RESUME  │
   │         │  └────┬─────┘
   │         │       │
   │         └───────┤
   │                 │ re-execute
   │                 ▼
   │           ┌──────────┐
   │           │ EXECUTE  │
   │           └──────────┘
   │
   │ next loop
   ▼
┌──────────┐
│ (next)   │
└──────────┘
```

### 11.3 Engineering Loop State Descriptions

| State | Description | Valid Transitions |
|---|---|---|
| **IDLE** | Loop initialized, not started | → PLAN |
| **PLAN** | Loop creating execution plan | → EXECUTE |
| **EXECUTE** | Loop executing tasks | → REVIEW |
| **REVIEW** | Loop reviewing outputs | → COMPLETE, → REMEDIATE, → ESCALATE, → FAILED |
| **COMPLETE** | Loop completed successfully | → (terminal for this loop) |
| **REMEDIATE** | Loop requires remediation | → EXECUTE |
| **ESCALATE** | Loop requires human intervention | → RESUME (after human decision) |
| **FAILED** | Loop failed after exhausting retries | → (terminal for this loop) |

### 11.4 Engineering Loop State Transition Rules

- A loop can only transition to PLAN from IDLE
- A loop can only transition to EXECUTE from PLAN or REMEDIATE
- A loop can only transition to REVIEW from EXECUTE
- A loop can only transition to COMPLETE from REVIEW
- A loop can only transition to REMEDIATE from REVIEW
- A loop can only transition to ESCALATE from REVIEW
- A loop can only transition to FAILED from REVIEW
- A loop can only transition to RESUME from ESCALATE (after human decision)
- A loop in COMPLETE or FAILED is terminal — no further transitions are allowed
- Human intervention is required to transition from ESCALATE to RESUME

---

## 12. Worker State Model

The worker state model defines the structure and lifecycle of worker state.

### 12.1 Worker State Structure

| Field | Type | Description |
|---|---|---|
| `workerId` | UUID | Unique worker identifier |
| `workerType` | Enum | Worker type (Backend Engineer, Frontend Engineer, etc.) |
| `status` | Enum | Current worker status (Idle, Busy, Draining, Offline) |
| `currentTaskId` | UUID | Currently executing task (if Busy) |
| `assignedModel` | String | Assigned AI model |
| `capabilities` | List[String] | Worker capabilities |
| `capacity` | Integer | Maximum concurrent tasks |
| `currentLoad` | Integer | Current number of tasks |
| `startedAt` | Timestamp | When worker became active |
| `taskCount` | Integer | Number of tasks completed |
| `totalCost` | Float | Total token cost incurred |
| `successRate` | Float | Task success rate (0.0–1.0) |
| `averageDuration` | Duration | Average task duration |
| `lastHeartbeat` | Timestamp | Last heartbeat timestamp |
| `metadata` | JSON | Flexible metadata |
| `version` | Integer | State version for optimistic concurrency |
| `createdAt` | Timestamp | When worker was registered |
| `updatedAt` | Timestamp | When worker was last updated |

### 12.2 Worker State Transitions

```
┌──────────┐
│   Idle   │  Worker available for tasks
└────┬─────┘
     │
     │ dispatch
     ▼
┌──────────┐
│  Busy    │  Worker executing task
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┐
│         │        │
▼         ▼        ▼
Idle    Draining  Offline
         │
         │
         │
         ▼
     ┌──────────┐
     │ Offline  │
     └──────────┘
```

### 12.3 Worker State Descriptions

| State | Description | Valid Transitions |
|---|---|---|
| **Idle** | Worker available for tasks | → Busy, → Offline |
| **Busy** | Worker executing task | → Idle, → Draining, → Offline |
| **Draining** | Worker completing current task, not accepting new tasks | → Idle, → Offline |
| **Offline** | Worker not available | → Idle |

### 12.4 Worker State Transition Rules

- A worker can only transition to Busy from Idle
- A worker can only transition to Idle from Busy or Draining
- A worker can only transition to Draining from Busy
- A worker can only transition to Offline from Idle, Busy, or Draining
- A worker can only transition to Idle from Offline (when worker comes online)

---

## 13. Task State Model

The task state model defines the structure and lifecycle of task state.

### 13.1 Task State Structure

| Field | Type | Description |
|---|---|---|
| `taskId` | UUID | Unique task identifier |
| `projectId` | UUID | Parent project identifier |
| `workflowId` | UUID | Parent workflow identifier |
| `loopId` | UUID | Parent loop identifier |
| `taskType` | Enum | Task type |
| `status` | Enum | Current task status (see state machine) |
| `priority` | Enum | Task priority |
| `assignedWorker` | String | Assigned worker type |
| `assignedWorkerId` | UUID | Assigned worker instance ID |
| `assignedModel` | String | Assigned AI model |
| `inputArtifacts` | List[UUID] | Input artifact IDs |
| `outputArtifacts` | List[UUID] | Output artifact IDs |
| `dependencies` | List[UUID] | Dependent task IDs |
| `dependents` | List[UUID] | Tasks that depend on this task |
| `retryCount` | Integer | Current retry count |
| `maxRetries` | Integer | Maximum retries allowed |
| `approvalRequired` | Boolean | Whether approval is required |
| `approvalId` | UUID | Approval request ID (if applicable) |
| `blockedBy` | UUID | Task ID blocking this task (if blocked) |
| `error` | JSON | Error information (if failed) |
| `result` | JSON | Task result (if completed) |
| `startedAt` | Timestamp | When task started |
| `completedAt` | Timestamp | When task completed |
| `estimatedDuration` | Duration | Estimated duration |
| `actualDuration` | Duration | Actual elapsed duration |
| `estimatedCost` | Float | Estimated cost |
| `actualCost` | Float | Actual cost |
| `metadata` | JSON | Flexible metadata |
| `version` | Integer | State version for optimistic concurrency |
| `createdAt` | Timestamp | When task was created |
| `updatedAt` | Timestamp | When task was last updated |

### 13.2 Task State Transitions

```
┌──────────┐
│ Pending  │  Task created, not yet dispatched
└────┬─────┘
     │
     │ dispatch
     ▼
┌──────────┐
│  Ready   │  Task ready for execution
└────┬─────┘
     │
     │ start
     ▼
┌──────────┐
│ Running  │  Task executing
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┬────────┬────────┐
│         │        │        │        │
▼         ▼        ▼        ▼        ▼
Completed Failed  Waiting  Blocked  Retrying
   │         │        │        │        │
   │         │        │        │        │ retry
   │         │        │        │        ▼
   │         │        │        │  ┌──────────┐
   │         │        │        │  │ Running  │
   │         │        │        │  └──────────┘
   │         │        │        │
   │         │        │        │ dependency
   │         │        │        │ resolved
   │         │        │        │
   │         │        │        ▼
   │         │        │  ┌──────────┐
   │         │        │  │  Ready   │
   │         │        │  └────┬─────┘
   │         │        │       │ dispatch
   │         │        │       ▼
   │         │        │  ┌──────────┐
   │         │        └──│ Running  │
   │         │           └──────────┘
   │         │
   │         │ retry
   │         ▼
   │   ┌──────────┐
   │   │ Retrying │
   │   └────┬─────┘
   │        │ retry
   │        ▼
   │   ┌──────────┐
   └───│ Running  │
       └──────────┘
```

### 13.3 Task State Descriptions

| State | Description | Valid Transitions |
|---|---|---|
| **Pending** | Task created, not yet ready | → Ready, → Cancelled |
| **Ready** | Task ready for execution | → Running, → Blocked, → Cancelled |
| **Running** | Task executing | → Completed, → Failed, → Waiting, → Retrying |
| **Completed** | Task completed successfully | → (terminal) |
| **Failed** | Task failed | → Retrying, → Cancelled |
| **Waiting** | Task waiting for external input (approval) | → Running, → Cancelled |
| **Blocked** | Task blocked by dependency | → Ready (when dependency resolved), → Cancelled |
| **Retrying** | Task retrying after failure | → Running, → Failed |

### 13.4 Task State Transition Rules

- A task can only transition to Ready from Pending or Blocked
- A task can only transition to Running from Ready, Waiting, or Retrying
- A task can only transition to Completed from Running
- A task can only transition to Failed from Running
- A task can only transition to Waiting from Running
- A task can only transition to Blocked from Ready
- A task can only transition to Retrying from Failed
- A task can only transition to Ready from Blocked (when dependency resolved)
- A task in Completed is terminal — no further transitions are allowed
- A task can transition from Failed to Retrying up to maxRetries times
- A task can be cancelled from Pending, Ready, Running, Waiting, Blocked, or Retrying

---

## 14. Checkpoint Model

The checkpoint model defines the structure and management of checkpoints.

### 14.1 Checkpoint Structure

| Field | Type | Description |
|---|---|---|
| `checkpointId` | UUID | Unique checkpoint identifier |
| `projectId` | UUID | Parent project identifier |
| `checkpointType` | Enum | Checkpoint type (Automatic, Manual, Recovery, Rollback, Resume) |
| `status` | Enum | Checkpoint status (Active, Restored, Obsolete) |
| `label` | String | Human-readable checkpoint label |
| `description` | String | Checkpoint description |
| `stateSnapshot` | JSON | Complete state snapshot at checkpoint time |
| `parentCheckpointId` | UUID | Parent checkpoint ID (for lineage) |
| `childCheckpointIds` | List[UUID] | Child checkpoint IDs |
| `createdBy` | String | Who created the checkpoint (system, user, recovery) |
| `createdAt` | Timestamp | When checkpoint was created |
| `restoredAt` | Timestamp | When checkpoint was restored (if applicable) |
| `restoredBy` | String | Who restored the checkpoint (if applicable) |
| `size` | Integer | Checkpoint size in bytes |
| `metadata` | JSON | Flexible metadata |
| `version` | Integer | State version for optimistic concurrency |

### 14.2 Checkpoint Types

**Automatic Checkpoint**
- Created automatically by the system
- Triggered by defined events (task completion, loop completion, etc.)
- Managed by checkpoint policy
- Example: Checkpoint after each loop completion

**Manual Checkpoint**
- Created explicitly by user or operator
- Triggered by explicit request
- User-provided label and description
- Example: User creates checkpoint before major change

**Recovery Checkpoint**
- Created before recovery operation
- Enables rollback if recovery fails
- Created automatically before risky operations
- Example: Checkpoint before provider failover

**Rollback Checkpoint**
- Created for rollback purposes
- Marks a known-good state
- Can be used to undo changes
- Example: Checkpoint before deployment

**Resume Checkpoint**
- Created for execution resumption
- Enables execution to resume from specific point
- Created before pause or expected interruption
- Example: Checkpoint before system maintenance

### 14.3 Checkpoint Lifecycle

```
┌──────────┐
│  Active  │  Checkpoint is valid and can be restored
└────┬─────┘
     │
     │ restore
     ▼
┌──────────┐
│ Restored │  Checkpoint has been restored
└────┬─────┘
     │
     │ obsolete
     ▼
┌──────────┐
│ Obsolete │  Checkpoint is no longer needed
└──────────┘
```

### 14.4 Checkpoint Creation Policy

**Automatic Checkpoints**
- Created after each engineering loop completion
- Created before human approval gates
- Created before deployment
- Created at defined intervals during long-running executions
- Created before system maintenance

**Manual Checkpoints**
- Created on user request
- User provides label and description
- User can create checkpoint at any time

**Retention Policy**
- Keep all checkpoints for active projects
- Keep last 10 checkpoints for completed projects
- Archive checkpoints older than 30 days
- Delete archived checkpoints older than 90 days
- User can mark checkpoints as permanent

### 14.5 Checkpoint Lineage

Checkpoints maintain lineage to support:

**Parent-Child Relationships**
- Each checkpoint can have one parent
- Each checkpoint can have multiple children
- Lineage forms a tree structure

**Restoration History**
- Track which checkpoints were restored
- Track when checkpoints were restored
- Track who restored checkpoints

**Branching**
- Support branching from checkpoints
- Enable parallel execution from checkpoint
- Support checkpoint merging

---

## 15. Runtime Persistence Model

The runtime persistence model defines how state is persisted to durable storage.

### 15.1 Persistence Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    State Write Request                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Persistence Coordinator                   │
│  (Coordinates persistence operations)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Transaction Manager                       │
│  (Ensures atomicity and durability)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Write Path                                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Validate   │→ │   Write to   │→ │   Update     │      │
│  │   State      │  │   Database   │  │   Cache      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Read Path                                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Check      │→ │   Read from  │→ │   Return     │      │
│  │   Cache      │  │   Database   │  │   State      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 15.2 Persistence Layers

**Cache Layer**
- In-memory cache (Redis)
- Stores frequently accessed state
- Provides low-latency reads
- Keeps cache consistent with database
- Implements cache invalidation on writes

**Persistent Store**
- Relational database (PostgreSQL)
- Durable storage for all state
- Supports transactions
- Ensures durability
- Supports backup and restore

**History Store**
- Append-only log of state transitions
- Immutable audit trail
- Supports historical queries
- Enables state replay

### 15.3 Write Path

1. Component submits state transition request
2. Persistence Coordinator receives request
3. Transaction Manager begins transaction
4. State Transition Engine validates transition
5. If valid:
   - Write state to database
   - Update cache
   - Write to history store
   - Commit transaction
   - Publish state change event
   - Return success
6. If invalid:
   - Rollback transaction
   - Return validation error

### 15.4 Read Path

1. Component requests state
2. Persistence Coordinator receives request
3. Check cache for state
4. If cache hit:
   - Return state from cache
5. If cache miss:
   - Read state from database
   - Update cache
   - Return state

### 15.5 Consistency Guarantees

**Read-Your-Writes**
- After writing state, subsequent reads return the written state
- Ensures components see their own writes
- Prevents read-after-write inconsistencies

**Atomic Transitions**
- State transitions are atomic
- State is never in an inconsistent state
- Transactions ensure atomicity

**Eventual Consistency Across Components**
- Different components may see slightly different views
- Event Bus provides ordering mechanism
- Components reconcile state through events

**Versioning**
- State includes version numbers
- Optimistic concurrency control prevents conflicts
- Version conflicts trigger retry

---

## 16. Runtime Lifecycle

The Runtime State Manager lifecycle describes how the Runtime State Manager process itself is managed.

### 16.1 Runtime States

```
┌──────────┐
│  Created │  Runtime State Manager instantiated
└────┬─────┘
     │
     │ initialize
     ▼
┌──────────┐
│Starting  │  Initialize components, load configuration
└────┬─────┘
     │
     │ success
     ▼
┌──────────┐
│  Ready    │  Accepting state operations
└────┬─────┘
     │
     │
     │
┌────┴────┬────────┐
│        │        │
▼        ▼        ▼
Processing Paused  Stopping
           │        │
           │        │
           │        │
           │        ▼
           │  ┌──────────┐
           │  │ Stopped  │
           │  └──────────┘
           │
           │ resume
           └───────────┤
                       │
                       ▼
                 ┌──────────┐
                 │ Ready    │
                 └──────────┘
```

### 16.2 Runtime Lifecycle Stages

#### Created

**Description:** Runtime State Manager instantiated but not yet initialized.

**Activities:**
- Process instantiated
- Configuration loaded
- Dependencies injected

**Transitions:**
- To Starting: Initialization begins

#### Starting

**Description:** Runtime State Manager is initializing components and loading state.

**Activities:**
- Initialize State Transition Engine
- Initialize State Models
- Initialize Persistence Layer
- Initialize Checkpoint Manager
- Initialize Query Engine
- Initialize Event Publisher
- Connect to Event Bus
- Load persisted state (if recovering)
- Publish `runtime.created` event

**Transitions:**
- To Ready: Initialization successful
- To Stopped: Initialization failed

#### Ready

**Description:** Runtime State Manager is ready to accept state operations.

**Activities:**
- Accept state transition requests
- Accept state queries
- Process background tasks (checkpoint cleanup, history archival)
- Monitor system health

**Transitions:**
- To Processing: State operation received
- To Paused: Pause requested
- To Stopping: Shutdown requested

#### Processing

**Description:** Runtime State Manager is actively processing state operations.

**Activities:**
- Process state transition requests
- Execute state transitions
- Persist state
- Publish state change events
- Record state history
- Handle state queries

**Transitions:**
- To Ready: All operations completed
- To Paused: Pause requested
- To Stopping: Shutdown requested

#### Paused

**Description:** Runtime State Manager is temporarily not accepting new state operations.

**Activities:**
- Complete in-flight operations
- Stop accepting new operations
- Wait for resume or shutdown

**Transitions:**
- To Ready: Resume requested
- To Stopping: Shutdown requested

#### Stopping

**Description:** Runtime State Manager is performing graceful shutdown.

**Activities:**
- Stop accepting new operations
- Complete in-flight operations
- Save final state
- Publish `runtime.stopping` event
- Close connections
- Clean up resources

**Transitions:**
- To Stopped: Shutdown complete

#### Stopped

**Description:** Runtime State Manager process has terminated.

**Activities:**
- None (process terminated)

**Transitions:**
- To Created: Process restarted

### 16.3 Runtime Lifecycle Events

| Event | Trigger | Payload |
|---|---|---|
| `runtime.created` | Process instantiated | runtimeId, version |
| `runtime.starting` | Initialization begins | runtimeId, timestamp |
| `runtime.started` | Initialization complete | runtimeId, timestamp |
| `runtime.processing` | Processing state operations | runtimeId, timestamp |
| `runtime.pausing` | Pause requested | runtimeId, reason |
| `runtime.paused` | Pause complete | runtimeId, timestamp |
| `runtime.resuming` | Resume requested | runtimeId, timestamp |
| `runtime.ready` | Resume complete | runtimeId, timestamp |
| `runtime.stopping` | Shutdown requested | runtimeId, reason |
| `runtime.stopped` | Shutdown complete | runtimeId, timestamp, uptime |

---

## 17. State Transition Engine

The State Transition Engine is responsible for validating and executing state transitions.

### 17.1 Transition Request Flow

```
Component
   │
   │ 1. Request state transition
   ▼
State Transition Engine
   │
   │ 2. Validate transition
   │
   ├─── Valid ────┐
   │             │
   │             ▼
   │       Execute Transition
   │             │
   │             ▼
   │       Persist State
   │             │
   │             ▼
   │       Publish Event
   │             │
   │             ▼
   │       Record History
   │             │
   │             ▼
   │       Return Success
   │
   └─── Invalid ──┘
             │
             ▼
       Return Validation Error
```

### 17.2 Transition Validation

**Pre-Conditions**
- Current state exists
- Current state allows transition to requested state
- Entity is not in terminal state
- Required metadata is provided

**Post-Conditions**
- New state is valid
- State invariants are maintained
- Related entities are updated (if applicable)
- Events are published

**Validation Rules**
- Defined in State Models
- Enforced by Validation Engine
- Immutable once defined
- Extensible through configuration

### 17.3 Transition Execution

**Atomic Execution**
- State transitions are atomic
- State is never in an inconsistent state
- Transactions ensure atomicity

**Optimistic Concurrency**
- State includes version number
- Transitions check version before writing
- Version conflicts trigger retry
- Retry uses latest state

**Eventual Consistency**
- State changes are eventually consistent
- Event Bus provides ordering
- Components reconcile through events

### 17.4 Transition Recording

**History Recording**
- All transitions recorded in history store
- Immutable audit trail
- Includes timestamp, actor, and metadata
- Supports historical queries

**Event Publishing**
- State change events published to Event Bus
- Events include old state, new state, and metadata
- Events are immutable
- Events are ordered by timestamp

---

## 18. Transition Validation Rules

The Runtime State Manager enforces the following transition validation rules:

### 18.1 Project State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| Created | Planning, Cancelled | None |
| Planning | Running, Failed, Cancelled | Strategic plan and executable workflow must be complete for Running |
| Running | Reviewing, Paused, Completing, Failed, Cancelled | None |
| Reviewing | Running, Paused, Failed, Cancelled | Human approval required for Running |
| Paused | Running, Cancelled | None |
| Completing | Finished, Failed | All acceptance criteria must be met for Finished |
| Finished | (none) | Terminal state |
| Failed | (none) | Terminal state |
| Cancelled | (none) | Terminal state |

### 18.2 Workflow State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| Created | Running, Cancelled | None |
| Running | Paused, Completing, Failed, Cancelled | None |
| Paused | Running, Cancelled | None |
| Completing | Finished, Failed | All tasks must be completed for Finished |
| Finished | (none) | Terminal state |
| Failed | (none) | Terminal state |
| Cancelled | (none) | Terminal state |

### 18.3 Engineering Loop State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| IDLE | PLAN | None |
| PLAN | EXECUTE | Plan must be complete |
| EXECUTE | REVIEW | Execution must be complete |
| REVIEW | COMPLETE, REMEDIATE, ESCALATE, FAILED | Review must be complete |
| COMPLETE | (none) | Terminal state for this loop |
| REMEDIATE | EXECUTE | Remediation plan must be defined |
| ESCALATE | RESUME | Human decision required |
| FAILED | (none) | Terminal state for this loop |

### 18.4 Task State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| Pending | Ready, Cancelled | Dependencies must be satisfied for Ready |
| Ready | Running, Blocked, Cancelled | None |
| Running | Completed, Failed, Waiting, Retrying | None |
| Completed | (none) | Terminal state |
| Failed | Retrying, Cancelled | Retry count < max retries for Retrying |
| Waiting | Running, Cancelled | Approval decision required for Running |
| Blocked | Ready, Cancelled | Dependencies must be resolved for Ready |
| Retrying | Running, Failed | Retry count < max retries for Running |

### 18.5 Worker State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| Idle | Busy, Offline | Worker must be available for Busy |
| Busy | Idle, Draining, Offline | None |
| Draining | Idle, Offline | Current task must be completed |
| Offline | Idle | Worker must be online |

### 18.6 Checkpoint State Transition Rules

| Current State | Allowed Transitions | Conditions |
|---|---|---|
| Active | Restored, Obsolete | None |
| Restored | Obsolete | None |
| Obsolete | (none) | Terminal state |

### 18.7 Validation Error Codes

| Error Code | Description |
|---|---|
| `INVALID_TRANSITION` | Requested transition is not allowed |
| `TERMINAL_STATE` | Entity is in terminal state, no transitions allowed |
| `PRECONDITION_FAILED` | Pre-conditions for transition not met |
| `POSTCONDITION_FAILED` | Post-conditions for transition not met |
| `VERSION_CONFLICT` | State version conflict (optimistic concurrency) |
| `ENTITY_NOT_FOUND` | Entity does not exist |
| `INVALID_STATE` | Current state is invalid |
| `MISSING_METADATA` | Required metadata not provided |

---

## 19. Recovery Model

The recovery model defines how the Runtime State Manager supports system recovery.

### 19.1 Recovery Capabilities

**State Restoration**
- Restore state from checkpoints
- Restore state from history
- Restore state from persistent store
- Validate restored state integrity

**Checkpoint Restoration**
- Restore from specific checkpoint
- Restore from most recent checkpoint
- Restore from checkpoint by type
- Validate checkpoint lineage

**State Reconstruction**
- Reconstruct state from event history
- Replay events to rebuild state
- Validate reconstructed state
- Handle missing events

**Failure Recovery**
- Recover from system failure
- Recover from corruption
- Recover from inconsistency
- Validate recovery success

### 19.2 Recovery Process

**System Failure Recovery**

1. System restarts
2. Runtime State Manager initializes
3. Load most recent checkpoint
4. Validate checkpoint integrity
5. Restore state from checkpoint
6. Replay events since checkpoint (if available)
7. Validate state consistency
8. Publish `runtime.recovered` event
9. Resume operations

**Checkpoint Restoration**

1. Receive checkpoint restoration request
2. Validate checkpoint exists and is restorable
3. Load checkpoint state
4. Validate checkpoint integrity
5. Create recovery checkpoint (of current state)
6. Restore state from checkpoint
7. Publish `checkpoint.restored` event
8. Record restoration in history
9. Return success

**State Reconstruction from Events**

1. Receive reconstruction request
2. Load event history for entity
3. Replay events in order
4. Reconstruct state from events
5. Validate reconstructed state
6. Compare with persisted state (if available)
7. Resolve conflicts (if any)
8. Return reconstructed state

### 19.3 Recovery Guarantees

**Durability**
- State is persisted before transition is confirmed
- No data loss on system failure
- Checkpoints are durable

**Consistency**
- Restored state is consistent
- No partial state restoration
- State invariants maintained

**Atomicity**
- Recovery is atomic
- State is never in inconsistent state during recovery
- Recovery either completes fully or fails completely

**Idempotency**
- Recovery can be retried safely
- Multiple recovery attempts produce same result
- No side effects from retries

---

## 20. Runtime Queries

The Runtime State Manager provides rich query APIs for runtime state.

### 20.1 Query Categories

**Entity Queries**
- Get entity by ID
- Get entities by status
- Get entities by project
- Get entities by type

**Relationship Queries**
- Get entity dependencies
- Get entity dependents
- Get entity lineage
- Get entity hierarchy

**Temporal Queries**
- Get entity state at time
- Get state history
- Get state transitions in time range
- Get state changes over time

**Aggregation Queries**
- Count entities by status
- Calculate progress metrics
- Compute average duration
- Compute cost metrics

**Search Queries**
- Search entities by metadata
- Search entities by attributes
- Full-text search on entity fields

### 20.2 Query Examples

**Get Current Project**
- Input: `projectId`
- Output: Current project state
- Use case: Display project status to user

**Get Running Workflows**
- Input: None
- Output: List of running workflows
- Use case: Monitor active workflows

**Get Worker Status**
- Input: None
- Output: List of all workers with status
- Use case: Monitor worker utilization

**Get Task Status**
- Input: `projectId` (optional)
- Output: List of tasks with status
- Use case: Monitor task progress

**Get Execution Progress**
- Input: `projectId`
- Output: Progress metrics (completed, running, failed, blocked)
- Use case: Display progress to user

**Get Runtime History**
- Input: `entityType`, `entityId`, `timeRange` (optional)
- Output: List of state transitions
- Use case: Debug execution, audit trail

**Get Checkpoint History**
- Input: `projectId`
- Output: List of checkpoints
- Use case: Select checkpoint for restoration

**Get Failure History**
- Input: `projectId` (optional)
- Output: List of failures
- Use case: Analyze failure patterns

**Get Loop History**
- Input: `projectId`
- Output: List of engineering loops with status
- Use case: Monitor loop execution

### 20.3 Query Performance

**Indexing**
- All query fields are indexed
- Composite indexes for common queries
- Time-based indexes for temporal queries

**Caching**
- Frequently accessed queries are cached
- Cache invalidation on state changes
- Configurable cache TTL

**Optimization**
- Query optimization for common patterns
- Pagination for large result sets
- Streaming for history queries

---

## 21. Runtime Events

The Runtime State Manager publishes the following runtime events:

### 21.1 Project State Events

| Event | Trigger | Payload |
|---|---|---|
| `project.created` | New project created | projectId, request, configuration, timestamp |
| `project.updated` | Project state updated | projectId, changes, timestamp |
| `project.planning` | Project enters planning | projectId, timestamp |
| `project.running` | Project starts execution | projectId, timestamp |
| `project.reviewing` | Project enters review | projectId, approvalId, timestamp |
| `project.paused` | Project paused | projectId, reason, checkpointId, timestamp |
| `project.resumed` | Project resumed | projectId, checkpointId, timestamp |
| `project.completing` | Project validating completion | projectId, timestamp |
| `project.finished` | Project completed | projectId, summary, duration, cost, artifacts, timestamp |
| `project.failed` | Project failed | projectId, error, failedTasks, timestamp |
| `project.cancelled` | Project cancelled | projectId, reason, timestamp |

### 21.2 Workflow State Events

| Event | Trigger | Payload |
|---|---|---|
| `workflow.created` | New workflow created | workflowId, projectId, timestamp |
| `workflow.started` | Workflow started | workflowId, projectId, timestamp |
| `workflow.running` | Workflow executing | workflowId, progress, timestamp |
| `workflow.paused` | Workflow paused | workflowId, reason, checkpointId, timestamp |
| `workflow.resumed` | Workflow resumed | workflowId, checkpointId, timestamp |
| `workflow.completing` | Workflow completing | workflowId, timestamp |
| `workflow.finished` | Workflow finished | workflowId, timestamp |
| `workflow.failed` | Workflow failed | workflowId, error, timestamp |
| `workflow.cancelled` | Workflow cancelled | workflowId, reason, timestamp |

### 21.3 Engineering Loop State Events

| Event | Trigger | Payload |
|---|---|---|
| `loop.created` | New loop created | loopId, workflowId, projectId, loopType, timestamp |
| `loop.started` | Loop started | loopId, loopType, timestamp |
| `loop.planning` | Loop in planning phase | loopId, timestamp |
| `loop.executing` | Loop executing tasks | loopId, timestamp |
| `loop.reviewing` | Loop reviewing outputs | loopId, timestamp |
| `loop.completed` | Loop completed | loopId, loopType, results, timestamp |
| `loop.remediating` | Loop requires remediation | loopId, findings, timestamp |
| `loop.escalated` | Loop escalated | loopId, reason, timestamp |
| `loop.failed` | Loop failed | loopId, error, timestamp |

### 21.4 Task State Events

| Event | Trigger | Payload |
|---|---|---|
| `task.created` | New task created | taskId, projectId, workflowId, loopId, timestamp |
| `task.updated` | Task state updated | taskId, changes, timestamp |
| `task.ready` | Task ready for execution | taskId, timestamp |
| `task.started` | Task started | taskId, workerId, model, timestamp |
| `task.completed` | Task completed | taskId, result, artifacts, timestamp |
| `task.failed` | Task failed | taskId, error, recoverable, timestamp |
| `task.retrying` | Task retrying | taskId, retryCount, maxRetries, timestamp |
| `task.waiting` | Task waiting for approval | taskId, approvalId, timestamp |
| `task.blocked` | Task blocked | taskId, blockedBy, timestamp |
| `task.cancelled` | Task cancelled | taskId, reason, timestamp |

### 21.5 Worker State Events

| Event | Trigger | Payload |
|---|---|---|
| `worker.registered` | Worker registered | workerId, workerType, capabilities, timestamp |
| `worker.dispatched` | Worker dispatched to task | workerId, taskId, timestamp |
| `worker.busy` | Worker became busy | workerId, taskId, timestamp |
| `worker.idle` | Worker became idle | workerId, timestamp |
| `worker.draining` | Worker draining | workerId, timestamp |
| `worker.offline` | Worker went offline | workerId, timestamp |
| `worker.online` | Worker came online | workerId, timestamp |

### 21.6 Checkpoint Events

| Event | Trigger | Payload |
|---|---|---|
| `checkpoint.created` | Checkpoint created | checkpointId, projectId, checkpointType, timestamp |
| `checkpoint.restored` | Checkpoint restored | checkpointId, projectId, restoredBy, timestamp |
| `checkpoint.obsoleted` | Checkpoint obsoleted | checkpointId, projectId, timestamp |

### 21.7 Runtime Lifecycle Events

| Event | Trigger | Payload |
|---|---|---|
| `runtime.created` | Runtime instantiated | runtimeId, version |
| `runtime.starting` | Initialization begins | runtimeId, timestamp |
| `runtime.started` | Initialization complete | runtimeId, timestamp |
| `runtime.processing` | Processing operations | runtimeId, timestamp |
| `runtime.pausing` | Pause requested | runtimeId, reason |
| `runtime.paused` | Pause complete | runtimeId, timestamp |
| `runtime.resuming` | Resume requested | runtimeId, timestamp |
| `runtime.ready` | Resume complete | runtimeId, timestamp |
| `runtime.stopping` | Shutdown requested | runtimeId, reason |
| `runtime.stopped` | Shutdown complete | runtimeId, timestamp, uptime |
| `runtime.recovered` | Runtime recovered | runtimeId, recoveryType, timestamp |

---

## 22. Event Interactions

The Runtime State Manager interacts with the Event Bus throughout the state lifecycle.

### 22.1 Published Events

The Runtime State Manager publishes events for all state changes:

**State Change Events**
- Published for every state transition
- Include old state, new state, and metadata
- Immutable once published
- Ordered by timestamp

**Lifecycle Events**
- Published for runtime lifecycle changes
- Include runtime state and metadata
- Used for monitoring and observability

**Checkpoint Events**
- Published for checkpoint operations
- Include checkpoint metadata
- Used for recovery and audit

### 22.2 Subscribed Events

The Runtime State Manager subscribes to the following events:

**From Kernel**
- `project.created` — Create project state
- `project.started` — Transition project to Running
- `project.paused` — Transition project to Paused
- `project.resumed` — Transition project to Running
- `project.finished` — Transition project to Finished
- `project.failed` — Transition project to Failed
- `project.cancelled` — Transition project to Cancelled

**From Execution Engine**
- `task.started` — Transition task to Running
- `task.completed` — Transition task to Completed
- `task.failed` — Transition task to Failed
- `task.retrying` — Transition task to Retrying
- `task.waiting` — Transition task to Waiting
- `task.blocked` — Transition task to Blocked

**From Workflow Engine**
- `workflow.created` — Create workflow state
- `workflow.started` — Transition workflow to Running
- `workflow.paused` — Transition workflow to Paused
- `workflow.resumed` — Transition workflow to Running
- `workflow.finished` — Transition workflow to Finished
- `workflow.failed` — Transition workflow to Failed

**From Engineering Loops**
- `loop.started` — Transition loop to PLAN
- `loop.planning` — Transition loop to PLAN
- `loop.executing` — Transition loop to EXECUTE
- `loop.reviewing` — Transition loop to REVIEW
- `loop.completed` — Transition loop to COMPLETE
- `loop.remediating` — Transition loop to REMEDIATE
- `loop.escalated` — Transition loop to ESCALATE
- `loop.failed` — Transition loop to FAILED

**From Workers**
- `worker.registered` — Create worker state
- `worker.dispatched` — Transition worker to Busy
- `worker.idle` — Transition worker to Idle
- `worker.draining` — Transition worker to Draining
- `worker.offline` — Transition worker to Offline
- `worker.online` — Transition worker to Idle

**From Execution Continuity Manager**
- `checkpoint.created` — Create checkpoint state
- `checkpoint.restored` — Update checkpoint state
- `recovery.completed` — Update recovery state

### 22.3 Event Handling

**Event Reception**
- Runtime State Manager subscribes to event topics
- Event Bus delivers events to Runtime State Manager
- Runtime State Manager receives events asynchronously

**Event Processing**
- Runtime State Manager validates event
- Runtime State Manager correlates event with entity
- Runtime State Manager updates state based on event
- Runtime State Manager publishes confirmation event (if applicable)

**Event Correlation**
- Runtime State Manager uses correlationId to correlate related events
- Runtime State Manager uses causationId to trace event chains
- Runtime State Manager uses entity IDs to scope events

**Event Ordering**
- Runtime State Manager processes events in order within an entity
- Runtime State Manager handles out-of-order events gracefully
- Runtime State Manager uses event versioning for backward compatibility

---

## 23. Kernel Interactions

The Runtime State Manager interacts with the Kernel throughout the request lifecycle.

### 23.1 State Operations for Kernel

**Project Creation**
- Kernel requests project creation
- Runtime State Manager creates project state
- Runtime State Manager returns projectId
- Runtime State Manager publishes `project.created` event

**State Transitions**
- Kernel requests state transitions
- Runtime State Manager validates and executes transitions
- Runtime State Manager publishes state change events
- Runtime State Manager returns transition result

**State Queries**
- Kernel queries project state
- Runtime State Manager returns current state
- Kernel uses state to make orchestration decisions

**Checkpoint Management**
- Kernel requests checkpoint creation
- Runtime State Manager creates checkpoint
- Kernel requests checkpoint restoration
- Runtime State Manager restores checkpoint

### 23.2 Kernel Coordination Points

**Request Intake**
- Kernel invokes Runtime State Manager to create project
- Runtime State Manager initializes project state
- Runtime State Manager publishes `project.created` event

**Planning Coordination**
- Kernel updates project state with strategic plan
- Kernel updates project state with executable workflow
- Runtime State Manager persists planning outputs

**Execution Orchestration**
- Kernel transitions project to Running
- Kernel updates loop states
- Kernel updates task states
- Runtime State Manager persists all state changes

**Failure Recovery**
- Kernel requests checkpoint creation before recovery
- Kernel requests checkpoint restoration after recovery
- Runtime State Manager manages checkpoint operations

**Completion**
- Kernel transitions project to Completing
- Kernel validates completion criteria
- Kernel transitions project to Finished
- Runtime State Manager persists final state

### 23.3 Kernel State Dependencies

The Kernel depends on the Runtime State Manager for:

**Project State**
- Current project status
- Project progress
- Current phase
- Active tasks

**Workflow State**
- Current workflow status
- Task graph state
- Queue states
- Task dependencies

**Loop State**
- Current loop status
- Loop progress
- Loop iteration count
- Loop results

**Task State**
- Task status
- Task assignments
- Task progress
- Task results

**Worker State**
- Worker availability
- Worker assignments
- Worker capacity

**Checkpoint State**
- Available checkpoints
- Checkpoint lineage
- Checkpoint metadata

---

## 24. Platform Engine Interactions

The Runtime State Manager interacts with Platform Engines throughout the execution lifecycle.

### 24.1 Strategic Engine Interactions

**State Operations**
- Strategic Engine does not directly interact with Runtime State Manager
- Kernel coordinates Strategic Engine participation
- Kernel updates project state with strategic plan

**State Reads**
- Strategic Engine does not read runtime state
- Strategic Engine receives context from Kernel

**State Writes**
- Strategic Engine does not write runtime state
- Strategic Engine returns strategic plan to Kernel
- Kernel writes strategic plan to project state

### 24.2 Workflow Engine Interactions

**State Operations**
- Workflow Engine receives executable workflow from Kernel
- Workflow Engine does not directly interact with Runtime State Manager
- Kernel updates project state with executable workflow

**State Reads**
- Workflow Engine does not read runtime state
- Workflow Engine receives context from Kernel

**State Writes**
- Workflow Engine does not write runtime state
- Workflow Engine returns executable workflow to Kernel
- Kernel writes executable workflow to project state

### 24.3 Execution Engine Interactions

**State Operations**
- Execution Engine publishes task lifecycle events
- Runtime State Manager subscribes to task events
- Runtime State Manager updates task state based on events

**State Reads**
- Execution Engine does not read runtime state directly
- Execution Engine receives task assignments from Kernel
- Kernel reads task state from Runtime State Manager

**State Writes**
- Execution Engine publishes events for task state changes
- Runtime State Manager updates task state based on events
- Execution Engine does not directly write state

### 24.4 Review Engine Interactions

**State Operations**
- Review Engine publishes review events
- Runtime State Manager subscribes to review events
- Runtime State Manager updates task state based on review results

**State Reads**
- Review Engine does not read runtime state
- Review Engine receives artifacts and criteria from Kernel

**State Writes**
- Review Engine publishes review results
- Runtime State Manager updates task state
- Review Engine does not directly write state

### 24.5 Engineering Loop Interactions

**State Operations**
- Engineering Loops publish loop lifecycle events
- Runtime State Manager subscribes to loop events
- Runtime State Manager updates loop state based on events

**State Reads**
- Engineering Loops do not read runtime state
- Engineering Loops receive context from Execution Engine

**State Writes**
- Engineering Loops publish events for loop state changes
- Runtime State Manager updates loop state based on events
- Engineering Loops do not directly write state

---

## 25. Shared Platform Service Interactions

The Runtime State Manager interacts with Shared Platform Services.

### 25.1 Event Bus Interactions

**Published Events**
- Runtime State Manager publishes state change events
- Events include entity ID, old state, new state, and metadata
- Events are published to appropriate topics
- Event Bus confirms delivery

**Subscribed Events**
- Runtime State Manager subscribes to state change events from components
- Event Bus delivers events to Runtime State Manager
- Runtime State Manager processes events asynchronously

**Event Format**
- Events conform to Canonical Event Model
- Events include correlationId and causationId
- Events are immutable once published

### 25.2 Memory Engine Interactions

**State Storage**
- Runtime State Manager may use Memory Engine for state caching
- Memory Engine provides fast access to frequently used state
- Runtime State Manager ensures consistency between Memory Engine and persistent store

**Context Retrieval**
- Runtime State Manager does not retrieve context from Memory Engine
- Runtime State Manager stores current state, not historical context

### 25.3 Knowledge Engine Interactions

**Knowledge Usage**
- Runtime State Manager does not use Knowledge Engine
- Runtime State Manager manages state, not knowledge

### 25.4 Model Router Interactions

**Model Assignments**
- Runtime State Manager records model assignments in task state
- Model Router selects models
- Runtime State Manager does not select models

### 25.5 Execution Continuity Manager Interactions

**Recovery Support**
- Execution Continuity Manager requests checkpoint creation
- Runtime State Manager creates checkpoints
- Execution Continuity Manager requests checkpoint restoration
- Runtime State Manager restores checkpoints

**Recovery State**
- Runtime State Manager records recovery state
- Execution Continuity Manager updates recovery state
- Runtime State Manager persists recovery state

### 25.6 Connector Layer Interactions

**Persistence Connectors**
- Runtime State Manager uses connectors for persistence
- Connectors provide access to databases, object storage, etc.
- Runtime State Manager is provider-agnostic

**Checkpoint Storage**
- Runtime State Manager uses connectors for checkpoint storage
- Connectors provide access to object storage, file systems, etc.
- Runtime State Manager is provider-agnostic

### 25.7 Observability Interactions

**Metrics**
- Runtime State Manager emits state metrics
- Metrics include state counts, transition rates, query latencies
- Observability collects and exposes metrics

**Logs**
- Runtime State Manager logs state transitions
- Logs include transition details, validation results, errors
- Observability collects and stores logs

**Traces**
- Runtime State Manager creates traces for state operations
- Traces include operation details and timing
- Observability collects and stores traces

### 25.8 Security Interactions

**Access Control**
- Security enforces access control for state operations
- Runtime State Manager validates permissions
- Security provides identity and permissions

**Audit**
- Security records security-relevant state operations
- Runtime State Manager provides audit data
- Security maintains audit trail

---

## 26. Failure Recovery

The Runtime State Manager handles failures through a comprehensive failure recovery strategy.

### 26.1 Failure Detection

**Internal Failures**
- Runtime State Manager detects internal failures
- Runtime State Manager logs failures
- Runtime State Manager attempts recovery

**External Failures**
- Runtime State Manager detects persistence failures
- Runtime State Manager detects Event Bus failures
- Runtime State Manager attempts recovery or escalates

**Health Monitoring**
- Runtime State Manager monitors component health
- Runtime State Manager detects degraded components
- Runtime State Manager adjusts behavior

### 26.2 Failure Classification

**By Source:**
- Persistence failure
- Event Bus failure
- Internal error
- Resource exhaustion
- Network failure

**By Severity:**
- Warning
- Error
- Critical
- Fatal

**By Recoverability:**
- Recoverable
- Non-recoverable
- Unknown

### 26.3 Recovery Strategies

**Persistence Failure**
- Retry persistence operation
- Failover to alternative persistence provider
- Restore from checkpoint
- Escalate to human if unrecoverable

**Event Bus Failure**
- Retry event publishing
- Buffer events locally
- Publish events when Event Bus recovers
- Escalate to human if unrecoverable

**Internal Error**
- Attempt automatic recovery
- Restore from checkpoint
- Escalate to human if unrecoverable

**Resource Exhaustion**
- Free resources
- Reduce cache size
- Throttle operations
- Escalate to human if unrecoverable

**Network Failure**
- Retry operation
- Use cached state
- Buffer operations for later
- Escalate to human if unrecoverable

### 26.4 Recovery Procedures

**Persistence Failure Recovery**

1. Detect persistence failure
2. Classify failure
3. If recoverable:
   - Retry persistence operation
   - If retry succeeds: Continue
   - If retry fails: Failover to alternative provider
4. If non-recoverable:
   - Notify human
   - Human decides: retry, use cached state, or fail
5. If unknown:
   - Escalate to human

**Event Bus Failure Recovery**

1. Detect Event Bus failure
2. Classify failure
3. If recoverable:
   - Buffer events locally
   - Retry event publishing
   - If Event Bus recovers: Publish buffered events
4. If non-recoverable:
   - Notify human
   - Human decides: continue without events or fail
5. If unknown:
   - Escalate to human

**System Failure Recovery**

1. System restarts
2. Runtime State Manager initializes
3. Load most recent checkpoint
4. Validate checkpoint integrity
5. Restore state from checkpoint
6. Replay events since checkpoint (if available)
7. Validate state consistency
8. Publish `runtime.recovered` event
9. Resume operations

### 26.5 Recovery Guarantees

**Durability**
- State is persisted before transition is confirmed
- No data loss on failure
- Checkpoints are durable

**Consistency**
- Recovered state is consistent
- No partial recovery
- State invariants maintained

**Atomicity**
- Recovery is atomic
- State is never in inconsistent state during recovery
- Recovery either completes fully or fails completely

**Idempotency**
- Recovery can be retried safely
- Multiple recovery attempts produce same result
- No side effects from retries

---

## 27. State Consistency Guarantees

The Runtime State Manager provides the following consistency guarantees:

### 27.1 Read-Your-Writes Consistency

**Guarantee:** After a component writes a state update, it is guaranteed to read that update on subsequent reads.

**Implementation:**
- Writes are immediately visible to the writing component
- Cache is updated before write confirmation
- Subsequent reads return the written state

**Benefits:**
- Components can safely read their own writes
- No read-after-write inconsistencies
- Simplified component logic

### 27.2 Atomic State Transitions

**Guarantee:** All state transitions are atomic. State is never in an inconsistent state.

**Implementation:**
- Transactions ensure atomicity
- State transitions use database transactions
- Rollback on failure

**Benefits:**
- State is always consistent
- No partial state updates
- Simplified reasoning about state

### 27.3 Eventual Consistency Across Components

**Guarantee:** State is eventually consistent across components. Different components may see slightly different views at any instant, but all views converge.

**Implementation:**
- Event Bus provides ordering mechanism
- Components reconcile state through events
- Eventual consistency is acceptable for most use cases

**Benefits:**
- High availability
- High performance
- Loose coupling

### 27.4 Optimistic Concurrency Control

**Guarantee:** Concurrent state updates are handled safely without locking.

**Implementation:**
- State includes version number
- Transitions check version before writing
- Version conflicts trigger retry
- Retry uses latest state

**Benefits:**
- High concurrency
- No deadlocks
- High performance

### 27.5 State Invariants

**Guarantee:** State invariants are always maintained.

**Invariants:**
- A task cannot be in both Running and Completed states
- A project cannot have more completed tasks than total tasks
- A worker cannot be assigned to multiple tasks simultaneously (if capacity = 1)
- Checkpoint state must be consistent with project state

**Implementation:**
- Validation Engine enforces invariants
- Transactions ensure invariants
- Invariants are checked on every transition

**Benefits:**
- State is always valid
- Simplified reasoning about state
- Early error detection

### 27.6 Durability

**Guarantee:** State is durable once persisted. No data loss on system failure.

**Implementation:**
- State is written to persistent store before confirmation
- Transactions ensure durability
- Checkpoints are durable
- Replication for high availability (optional)

**Benefits:**
- No data loss
- Reliable recovery
- High availability

---

## 28. Concurrency Model

The Runtime State Manager is thread-safe by design and supports concurrent access.

### 28.1 Concurrency Control Mechanism

**Optimistic Concurrency Control**
- State includes version number
- Transitions check version before writing
- Version conflicts trigger retry
- Retry uses latest state

**Benefits:**
- High concurrency
- No deadlocks
- High performance
- Simple implementation

### 28.2 Concurrent Access Patterns

**Read-Heavy Workloads**
- Multiple components can read state concurrently
- Reads do not block other reads
- Reads do not block writes
- Cache improves read performance

**Write-Heavy Workloads**
- Writes use optimistic concurrency control
- Version conflicts trigger retry
- Retry is transparent to components
- High write throughput

**Mixed Workloads**
- Reads and writes can occur concurrently
- Optimistic concurrency handles conflicts
- No locking required
- High performance

### 28.3 Conflict Resolution

**Version Conflict**
- Two components attempt to update same state
- One component succeeds, other gets version conflict
- Component with conflict retries with latest state
- Retry succeeds with latest state

**Resolution Strategy:**
- Last writer wins (based on version)
- Retry ensures eventual consistency
- No data loss

### 28.4 Thread Safety

**Thread-Safe Operations**
- All state operations are thread-safe
- No external synchronization required
- Components can call operations concurrently

**Implementation:**
- Optimistic concurrency control
- Atomic transactions
- Thread-safe data structures
- No shared mutable state

### 28.5 Performance Considerations

**Cache**
- Frequently accessed state is cached
- Cache reduces database load
- Cache invalidation on writes

**Connection Pooling**
- Database connections are pooled
- Reduces connection overhead
- Improves throughput

**Batching**
- Multiple state updates can be batched
- Reduces database round-trips
- Improves throughput

**Async Operations**
- Event publishing is asynchronous
- Non-blocking I/O
- Improves responsiveness

---

## 29. Sequence Diagrams

### 29.1 Project Creation

```
User
  │
  │ 1. Submit request
  ▼
Kernel
  │
  │ 2. Request project creation
  ▼
Runtime State Manager
  │
  │ 3. Validate project data
  │ 4. Create project state
  │ 5. Persist state
  │ 6. Publish project.created event
  ▼
Event Bus
  │
  │ 7. Deliver event
  ▼
Kernel
  │
  │ 8. Receive projectId
  ▼
User
  │
  │ 9. Receive projectId
  └──
```

### 29.2 State Transition

```
Component
  │
  │ 1. Request state transition
  ▼
Runtime State Manager
  │
  │ 2. Validate transition
  │ 3. Execute transition
  │ 4. Persist state
  │ 5. Publish state change event
  ▼
Event Bus
  │
  │ 6. Deliver event
  ▼
Subscribers
  │
  │ 7. Receive event
  └──
```

### 29.3 Checkpoint Creation

```
Kernel
  │
  │ 1. Request checkpoint creation
  ▼
Runtime State Manager
  │
  │ 2. Capture state snapshot
  │ 3. Create checkpoint record
  │ 4. Persist checkpoint
  │ 5. Publish checkpoint.created event
  ▼
Event Bus
  │
  │ 6. Deliver event
  ▼
Kernel
  │
  │ 7. Receive checkpointId
  └──
```

### 29.4 Checkpoint Restoration

```
Kernel
  │
  │ 1. Request checkpoint restoration
  ▼
Runtime State Manager
  │
  │ 2. Validate checkpoint
  │ 3. Load checkpoint state
  │ 4. Restore state
  │ 5. Publish checkpoint.restored event
  ▼
Event Bus
  │
  │ 6. Deliver event
  ▼
Kernel
  │
  │ 7. Resume execution
  └──
```

### 29.5 State Query

```
Component
  │
  │ 1. Request state query
  ▼
Runtime State Manager
  │
  │ 2. Check cache
  │ 3. [If cache miss] Read from database
  │ 4. Return state
  ▼
Component
  │
  │ 5. Receive state
  └──
```

### 29.6 Failure Recovery

```
System
  │
  │ 1. System failure
  ▼
System
  │
  │ 2. System restarts
  ▼
Runtime State Manager
  │
  │ 3. Initialize
  │ 4. Load most recent checkpoint
  │ 5. Validate checkpoint
  │ 6. Restore state
  │ 7. Publish runtime.recovered event
  ▼
Event Bus
  │
  │ 8. Deliver event
  ▼
Kernel
  │
  │ 9. Resume execution
  └──
```

---

## 30. State Diagrams

### 30.1 Runtime State Machine

```
┌──────────┐
│  Created │
└────┬─────┘
     │ initialize
     ▼
┌──────────┐
│ Starting │
└────┬─────┘
     │ success
     ▼
┌──────────┐
│  Ready   │◄────────────────────┐
└────┬─────┘                      │
     │ operation                   │ resume
     ▼                              │
┌──────────┐                       │
│Processing│                       │
└────┬─────┘                       │
     │ all operations complete      │ pause
     ▼ or pause                     │
┌──────────┐                       │
│  Paused  │───────────────────────┘
└────┬─────┘
     │ shutdown
     ▼
┌──────────┐
│ Stopping │
└────┬─────┘
     │ complete
     ▼
┌──────────┐
│ Stopped  │
└──────────┘
```

**States:**
- **Created** — Runtime State Manager instantiated
- **Starting** — Runtime State Manager initializing
- **Ready** — Runtime State Manager ready for operations
- **Processing** — Runtime State Manager processing operations
- **Paused** — Runtime State Manager paused
- **Stopping** — Runtime State Manager shutting down
- **Stopped** — Runtime State Manager terminated

**Transitions:**
- **initialize** — Begin initialization
- **success** — Initialization successful
- **operation** — State operation received
- **all operations complete** — All operations completed
- **pause** — Pause requested
- **resume** — Resume requested
- **shutdown** — Shutdown requested
- **complete** — Shutdown complete

### 30.2 Project State Machine

```
┌──────────┐
│  Created │
└────┬─────┘
     │ start planning
     ▼
┌──────────┐
│ Planning │
└────┬─────┘
     │ plan complete
     ▼
┌──────────┐
│ Running  │
└────┬─────┘
     │
     │
┌────┴────┬────────┬────────┐
│         │        │        │
▼         ▼        ▼        ▼
Reviewing Paused  Completing Failed
           │        │        │
           │        │        │ cancel
           │        │        ▼
           │        │  ┌──────────┐
           │        │  │ Cancelled │
           │        │  └──────────┘
           │        │
           │        │ complete
           │        ▼
           │  ┌──────────┐
           │  │ Finished  │
           │  └──────────┘
           │
           │ resume
           └───────────┤
                       │
                       ▼
                 ┌──────────┐
                 │ Running  │
                 └──────────┘
```

### 30.3 Task State Machine

```
┌──────────┐
│ Pending  │
└────┬─────┘
     │ dispatch
     ▼
┌──────────┐
│  Ready   │
└────┬─────┘
     │ start
     ▼
┌──────────┐
│ Running  │
└────┬─────┘
     │
     │
┌────┴────┬────────┬────────┬────────┐
│         │        │        │        │
▼         ▼        ▼        ▼        ▼
Completed Failed  Waiting  Blocked  Retrying
   │         │        │        │        │
   │         │        │        │        │ retry
   │         │        │        │        ▼
   │         │        │        │  ┌──────────┐
   │         │        │        │  │ Running  │
   │         │        │        │  └──────────┘
   │         │        │        │
   │         │        │        │ dependency
   │         │        │        │ resolved
   │         │        │        │
   │         │        │        ▼
   │         │        │  ┌──────────┐
   │         │        │  │  Ready   │
   │         │        │  └────┬─────┘
   │         │        │       │ dispatch
   │         │        │       ▼
   │         │        │  ┌──────────┐
   │         │        └──│ Running  │
   │         │           └──────────┘
   │         │
   │         │ retry
   │         ▼
   │   ┌──────────┐
   │   │ Retrying │
   │   └────┬─────┘
   │        │ retry
   │        ▼
   │   ┌──────────┐
   └───│ Running  │
       └──────────┘
```

### 30.4 Checkpoint State Machine

```
┌──────────┐
│  Active  │
└────┬─────┘
     │ restore
     ▼
┌──────────┐
│ Restored │
└────┬─────┘
     │ obsolete
     ▼
┌──────────┐
│ Obsolete │
└──────────┘
```

### 30.5 Recovery Lifecycle

```
┌──────────┐
│  Normal  │
│Operation │
└────┬─────┘
     │
     │ failure detected
     ▼
┌──────────┐
│Failure   │
│Detected  │
└────┬─────┘
     │
     ▼
┌──────────┐
│Failure   │
│Classified│
└────┬─────┘
     │
     │
┌────┴────┬────────┬────────┐
│         │        │        │
▼         ▼        ▼        ▼
Recoverable Non-Rec. Unknown Fatal
   │         │        │        │
   │         │        │        │ restore
   │         │        │        ▼
   │         │        │  ┌──────────┐
   │         │        │  │Checkpoint│
   │         │        │  │Restored  │
   │         │        │  └────┬─────┘
   │         │        │       │
   │         │        │       ▼
   │         │        │  ┌──────────┐
   │         │        │  │Resumed   │
   │         │        │  └──────────┘
   │         │        │
   │         │        │ escalate
   │         │        ▼
   │         │  ┌──────────┐
   │         │  │  Human   │
   │         │  │Intervention│
   │         │  └────┬─────┘
   │         │       │
   │         └───────┤
   │                 │ notify human
   │                 ▼
   │           ┌──────────┐
   │           │  Human   │
   │           │ notified │
   │           └────┬─────┘
   │                │
   │                ▼
   │           ┌──────────┐
   └──────────│  Retry   │
              └────┬─────┘
                   │ retry
                   ▼
             ┌──────────┐
             │Execution │
             │Resumed   │
             └──────────┘
```

---

## 31. Public API Reference

### 31.1 State Write API

**create_project**
```python
def create_project(project_data: ProjectData) -> UUID:
    """
    Create a new project.

    Args:
        project_data: Project initialization data

    Returns:
        UUID: Unique project identifier

    Raises:
        ValidationError: If project data is invalid
        PersistenceError: If state cannot be persisted
    """
```

**transition_project_state**
```python
def transition_project_state(
    project_id: UUID,
    new_status: ProjectStatus,
    metadata: Optional[dict] = None
) -> TransitionResult:
    """
    Transition project to new status.

    Args:
        project_id: Project identifier
        new_status: New project status
        metadata: Optional metadata

    Returns:
        TransitionResult: Transition result

    Raises:
        InvalidTransitionError: If transition is not allowed
        EntityNotFoundError: If project does not exist
        VersionConflictError: If state version conflict
    """
```

**update_task_state**
```python
def update_task_state(
    task_id: UUID,
    new_status: TaskStatus,
    metadata: Optional[dict] = None
) -> TransitionResult:
    """
    Update task state.

    Args:
        task_id: Task identifier
        new_status: New task status
        metadata: Optional metadata

    Returns:
        TransitionResult: Transition result

    Raises:
        InvalidTransitionError: If transition is not allowed
        EntityNotFoundError: If task does not exist
        VersionConflictError: If state version conflict
    """
```

**create_checkpoint**
```python
def create_checkpoint(
    project_id: UUID,
    checkpoint_type: CheckpointType,
    label: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[dict] = None
) -> UUID:
    """
    Create a checkpoint.

    Args:
        project_id: Project identifier
        checkpoint_type: Checkpoint type
        label: Optional human-readable label
        description: Optional description
        metadata: Optional metadata

    Returns:
        UUID: Unique checkpoint identifier

    Raises:
        EntityNotFoundError: If project does not exist
        PersistenceError: If checkpoint cannot be created
    """
```

**restore_checkpoint**
```python
def restore_checkpoint(
    checkpoint_id: UUID,
    restore_type: RestoreType = RestoreType.FULL
) -> TransitionResult:
    """
    Restore state from checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier
        restore_type: Type of restoration (full/partial)

    Returns:
        TransitionResult: Restoration result

    Raises:
        EntityNotFoundError: If checkpoint does not exist
        InvalidStateError: If checkpoint cannot be restored
        PersistenceError: If state cannot be restored
    """
```

### 31.2 State Read API

**get_project_state**
```python
def get_project_state(project_id: UUID) -> ProjectState:
    """
    Get project state.

    Args:
        project_id: Project identifier

    Returns:
        ProjectState: Current project state

    Raises:
        EntityNotFoundError: If project does not exist
    """
```

**get_task_state**
```python
def get_task_state(task_id: UUID) -> TaskState:
    """
    Get task state.

    Args:
        task_id: Task identifier

    Returns:
        TaskState: Current task state

    Raises:
        EntityNotFoundError: If task does not exist
    """
```

**get_worker_state**
```python
def get_worker_state(worker_id: UUID) -> WorkerState:
    """
    Get worker state.

    Args:
        worker_id: Worker identifier

    Returns:
        WorkerState: Current worker state

    Raises:
        EntityNotFoundError: If worker does not exist
    """
```

**get_checkpoint**
```python
def get_checkpoint(checkpoint_id: UUID) -> CheckpointState:
    """
    Get checkpoint state.

    Args:
        checkpoint_id: Checkpoint identifier

    Returns:
        CheckpointState: Checkpoint state

    Raises:
        EntityNotFoundError: If checkpoint does not exist
    """
```

### 31.3 Query API

**get_projects_by_status**
```python
def get_projects_by_status(status: ProjectStatus) -> List[ProjectState]:
    """
    Get projects by status.

    Args:
        status: Project status filter

    Returns:
        List[ProjectState]: Projects matching status
    """
```

**get_tasks_by_project**
```python
def get_tasks_by_project(project_id: UUID) -> List[TaskState]:
    """
    Get tasks by project.

    Args:
        project_id: Project identifier

    Returns:
        List[TaskState]: Tasks in project
    """
```

**get_tasks_by_status**
```python
def get_tasks_by_status(status: TaskStatus) -> List[TaskState]:
    """
    Get tasks by status.

    Args:
        status: Task status filter

    Returns:
        List[TaskState]: Tasks matching status
    """
```

**get_running_workflows**
```python
def get_running_workflows() -> List[WorkflowState]:
    """
    Get all running workflows.

    Returns:
        List[WorkflowState]: Running workflows
    """
```

**get_worker_status**
```python
def get_worker_status() -> List[WorkerState]:
    """
    Get all worker statuses.

    Returns:
        List[WorkerState]: All worker states
    """
```

**get_execution_progress**
```python
def get_execution_progress(project_id: UUID) -> ProgressMetrics:
    """
    Get execution progress.

    Args:
        project_id: Project identifier

    Returns:
        ProgressMetrics: Progress metrics

    Raises:
        EntityNotFoundError: If project does not exist
    """
```

**get_runtime_history**
```python
def get_runtime_history(
    entity_type: EntityType,
    entity_id: UUID,
    time_range: Optional[TimeRange] = None
) -> List[StateTransition]:
    """
    Get runtime history.

    Args:
        entity_type: Entity type
        entity_id: Entity identifier
        time_range: Optional time range filter

    Returns:
        List[StateTransition]: State transition history
    """
```

**get_checkpoint_history**
```python
def get_checkpoint_history(project_id: UUID) -> List[CheckpointState]:
    """
    Get checkpoint history.

    Args:
        project_id: Project identifier

    Returns:
        List[CheckpointState]: Checkpoint history
    """
```

**get_failure_history**
```python
def get_failure_history(project_id: Optional[UUID] = None) -> List[FailureRecord]:
    """
    Get failure history.

    Args:
        project_id: Optional project filter

    Returns:
        List[FailureRecord]: Failure records
    """
```

### 31.4 Event Subscription API

**subscribe_to_state_changes**
```python
def subscribe_to_state_changes(
    entity_type: EntityType,
    callback: Callable[[StateChangeEvent], None]
) -> UUID:
    """
    Subscribe to state changes.

    Args:
        entity_type: Entity type to subscribe to
        callback: Callback function

    Returns:
        UUID: Subscription identifier

    Raises:
        InvalidEntityTypeError: If entity type is invalid
    """
```

**unsubscribe**
```python
def unsubscribe(subscription_id: UUID) -> bool:
    """
    Unsubscribe from state changes.

    Args:
        subscription_id: Subscription identifier

    Returns:
        bool: True if unsubscribed successfully

    Raises:
        EntityNotFoundError: If subscription does not exist
    """
```

---

## 32. Internal Components Reference

### 32.1 State Transition Engine

**Purpose:** Validate and execute state transitions.

**Key Methods:**
- `validate_transition(entity, current_state, new_state) -> ValidationResult`
- `execute_transition(entity, new_state, metadata) -> TransitionResult`
- `handle_version_conflict(entity, attempted_version) -> ResolutionResult`

**Dependencies:**
- State Models (for validation rules)
- Persistence Layer (for state persistence)
- Event Publisher (for event publishing)

### 32.2 Validation Engine

**Purpose:** Validate state transition requests.

**Key Methods:**
- `validate_project_transition(current_status, new_status) -> ValidationResult`
- `validate_task_transition(current_status, new_status) -> ValidationResult`
- `validate_loop_transition(current_status, new_status) -> ValidationResult`

**Dependencies:**
- State Models (for transition rules)

### 32.3 Concurrency Controller

**Purpose:** Manage concurrent state access.

**Key Methods:**
- `acquire_lock(entity_id) -> Lock`
- `release_lock(lock) -> None`
- `handle_version_conflict(entity, attempted_version) -> ResolutionResult`

**Dependencies:**
- Persistence Layer (for version checking)

### 32.4 Persistence Layer

**Purpose:** Persist state to durable storage.

**Key Methods:**
- `write_state(entity_type, entity_id, state) -> None`
- `read_state(entity_type, entity_id) -> State`
- `write_history(transition) -> None`
- `write_checkpoint(checkpoint) -> None`

**Dependencies:**
- Cache Layer (for caching)
- Persistent Store (for durable storage)
- History Store (for audit trail)

### 32.5 Checkpoint Manager

**Purpose:** Create and manage checkpoints.

**Key Methods:**
- `create_checkpoint(project_id, checkpoint_type, metadata) -> Checkpoint`
- `restore_checkpoint(checkpoint_id, restore_type) -> RestorationResult`
- `cleanup_checkpoints(project_id, policy) -> None`

**Dependencies:**
- Persistence Layer (for checkpoint storage)
- State Models (for state snapshots)

### 32.6 Query Engine

**Purpose:** Provide rich query APIs.

**Key Methods:**
- `query(entity_type, filters) -> QueryResult`
- `aggregate(entity_type, aggregation) -> AggregationResult`
- `search(entity_type, query) -> SearchResult`

**Dependencies:**
- Persistence Layer (for state access)

### 32.7 Event Publisher

**Purpose:** Publish state change events.

**Key Methods:**
- `publish_state_change(event) -> None`
- `publish_lifecycle_event(event) -> None`
- `format_state_change(entity, old_state, new_state) -> Event`

**Dependencies:**
- Event Bus (for event publishing)

---

## 33. Extension Points

The Runtime State Manager is designed to accommodate future extensions without architectural changes.

### 33.1 New Entity Types

**Extension:** Add new state entity types

**Mechanism:**
- Define new state model
- Define state transitions
- Define validation rules
- Register entity type with Runtime State Manager

**Example:** Add Deployment State, Environment State

### 33.2 New State Transitions

**Extension:** Add new state transitions for existing entities

**Mechanism:**
- Define new transition in state model
- Define validation rules
- Update transition validation logic

**Example:** Add new project status, add new task status

### 33.3 New Checkpoint Types

**Extension:** Add new checkpoint types

**Mechanism:**
- Define new checkpoint type
- Define checkpoint creation policy
- Define checkpoint restoration logic

**Example:** Add deployment checkpoint, add environment checkpoint

### 33.4 New Query Patterns

**Extension:** Add new query patterns

**Mechanism:**
- Define new query type
- Implement query logic
- Register query with Query Engine

**Example:** Add full-text search, add graph queries

### 33.5 New Persistence Providers

**Extension:** Add new persistence providers

**Mechanism:**
- Implement persistence provider interface
- Register provider with Persistence Layer
- Configure provider in configuration

**Example:** Add cloud storage provider, add distributed database

### 33.6 New Event Formats

**Extension:** Add new event formats

**Mechanism:**
- Define new event format
- Implement event formatter
- Register formatter with Event Publisher

**Example:** Add Avro format, add Protobuf format

### 33.7 Extension Mechanisms

**Plugin Registration**
- Extensions register with Runtime State Manager
- Runtime State Manager discovers extensions at startup
- Runtime State Manager invokes extensions through standard interfaces

**Configuration-Driven**
- Extensions configured via configuration files
- No code changes required
- Dynamic extension activation

**Contract-Based**
- Extensions implement standard contracts
- Runtime State Manager depends on contracts, not implementations
- Extensions evolve independently

### 33.8 Extension Principles

**Backward Compatibility**
- Extensions must not break existing functionality
- Extensions must support existing contracts
- Extensions must be backward compatible

**Isolation**
- Extensions are isolated from core Runtime State Manager
- Extension failures do not affect core Runtime State Manager
- Extensions can be added or removed without affecting core

**Discoverability**
- Extensions are discoverable by Runtime State Manager
- Extensions self-register
- Runtime State Manager discovers extensions at startup

**Configurability**
- Extensions are configurable
- Extensions can be enabled/disabled
- Extensions can be configured per deployment

---

## 34. ADR Requirements

All changes to the Runtime State Manager require an Architecture Decision Record (ADR) in the following cases:

### 34.1 Changes Requiring ADR

**Architectural Changes**
- Changes to state models
- Changes to state transitions
- Changes to validation rules
- Changes to consistency guarantees
- Changes to concurrency model
- Changes to persistence architecture
- Changes to checkpoint architecture
- Changes to event model

**Interface Changes**
- Changes to public APIs
- Changes to event formats
- Changes to query APIs
- Changes to subscription APIs

**Extension Mechanism Changes**
- Changes to extension points
- Changes to plugin registration
- Changes to configuration format

**Non-Functional Changes**
- Changes to performance characteristics
- Changes to scalability characteristics
- Changes to reliability characteristics
- Changes to security characteristics

### 34.2 ADR Format

All ADRs must include:

**Context**
- Why is this change needed?
- What problem does it solve?
- What are the constraints?

**Decision**
- What is the decision?
- What are the alternatives considered?
- Why was this alternative chosen?

**Rationale**
- Why is this the best solution?
- What are the trade-offs?
- What are the risks?

**Consequences**
- What are the positive consequences?
- What are the negative consequences?
- What are the neutral consequences?

**Implementation**
- How will this be implemented?
- What is the migration plan?
- What is the rollback plan?

### 34.3 ADR Process

1. **Proposal** — Propose change with ADR
2. **Review** — Architecture team reviews ADR
3. **Approval** — Architecture team approves or rejects ADR
4. **Implementation** — Implement approved ADR
5. **Validation** — Validate implementation against ADR
6. **Documentation** — Update documentation

### 34.4 ADR Storage

All ADRs are stored in `docs/adr/` directory:

- `ADR-001-<short-name>.md` — First ADR
- `ADR-002-<short-name>.md` — Second ADR
- etc.

ADRs are immutable once approved. Changes require new ADRs.

---

## 35. Glossary

**Runtime State Manager** — The authoritative source of runtime state for the entire AutoForge AI OS. Owns all runtime state, state transitions, checkpoints, and state history.

**State** — The current condition of an entity (project, workflow, loop, task, worker, checkpoint). State is owned by the Runtime State Manager.

**State Transition** — A change from one state to another. State transitions are validated, executed, persisted, and published as events by the Runtime State Manager.

**Checkpoint** — A persisted snapshot of execution state for recovery. Checkpoints are first-class citizens in the Runtime State Manager.

**Project State** — The state of a project, including status, progress, tasks, artifacts, and metadata.

**Workflow State** — The state of a workflow, including status, task graph, queues, and execution progress.

**Engineering Loop State** — The state of an engineering loop, including status, iteration, tasks, and results.

**Task State** — The state of a task, including status, assignments, dependencies, and results.

**Worker State** — The state of a worker, including status, current assignment, and capacity.

**Checkpoint State** — The state of a checkpoint, including metadata, state snapshot, and lineage.

**Recovery State** — The state of a recovery operation, including status, strategy, and progress.

**Runtime Metadata** — Platform-wide runtime metadata, including system state and configuration.

**State Transition Engine** — The component responsible for validating and executing state transitions.

**Validation Engine** — The component responsible for validating state transition requests.

**Concurrency Controller** — The component responsible for managing concurrent state access.

**Persistence Layer** — The component responsible for persisting state to durable storage.

**Checkpoint Manager** — The component responsible for creating and managing checkpoints.

**Query Engine** — The component responsible for providing rich query APIs.

**Event Publisher** — The component responsible for publishing state change events.

**Optimistic Concurrency Control** — A concurrency control mechanism that uses version numbers to detect conflicts and trigger retries.

**Read-Your-Writes Consistency** — A consistency guarantee that a component will read its own writes.

**Atomic State Transition** — A state transition that is atomic — either it completes fully or it does not complete at all.

**Eventual Consistency** — A consistency model where state is eventually consistent across components, but different components may see slightly different views at any instant.

**State Invariant** — A property of state that must always be true. State invariants are enforced by the Runtime State Manager.

**Checkpoint Lineage** — The parent-child relationships between checkpoints, forming a tree structure.

**State History** — The complete, immutable audit trail of all state transitions.

**State Replay** — The process of replaying state transitions to reconstruct state or debug issues.

**Entity** — A stateful object in the platform (project, workflow, loop, task, worker, checkpoint).

**Entity ID** — A unique identifier for an entity (UUID).

**Entity Type** — The type of an entity (project, workflow, loop, task, worker, checkpoint).

**State Version** — A version number for state, used for optimistic concurrency control.

**Transition Validation** — The process of validating that a state transition is allowed.

**Transition Execution** — The process of executing a validated state transition.

**Transition Recording** — The process of recording a state transition in the history store.

**Event Publishing** — The process of publishing a state change event to the Event Bus.

**Persistence** — The process of writing state to durable storage.

**Recovery** — The process of restoring state after a failure.

**Checkpoint Restoration** — The process of restoring state from a checkpoint.

**State Reconstruction** — The process of reconstructing state from event history.

**Query** — A request for state information with optional filters and aggregations.

**Aggregation** — A computation over state (count, sum, average, etc.).

**Filter** — A criterion for selecting state entities.

**Subscription** — A registration for state change events.

**Callback** — A function invoked when a state change event is received.

**Correlation ID** — An identifier for correlating related events.

**Causation ID** — An identifier for tracing event chains.

**Optimistic Concurrency** — A concurrency control mechanism that detects conflicts and retries, rather than preventing conflicts with locks.

**Version Conflict** — A conflict that occurs when two components attempt to update the same state with different versions.

**Retry** — The process of re-attempting a failed operation.

**Idempotency** — The property that an operation can be invoked multiple times with the same result as if it were invoked once.

**Thread Safety** — The property that an operation is safe to execute concurrently from multiple threads.

**Durability** — The guarantee that persisted state will not be lost.

**Atomicity** — The guarantee that an operation either completes fully or does not complete at all.

**Consistency** — The guarantee that state is always valid and invariants are maintained.

**Isolation** — The guarantee that concurrent operations do not interfere with each other.

---

**End of Runtime State Manager Specification v1.0**

This document is the canonical reference for the Runtime State Manager subsystem. All implementation must conform to this specification. Deviations require an Architecture Decision Record (ADR) and approval from the architecture governance board.

**Status:** Frozen — Phase 3.1 Deliverable
**Version:** 1.0
**Date:** 2026-07-30