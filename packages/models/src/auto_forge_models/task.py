"""
Task model — a unit of work within a project.

A Task represents a single, well-defined unit of work that can be
planned, scheduled, executed, and reviewed. Tasks form a directed
acyclic graph (DAG) via dependency relationships.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from pydantic import Field, field_validator

from auto_forge_models.base import AutoForgeBaseModel, AuditableModel
from auto_forge_models.enums import TaskPriority, TaskStatus


class ResourceRequirements(AutoForgeBaseModel):
    """
    Resource requirements for executing a task.

    Specifies the computational and time resources needed.
    """

    estimated_cpu_cores: float | None = Field(
        default=None,
        ge=0.1,
        le=128.0,
        description="Estimated number of CPU cores required.",
    )
    estimated_memory_mb: int | None = Field(
        default=None,
        ge=64,
        le=1_048_576,
        description="Estimated memory in megabytes required.",
    )
    estimated_duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=86_400,  # 24 hours
        description="Estimated execution duration in seconds.",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=100,
        description="Maximum number of retry attempts on failure.",
    )
    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        le=604_800,  # 7 days
        description="Maximum wall-clock time in seconds before timeout.",
    )


class Task(AuditableModel):
    """
    A unit of work within a project.

    Tasks are the fundamental building blocks of project execution.
    They can depend on other tasks, produce artifacts, and be assigned
    to employees for execution.
    """

    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent Project.",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Short, human-readable title of the task.",
    )
    description: str = Field(
        default="",
        max_length=16384,
        description="Detailed description of the work to be performed.",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current lifecycle status of the task.",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level for scheduling.",
    )
    parent_task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the parent task in a hierarchical decomposition.",
    )
    depends_on: list[uuid.UUID] = Field(
        default_factory=list,
        description="UUIDs of tasks that must complete before this task can start.",
    )
    assigned_to: list[uuid.UUID] = Field(
        default_factory=list,
        description="UUIDs of Employees assigned to execute this task.",
    )
    resources: ResourceRequirements = Field(
        default_factory=ResourceRequirements,
        description="Resource requirements for executing this task.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering the task.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when execution started.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when execution completed.",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Display order within the parent task or project.",
    )

    @field_validator("depends_on")
    @classmethod
    def _validate_no_self_dependency(cls, v: list[uuid.UUID], info: Any) -> list[uuid.UUID]:
        """Ensure a task does not depend on itself."""
        return v