"""
Comprehensive tests for the Runtime State Manager.

Covers:
    - CRUD operations for all entity types
    - Snapshots and restore
    - Transition validation
    - Concurrency safety
    - Exceptions
    - Read-only access
    - Edge cases
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from autoforge_models.artifact import Artifact
from autoforge_models.enums import (
    ArtifactType,
    ExecutionStatus,
    MemoryType,
    TaskPriority,
    TaskStatus,
)
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.project import Project
from autoforge_models.task import Task

from autoforge_runtime import RuntimeStateManager, RuntimeSnapshot
from autoforge_runtime.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidTransitionError,
    SnapshotError,
)
from autoforge_runtime.transitions import (
    get_allowed_execution_transitions,
    get_allowed_task_transitions,
    is_terminal,
    validate_execution_transition,
    validate_task_transition,
)


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def manager() -> RuntimeStateManager:
    """Create a fresh RuntimeStateManager for each test."""
    return RuntimeStateManager()


@pytest.fixture
def project() -> Project:
    """Create a sample Project."""
    return Project(name="Test Project", description="A test project")


@pytest.fixture
def task(project: Project) -> Task:
    """Create a sample Task belonging to the sample Project."""
    return Task(
        project_id=project.id,
        title="Test Task",
        description="A test task",
        status=TaskStatus.PENDING,
    )


@pytest.fixture
def execution_session(project: Project, task: Task) -> ExecutionSession:
    """Create a sample ExecutionSession."""
    return ExecutionSession(
        project_id=project.id,
        task_id=task.id,
        status=ExecutionStatus.PENDING,
    )


@pytest.fixture
def artifact(project: Project, task: Task) -> Artifact:
    """Create a sample Artifact."""
    return Artifact(
        project_id=project.id,
        task_id=task.id,
        name="test.py",
        artifact_type=ArtifactType.CODE,
        file_path="/tmp/test.py",
    )


@pytest.fixture
def memory_entry(project: Project) -> MemoryEntry:
    """Create a sample MemoryEntry."""
    return MemoryEntry(
        project_id=project.id,
        memory_type=MemoryType.SEMANTIC,
        key="test-key",
        title="Test Memory",
        content="This is a test memory entry.",
    )


# ── Project CRUD Tests ──────────────────────────────────────────────────


class TestProjectCRUD:
    """Tests for Project CRUD operations."""

    async def test_register_and_get_project(self, manager: RuntimeStateManager, project: Project) -> None:
        """Register a project and retrieve it by ID."""
        await manager.register_project(project)
        found = await manager.get_project(project.id)
        assert found is not None
        assert found.id == project.id
        assert found.name == "Test Project"

    async def test_register_duplicate_project_raises(self, manager: RuntimeStateManager, project: Project) -> None:
        """Registering a project with a duplicate ID raises DuplicateEntityError."""
        await manager.register_project(project)
        with pytest.raises(DuplicateEntityError) as exc_info:
            await manager.register_project(project)
        assert "already exists" in str(exc_info.value)

    async def test_update_project(self, manager: RuntimeStateManager, project: Project) -> None:
        """Update an existing project."""
        await manager.register_project(project)
        updated = project.model_copy(update={"description": "Updated description"})
        await manager.update_project(updated)
        found = await manager.get_project(project.id)
        assert found is not None
        assert found.description == "Updated description"

    async def test_update_nonexistent_project_raises(self, manager: RuntimeStateManager) -> None:
        """Updating a project that doesn't exist raises EntityNotFoundError."""
        fake_id = uuid.uuid4()
        fake_project = Project(id=fake_id, name="Fake")
        with pytest.raises(EntityNotFoundError) as exc_info:
            await manager.update_project(fake_project)
        assert "not found" in str(exc_info.value)

    async def test_remove_project(self, manager: RuntimeStateManager, project: Project) -> None:
        """Remove a project and verify it's gone."""
        await manager.register_project(project)
        await manager.remove_project(project.id)
        found = await manager.get_project(project.id)
        assert found is None

    async def test_remove_nonexistent_project_raises(self, manager: RuntimeStateManager) -> None:
        """Removing a project that doesn't exist raises EntityNotFoundError."""
        fake_id = uuid.uuid4()
        with pytest.raises(EntityNotFoundError) as exc_info:
            await manager.remove_project(fake_id)
        assert "not found" in str(exc_info.value)

    async def test_get_project_or_raise(self, manager: RuntimeStateManager, project: Project) -> None:
        """get_project_or_raise returns the project or raises."""
        await manager.register_project(project)
        found = await manager.get_project_or_raise(project.id)
        assert found.id == project.id

        with pytest.raises(EntityNotFoundError):
            await manager.get_project_or_raise(uuid.uuid4())

    async def test_has_project(self, manager: RuntimeStateManager, project: Project) -> None:
        """Check project existence."""
        assert await manager.has_project(project.id) is False
        await manager.register_project(project)
        assert await manager.has_project(project.id) is True

    async def test_list_projects(self, manager: RuntimeStateManager) -> None:
        """List all registered projects."""
        p1 = Project(name="Project 1")
        p2 = Project(name="Project 2")
        await manager.register_project(p1)
        await manager.register_project(p2)
        projects = await manager.list_projects()
        assert len(projects) == 2
        assert {p.id for p in projects} == {p1.id, p2.id}

    async def test_list_projects_empty(self, manager: RuntimeStateManager) -> None:
        """List projects returns empty list when none registered."""
        assert await manager.list_projects() == []


# ── Task CRUD Tests ─────────────────────────────────────────────────────


class TestTaskCRUD:
    """Tests for Task CRUD operations."""

    async def test_register_and_get_task(self, manager: RuntimeStateManager, task: Task) -> None:
        """Register a task and retrieve it by ID."""
        await manager.register_task(task)
        found = await manager.get_task(task.id)
        assert found is not None
        assert found.id == task.id
        assert found.title == "Test Task"

    async def test_register_duplicate_task_raises(self, manager: RuntimeStateManager, task: Task) -> None:
        """Registering a duplicate task raises DuplicateEntityError."""
        await manager.register_task(task)
        with pytest.raises(DuplicateEntityError):
            await manager.register_task(task)

    async def test_update_task(self, manager: RuntimeStateManager, task: Task) -> None:
        """Update an existing task."""
        await manager.register_task(task)
        updated = task.model_copy(update={"title": "Updated Task"})
        await manager.update_task(updated)
        found = await manager.get_task(task.id)
        assert found is not None
        assert found.title == "Updated Task"

    async def test_remove_task(self, manager: RuntimeStateManager, task: Task) -> None:
        """Remove a task and verify it's gone."""
        await manager.register_task(task)
        await manager.remove_task(task.id)
        assert await manager.get_task(task.id) is None

    async def test_list_tasks(self, manager: RuntimeStateManager, project: Project) -> None:
        """List all registered tasks."""
        t1 = Task(project_id=project.id, title="Task 1")
        t2 = Task(project_id=project.id, title="Task 2")
        await manager.register_task(t1)
        await manager.register_task(t2)
        tasks = await manager.list_tasks()
        assert len(tasks) == 2

    async def test_list_tasks_by_project(self, manager: RuntimeStateManager, project: Project) -> None:
        """List tasks filtered by project."""
        t1 = Task(project_id=project.id, title="Task 1")
        other_project = Project(name="Other")
        t2 = Task(project_id=other_project.id, title="Task 2")
        await manager.register_task(t1)
        await manager.register_task(t2)
        project_tasks = await manager.list_tasks_by_project(project.id)
        assert len(project_tasks) == 1
        assert project_tasks[0].id == t1.id

    async def test_get_task_or_raise(self, manager: RuntimeStateManager, task: Task) -> None:
        """get_task_or_raise returns the task or raises."""
        await manager.register_task(task)
        found = await manager.get_task_or_raise(task.id)
        assert found.id == task.id

        with pytest.raises(EntityNotFoundError):
            await manager.get_task_or_raise(uuid.uuid4())

    async def test_has_task(self, manager: RuntimeStateManager, task: Task) -> None:
        """Check task existence."""
        assert await manager.has_task(task.id) is False
        await manager.register_task(task)
        assert await manager.has_task(task.id) is True


# ── ExecutionSession CRUD Tests ─────────────────────────────────────────


class TestExecutionSessionCRUD:
    """Tests for ExecutionSession CRUD operations."""

    async def test_register_and_get_session(
        self, manager: RuntimeStateManager, execution_session: ExecutionSession
    ) -> None:
        """Register an execution session and retrieve it."""
        await manager.register_execution_session(execution_session)
        found = await manager.get_execution_session(execution_session.id)
        assert found is not None
        assert found.id == execution_session.id

    async def test_register_duplicate_session_raises(
        self, manager: RuntimeStateManager, execution_session: ExecutionSession
    ) -> None:
        """Registering a duplicate session raises DuplicateEntityError."""
        await manager.register_execution_session(execution_session)
        with pytest.raises(DuplicateEntityError):
            await manager.register_execution_session(execution_session)

    async def test_update_session(
        self, manager: RuntimeStateManager, execution_session: ExecutionSession
    ) -> None:
        """Update an existing execution session."""
        await manager.register_execution_session(execution_session)
        updated = execution_session.model_copy(update={"retry_count": 1})
        await manager.update_execution_session(updated)
        found = await manager.get_execution_session(execution_session.id)
        assert found is not None
        assert found.retry_count == 1

    async def test_list_sessions_by_task(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """List sessions filtered by task."""
        s1 = ExecutionSession(project_id=project.id, task_id=task.id)
        s2 = ExecutionSession(project_id=project.id, task_id=task.id)
        await manager.register_execution_session(s1)
        await manager.register_execution_session(s2)
        sessions = await manager.list_execution_sessions_by_task(task.id)
        assert len(sessions) == 2

    async def test_list_sessions_by_project(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """List sessions filtered by project."""
        s1 = ExecutionSession(project_id=project.id, task_id=task.id)
        other_project = Project(name="Other")
        s2 = ExecutionSession(project_id=other_project.id)
        await manager.register_execution_session(s1)
        await manager.register_execution_session(s2)
        sessions = await manager.list_execution_sessions_by_project(project.id)
        assert len(sessions) == 1


# ── Artifact CRUD Tests ─────────────────────────────────────────────────


class TestArtifactCRUD:
    """Tests for Artifact CRUD operations."""

    async def test_register_and_get_artifact(
        self, manager: RuntimeStateManager, artifact: Artifact
    ) -> None:
        """Register an artifact and retrieve it."""
        await manager.register_artifact(artifact)
        found = await manager.get_artifact(artifact.id)
        assert found is not None
        assert found.id == artifact.id

    async def test_register_duplicate_artifact_raises(
        self, manager: RuntimeStateManager, artifact: Artifact
    ) -> None:
        """Registering a duplicate artifact raises DuplicateEntityError."""
        await manager.register_artifact(artifact)
        with pytest.raises(DuplicateEntityError):
            await manager.register_artifact(artifact)

    async def test_list_artifacts_by_task(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """List artifacts filtered by task."""
        a1 = Artifact(
            project_id=project.id,
            task_id=task.id,
            name="a1.py",
            artifact_type=ArtifactType.CODE,
            file_path="/tmp/a1.py",
        )
        a2 = Artifact(
            project_id=project.id,
            task_id=task.id,
            name="a2.py",
            artifact_type=ArtifactType.CODE,
            file_path="/tmp/a2.py",
        )
        await manager.register_artifact(a1)
        await manager.register_artifact(a2)
        artifacts = await manager.list_artifacts_by_task(task.id)
        assert len(artifacts) == 2

    async def test_list_artifacts_by_project(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """List artifacts filtered by project."""
        a1 = Artifact(
            project_id=project.id,
            task_id=task.id,
            name="a1.py",
            artifact_type=ArtifactType.CODE,
            file_path="/tmp/a1.py",
        )
        other_project = Project(name="Other")
        a2 = Artifact(
            project_id=other_project.id,
            name="a2.py",
            artifact_type=ArtifactType.CODE,
            file_path="/tmp/a2.py",
        )
        await manager.register_artifact(a1)
        await manager.register_artifact(a2)
        artifacts = await manager.list_artifacts_by_project(project.id)
        assert len(artifacts) == 1


# ── MemoryEntry CRUD Tests ──────────────────────────────────────────────


class TestMemoryEntryCRUD:
    """Tests for MemoryEntry CRUD operations."""

    async def test_register_and_get_memory_entry(
        self, manager: RuntimeStateManager, memory_entry: MemoryEntry
    ) -> None:
        """Register a memory entry and retrieve it."""
        await manager.register_memory_entry(memory_entry)
        found = await manager.get_memory_entry(memory_entry.id)
        assert found is not None
        assert found.id == memory_entry.id

    async def test_register_duplicate_memory_raises(
        self, manager: RuntimeStateManager, memory_entry: MemoryEntry
    ) -> None:
        """Registering a duplicate memory entry raises DuplicateEntityError."""
        await manager.register_memory_entry(memory_entry)
        with pytest.raises(DuplicateEntityError):
            await manager.register_memory_entry(memory_entry)

    async def test_list_memory_by_project(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """List memory entries filtered by project."""
        m1 = MemoryEntry(
            project_id=project.id,
            memory_type=MemoryType.SEMANTIC,
            key="key1",
            title="Memory 1",
            content="Content 1",
        )
        other_project = Project(name="Other")
        m2 = MemoryEntry(
            project_id=other_project.id,
            memory_type=MemoryType.EPISODIC,
            key="key2",
            title="Memory 2",
            content="Content 2",
        )
        await manager.register_memory_entry(m1)
        await manager.register_memory_entry(m2)
        entries = await manager.list_memory_entries_by_project(project.id)
        assert len(entries) == 1
        assert entries[0].id == m1.id


# ── Snapshot Tests ──────────────────────────────────────────────────────


class TestSnapshots:
    """Tests for snapshot creation and restoration."""

    async def test_create_empty_snapshot(self, manager: RuntimeStateManager) -> None:
        """Create a snapshot when no entities are registered."""
        snapshot = await manager.create_snapshot()
        assert isinstance(snapshot, RuntimeSnapshot)
        assert len(snapshot) == 0

    async def test_create_snapshot_with_entities(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """Create a snapshot with registered entities."""
        await manager.register_project(project)
        await manager.register_task(task)
        snapshot = await manager.create_snapshot()
        assert len(snapshot) == 2
        assert project.id in snapshot.projects
        assert task.id in snapshot.tasks

    async def test_snapshot_is_immutable(self, manager: RuntimeStateManager, project: Project) -> None:
        """Verify that a snapshot's collections are immutable."""
        await manager.register_project(project)
        snapshot = await manager.create_snapshot()
        # Verify the snapshot is a RuntimeSnapshot (frozen Pydantic model)
        assert isinstance(snapshot, RuntimeSnapshot)
        # Verify the collections are Mapping types (not plain dicts)
        from collections.abc import Mapping
        assert isinstance(snapshot.projects, Mapping)
        # Verify the snapshot model itself is frozen (Pydantic v2 raises ValidationError)
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            snapshot.snapshot_id = uuid.uuid4()  # type: ignore[assignment]

    async def test_snapshot_deep_copy(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Verify that snapshot contains deep copies, not references."""
        await manager.register_project(project)
        snapshot = await manager.create_snapshot()
        # Modify the original
        updated = project.model_copy(update={"name": "Changed"})
        await manager.update_project(updated)
        # Snapshot should still have the old value
        assert snapshot.projects[project.id].name == "Test Project"

    async def test_restore_snapshot(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """Restore state from a snapshot."""
        await manager.register_project(project)
        await manager.register_task(task)
        snapshot = await manager.create_snapshot()

        # Modify state after snapshot
        await manager.reset()
        assert await manager.is_empty()

        # Restore
        await manager.restore_snapshot(snapshot)
        assert await manager.has_project(project.id)
        assert await manager.has_task(task.id)

    async def test_restore_snapshot_replaces_state(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Restoring a snapshot replaces all current state."""
        await manager.register_project(project)
        snapshot = await manager.create_snapshot()

        # Add another project after snapshot
        p2 = Project(name="Extra")
        await manager.register_project(p2)

        # Restore should remove the extra project
        await manager.restore_snapshot(snapshot)
        assert await manager.has_project(project.id)
        assert not await manager.has_project(p2.id)

    async def test_snapshot_has_unique_id(self, manager: RuntimeStateManager) -> None:
        """Each snapshot gets a unique ID."""
        s1 = await manager.create_snapshot()
        s2 = await manager.create_snapshot()
        assert s1.snapshot_id != s2.snapshot_id


# ── Transition Validation Tests ─────────────────────────────────────────


class TestTaskTransitions:
    """Tests for Task status transition validation."""

    def test_valid_transition_pending_to_ready(self) -> None:
        """PENDING -> READY is valid."""
        validate_task_transition(TaskStatus.PENDING, TaskStatus.READY)

    def test_valid_transition_ready_to_running(self) -> None:
        """READY -> RUNNING is valid."""
        validate_task_transition(TaskStatus.READY, TaskStatus.RUNNING)

    def test_valid_transition_running_to_completed(self) -> None:
        """RUNNING -> COMPLETED is valid."""
        validate_task_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED)

    def test_valid_transition_running_to_failed(self) -> None:
        """RUNNING -> FAILED is valid."""
        validate_task_transition(TaskStatus.RUNNING, TaskStatus.FAILED)

    def test_valid_transition_running_to_cancelled(self) -> None:
        """RUNNING -> CANCELLED is valid."""
        validate_task_transition(TaskStatus.RUNNING, TaskStatus.CANCELLED)

    def test_valid_transition_pending_to_cancelled(self) -> None:
        """PENDING -> CANCELLED is valid."""
        validate_task_transition(TaskStatus.PENDING, TaskStatus.CANCELLED)

    def test_valid_transition_running_to_paused(self) -> None:
        """RUNNING -> PAUSED is valid."""
        validate_task_transition(TaskStatus.RUNNING, TaskStatus.PAUSED)

    def test_valid_transition_paused_to_running(self) -> None:
        """PAUSED -> RUNNING is valid."""
        validate_task_transition(TaskStatus.PAUSED, TaskStatus.RUNNING)

    def test_valid_transition_blocked_to_ready(self) -> None:
        """BLOCKED -> READY is valid."""
        validate_task_transition(TaskStatus.BLOCKED, TaskStatus.READY)

    def test_invalid_transition_pending_to_completed(self) -> None:
        """PENDING -> COMPLETED is invalid."""
        with pytest.raises(InvalidTransitionError) as exc_info:
            validate_task_transition(TaskStatus.PENDING, TaskStatus.COMPLETED)
        assert "Invalid Task status transition" in str(exc_info.value)

    def test_invalid_transition_completed_to_running(self) -> None:
        """COMPLETED -> RUNNING is invalid (terminal state)."""
        with pytest.raises(InvalidTransitionError):
            validate_task_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING)

    def test_invalid_transition_failed_to_running(self) -> None:
        """FAILED -> RUNNING is invalid (terminal state)."""
        with pytest.raises(InvalidTransitionError):
            validate_task_transition(TaskStatus.FAILED, TaskStatus.RUNNING)

    def test_invalid_transition_cancelled_to_pending(self) -> None:
        """CANCELLED -> PENDING is invalid (terminal state)."""
        with pytest.raises(InvalidTransitionError):
            validate_task_transition(TaskStatus.CANCELLED, TaskStatus.PENDING)

    def test_invalid_transition_ready_to_completed(self) -> None:
        """READY -> COMPLETED is invalid (must go through RUNNING)."""
        with pytest.raises(InvalidTransitionError):
            validate_task_transition(TaskStatus.READY, TaskStatus.COMPLETED)

    def test_get_allowed_task_transitions(self) -> None:
        """get_allowed_task_transitions returns correct set."""
        allowed = get_allowed_task_transitions(TaskStatus.PENDING)
        assert TaskStatus.READY in allowed
        assert TaskStatus.CANCELLED in allowed
        assert TaskStatus.RUNNING not in allowed

    def test_terminal_states(self) -> None:
        """is_terminal returns True for terminal states."""
        assert is_terminal(TaskStatus.COMPLETED)
        assert is_terminal(TaskStatus.FAILED)
        assert is_terminal(TaskStatus.CANCELLED)
        assert not is_terminal(TaskStatus.PENDING)
        assert not is_terminal(TaskStatus.RUNNING)


class TestExecutionTransitions:
    """Tests for ExecutionSession status transition validation."""

    def test_valid_transition_pending_to_running(self) -> None:
        """PENDING -> RUNNING is valid."""
        validate_execution_transition(ExecutionStatus.PENDING, ExecutionStatus.RUNNING)

    def test_valid_transition_running_to_completed(self) -> None:
        """RUNNING -> COMPLETED is valid."""
        validate_execution_transition(ExecutionStatus.RUNNING, ExecutionStatus.COMPLETED)

    def test_valid_transition_running_to_failed(self) -> None:
        """RUNNING -> FAILED is valid."""
        validate_execution_transition(ExecutionStatus.RUNNING, ExecutionStatus.FAILED)

    def test_valid_transition_running_to_cancelled(self) -> None:
        """RUNNING -> CANCELLED is valid."""
        validate_execution_transition(ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED)

    def test_valid_transition_running_to_paused(self) -> None:
        """RUNNING -> PAUSED is valid."""
        validate_execution_transition(ExecutionStatus.RUNNING, ExecutionStatus.PAUSED)

    def test_valid_transition_paused_to_running(self) -> None:
        """PAUSED -> RUNNING is valid."""
        validate_execution_transition(ExecutionStatus.PAUSED, ExecutionStatus.RUNNING)

    def test_invalid_transition_pending_to_completed(self) -> None:
        """PENDING -> COMPLETED is invalid."""
        with pytest.raises(InvalidTransitionError):
            validate_execution_transition(ExecutionStatus.PENDING, ExecutionStatus.COMPLETED)

    def test_invalid_transition_completed_to_running(self) -> None:
        """COMPLETED -> RUNNING is invalid."""
        with pytest.raises(InvalidTransitionError):
            validate_execution_transition(ExecutionStatus.COMPLETED, ExecutionStatus.RUNNING)

    def test_invalid_transition_cancelled_to_pending(self) -> None:
        """CANCELLED -> PENDING is invalid."""
        with pytest.raises(InvalidTransitionError):
            validate_execution_transition(ExecutionStatus.CANCELLED, ExecutionStatus.PENDING)

    def test_invalid_transition_timed_out_to_running(self) -> None:
        """TIMED_OUT -> RUNNING is invalid."""
        with pytest.raises(InvalidTransitionError):
            validate_execution_transition(ExecutionStatus.TIMED_OUT, ExecutionStatus.RUNNING)

    def test_get_allowed_execution_transitions(self) -> None:
        """get_allowed_execution_transitions returns correct set."""
        allowed = get_allowed_execution_transitions(ExecutionStatus.RUNNING)
        assert ExecutionStatus.COMPLETED in allowed
        assert ExecutionStatus.FAILED in allowed
        assert ExecutionStatus.CANCELLED in allowed
        assert ExecutionStatus.PAUSED in allowed
        assert ExecutionStatus.PENDING not in allowed

    def test_execution_terminal_states(self) -> None:
        """is_terminal returns True for terminal execution states."""
        assert is_terminal(ExecutionStatus.COMPLETED)
        assert is_terminal(ExecutionStatus.FAILED)
        assert is_terminal(ExecutionStatus.CANCELLED)
        assert is_terminal(ExecutionStatus.TIMED_OUT)
        assert not is_terminal(ExecutionStatus.PENDING)
        assert not is_terminal(ExecutionStatus.RUNNING)


# ── Status Update via Manager Tests ─────────────────────────────────────


class TestStatusUpdates:
    """Tests for status updates through the manager."""

    async def test_update_task_status_valid(
        self, manager: RuntimeStateManager, task: Task
    ) -> None:
        """Update task status through the manager with valid transition."""
        await manager.register_task(task)
        updated = await manager.update_task_status(task.id, TaskStatus.READY)
        assert updated.status == TaskStatus.READY

    async def test_update_task_status_invalid(
        self, manager: RuntimeStateManager, task: Task
    ) -> None:
        """Update task status through the manager with invalid transition."""
        await manager.register_task(task)
        with pytest.raises(InvalidTransitionError):
            await manager.update_task_status(task.id, TaskStatus.COMPLETED)

    async def test_update_task_status_nonexistent(
        self, manager: RuntimeStateManager
    ) -> None:
        """Update task status for nonexistent task raises EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await manager.update_task_status(uuid.uuid4(), TaskStatus.READY)

    async def test_update_execution_status_valid(
        self, manager: RuntimeStateManager, execution_session: ExecutionSession
    ) -> None:
        """Update execution session status with valid transition."""
        await manager.register_execution_session(execution_session)
        updated = await manager.update_execution_session_status(
            execution_session.id, ExecutionStatus.RUNNING
        )
        assert updated.status == ExecutionStatus.RUNNING

    async def test_update_execution_status_invalid(
        self, manager: RuntimeStateManager, execution_session: ExecutionSession
    ) -> None:
        """Update execution session status with invalid transition."""
        await manager.register_execution_session(execution_session)
        with pytest.raises(InvalidTransitionError):
            await manager.update_execution_session_status(
                execution_session.id, ExecutionStatus.COMPLETED
            )


# ── Lifecycle Tests ─────────────────────────────────────────────────────


class TestLifecycle:
    """Tests for lifecycle operations (reset, is_empty, total_entities)."""

    async def test_is_empty_initially(self, manager: RuntimeStateManager) -> None:
        """Manager starts empty."""
        assert await manager.is_empty()

    async def test_is_empty_after_register(self, manager: RuntimeStateManager, project: Project) -> None:
        """Manager is not empty after registering an entity."""
        await manager.register_project(project)
        assert not await manager.is_empty()

    async def test_reset_clears_state(
        self, manager: RuntimeStateManager, project: Project, task: Task
    ) -> None:
        """Reset removes all entities."""
        await manager.register_project(project)
        await manager.register_task(task)
        assert await manager.total_entities() == 2
        await manager.reset()
        assert await manager.is_empty()
        assert await manager.total_entities() == 0

    async def test_total_entities(
        self, manager: RuntimeStateManager, project: Project, task: Task,
        execution_session: ExecutionSession, artifact: Artifact, memory_entry: MemoryEntry
    ) -> None:
        """total_entities returns correct count."""
        await manager.register_project(project)
        await manager.register_task(task)
        await manager.register_execution_session(execution_session)
        await manager.register_artifact(artifact)
        await manager.register_memory_entry(memory_entry)
        assert await manager.total_entities() == 5


# ── Bulk Operation Tests ────────────────────────────────────────────────


class TestBulkOperations:
    """Tests for bulk registration operations."""

    async def test_register_projects(self, manager: RuntimeStateManager) -> None:
        """Register multiple projects."""
        projects = [Project(name=f"Project {i}") for i in range(3)]
        await manager.register_projects(projects)
        assert await manager.total_entities() == 3

    async def test_register_tasks(self, manager: RuntimeStateManager, project: Project) -> None:
        """Register multiple tasks."""
        tasks = [Task(project_id=project.id, title=f"Task {i}") for i in range(3)]
        await manager.register_tasks(tasks)
        assert await manager.total_entities() == 3

    async def test_register_execution_sessions(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Register multiple execution sessions."""
        sessions = [ExecutionSession(project_id=project.id) for _ in range(3)]
        await manager.register_execution_sessions(sessions)
        assert await manager.total_entities() == 3

    async def test_register_artifacts(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Register multiple artifacts."""
        artifacts = [
            Artifact(
                project_id=project.id,
                name=f"a{i}.py",
                artifact_type=ArtifactType.CODE,
                file_path=f"/tmp/a{i}.py",
            )
            for i in range(3)
        ]
        await manager.register_artifacts(artifacts)
        assert await manager.total_entities() == 3

    async def test_register_memory_entries(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Register multiple memory entries."""
        entries = [
            MemoryEntry(
                project_id=project.id,
                memory_type=MemoryType.SEMANTIC,
                key=f"key{i}",
                title=f"Memory {i}",
                content=f"Content {i}",
            )
            for i in range(3)
        ]
        await manager.register_memory_entries(entries)
        assert await manager.total_entities() == 3


# ── Concurrency Tests ───────────────────────────────────────────────────


class TestConcurrency:
    """Tests for concurrent access safety."""

    async def test_concurrent_registrations(
        self, manager: RuntimeStateManager
    ) -> None:
        """Register entities concurrently without data loss."""
        import asyncio

        async def register_project(i: int) -> None:
            p = Project(name=f"Concurrent Project {i}")
            await manager.register_project(p)

        tasks = [register_project(i) for i in range(20)]
        await asyncio.gather(*tasks)
        assert await manager.total_entities() == 20

    async def test_concurrent_reads_and_writes(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Concurrent reads and writes don't cause errors."""
        import asyncio

        await manager.register_project(project)

        async def read_project() -> None:
            for _ in range(50):
                await manager.get_project(project.id)

        async def write_project() -> None:
            for i in range(50):
                updated = project.model_copy(update={"name": f"Update {i}"})
                await manager.update_project(updated)

        await asyncio.gather(read_project(), write_project())
        # Verify state is still consistent
        assert await manager.has_project(project.id)


# ── Edge Case Tests ─────────────────────────────────────────────────────


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    async def test_register_and_remove_all_entity_types(
        self, manager: RuntimeStateManager, project: Project, task: Task,
        execution_session: ExecutionSession, artifact: Artifact, memory_entry: MemoryEntry
    ) -> None:
        """Register and remove all entity types."""
        await manager.register_project(project)
        await manager.register_task(task)
        await manager.register_execution_session(execution_session)
        await manager.register_artifact(artifact)
        await manager.register_memory_entry(memory_entry)
        assert await manager.total_entities() == 5

        await manager.remove_project(project.id)
        await manager.remove_task(task.id)
        await manager.remove_execution_session(execution_session.id)
        await manager.remove_artifact(artifact.id)
        await manager.remove_memory_entry(memory_entry.id)
        assert await manager.is_empty()

    async def test_get_nonexistent_returns_none(
        self, manager: RuntimeStateManager
    ) -> None:
        """Getting a nonexistent entity returns None (not raises)."""
        fake_id = uuid.uuid4()
        assert await manager.get_project(fake_id) is None
        assert await manager.get_task(fake_id) is None
        assert await manager.get_execution_session(fake_id) is None
        assert await manager.get_artifact(fake_id) is None
        assert await manager.get_memory_entry(fake_id) is None

    async def test_has_nonexistent_returns_false(
        self, manager: RuntimeStateManager
    ) -> None:
        """Checking existence of nonexistent entity returns False."""
        fake_id = uuid.uuid4()
        assert await manager.has_project(fake_id) is False
        assert await manager.has_task(fake_id) is False
        assert await manager.has_execution_session(fake_id) is False
        assert await manager.has_artifact(fake_id) is False
        assert await manager.has_memory_entry(fake_id) is False

    async def test_list_returns_copies(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """list_* methods return copies, not internal references."""
        await manager.register_project(project)
        projects = await manager.list_projects()
        # Modifying the returned list should not affect internal state
        projects.clear()
        assert await manager.total_entities() == 1

    async def test_snapshot_restore_preserves_immutability(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """After restore, the snapshot is still immutable."""
        await manager.register_project(project)
        snapshot = await manager.create_snapshot()
        await manager.restore_snapshot(snapshot)
        # Snapshot should still be immutable (frozen model)
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            snapshot.snapshot_id = uuid.uuid4()  # type: ignore[assignment]

    async def test_multiple_snapshots(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Create multiple snapshots at different points in time."""
        s1 = await manager.create_snapshot()
        assert len(s1) == 0

        await manager.register_project(project)
        s2 = await manager.create_snapshot()
        assert len(s2) == 1

        # s1 should still be empty
        assert len(s1) == 0

    async def test_restore_empty_snapshot(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """Restoring an empty snapshot clears all state."""
        await manager.register_project(project)
        snapshot = await manager.create_snapshot()
        # Create a new empty snapshot
        empty_snapshot = await RuntimeStateManager().create_snapshot()
        await manager.restore_snapshot(empty_snapshot)
        assert await manager.is_empty()


# ── Exception Detail Tests ──────────────────────────────────────────────


class TestExceptionDetails:
    """Tests that exceptions carry proper detail information."""

    async def test_duplicate_entity_error_details(
        self, manager: RuntimeStateManager, project: Project
    ) -> None:
        """DuplicateEntityError includes entity details."""
        await manager.register_project(project)
        with pytest.raises(DuplicateEntityError) as exc_info:
            await manager.register_project(project)
        assert exc_info.value.details["entity_type"] == "project"
        assert exc_info.value.details["entity_id"] == str(project.id)

    async def test_entity_not_found_error_details(
        self, manager: RuntimeStateManager
    ) -> None:
        """EntityNotFoundError includes entity details."""
        fake_id = uuid.uuid4()
        with pytest.raises(EntityNotFoundError) as exc_info:
            await manager.get_project_or_raise(fake_id)
        assert exc_info.value.details["entity_type"] == "project"
        assert exc_info.value.details["entity_id"] == str(fake_id)

    async def test_invalid_transition_error_details(
        self, manager: RuntimeStateManager, task: Task
    ) -> None:
        """InvalidTransitionError includes transition details."""
        await manager.register_task(task)
        with pytest.raises(InvalidTransitionError) as exc_info:
            await manager.update_task_status(task.id, TaskStatus.COMPLETED)
        assert exc_info.value.details["current"] == "pending"
        assert exc_info.value.details["target"] == "completed"
        assert exc_info.value.details["entity_type"] == "task"