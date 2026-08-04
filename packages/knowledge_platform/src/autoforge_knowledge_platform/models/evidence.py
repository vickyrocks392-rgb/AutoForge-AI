"""
Evidence Model

Represents evidence supporting a knowledge claim as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class EvidenceType(str, Enum):
    """Types of evidence."""
    SOURCE = "source"
    EXPERIMENT = "experiment"
    OBSERVATION = "observation"
    EXPERT = "expert"


class EvidenceStrength(str, Enum):
    """Strength of evidence."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class Evidence(IdentifiedModel):
    """
    Evidence supporting a knowledge claim.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.4.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    knowledge_item_id: uuid.UUID = Field(
        description="Knowledge item identifier"
    )
    type: EvidenceType = Field(
        description="Evidence type (source, experiment, observation, expert)"
    )
    description: str = Field(
        description="Evidence description"
    )
    sources: List[uuid.UUID] = Field(
        default_factory=list,
        description="Supporting sources"
    )
    strength: EvidenceStrength = Field(
        description="Evidence strength (strong, moderate, weak)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in evidence (0.0-1.0)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When evidence was created"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )