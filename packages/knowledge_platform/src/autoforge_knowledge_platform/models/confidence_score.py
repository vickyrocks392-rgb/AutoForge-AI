"""
Confidence Score Model

Represents a confidence score for a knowledge retrieval or validation as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class ConfidenceTargetType(str, Enum):
    """Types of confidence score targets."""
    RETRIEVAL = "retrieval"
    VALIDATION = "validation"


class ConfidenceScore(IdentifiedModel):
    """
    A confidence score for a knowledge retrieval or validation.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.6.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    target_id: uuid.UUID = Field(
        description="Retrieval or validation identifier"
    )
    target_type: ConfidenceTargetType = Field(
        description="Target type (retrieval, validation)"
    )
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0-1.0)"
    )
    factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence factors and weights"
    )
    calculated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When score was calculated"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )