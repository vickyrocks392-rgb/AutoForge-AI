"""
Citation Model

Represents a citation linking a knowledge item to its source as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import TimestampedModel


class CitationType(str, Enum):
    """Types of citations."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    REFERENCE = "reference"


class CitationFormat(str, Enum):
    """Citation format standards."""
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CODE = "code"
    INTERNAL = "internal"


class Citation(TimestampedModel):
    """
    A citation linking a knowledge item to its source.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.3.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    knowledge_item_id: uuid.UUID = Field(
        description="Knowledge item identifier"
    )
    source_id: uuid.UUID = Field(
        description="Source identifier"
    )
    type: CitationType = Field(
        description="Citation type (direct, indirect, reference)"
    )
    location: str = Field(
        description="Location in source (URL, page, section, line numbers)"
    )
    excerpt: str = Field(
        description="Excerpt from source"
    )
    context: str = Field(
        description="Context around excerpt"
    )
    format: CitationFormat = Field(
        description="Citation format (academic, technical, code, internal)"
    )
    formatted_citation: str = Field(
        description="Formatted citation string"
    )
    accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When source was accessed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )