"""
Retrieval Result Model

Represents a result from a knowledge retrieval operation as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class RetrievalStrategy(str, Enum):
    """Retrieval strategies."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    MULTI_SOURCE = "multi_source"


class RetrievalResultStatus(str, Enum):
    """Lifecycle states of a retrieval result."""
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    CACHED = "cached"


class RetrievalResult(IdentifiedModel):
    """
    A result from a knowledge retrieval operation.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.7.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    query_id: uuid.UUID = Field(
        description="Query identifier"
    )
    knowledge_items: List[uuid.UUID] = Field(
        default_factory=list,
        description="Retrieved knowledge items"
    )
    rankings: List[float] = Field(
        default_factory=list,
        description="Relevance scores for each item"
    )
    sources: List[uuid.UUID] = Field(
        default_factory=list,
        description="Sources consulted"
    )
    strategy: RetrievalStrategy = Field(
        description="Retrieval strategy used"
    )
    retrieval_time: float = Field(
        description="Time taken to retrieve (in seconds)"
    )
    result_count: int = Field(
        description="Number of results"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence (0.0-1.0)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When retrieval was performed"
    )
    status: RetrievalResultStatus = Field(
        default=RetrievalResultStatus.CREATED,
        description="Current lifecycle status"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )