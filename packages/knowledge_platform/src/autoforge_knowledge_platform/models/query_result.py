"""
Query Result Model

Represents the result of a knowledge query as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class QueryResult(IdentifiedModel):
    """
    A result from a knowledge query operation.
    
    As defined in Knowledge Platform Specification v1.0, Section 6.2.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    query: str = Field(
        description="The original query"
    )
    results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of knowledge items matching the query"
    )
    total_results: int = Field(
        default=0,
        ge=0,
        description="Total number of matching results"
    )
    sources: List[uuid.UUID] = Field(
        default_factory=list,
        description="Sources consulted"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in results (0.0-1.0)"
    )
    citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Citations for results"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When query was performed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )