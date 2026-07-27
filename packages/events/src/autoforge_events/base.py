"""
Base event model for the AutoForge AI platform.

Defines the canonical ``BaseEvent`` that every domain event inherits from.
Events are **immutable** records of something that happened in the system.
They carry no behaviour, no handlers, and no publishing logic — only data.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from autoforge_events.event_types import EventCategory, EventType


def _utc_now() -> datetime:
    """Return the current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


def _new_uuid() -> uuid.UUID:
    """Return a new UUID v4."""
    return uuid.uuid4()


class BaseEvent(BaseModel):
    """
    Immutable base event for all AutoForge AI domain events.

    Every event in the system is a frozen (immutable) record that captures
    something that happened at a point in time. Events are the universal
    language of the platform — they are produced by subsystems and consumed
    by other subsystems via the Event Bus (not included in this package).

    Fields
    ------
    event_id : UUID
        Globally unique identifier for this event instance.
    event_type : EventType
        The specific type of event (e.g. ``TaskStarted``, ``ProjectCreated``).
    event_category : EventCategory
        The high-level category this event belongs to (e.g. ``PROJECT``, ``TASK``).
    occurred_at : datetime
        UTC timestamp of when the event occurred.
    correlation_id : UUID | None
        Identifier for correlating related events across subsystems.
        All events that are part of the same logical operation share the
        same correlation ID.
    causation_id : UUID | None
        Identifier of the event that *caused* this event. This forms a
        causation chain that can be traced for debugging and audit.
    aggregate_id : UUID
        The ID of the domain aggregate this event relates to
        (e.g. a Project ID, Task ID, Execution ID).
    aggregate_type : str
        The type name of the aggregate (e.g. ``"Project"``, ``"Task"``).
    version : int
        Schema version for forward/backward compatibility.
    metadata : dict[str, Any]
        Extensible key-value store for additional context.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,
        use_enum_values=False,
    )

    # ------------------------------------------------------------------
    # Core event identity
    # ------------------------------------------------------------------
    event_id: uuid.UUID = Field(
        default_factory=_new_uuid,
        description="Globally unique identifier for this event instance.",
    )
    event_type: EventType = Field(
        ...,
        description="The specific type of event (e.g. TaskStarted, ProjectCreated).",
    )
    event_category: EventCategory = Field(
        ...,
        description="The high-level category this event belongs to.",
    )

    # ------------------------------------------------------------------
    # Temporal
    # ------------------------------------------------------------------
    occurred_at: datetime = Field(
        default_factory=_utc_now,
        description="UTC timestamp of when the event occurred.",
    )

    # ------------------------------------------------------------------
    # Correlation / causation chain
    # ------------------------------------------------------------------
    correlation_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Identifier for correlating related events across subsystems. "
            "All events that are part of the same logical operation share "
            "the same correlation ID."
        ),
    )
    causation_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Identifier of the event that caused this event. "
            "This forms a causation chain for debugging and audit."
        ),
    )

    # ------------------------------------------------------------------
    # Aggregate reference
    # ------------------------------------------------------------------
    aggregate_id: uuid.UUID = Field(
        ...,
        description="The ID of the domain aggregate this event relates to.",
    )
    aggregate_type: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The type name of the aggregate (e.g. 'Project', 'Task').",
    )

    # ------------------------------------------------------------------
    # Schema versioning
    # ------------------------------------------------------------------
    version: int = Field(
        default=1,
        ge=1,
        description="Schema version for forward/backward compatibility.",
    )

    # ------------------------------------------------------------------
    # Extensible metadata
    # ------------------------------------------------------------------
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible key-value store for additional context.",
    )

    # ------------------------------------------------------------------
    # Class-level constants
    # ------------------------------------------------------------------
    _event_category: ClassVar[EventCategory]
    """Subclasses must set this to the appropriate category."""

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("occurred_at")
    @classmethod
    def _ensure_utc(cls, v: datetime) -> datetime:
        """Ensure the timestamp is timezone-aware and in UTC."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary (Python types)."""
        return self.model_dump(mode="python")

    def to_json(self, **kwargs: Any) -> str:
        """Serialize to a JSON string."""
        return self.model_dump_json(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseEvent:
        """Deserialize from a plain dictionary."""
        return cls.model_validate(data)