"""
ExecutionSession model — a single run of a task or workflow.

An ExecutionSession represents one attempt to execute a unit of work.
It tracks the lifecycle of that execution, including its status,
timing, and associated resources.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import ExecutionStatus


class ExecutionSession(TimestampedModel):
    """
    A single run of a task or workflow.

    Each execution attempt creates a new session. Sessions track the
    full lifecycle of execution, including timing, assigned resources,
    and final outcome.
    """

    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent Project.",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Task being executed (if single-task session).",
    )
    workflow_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the workflow definition (if multi-task session).",
    )
    status: ExecutionStatus = Field(
        default=ExecutionStatus.PENDING,
        description="Current status of the execution session.",
    )
    assigned_employee_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Employee assigned to execute this session.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when execution started.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when execution completed (success or failure).",
    )
    error_message: str | None = Field(
        default=None,
        max_length=8192,
        description="Error message if the session failed.",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Number of times this session has been retried.",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=100,
        description="Maximum number of retries allowed.",
    )
    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        le=604_800,
        description="Maximum wall-clock time in seconds before timeout.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )