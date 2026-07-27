"""
Memory entry events for the AutoForge AI platform.

These events capture state changes in memory entries:
storage, update, deletion, and retrieval.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_events.base import BaseEvent
from autoforge_events.event_types import EventCategory, EventType


class MemoryStored(BaseEvent):
    """
    Emitted when a new memory entry is stored.

    Memory entries represent knowledge that the system has learned
    and can be of various types (episodic, semantic, procedural).
    """

    event_type: EventType = Field(
        default=EventType.MEMORY_STORED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.MEMORY,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="MemoryEntry",
        description="The type name of the aggregate.",
    )

    # Memory-specific payload
    memory_type: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="The type of memory (e.g. 'episodic', 'semantic', 'procedural').",
    )
    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the project this memory is associated with.",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the task this memory is associated with.",
    )
    agent_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the agent that stored this memory.",
    )
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The key or identifier for this memory entry.",
    )
    value: dict[str, Any] = Field(
        ...,
        description="The value or content of the memory entry.",
    )
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score from 0.0 (low) to 1.0 (critical).",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorizing and retrieving this memory.",
    )
    ttl_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Time-to-live in seconds. None means permanent.",
    )


class MemoryUpdated(BaseEvent):
    """
    Emitted when an existing memory entry is updated.

    Memory entries may be updated when new information is learned
    that refines or corrects previous knowledge.
    """

    event_type: EventType = Field(
        default=EventType.MEMORY_UPDATED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.MEMORY,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="MemoryEntry",
        description="The type name of the aggregate.",
    )

    # Memory-specific payload
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The key of the memory entry that was updated.",
    )
    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the project this memory is associated with.",
    )
    updated_fields: list[str] = Field(
        ...,
        min_length=1,
        description="List of field names that were changed.",
    )
    previous_value: dict[str, Any] = Field(
        default_factory=dict,
        description="The previous value before the update.",
    )
    new_value: dict[str, Any] = Field(
        default_factory=dict,
        description="The new value after the update.",
    )
    previous_importance: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The previous importance score.",
    )
    new_importance: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The new importance score.",
    )


class MemoryDeleted(BaseEvent):
    """
    Emitted when a memory entry is deleted from the system.
    """

    event_type: EventType = Field(
        default=EventType.MEMORY_DELETED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.MEMORY,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="MemoryEntry",
        description="The type name of the aggregate.",
    )

    # Memory-specific payload
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The key of the memory entry that was deleted.",
    )
    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the project this memory was associated with.",
    )
    reason: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional reason for deleting the memory entry.",
    )
    deleted_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee who deleted the memory.",
    )


class MemoryRetrieved(BaseEvent):
    """
    Emitted when a memory entry is retrieved (read access).

    This event is useful for auditing and tracking memory access patterns.
    """

    event_type: EventType = Field(
        default=EventType.MEMORY_RETRIEVED,
        description="The specific type of event.",
    )
    event_category: EventCategory = Field(
        default=EventCategory.MEMORY,
        description="The high-level category this event belongs to.",
    )
    aggregate_type: str = Field(
        default="MemoryEntry",
        description="The type name of the aggregate.",
    )

    # Memory-specific payload
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="The key of the memory entry that was retrieved.",
    )
    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the project this memory is associated with.",
    )
    retrieved_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the employee or agent that retrieved the memory.",
    )
    retrieval_context: str | None = Field(
        default=None,
        max_length=1024,
        description="Context or reason for the retrieval.",
    )