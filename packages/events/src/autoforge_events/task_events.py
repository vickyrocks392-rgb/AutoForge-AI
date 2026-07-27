"""
Task lifecycle events for the AutoForge AI platform.

These events capture state changes in a task's lifecycle:
creation, queuing, readiness, execution, completion, failure, etc.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from pydantic import Field

from autoforge_events.base import BaseEvent
from autoforge_events.event_types import EventCategory, EventType


class TaskCreated(BaseEvent):
    """
    Emitted when a new task is created within a project.

    Carries the task's initial definition, priority, and dependencies.
    """

    event_type: EventType = Field(
        default=EventType.TASK_CREATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    task_title: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The title of the task.",
    )
    task_description: str | None = Field(
        default=None,
        max_length=8192,
        description="Optional description of the task.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    parent_task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the parent task, if this is a sub-task.",
    )
    priority: str = Field(
        default="medium",
        pattern=r"^(low|medium|high|critical)$",
        description="Priority level of the task.",
    )
    depends_on: list[uuid.UUID] = Field(
        default_factory=list,
        description="List of task UUIDs that this task depends on.",
    )
    assigned_to: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee assigned to this task.",
    )
    estimated_cost: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated cost in credits for executing this task.",
    )


class TaskUpdated(BaseEvent):
    """
    Emitted when an existing task's metadata is updated.
    """

    event_type: EventType = Field(
        default=EventType.TASK_UPDATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    updated_fields: list[str] = Field(
        ...,
        min_length=1,
        description="List of field names that were changed.",
    )
    previous_values: dict[str, Any] = Field(
        default_factory=dict,
        description="Map of field name to previous value before the update.",
    )
    new_values: dict[str, Any] = Field(
        default_factory=dict,
        description="Map of field name to new value after the update.",
    )


class TaskQueued(BaseEvent):
    """
    Emitted when a task is queued and waiting for scheduling.

    The task has been created but is not yet ready to execute
    (e.g. it may have unmet dependencies).
    """

    event_type: EventType = Field(
        default=EventType.TASK_QUEUED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    queue_position: int | None = Field(
        default=None,
        ge=0,
        description="Position in the queue, if applicable.",
    )
    unmet_dependencies: list[uuid.UUID] = Field(
        default_factory=list,
        description="List of dependency UUIDs that are not yet satisfied.",
    )


class TaskReady(BaseEvent):
    """
    Emitted when all task dependencies are satisfied and the task
    is ready to be scheduled for execution.
    """

    event_type: EventType = Field(
        default=EventType.TASK_READY,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    ready_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the task became ready.",
    )


class TaskStarted(BaseEvent):
    """
    Emitted when a task begins execution.

    The task has been assigned to an agent and execution has started.
    """

    event_type: EventType = Field(
        default=EventType.TASK_STARTED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    started_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who started the task.",
    )
    input_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data provided to the task at start.",
    )


class TaskPaused(BaseEvent):
    """
    Emitted when a task is paused during execution.

    A task may be paused because it is waiting for external input,
    a review, or a manual intervention.
    """

    event_type: EventType = Field(
        default=EventType.TASK_PAUSED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Reason the task was paused.",
    )
    paused_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who paused the task.",
    )


class TaskResumed(BaseEvent):
    """
    Emitted when a paused task is resumed and continues execution.
    """

    event_type: EventType = Field(
        default=EventType.TASK_RESUMED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    resumed_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who resumed the task.",
    )


class TaskCompleted(BaseEvent):
    """
    Emitted when a task completes successfully.

    Carries the output produced by the task and execution metrics.
    """

    event_type: EventType = Field(
        default=EventType.TASK_COMPLETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    output_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Output data produced by the task.",
    )
    actual_cost: float | None = Field(
        default=None,
        ge=0.0,
        description="Actual cost in credits incurred by this task.",
    )
    duration_seconds: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration of task execution in seconds.",
    )
    artifact_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="UUIDs of artifacts produced by this task.",
    )


class TaskFailed(BaseEvent):
    """
    Emitted when a task fails with an error.

    Carries error information and whether the failure is recoverable.
    """

    event_type: EventType = Field(
        default=EventType.TASK_FAILED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    error_code: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Machine-readable error code.",
    )
    error_message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Human-readable error message.",
    )
    recoverable: bool = Field(
        default=False,
        description="Whether the failure is recoverable and the task can be retried.",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this task has been retried.",
    )


class TaskCancelled(BaseEvent):
    """
    Emitted when a task is cancelled before completion.
    """

    event_type: EventType = Field(
        default=EventType.TASK_CANCELLED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Reason the task was cancelled.",
    )
    cancelled_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who cancelled the task.",
    )


class TaskBlocked(BaseEvent):
    """
    Emitted when a task becomes blocked by an unresolved dependency.
    """

    event_type: EventType = Field(
        default=EventType.TASK_BLOCKED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belongs to.",
    )
    blocked_by: list[uuid.UUID] = Field(
        ...,
        min_length=1,
        description="UUIDs of the tasks or resources blocking this task.",
    )
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional description of why the task is blocked.",
    )


class TaskDeleted(BaseEvent):
    """
    Emitted when a task is deleted from the system.
    """

    event_type: EventType = Field(
        default=EventType.TASK_DELETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.TASK,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Task",
        description="The type name of the aggregate.",
    )

    # Task-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this task belonged to.",
    )
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional reason for deleting the task.",
    )