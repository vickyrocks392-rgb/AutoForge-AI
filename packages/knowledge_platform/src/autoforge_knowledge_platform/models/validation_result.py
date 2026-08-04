"""
Validation Result Model

Represents the result of a knowledge validation as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class ValidationResult(IdentifiedModel):
    """
    A result from a knowledge validation operation.
    
    As defined in Knowledge Platform Specification v1.0, Section 6.3.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    claim: str = Field(
        description="The knowledge claim that was validated"
    )
    valid: bool = Field(
        default=False,
        description="Whether the claim is valid"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in validation (0.0-1.0)"
    )
    supporting_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sources that support the claim"
    )
    contradicting_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sources that contradict the claim"
    )
    consensus: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consensus level across sources (0.0-1.0)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When validation was performed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )