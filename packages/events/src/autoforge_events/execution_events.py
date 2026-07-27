"""
Execution session events for the AutoForge AI platform.

These events capture state changes in an execution session's lifecycle:
start, complete, fail, pause, resume, cancel, and timeout.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_events.base import BaseEvent
from autoforge_events.event_types import EventCategory, EventType


class ExecutionStarted(BaseEvent):
    """
    Emitted when an execution session starts.

    An execution session represents a single run of a task or workflow
    by an AI agent or service.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_STARTED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    agent_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the agent performing the execution.",
    )
    model_profile_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the model profile used for this execution.",
    )
    input_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for this execution session.",
    )
    max_duration_seconds: float | None = Field(
        default=None,
        ge=1.0,
        description="Maximum allowed duration in seconds before timeout.",
    )


class ExecutionCompleted(BaseEvent):
    """
    Emitted when an execution session completes successfully.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_COMPLETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task that was executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    output_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Output data produced by this execution.",
    )
    duration_seconds: float = Field(
        ...,
        ge=0.0,
        description="Actual duration of the execution in seconds.",
    )
    total_cost: float | None = Field(
        default=None,
        ge=0.0,
        description="Total cost in credits incurred by this execution.",
    )
    token_count: int | None = Field(
        default=None,
        ge=0,
        description="Total number of tokens consumed during execution.",
    )
    artifact_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="UUIDs of artifacts produced during this execution.",
    )


class ExecutionFailed(BaseEvent):
    """
    Emitted when an execution session fails with an error.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_FAILED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task that was being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
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
    error_details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context (stack trace, state dump, etc.).",
    )
    recoverable: bool = Field(
        default=False,
        description="Whether the execution can be retried.",
    )
    duration_seconds: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration of the execution before failure.",
    )


class ExecutionPaused(BaseEvent):
    """
    Emitted when an execution session is paused.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_PAUSED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Reason the execution was paused.",
    )
    paused_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who paused the execution.",
    )


class ExecutionResumed(BaseEvent):
    """
    Emitted when a paused execution session is resumed.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_RESUMED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    resumed_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who resumed the execution.",
    )


class ExecutionCancelled(BaseEvent):
    """
    Emitted when an execution session is cancelled before completion.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_CANCELLED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task that was being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Reason the execution was cancelled.",
    )
    cancelled_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who cancelled the execution.",
    )


class ExecutionTimedOut(BaseEvent):
    """
    Emitted when an execution session exceeds its time limit.
    """

    event_type: EventType = Field(
        default=EventType.EXECUTION_TIMED_OUT,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.EXECUTION,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="ExecutionSession",
        description="The type name of the aggregate.",
    )

    # Execution-specific payload
    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the task that was being executed.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this execution belongs to.",
    )
    max_duration_seconds: float = Field(
        ...,
        ge=1.0,
        description="The maximum allowed duration that was exceeded.",
    )
    actual_duration_seconds: float = Field(
        ...,
        ge=0.0,
        description="The actual duration before timeout was triggered.",
    )
    partial_output: dict[str, Any] = Field(
        default_factory=dict,
        description="Any partial output produced before the timeout.",
    )