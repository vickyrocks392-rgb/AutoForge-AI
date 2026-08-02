"""Query Engine — provides rich query APIs for runtime state.

Implements the Query Engine from Runtime State Manager Specification v1.0, Section 7.5 and 20.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_runtime.exceptions import EntityNotFoundError
from autoforge_runtime.models import (
    CheckpointState,
    EngineeringLoopState,
    EntityType,
    FailureRecord,
    ProgressMetrics,
    ProjectState,
    StateModel,
    StateTransition,
    TaskState,
    TimeRange,
    WorkerState,
    WorkflowState,
)
from autoforge_runtime.persistence import PersistenceLayer


class QueryParser:
    """Parses and validates query requests."""

    def parse_filters(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Parse and validate query filters."""
        return dict(filters)


class FilterEngine:
    """Filters state by criteria."""

    def filter_by_status(self, states: list[StateModel], status: str) -> list[StateModel]:
        """Filter states by status."""
        return [s for s in states if getattr(s, "status", None) is not None and str(getattr(s, "status", "")) == status]

    def filter_by_project(self, states: list[StateModel], project_id: uuid.UUID) -> list[StateModel]:
        """Filter states by project."""
        return [s for s in states if getattr(s, "project_id", None) == project_id]

    def filter_by_time_range(self, states: list[StateModel], time_range: TimeRange) -> list[StateModel]:
        """Filter states by time range."""
        result = states
        if time_range.start:
            result = [s for s in result if getattr(s, "created_at", None) and s.created_at >= time_range.start]
        if time_range.end:
            result = [s for s in result if getattr(s, "created_at", None) and s.created_at <= time_range.end]
        return result


class AggregationEngine:
    """Aggregates state metrics and statistics."""

    def count_by_status(self, states: list[StateModel]) -> dict[str, int]:
        """Count states by status."""
        counts: dict[str, int] = {}
        for s in states:
            status = str(getattr(s, "status", "unknown"))
            counts[status] = counts.get(status, 0) + 1
        return counts

    def compute_progress(self, tasks: list[TaskState]) -> ProgressMetrics:
        """Compute progress metrics from task states."""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "completed")
        running = sum(1 for t in tasks if t.status == "running")
        failed = sum(1 for t in tasks if t.status == "failed")
        blocked = sum(1 for t in tasks if t.status == "blocked")
        pending = sum(1 for t in tasks if t.status == "pending")

        progress = (completed / total * 100.0) if total > 0 else 0.0

        project_id = tasks[0].project_id if tasks else uuid.uuid4()

        return ProgressMetrics(
            project_id=project_id,
            total_tasks=total,
            completed_tasks=completed,
            running_tasks=running,
            failed_tasks=failed,
            blocked_tasks=blocked,
            pending_tasks=pending,
            progress_percentage=progress,
            estimated_cost=sum(t.estimated_cost for t in tasks),
            actual_cost=sum(t.actual_cost for t in tasks),
        )


class QueryEngine:
    """Provides rich query APIs for runtime state.

    Implements the Query Engine from Specification Section 7.5.
    """

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the query engine."""
        self._persistence = persistence
        self.parser = QueryParser()
        self.filter = FilterEngine()
        self.aggregation = AggregationEngine()

    def get_project_state(self, project_id: uuid.UUID) -> ProjectState:
        """Get project state by ID."""
        state = self._persistence.read_state(EntityType.PROJECT, project_id)
        if not isinstance(state, ProjectState):
            raise EntityNotFoundError(
                f"Project with ID {project_id} not found",
                details={"entity_id": str(project_id), "entity_type": "project"},
            )
        return state

    def get_task_state(self, task_id: uuid.UUID) -> TaskState:
        """Get task state by ID."""
        state = self._persistence.read_state(EntityType.TASK, task_id)
        if not isinstance(state, TaskState):
            raise EntityNotFoundError(
                f"Task with ID {task_id} not found",
                details={"entity_id": str(task_id), "entity_type": "task"},
            )
        return state

    def get_worker_state(self, worker_id: uuid.UUID) -> WorkerState:
        """Get worker state by ID."""
        state = self._persistence.read_state(EntityType.WORKER, worker_id)
        if not isinstance(state, WorkerState):
            raise EntityNotFoundError(
                f"Worker with ID {worker_id} not found",
                details={"entity_id": str(worker_id), "entity_type": "worker"},
            )
        return state

    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> CheckpointState:
        """Get checkpoint by ID."""
        state = self._persistence.read_state(EntityType.CHECKPOINT, checkpoint_id)
        if not isinstance(state, CheckpointState):
            raise EntityNotFoundError(
                f"Checkpoint with ID {checkpoint_id} not found",
                details={"entity_id": str(checkpoint_id), "entity_type": "checkpoint"},
            )
        return state

    def get_projects_by_status(self, status: str) -> list[ProjectState]:
        """Get projects by status."""
        states = self._persistence.read_all(EntityType.PROJECT)
        return [s for s in states if isinstance(s, ProjectState) and s.status.value == status]

    def get_tasks_by_project(self, project_id: uuid.UUID) -> list[TaskState]:
        """Get tasks by project."""
        states = self._persistence.read_all(EntityType.TASK)
        return [s for s in states if isinstance(s, TaskState) and s.project_id == project_id]

    def get_tasks_by_status(self, status: str) -> list[TaskState]:
        """Get tasks by status."""
        states = self._persistence.read_all(EntityType.TASK)
        return [s for s in states if isinstance(s, TaskState) and s.status == status]

    def get_running_workflows(self) -> list[WorkflowState]:
        """Get all running workflows."""
        states = self._persistence.read_all(EntityType.WORKFLOW)
        return [s for s in states if isinstance(s, WorkflowState) and s.status.value == "running"]

    def get_worker_status(self) -> list[WorkerState]:
        """Get all worker states."""
        states = self._persistence.read_all(EntityType.WORKER)
        return [s for s in states if isinstance(s, WorkerState)]

    def get_execution_progress(self, project_id: uuid.UUID) -> ProgressMetrics:
        """Get execution progress for a project."""
        tasks = self.get_tasks_by_project(project_id)
        return self.aggregation.compute_progress(tasks)

    def get_runtime_history(
        self,
        entity_type: EntityType,
        entity_id: uuid.UUID,
        time_range: TimeRange | None = None,
    ) -> list[StateTransition]:
        """Get runtime history for an entity."""
        transitions = self._persistence.history.read_by_entity(entity_type, entity_id)
        if time_range:
            if time_range.start:
                transitions = [t for t in transitions if t.timestamp >= time_range.start]
            if time_range.end:
                transitions = [t for t in transitions if t.timestamp <= time_range.end]
        return transitions

    def get_checkpoint_history(self, project_id: uuid.UUID) -> list[CheckpointState]:
        """Get checkpoint history for a project."""
        states = self._persistence.read_all(EntityType.CHECKPOINT)
        return [s for s in states if isinstance(s, CheckpointState) and s.project_id == project_id]

    def get_failure_history(self, project_id: uuid.UUID | None = None) -> list[FailureRecord]:
        """Get failure history."""
        failures: list[FailureRecord] = []
        states = self._persistence.read_all(EntityType.PROJECT)
        for s in states:
            if isinstance(s, ProjectState):
                if project_id is None or s.project_id == project_id:
                    failures.extend(s.failure_history)
        return failures

    def get_loop_history(self, project_id: uuid.UUID) -> list[EngineeringLoopState]:
        """Get engineering loop history for a project."""
        states = self._persistence.read_all(EntityType.LOOP)
        return [s for s in states if isinstance(s, EngineeringLoopState) and s.project_id == project_id]