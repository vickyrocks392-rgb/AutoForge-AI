# AutoForge Runtime State Manager

## Purpose

The Runtime State Manager is the authoritative in-memory state management subsystem for AutoForge AI. It maintains the current runtime state of all active entities — Projects, Tasks, ExecutionSessions, Artifacts, and MemoryEntries — providing fast, concurrent-safe access to the live state of the platform.

## Runtime State vs. Persistence

| Aspect | Runtime State Manager | Persistence Layer |
|--------|----------------------|-------------------|
| **Purpose** | Maintain live, in-memory state for active operations | Store data durably for long-term retention |
| **Lifetime** | Application lifetime (volatile) | Survives restarts |
| **Access Pattern** | O(1) lookup by ID, read-heavy | Query, filter, paginate |
| **Consistency** | Strong, immediate | Eventual (via event bus) |
| **Concurrency** | asyncio locks for thread safety | Database transactions |

The Runtime State Manager is **not** a database, cache, or persistence mechanism. It is the single source of truth for the *current* state of the system while it is running.

## Snapshot Philosophy

Snapshots are immutable, point-in-time captures of the entire runtime state. They serve two purposes:

1. **Checkpoint/Restore**: Allow subsystems to capture state before a risky operation and restore it if needed.
2. **Consistent Views**: Provide a frozen, consistent view of state for analysis or reporting without holding locks.

Snapshots are **memory-only**. They are not persisted to disk. A snapshot is a deep copy of all runtime collections at a given moment.

## Future Integration with Event Bus

When the Event Bus subsystem is implemented, the Runtime State Manager will:

- Subscribe to domain events to keep runtime state in sync with persisted state
- Publish state change notifications for interested subscribers
- Support event-sourced restoration of runtime state from the event log

Currently, the Runtime State Manager operates independently with direct CRUD operations.

## Usage

```python
from autoforge_runtime import RuntimeStateManager

manager = RuntimeStateManager()

# Register entities
project = Project(name="My Project")
manager.register_project(project)

# Lookup
found = manager.get_project(project.id)

# Update
updated = project.model_copy(update={"description": "Updated"})
manager.update_project(updated)

# Snapshots
snapshot = manager.create_snapshot()
manager.restore_snapshot(snapshot)

# Reset
manager.reset()

# Read-only views
projects_view = manager.list_projects()