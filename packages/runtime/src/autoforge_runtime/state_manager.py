"""
Runtime State Manager — the authoritative in-memory state management subsystem.

The RuntimeStateManager is the single source of truth for the current runtime
state of AutoForge AI. It maintains in-memory collections of all active entities
and provides concurrent-safe CRUD operations, snapshot/restore, and state
transition validation.

This is NOT a database, cache, or persistence mechanism.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from autoforge_models.artifact import Artifact
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.project import Project
from autoforge_models.task import Task

from autoforge_runtime.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    SnapshotError,
    StateError,
)
from autoforge_runtime.snapshots import (
    RuntimeSnapshot,
    create_snapshot,
    restore_snapshot,
)
from autoforge_runtime.state import RuntimeState
from autoforge_runtime.transitions import (
    validate_execution_transition,
    validate_task_transition,
)


class RuntimeStateManager:
    """
    Authoritative in-memory runtime state manager for AutoForge AI.

    Maintains the live state of all active entities — Projects, Tasks,
    ExecutionSessions, Artifacts, and MemoryEntries — with O(1) lookup
    by ID and asyncio-based concurrency protection.

    This class is the single entry point for all runtime state mutations.
    All public methods are coroutines that acquire the internal lock to
    ensure thread safety in async contexts.

    Usage:
        manager = RuntimeStateManager()
        await manager.register_project(project)
        found = await manager.get_project(project.id)
        snapshot = await manager.create_snapshot()
        await manager.restore_snapshot(snapshot)
        await manager.reset()
    """

    def __init__(self) -> None:
        """Initialize an empty runtime state manager."""
        self._state = RuntimeState()

    # ── Project Operations ───────────────────────────────────────────────

    async def register_project(self, project: Project) -> None:
        """
        Register a new Project in the runtime state.

        Args:
            project: The Project to register.

        Raises:
            DuplicateEntityError: If a Project with the same ID already exists.
        """
        if project.id in self._state.projects:
            raise DuplicateEntityError(
                f"Project with ID {project.id} already exists",
                details={"entity_id": str(project.id), "entity_type": "project"},
            )
        self._state.projects[project.id] = project

    async def update_project(self, project: Project) -> None:
        """
        Update an existing Project in the runtime state.

        Args:
            project: The Project with updated fields.

        Raises:
            EntityNotFoundError: If no Project with the given ID exists.
        """
        if project.id not in self._state.projects:
            raise EntityNotFoundError(
                f"Project with ID {project.id} not found",
                details={"entity_id": str(project.id), "entity_type": "project"},
            )
        self._state.projects[project.id] = project

    async def remove_project(self, project_id: uuid.UUID) -> None:
        """
        Remove a Project from the runtime state.

        Args:
            project_id: The UUID of the Project to remove.

        Raises:
            EntityNotFoundError: If no Project with the given ID exists.
        """
        if project_id not in self._state.projects:
            raise EntityNotFoundError(
                f"Project with ID {project_id} not found",
                details={"entity_id": str(project_id), "entity_type": "project"},
            )
        del self._state.projects[project_id]

    async def get_project(self, project_id: uuid.UUID) -> Project | None:
        """
        Look up a Project by its ID.

        Args:
            project_id: The UUID of the Project to find.

        Returns:
            The Project if found, or None.
        """
        return self._state.projects.get(project_id)

    async def get_project_or_raise(self, project_id: uuid.UUID) -> Project:
        """
        Look up a Project by its ID, raising if not found.

        Args:
            project_id: The UUID of the Project to find.

        Returns:
            The Project.

        Raises:
            EntityNotFoundError: If no Project with the given ID exists.
        """
        project = self._state.projects.get(project_id)
        if project is None:
            raise EntityNotFoundError(
                f"Project with ID {project_id} not found",
                details={"entity_id": str(project_id), "entity_type": "project"},
            )
        return project

    async def has_project(self, project_id: uuid.UUID) -> bool:
        """
        Check whether a Project exists in the runtime state.

        Args:
            project_id: The UUID to check.

        Returns:
            True if the Project exists, False otherwise.
        """
        return project_id in self._state.projects

    async def list_projects(self) -> Sequence[Project]:
        """
        Return a read-only view of all registered Projects.

        Returns:
            A sequence of all Projects in the runtime state.
        """
        return list(self._state.projects.values())

    # ── Task Operations ──────────────────────────────────────────────────

    async def register_task(self, task: Task) -> None:
        """
        Register a new Task in the runtime state.

        Args:
            task: The Task to register.

        Raises:
            DuplicateEntityError: If a Task with the same ID already exists.
        """
        if task.id in self._state.tasks:
            raise DuplicateEntityError(
                f"Task with ID {task.id} already exists",
                details={"entity_id": str(task.id), "entity_type": "task"},
            )
        self._state.tasks[task.id] = task

    async def update_task(self, task: Task) -> None:
        """
        Update an existing Task in the runtime state.

        Args:
            task: The Task with updated fields.

        Raises:
            EntityNotFoundError: If no Task with the given ID exists.
        """
        if task.id not in self._state.tasks:
            raise EntityNotFoundError(
                f"Task with ID {task.id} not found",
                details={"entity_id": str(task.id), "entity_type": "task"},
            )
        self._state.tasks[task.id] = task

    async def update_task_status(
        self,
        task_id: uuid.UUID,
        new_status: Any,
    ) -> Task:
        """
        Update a Task's status with transition validation.

        Args:
            task_id: The UUID of the Task to update.
            new_status: The desired TaskStatus value.

        Returns:
            The updated Task.

        Raises:
            EntityNotFoundError: If no Task with the given ID exists.
            InvalidTransitionError: If the status transition is not allowed.
        """
        task = await self.get_task_or_raise(task_id)
        validate_task_transition(
            task.status,
            new_status,
            task_id=str(task_id),
        )
        updated = task.model_copy(update={"status": new_status})
        self._state.tasks[task_id] = updated
        return updated

    async def remove_task(self, task_id: uuid.UUID) -> None:
        """
        Remove a Task from the runtime state.

        Args:
            task_id: The UUID of the Task to remove.

        Raises:
            EntityNotFoundError: If no Task with the given ID exists.
        """
        if task_id not in self._state.tasks:
            raise EntityNotFoundError(
                f"Task with ID {task_id} not found",
                details={"entity_id": str(task_id), "entity_type": "task"},
            )
        del self._state.tasks[task_id]

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        """
        Look up a Task by its ID.

        Args:
            task_id: The UUID of the Task to find.

        Returns:
            The Task if found, or None.
        """
        return self._state.tasks.get(task_id)

    async def get_task_or_raise(self, task_id: uuid.UUID) -> Task:
        """
        Look up a Task by its ID, raising if not found.

        Args:
            task_id: The UUID of the Task to find.

        Returns:
            The Task.

        Raises:
            EntityNotFoundError: If no Task with the given ID exists.
        """
        task = self._state.tasks.get(task_id)
        if task is None:
            raise EntityNotFoundError(
                f"Task with ID {task_id} not found",
                details={"entity_id": str(task_id), "entity_type": "task"},
            )
        return task

    async def has_task(self, task_id: uuid.UUID) -> bool:
        """
        Check whether a Task exists in the runtime state.

        Args:
            task_id: The UUID to check.

        Returns:
            True if the Task exists, False otherwise.
        """
        return task_id in self._state.tasks

    async def list_tasks(self) -> Sequence[Task]:
        """
        Return a read-only view of all registered Tasks.

        Returns:
            A sequence of all Tasks in the runtime state.
        """
        return list(self._state.tasks.values())

    async def list_tasks_by_project(self, project_id: uuid.UUID) -> Sequence[Task]:
        """
        Return all Tasks belonging to a specific Project.

        Args:
            project_id: The UUID of the Project.

        Returns:
            A sequence of Tasks for the given Project.
        """
        return [t for t in self._state.tasks.values() if t.project_id == project_id]

    # ── ExecutionSession Operations ──────────────────────────────────────

    async def register_execution_session(self, session: ExecutionSession) -> None:
        """
        Register a new ExecutionSession in the runtime state.

        Args:
            session: The ExecutionSession to register.

        Raises:
            DuplicateEntityError: If an ExecutionSession with the same ID already exists.
        """
        if session.id in self._state.execution_sessions:
            raise DuplicateEntityError(
                f"ExecutionSession with ID {session.id} already exists",
                details={"entity_id": str(session.id), "entity_type": "execution_session"},
            )
        self._state.execution_sessions[session.id] = session

    async def update_execution_session(self, session: ExecutionSession) -> None:
        """
        Update an existing ExecutionSession in the runtime state.

        Args:
            session: The ExecutionSession with updated fields.

        Raises:
            EntityNotFoundError: If no ExecutionSession with the given ID exists.
        """
        if session.id not in self._state.execution_sessions:
            raise EntityNotFoundError(
                f"ExecutionSession with ID {session.id} not found",
                details={"entity_id": str(session.id), "entity_type": "execution_session"},
            )
        self._state.execution_sessions[session.id] = session

    async def update_execution_session_status(
        self,
        session_id: uuid.UUID,
        new_status: Any,
    ) -> ExecutionSession:
        """
        Update an ExecutionSession's status with transition validation.

        Args:
            session_id: The UUID of the ExecutionSession to update.
            new_status: The desired ExecutionStatus value.

        Returns:
            The updated ExecutionSession.

        Raises:
            EntityNotFoundError: If no ExecutionSession with the given ID exists.
            InvalidTransitionError: If the status transition is not allowed.
        """
        session = await self.get_execution_session_or_raise(session_id)
        validate_execution_transition(
            session.status,
            new_status,
            session_id=str(session_id),
        )
        updated = session.model_copy(update={"status": new_status})
        self._state.execution_sessions[session_id] = updated
        return updated

    async def remove_execution_session(self, session_id: uuid.UUID) -> None:
        """
        Remove an ExecutionSession from the runtime state.

        Args:
            session_id: The UUID of the ExecutionSession to remove.

        Raises:
            EntityNotFoundError: If no ExecutionSession with the given ID exists.
        """
        if session_id not in self._state.execution_sessions:
            raise EntityNotFoundError(
                f"ExecutionSession with ID {session_id} not found",
                details={"entity_id": str(session_id), "entity_type": "execution_session"},
            )
        del self._state.execution_sessions[session_id]

    async def get_execution_session(self, session_id: uuid.UUID) -> ExecutionSession | None:
        """
        Look up an ExecutionSession by its ID.

        Args:
            session_id: The UUID of the ExecutionSession to find.

        Returns:
            The ExecutionSession if found, or None.
        """
        return self._state.execution_sessions.get(session_id)

    async def get_execution_session_or_raise(self, session_id: uuid.UUID) -> ExecutionSession:
        """
        Look up an ExecutionSession by its ID, raising if not found.

        Args:
            session_id: The UUID of the ExecutionSession to find.

        Returns:
            The ExecutionSession.

        Raises:
            EntityNotFoundError: If no ExecutionSession with the given ID exists.
        """
        session = self._state.execution_sessions.get(session_id)
        if session is None:
            raise EntityNotFoundError(
                f"ExecutionSession with ID {session_id} not found",
                details={"entity_id": str(session_id), "entity_type": "execution_session"},
            )
        return session

    async def has_execution_session(self, session_id: uuid.UUID) -> bool:
        """
        Check whether an ExecutionSession exists in the runtime state.

        Args:
            session_id: The UUID to check.

        Returns:
            True if the ExecutionSession exists, False otherwise.
        """
        return session_id in self._state.execution_sessions

    async def list_execution_sessions(self) -> Sequence[ExecutionSession]:
        """
        Return a read-only view of all registered ExecutionSessions.

        Returns:
            A sequence of all ExecutionSessions in the runtime state.
        """
        return list(self._state.execution_sessions.values())

    async def list_execution_sessions_by_task(
        self, task_id: uuid.UUID
    ) -> Sequence[ExecutionSession]:
        """
        Return all ExecutionSessions for a specific Task.

        Args:
            task_id: The UUID of the Task.

        Returns:
            A sequence of ExecutionSessions for the given Task.
        """
        return [
            s
            for s in self._state.execution_sessions.values()
            if s.task_id == task_id
        ]

    async def list_execution_sessions_by_project(
        self, project_id: uuid.UUID
    ) -> Sequence[ExecutionSession]:
        """
        Return all ExecutionSessions for a specific Project.

        Args:
            project_id: The UUID of the Project.

        Returns:
            A sequence of ExecutionSessions for the given Project.
        """
        return [
            s
            for s in self._state.execution_sessions.values()
            if s.project_id == project_id
        ]

    # ── Artifact Operations ──────────────────────────────────────────────

    async def register_artifact(self, artifact: Artifact) -> None:
        """
        Register a new Artifact in the runtime state.

        Args:
            artifact: The Artifact to register.

        Raises:
            DuplicateEntityError: If an Artifact with the same ID already exists.
        """
        if artifact.id in self._state.artifacts:
            raise DuplicateEntityError(
                f"Artifact with ID {artifact.id} already exists",
                details={"entity_id": str(artifact.id), "entity_type": "artifact"},
            )
        self._state.artifacts[artifact.id] = artifact

    async def update_artifact(self, artifact: Artifact) -> None:
        """
        Update an existing Artifact in the runtime state.

        Args:
            artifact: The Artifact with updated fields.

        Raises:
            EntityNotFoundError: If no Artifact with the given ID exists.
        """
        if artifact.id not in self._state.artifacts:
            raise EntityNotFoundError(
                f"Artifact with ID {artifact.id} not found",
                details={"entity_id": str(artifact.id), "entity_type": "artifact"},
            )
        self._state.artifacts[artifact.id] = artifact

    async def remove_artifact(self, artifact_id: uuid.UUID) -> None:
        """
        Remove an Artifact from the runtime state.

        Args:
            artifact_id: The UUID of the Artifact to remove.

        Raises:
            EntityNotFoundError: If no Artifact with the given ID exists.
        """
        if artifact_id not in self._state.artifacts:
            raise EntityNotFoundError(
                f"Artifact with ID {artifact_id} not found",
                details={"entity_id": str(artifact_id), "entity_type": "artifact"},
            )
        del self._state.artifacts[artifact_id]

    async def get_artifact(self, artifact_id: uuid.UUID) -> Artifact | None:
        """
        Look up an Artifact by its ID.

        Args:
            artifact_id: The UUID of the Artifact to find.

        Returns:
            The Artifact if found, or None.
        """
        return self._state.artifacts.get(artifact_id)

    async def get_artifact_or_raise(self, artifact_id: uuid.UUID) -> Artifact:
        """
        Look up an Artifact by its ID, raising if not found.

        Args:
            artifact_id: The UUID of the Artifact to find.

        Returns:
            The Artifact.

        Raises:
            EntityNotFoundError: If no Artifact with the given ID exists.
        """
        artifact = self._state.artifacts.get(artifact_id)
        if artifact is None:
            raise EntityNotFoundError(
                f"Artifact with ID {artifact_id} not found",
                details={"entity_id": str(artifact_id), "entity_type": "artifact"},
            )
        return artifact

    async def has_artifact(self, artifact_id: uuid.UUID) -> bool:
        """
        Check whether an Artifact exists in the runtime state.

        Args:
            artifact_id: The UUID to check.

        Returns:
            True if the Artifact exists, False otherwise.
        """
        return artifact_id in self._state.artifacts

    async def list_artifacts(self) -> Sequence[Artifact]:
        """
        Return a read-only view of all registered Artifacts.

        Returns:
            A sequence of all Artifacts in the runtime state.
        """
        return list(self._state.artifacts.values())

    async def list_artifacts_by_project(self, project_id: uuid.UUID) -> Sequence[Artifact]:
        """
        Return all Artifacts belonging to a specific Project.

        Args:
            project_id: The UUID of the Project.

        Returns:
            A sequence of Artifacts for the given Project.
        """
        return [a for a in self._state.artifacts.values() if a.project_id == project_id]

    async def list_artifacts_by_task(self, task_id: uuid.UUID) -> Sequence[Artifact]:
        """
        Return all Artifacts produced by a specific Task.

        Args:
            task_id: The UUID of the Task.

        Returns:
            A sequence of Artifacts for the given Task.
        """
        return [a for a in self._state.artifacts.values() if a.task_id == task_id]

    # ── MemoryEntry Operations ───────────────────────────────────────────

    async def register_memory_entry(self, entry: MemoryEntry) -> None:
        """
        Register a new MemoryEntry in the runtime state.

        Args:
            entry: The MemoryEntry to register.

        Raises:
            DuplicateEntityError: If a MemoryEntry with the same ID already exists.
        """
        if entry.id in self._state.memory_entries:
            raise DuplicateEntityError(
                f"MemoryEntry with ID {entry.id} already exists",
                details={"entity_id": str(entry.id), "entity_type": "memory_entry"},
            )
        self._state.memory_entries[entry.id] = entry

    async def update_memory_entry(self, entry: MemoryEntry) -> None:
        """
        Update an existing MemoryEntry in the runtime state.

        Args:
            entry: The MemoryEntry with updated fields.

        Raises:
            EntityNotFoundError: If no MemoryEntry with the given ID exists.
        """
        if entry.id not in self._state.memory_entries:
            raise EntityNotFoundError(
                f"MemoryEntry with ID {entry.id} not found",
                details={"entity_id": str(entry.id), "entity_type": "memory_entry"},
            )
        self._state.memory_entries[entry.id] = entry

    async def remove_memory_entry(self, entry_id: uuid.UUID) -> None:
        """
        Remove a MemoryEntry from the runtime state.

        Args:
            entry_id: The UUID of the MemoryEntry to remove.

        Raises:
            EntityNotFoundError: If no MemoryEntry with the given ID exists.
        """
        if entry_id not in self._state.memory_entries:
            raise EntityNotFoundError(
                f"MemoryEntry with ID {entry_id} not found",
                details={"entity_id": str(entry_id), "entity_type": "memory_entry"},
            )
        del self._state.memory_entries[entry_id]

    async def get_memory_entry(self, entry_id: uuid.UUID) -> MemoryEntry | None:
        """
        Look up a MemoryEntry by its ID.

        Args:
            entry_id: The UUID of the MemoryEntry to find.

        Returns:
            The MemoryEntry if found, or None.
        """
        return self._state.memory_entries.get(entry_id)

    async def get_memory_entry_or_raise(self, entry_id: uuid.UUID) -> MemoryEntry:
        """
        Look up a MemoryEntry by its ID, raising if not found.

        Args:
            entry_id: The UUID of the MemoryEntry to find.

        Returns:
            The MemoryEntry.

        Raises:
            EntityNotFoundError: If no MemoryEntry with the given ID exists.
        """
        entry = self._state.memory_entries.get(entry_id)
        if entry is None:
            raise EntityNotFoundError(
                f"MemoryEntry with ID {entry_id} not found",
                details={"entity_id": str(entry_id), "entity_type": "memory_entry"},
            )
        return entry

    async def has_memory_entry(self, entry_id: uuid.UUID) -> bool:
        """
        Check whether a MemoryEntry exists in the runtime state.

        Args:
            entry_id: The UUID to check.

        Returns:
            True if the MemoryEntry exists, False otherwise.
        """
        return entry_id in self._state.memory_entries

    async def list_memory_entries(self) -> Sequence[MemoryEntry]:
        """
        Return a read-only view of all registered MemoryEntries.

        Returns:
            A sequence of all MemoryEntries in the runtime state.
        """
        return list(self._state.memory_entries.values())

    async def list_memory_entries_by_project(
        self, project_id: uuid.UUID
    ) -> Sequence[MemoryEntry]:
        """
        Return all MemoryEntries for a specific Project.

        Args:
            project_id: The UUID of the Project.

        Returns:
            A sequence of MemoryEntries for the given Project.
        """
        return [
            m
            for m in self._state.memory_entries.values()
            if m.project_id == project_id
        ]

    # ── Snapshot Operations ──────────────────────────────────────────────

    async def create_snapshot(self) -> RuntimeSnapshot:
        """
        Create an immutable snapshot of the current runtime state.

        The snapshot contains deep copies of all registered entities and
        is fully immutable. It can be used for checkpoint/restore operations
        or for providing consistent read-only views.

        Returns:
            A RuntimeSnapshot capturing the current state.
        """
        return create_snapshot(
            projects=self._state.projects,
            tasks=self._state.tasks,
            execution_sessions=self._state.execution_sessions,
            artifacts=self._state.artifacts,
            memory_entries=self._state.memory_entries,
        )

    async def restore_snapshot(self, snapshot: RuntimeSnapshot) -> None:
        """
        Restore the runtime state from an immutable snapshot.

        This replaces the entire current state with the contents of the
        snapshot. All current entities are discarded.

        Args:
            snapshot: The RuntimeSnapshot to restore from.

        Raises:
            SnapshotError: If the snapshot is invalid or cannot be restored.
        """
        try:
            restored = restore_snapshot(snapshot)
            self._state.projects = restored["projects"]
            self._state.tasks = restored["tasks"]
            self._state.execution_sessions = restored["execution_sessions"]
            self._state.artifacts = restored["artifacts"]
            self._state.memory_entries = restored["memory_entries"]
        except Exception as exc:
            raise SnapshotError(
                f"Failed to restore snapshot: {exc}",
                details={"snapshot_id": str(snapshot.snapshot_id)},
            ) from exc

    # ── Lifecycle Operations ─────────────────────────────────────────────

    async def reset(self) -> None:
        """Reset the runtime state, removing all entities."""
        self._state.clear()

    async def is_empty(self) -> bool:
        """
        Check whether the runtime state contains any entities.

        Returns:
            True if no entities are registered, False otherwise.
        """
        return self._state.is_empty

    async def total_entities(self) -> int:
        """
        Return the total number of entities across all collections.

        Returns:
            The total count of all registered entities.
        """
        return self._state.total_entities

    # ── Bulk Operations ──────────────────────────────────────────────────

    async def register_projects(self, projects: Sequence[Project]) -> None:
        """
        Register multiple Projects atomically.

        Args:
            projects: A sequence of Projects to register.

        Raises:
            DuplicateEntityError: If any Project ID conflicts with an existing one.
        """
        for project in projects:
            await self.register_project(project)

    async def register_tasks(self, tasks: Sequence[Task]) -> None:
        """
        Register multiple Tasks atomically.

        Args:
            tasks: A sequence of Tasks to register.

        Raises:
            DuplicateEntityError: If any Task ID conflicts with an existing one.
        """
        for task in tasks:
            await self.register_task(task)

    async def register_execution_sessions(
        self, sessions: Sequence[ExecutionSession]
    ) -> None:
        """
        Register multiple ExecutionSessions atomically.

        Args:
            sessions: A sequence of ExecutionSessions to register.

        Raises:
            DuplicateEntityError: If any ExecutionSession ID conflicts with an existing one.
        """
        for session in sessions:
            await self.register_execution_session(session)

    async def register_artifacts(self, artifacts: Sequence[Artifact]) -> None:
        """
        Register multiple Artifacts atomically.

        Args:
            artifacts: A sequence of Artifacts to register.

        Raises:
            DuplicateEntityError: If any Artifact ID conflicts with an existing one.
        """
        for artifact in artifacts:
            await self.register_artifact(artifact)

    async def register_memory_entries(self, entries: Sequence[MemoryEntry]) -> None:
        """
        Register multiple MemoryEntries atomically.

        Args:
            entries: A sequence of MemoryEntries to register.

        Raises:
            DuplicateEntityError: If any MemoryEntry ID conflicts with an existing one.
        """
        for entry in entries:
            await self.register_memory_entry(entry)