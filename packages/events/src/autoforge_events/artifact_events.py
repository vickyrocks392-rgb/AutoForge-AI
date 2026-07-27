"""
Artifact lifecycle events for the AutoForge AI platform.

These events capture state changes in an artifact's lifecycle:
creation, update, and deletion.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_events.base import BaseEvent
from autoforge_events.event_types import EventCategory, EventType


class ArtifactCreated(BaseEvent):
    """
    Emitted when a new artifact is produced.

    An artifact is any output produced during execution — code, docs,
    specs, test results, data files, etc.
    """

    event_type: EventType = Field(
        default=EventType.ARTIFACT_CREATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.ARTIFACT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Artifact",
        description="The type name of the aggregate.",
    )

    # Artifact-specific payload
    artifact_name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The name of the artifact.",
    )
    artifact_type: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The type of artifact (e.g. 'code', 'spec', 'doc', 'test').",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this artifact belongs to.",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the task that produced this artifact.",
    )
    execution_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the execution session that produced this artifact.",
    )
    file_path: str | None = Field(
        default=None,
        max_length=1024,
        description="Relative file path of the artifact in the workspace.",
    )
    mime_type: str | None = Field(
        default=None,
        max_length=128,
        description="MIME type of the artifact content.",
    )
    size_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Size of the artifact in bytes.",
    )
    content_hash: str | None = Field(
        default=None,
        max_length=128,
        description="Hash of the artifact content (e.g. SHA-256).",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags associated with this artifact.",
    )


class ArtifactUpdated(BaseEvent):
    """
    Emitted when an existing artifact is updated.

    Artifacts may be updated when new versions are produced or
    when metadata is modified.
    """

    event_type: EventType = Field(
        default=EventType.ARTIFACT_UPDATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.ARTIFACT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Artifact",
        description="The type name of the aggregate.",
    )

    # Artifact-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this artifact belongs to.",
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
    new_content_hash: str | None = Field(
        default=None,
        max_length=128,
        description="Hash of the updated artifact content.",
    )


class ArtifactDeleted(BaseEvent):
    """
    Emitted when an artifact is deleted from the system.
    """

    event_type: EventType = Field(
        default=EventType.ARTIFACT_DELETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.ARTIFACT,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="Artifact",
        description="The type name of the aggregate.",
    )

    # Artifact-specific payload
    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the project this artifact belonged to.",
    )
    artifact_name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The name of the deleted artifact.",
    )
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional reason for deleting the artifact.",
    )
    deleted_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who deleted the artifact.",
    )