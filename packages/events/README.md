# AutoForge Events — Canonical Runtime Event Model

## Overview

The `autoforge-events` package defines the **canonical runtime event model** for the AutoForge AI platform. Events are the universal language of the system — they represent something that happened and are used to communicate state changes between all subsystems.

This package defines **event types only**. There is no event bus, no networking, no persistence, no scheduler, and no runtime execution logic. Events are pure data.

## Event-Driven Architecture

AutoForge AI uses an **event-driven architecture** where components communicate by publishing and consuming events rather than by calling each other directly. This provides:

- **Decoupling** — Producers and consumers don't know about each other.
- **Auditability** — Every state change is recorded as an event.
- **Replayability** — System state can be reconstructed by replaying events.
- **Extensibility** — New consumers can be added without modifying producers.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Scheduler  │     │State Manager│     │  Checkpoint │
│             │     │             │     │   Manager   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Event Bus  │  ← Future integration
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
│    Model    │     │   Failure   │     │    Audit    │
│   Router    │     │  Recovery   │     │    Log      │
└─────────────┘     └─────────────┘     └─────────────┘
```

## State vs. Events

It is important to distinguish between **state** and **events**:

| Concept | State | Event |
|---------|-------|-------|
| What it is | A snapshot at a point in time | A record of something that happened |
| Mutability | Mutable (state changes over time) | Immutable (cannot be changed) |
| Example | `Task(status="running")` | `TaskStarted(task_id=..., occurred_at=...)` |
| Storage | Current values (overwritten) | Append-only log |
| Purpose | Answer "what is the current value?" | Answer "what happened and when?" |

**State is derived from events.** The current state of any entity can be reconstructed by replaying all events that affected it, in order.

## Why Events Are Immutable

Events are **immutable by design** for several critical reasons:

1. **Historical accuracy** — An event represents a fact that occurred at a specific point in time. Changing it would rewrite history and break the audit trail.

2. **Idempotent replay** — If events could change, replaying them would produce different results each time, making state reconstruction unreliable.

3. **Causality chains** — Events reference each other via `causation_id`. Changing a past event would break the causation chain and invalidate all downstream events.

4. **Concurrent consumers** — Multiple consumers may process the same event. If events were mutable, consumers could see different versions.

5. **Distributed systems** — In a distributed system, mutating past events is impractical and dangerous. Immutability simplifies replication and conflict resolution.

All event classes in this package use Pydantic's `frozen=True` configuration, which makes instances immutable after construction.

## BaseEvent Design

Every event inherits from `BaseEvent`, which provides the following common fields:

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `UUID` | Globally unique identifier for this event instance |
| `event_type` | `EventType` | The specific type of event (e.g. `TaskStarted`) |
| `event_category` | `EventCategory` | High-level category (e.g. `TASK`, `PROJECT`) |
| `occurred_at` | `datetime` | UTC timestamp of when the event occurred |
| `correlation_id` | `UUID \| None` | For correlating related events across subsystems |
| `causation_id` | `UUID \| None` | ID of the event that caused this event |
| `aggregate_id` | `UUID` | ID of the domain aggregate this event relates to |
| `aggregate_type` | `str` | Type name of the aggregate (e.g. `"Task"`) |
| `version` | `int` | Schema version for forward/backward compatibility |
| `metadata` | `dict[str, Any]` | Extensible key-value store for additional context |

## Event Hierarchy

```
BaseEvent
├── ProjectCreated
├── ProjectUpdated
├── ProjectArchived
├── ProjectDeleted
├── TaskCreated
├── TaskUpdated
├── TaskQueued
├── TaskReady
├── TaskStarted
├── TaskPaused
├── TaskResumed
├── TaskCompleted
├── TaskFailed
├── TaskCancelled
├── TaskBlocked
├── TaskDeleted
├── ExecutionStarted
├── ExecutionCompleted
├── ExecutionFailed
├── ExecutionPaused
├── ExecutionResumed
├── ExecutionCancelled
├── ExecutionTimedOut
├── ArtifactCreated
├── ArtifactUpdated
├── ArtifactDeleted
├── MemoryStored
├── MemoryUpdated
├── MemoryDeleted
└── MemoryRetrieved
```

## Event Categories

Events are grouped into five categories:

| Category | Events | Description |
|----------|--------|-------------|
| `PROJECT` | 4 | Project lifecycle (create, update, archive, delete) |
| `TASK` | 12 | Task lifecycle (create, queue, ready, start, pause, resume, complete, fail, cancel, block, delete) |
| `EXECUTION` | 7 | Execution session lifecycle (start, complete, fail, pause, resume, cancel, timeout) |
| `ARTIFACT` | 3 | Artifact lifecycle (create, update, delete) |
| `MEMORY` | 4 | Memory entry lifecycle (store, update, delete, retrieve) |

**Total: 30 event types**

## Event Types

Each event carries a strongly-typed `EventType` enum value:

- `project.created`, `project.updated`, `project.archived`, `project.deleted`
- `task.created`, `task.updated`, `task.queued`, `task.ready`, `task.started`, `task.paused`, `task.resumed`, `task.completed`, `task.failed`, `task.cancelled`, `task.blocked`, `task.deleted`
- `execution.started`, `execution.completed`, `execution.failed`, `execution.paused`, `execution.resumed`, `execution.cancelled`, `execution.timed_out`
- `artifact.created`, `artifact.updated`, `artifact.deleted`
- `memory.stored`, `memory.updated`, `memory.deleted`, `memory.retrieved`

## Usage

```python
from autoforge_events import TaskStarted, EventType, EventCategory
import uuid

event = TaskStarted(
    aggregate_id=uuid.uuid4(),
    aggregate_type="Task",
    project_id=uuid.uuid4(),
    correlation_id=uuid.uuid4(),
)

# Events are immutable — this would raise a ValidationError:
# event.event_type = EventType.TASK_COMPLETED

# Serialization
data = event.to_dict()
json_str = event.to_json()

# Deserialization
restored = TaskStarted.from_dict(data)
```

## Future Integration with Event Bus

This package defines the **event schema** only. In a future integration layer, these events will be:

1. **Published** to an Event Bus (in-memory, NATS, RabbitMQ, or Kafka)
2. **Persisted** to an append-only event log
3. **Subscribed to** by event handlers and processors
4. **Replayed** for state reconstruction and debugging

The Event Bus integration will be implemented in a separate package that depends on `autoforge-events`.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=autoforge_events
```

## License

MIT