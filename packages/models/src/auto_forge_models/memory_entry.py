"""
MemoryEntry model — a stored memory item.

Memory entries represent the platform's stored knowledge and experiences.
They are categorised by type (episodic, semantic, procedural) and can be
retrieved, searched, and composed to inform future work.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import MemoryType


class MemoryEntry(TimestampedModel):
    """
    A stored memory item in the platform's memory system.

    Memory entries capture what the platform has learned and experienced.
    They support three memory types:
    - Episodic: specific events or experiences
    - Semantic: facts, concepts, and knowledge
    - Procedural: how to perform tasks and processes
    """

    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the related Project, if applicable.",
    )
    memory_type: MemoryType = Field(
        ...,
        description="The type of memory this entry represents.",
    )
    key: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Unique key or identifier for this memory entry.",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Short title summarising this memory entry.",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=1_048_576,  # 1 MB of text
        description="The full content of the memory entry.",
    )
    summary: str = Field(
        default="",
        max_length=4096,
        description="Optional summary or abstract of the content.",
    )
    embedding: list[float] | None = Field(
        default=None,
        description="Vector embedding of the content for similarity search.",
    )
    source_event_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Event that created this memory entry.",
    )
    source_employee_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Employee that created this memory entry.",
    )
    importance_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score (0.0 to 1.0) for memory prioritisation.",
    )
    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this memory has been accessed.",
    )
    last_accessed_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of last access.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering memory entries.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )