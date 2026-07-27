"""
Project lifecycle events for the AutoForge AI platform.

These events capture state changes in a project's lifecycle:
creation, update, archival, and deletion.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_events.base import BaseEvent
from autoforge_events.event_types import EventCategory, EventType


class ProjectCreated(BaseEvent):
    """
    Emitted when a new project is created.

    Carries the initial project configuration and metadata.
    """

    event_type: EventType = Field(
        default=EventType.PROJECT_CREATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.PROJECT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Project",
        description="The type name of the aggregate.",
    )

    # Project-specific payload
    project_name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The name of the project.",
    )
    project_description: str | None = Field(
        default=None,
        max_length=4096,
        description="Optional description of the project.",
    )
    owner_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who created the project.",
    )
    initial_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial project configuration key-value pairs.",
    )


class ProjectUpdated(BaseEvent):
    """
    Emitted when an existing project's metadata or configuration is updated.
    """

    event_type: EventType = Field(
        default=EventType.PROJECT_UPDATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.PROJECT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Project",
        description="The type name of the aggregate.",
    )

    # Project-specific payload
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


class ProjectArchived(BaseEvent):
    """
    Emitted when a project is archived (soft-deleted).

    An archived project is hidden from normal views but can be restored.
    """

    event_type: EventType = Field(
        default=EventType.PROJECT_ARCHIVED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.PROJECT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Project",
        description="The type name of the aggregate.",
    )

    # Project-specific payload
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional reason for archiving the project.",
    )
    archived_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who archived the project.",
    )


class ProjectDeleted(BaseEvent):
    """
    Emitted when a project is permanently deleted.

    This is a destructive action — the project and all associated
    data are removed from the system.
    """

    event_type: EventType = Field(
        default=EventType.PROJECT_DELETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.PROJECT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Project",
        description="The type name of the aggregate.",
    )

    # Project-specific payload
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional reason for deleting the project.",
    )
    deleted_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who deleted the project.",
    )
    task_count: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that were associated with this project.",
    )