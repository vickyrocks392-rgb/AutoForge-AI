"""Public Interfaces — defines the public API contracts for the Runtime State Manager.

Implements the Public Interfaces from Runtime State Manager Specification v1.0, Section 6 and 31.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Protocol

from autoforge_runtime.models import (
    CheckpointState,
    CheckpointType,
    EntityType,
    ProgressMetrics,
    ProjectState,
    RestoreType,
    StateTransition,
    TaskState,
    TimeRange,
    TransitionResult,
    WorkerState,
    WorkflowState,
)


class StateWriteInterface(Protocol):
    """State Write Interface (Specification Section 6.1)."""

    def create_project(self, project_data: dict[str, Any]) -> uuid.UUID:
        """Create a new project."""
        ...

    def transition_project_state(
        self,
        project_id: uuid.UUID,
        new_status: str,
        metadata: dict[str, Any] | None = None,
    ) -> TransitionResult:
        """Transition project to new status."""
        ...

    def update_task_state(
        self,
        task_id: uuid.UUID,
        new_status: str,
        metadata: dict[str, Any] | None = None,
    ) -> TransitionResult:
        """Update task state."""
        ...

    def create_checkpoint(
        self,
        project_id: uuid.UUID,
        checkpoint_type: CheckpointType,
        label: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        """Create a checkpoint."""
        ...

    def restore_checkpoint(
        self,
        checkpoint_id: uuid.UUID,
        restore_type: RestoreType = RestoreType.FULL,
    ) -> TransitionResult:
        """Restore state from checkpoint."""
        ...


class StateReadInterface(Protocol):
    """State Read Interface (Specification Section 6.2)."""

    def get_project_state(self, project_id: uuid.UUID) -> ProjectState:
        """Get project state."""
        ...

    def get_task_state(self, task_id: uuid.UUID) -> TaskState:
        """Get task state."""
        ...

    def get_worker_state(self, worker_id: uuid.UUID) -> WorkerState:
        """Get worker state."""
        ...

    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> CheckpointState:
        """Get checkpoint."""
        ...


class QueryInterface(Protocol):
    """Query Interface (Specification Section 6.3)."""

    def get_projects_by_status(self, status: str) -> list[ProjectState]:
        """Get projects by status."""
        ...

    def get_tasks_by_project(self, project_id: uuid.UUID) -> list[TaskState]:
        """Get tasks by project."""
        ...

    def get_tasks_by_status(self, status: str) -> list[TaskState]:
        """Get tasks by status."""
        ...

    def get_running_workflows(self) -> list[WorkflowState]:
        """Get all running workflows."""
        ...

    def get_worker_status(self) -> list[WorkerState]:
        """Get all worker states."""
        ...

    def get_execution_progress(self, project_id: uuid.UUID) -> ProgressMetrics:
        """Get execution progress."""
        ...

    def get_runtime_history(
        self,
        entity_type: EntityType,
        entity_id: uuid.UUID,
        time_range: TimeRange | None = None,
    ) -> list[StateTransition]:
        """Get runtime history."""
        ...

    def get_checkpoint_history(self, project_id: uuid.UUID) -> list[CheckpointState]:
        """Get checkpoint history."""
        ...

    def get_failure_history(self, project_id: uuid.UUID | None = None) -> list[Any]:
        """Get failure history."""
        ...


class EventSubscriptionInterface(Protocol):
    """Event Subscription Interface (Specification Section 6.4)."""

    def subscribe_to_state_changes(
        self,
        entity_type: EntityType,
        callback: Callable[[dict[str, Any]], None],
    ) -> uuid.UUID:
        """Subscribe to state changes."""
        ...

    def unsubscribe(self, subscription_id: uuid.UUID) -> bool:
        """Unsubscribe from state changes."""
        ...