"""
Base model classes for the AutoForge AI platform.

Provides a hierarchy of reusable base classes that all domain models inherit from:
- AutoForgeBaseModel: Root base with common serialization/validation plumbing.
- IdentifiedModel: Adds a UUID primary key.
- TimestampedModel: Adds created_at / updated_at timestamps.
- AuditableModel: Adds created_by / updated_by audit fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _utc_now() -> datetime:
    """Return the current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


def _new_uuid() -> uuid.UUID:
    """Return a new UUID v4."""
    return uuid.uuid4()


class AutoForgeBaseModel(BaseModel):
    """
    Root base model for all AutoForge AI domain models.

    Provides:
    - Strict validation (forbid extra fields by default).
    - Population by field name (not alias).
    - JSON serialization with UUID and datetime support.
    - Frozen by default (immutable after construction).
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,
        use_enum_values=False,
        json_encoders={
            uuid.UUID: str,
            datetime: lambda dt: dt.isoformat(),
        },
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return self.model_dump(mode="python")

    def to_json(self, **kwargs: Any) -> str:
        """Serialize to a JSON string."""
        return self.model_dump_json(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AutoForgeBaseModel:
        """Deserialize from a plain dictionary."""
        return cls.model_validate(data)


class IdentifiedModel(AutoForgeBaseModel):
    """
    Base model with a UUID primary key.

    Every aggregate root in the platform has a unique identity.
    """

    id: uuid.UUID = Field(
        default_factory=_new_uuid,
        description="Unique identifier for this entity.",
    )


class TimestampedModel(IdentifiedModel):
    """
    Base model with identity and automatic timestamps.

    Tracks when the record was created and last updated.
    """

    created_at: datetime = Field(
        default_factory=_utc_now,
        description="Timestamp when this record was created.",
    )
    updated_at: datetime = Field(
        default_factory=_utc_now,
        description="Timestamp when this record was last updated.",
    )


class AuditableModel(TimestampedModel):
    """
    Base model with identity, timestamps, and audit fields.

    Tracks which employee created and last modified the record.
    """

    created_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Employee who created this record.",
    )
    updated_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Employee who last updated this record.",
    )