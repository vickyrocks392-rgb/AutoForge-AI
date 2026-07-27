"""
Internal mutable runtime state container for the AutoForge AI Runtime State Manager.

This module defines the RuntimeState dataclass that holds all in-memory
collections. It is the internal representation that the StateManager
protects with asyncio locks.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from autoforge_models.artifact import Artifact
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.project import Project
from autoforge_models.task import Task


@dataclass
class RuntimeState:
    """
    Mutable container for all runtime state collections.

    This is the internal data structure that holds the live runtime state.
    It is not exposed directly to consumers — all access goes through the
    RuntimeStateManager which provides concurrency protection.

    All collections are plain dicts keyed by entity UUID for O(1) lookup.
    """

    projects: dict[uuid.UUID, Project] = field(default_factory=dict)
    """All registered Projects, keyed by Project.id."""

    tasks: dict[uuid.UUID, Task] = field(default_factory=dict)
    """All registered Tasks, keyed by Task.id."""

    execution_sessions: dict[uuid.UUID, ExecutionSession] = field(default_factory=dict)
    """All registered ExecutionSessions, keyed by ExecutionSession.id."""

    artifacts: dict[uuid.UUID, Artifact] = field(default_factory=dict)
    """All registered Artifacts, keyed by Artifact.id."""

    memory_entries: dict[uuid.UUID, MemoryEntry] = field(default_factory=dict)
    """All registered MemoryEntries, keyed by MemoryEntry.id."""

    @property
    def is_empty(self) -> bool:
        """Check whether the runtime state contains any entities."""
        return (
            not self.projects
            and not self.tasks
            and not self.execution_sessions
            and not self.artifacts
            and not self.memory_entries
        )

    @property
    def total_entities(self) -> int:
        """Return the total number of entities across all collections."""
        return (
            len(self.projects)
            + len(self.tasks)
            + len(self.execution_sessions)
            + len(self.artifacts)
            + len(self.memory_entries)
        )

    def clear(self) -> None:
        """Remove all entities from all collections."""
        self.projects.clear()
        self.tasks.clear()
        self.execution_sessions.clear()
        self.artifacts.clear()
        self.memory_entries.clear()