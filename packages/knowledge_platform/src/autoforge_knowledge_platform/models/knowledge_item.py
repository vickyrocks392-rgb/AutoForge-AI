"""
Knowledge Item Model

Represents a single unit of knowledge as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel, TimestampedModel


class KnowledgeItemType(str, Enum):
    """Types of knowledge items."""
    FACT = "fact"
    CONCEPT = "concept"
    PROCEDURE = "procedure"
    OPINION = "opinion"
    EXAMPLE = "example"
    REFERENCE = "reference"
    WARNING = "warning"
    BEST_PRACTICE = "best_practice"


class KnowledgeItemStatus(str, Enum):
    """Lifecycle states of a knowledge item."""
    CREATED = "created"
    INDEXED = "indexed"
    ACTIVE = "active"
    UPDATED = "updated"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class KnowledgeItem(TimestampedModel):
    """
    A single unit of knowledge (fact, claim, concept, procedure, etc.)
    
    As defined in Knowledge Platform Specification v1.0, Section 8.1.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    type: KnowledgeItemType = Field(
        description="Type of knowledge item (fact, concept, procedure, etc.)"
    )
    content: str = Field(
        description="The knowledge content"
    )
    summary: str = Field(
        description="Brief summary of the knowledge"
    )
    domain: str = Field(
        description="Knowledge domain (e.g., 'backend', 'security', 'devops')"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
    source_id: uuid.UUID = Field(
        description="Primary source identifier"
    )
    sources: List[uuid.UUID] = Field(
        default_factory=list,
        description="All source identifiers"
    )
    trust_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Trust score (0.0-1.0)"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )
    validation_status: str = Field(
        default="unvalidated",
        description="Validation status (validated, unvalidated, contradicted)"
    )
    validation_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Validation confidence (0.0-1.0)"
    )
    accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When knowledge was last accessed"
    )
    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times accessed"
    )
    version: str = Field(
        default="1.0",
        description="Knowledge version"
    )
    superseded_by: Optional[uuid.UUID] = Field(
        default=None,
        description="ID of knowledge item that supersedes this (if any)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )
    embeddings: Optional[List[float]] = Field(
        default=None,
        description="Vector embeddings for semantic search"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords for keyword search"
    )
    status: KnowledgeItemStatus = Field(
        default=KnowledgeItemStatus.CREATED,
        description="Current lifecycle status"
    )