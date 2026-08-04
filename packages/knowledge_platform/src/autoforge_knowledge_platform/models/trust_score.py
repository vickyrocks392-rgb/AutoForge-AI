"""
Trust Score Model

Represents a trust score for a source or knowledge item as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class TrustTargetType(str, Enum):
    """Types of trust score targets."""
    SOURCE = "source"
    KNOWLEDGE_ITEM = "knowledgeItem"


class TrustFactor(str, Enum):
    """Factors contributing to trust score."""
    SOURCE_AUTHORITY = "sourceAuthority"
    HISTORICAL_ACCURACY = "historicalAccuracy"
    COMMUNITY_VALIDATION = "communityValidation"
    RECENCY = "recency"
    CROSS_REFERENCE_COUNT = "crossReferenceCount"


class TrustScore(IdentifiedModel):
    """
    A trust score for a source or knowledge item.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.5.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    target_id: uuid.UUID = Field(
        description="Source or knowledge item identifier"
    )
    target_type: TrustTargetType = Field(
        description="Target type (source, knowledgeItem)"
    )
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall trust score (0.0-1.0)"
    )
    factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Trust score factors and weights"
    )
    historical_scores: List[float] = Field(
        default_factory=list,
        description="Historical trust scores"
    )
    calculated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When score was calculated"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When score expires"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )