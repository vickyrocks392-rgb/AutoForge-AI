"""
Immutable runtime snapshots for the AutoForge AI Runtime State Manager.

Snapshots provide point-in-time, immutable captures of the entire runtime
state. They are used for checkpoint/restore operations and for providing
consistent read-only views of the runtime state.
"""

from __future__ import annotations

import copy
import uuid
from collections.abc import Mapping
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.artifact import Artifact
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.project import Project
from autoforge_models.task import Task


class RuntimeSnapshot(BaseModel):
    """
    An immutable, point-in-time capture of the entire runtime state.

    Snapshots are created by the RuntimeStateManager and contain deep copies
    of all registered entities at the moment of capture. They are fully
    immutable — all fields are frozen and all collections are Mapping types
    to prevent mutation.

    Snapshots are memory-only. They are not persisted to disk.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    snapshot_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this snapshot.",
    )

    projects: Mapping[uuid.UUID, Project] = Field(
        default_factory=dict,
        description="Snapshot of all registered Projects, keyed by ID.",
    )

    tasks: Mapping[uuid.UUID, Task] = Field(
        default_factory=dict,
        description="Snapshot of all registered Tasks, keyed by ID.",
    )

    execution_sessions: Mapping[uuid.UUID, ExecutionSession] = Field(
        default_factory=dict,
        description="Snapshot of all registered ExecutionSessions, keyed by ID.",
    )

    artifacts: Mapping[uuid.UUID, Artifact] = Field(
        default_factory=dict,
        description="Snapshot of all registered Artifacts, keyed by ID.",
    )

    memory_entries: Mapping[uuid.UUID, MemoryEntry] = Field(
        default_factory=dict,
        description="Snapshot of all registered MemoryEntries, keyed by ID.",
    )

    def __len__(self) -> int:
        """Return the total number of entities in this snapshot."""
        return (
            len(self.projects)
            + len(self.tasks)
            + len(self.execution_sessions)
            + len(self.artifacts)
            + len(self.memory_entries)
        )


def _deep_freeze_mapping(data: dict[Any, Any]) -> Mapping[Any, Any]:
    """
    Create an immutable mapping from a dictionary of Pydantic models.

    Each value is deep-copied to ensure the snapshot is fully isolated
    from the live runtime state.
    """
    frozen: dict[Any, Any] = {}
    for key, value in data.items():
        frozen[key] = copy.deepcopy(value)
    return frozen


def create_snapshot(
    projects: dict[uuid.UUID, Project],
    tasks: dict[uuid.UUID, Task],
    execution_sessions: dict[uuid.UUID, ExecutionSession],
    artifacts: dict[uuid.UUID, Artifact],
    memory_entries: dict[uuid.UUID, MemoryEntry],
) -> RuntimeSnapshot:
    """
    Create an immutable snapshot from the current runtime state dictionaries.

    This function performs deep copies of all entities to ensure the snapshot
    is fully isolated from the live state. The resulting snapshot is completely
    immutable and safe to pass across async boundaries.

    Args:
        projects: Current Projects dict from the runtime state.
        tasks: Current Tasks dict from the runtime state.
        execution_sessions: Current ExecutionSessions dict from the runtime state.
        artifacts: Current Artifacts dict from the runtime state.
        memory_entries: Current MemoryEntries dict from the runtime state.

    Returns:
        A fully immutable RuntimeSnapshot instance.
    """
    return RuntimeSnapshot(
        projects=_deep_freeze_mapping(projects),
        tasks=_deep_freeze_mapping(tasks),
        execution_sessions=_deep_freeze_mapping(execution_sessions),
        artifacts=_deep_freeze_mapping(artifacts),
        memory_entries=_deep_freeze_mapping(memory_entries),
    )


def restore_snapshot(snapshot: RuntimeSnapshot) -> dict[str, dict[uuid.UUID, Any]]:
    """
    Extract mutable copies of all entities from a snapshot for restoration.

    This is the inverse of create_snapshot. It takes an immutable snapshot
    and returns mutable dictionaries that can be used to restore the runtime
    state.

    Args:
        snapshot: The RuntimeSnapshot to restore from.

    Returns:
        A dictionary with keys 'projects', 'tasks', 'execution_sessions',
        'artifacts', and 'memory_entries', each containing a mutable dict
        of entities keyed by their UUID.
    """
    return {
        "projects": {k: copy.deepcopy(v) for k, v in snapshot.projects.items()},
        "tasks": {k: copy.deepcopy(v) for k, v in snapshot.tasks.items()},
        "execution_sessions": {k: copy.deepcopy(v) for k, v in snapshot.execution_sessions.items()},
        "artifacts": {k: copy.deepcopy(v) for k, v in snapshot.artifacts.items()},
        "memory_entries": {k: copy.deepcopy(v) for k, v in snapshot.memory_entries.items()},
    }