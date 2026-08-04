"""
Source Model

Represents a knowledge source as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import TimestampedModel


class SourceType(str, Enum):
    """Types of knowledge sources."""
    DOCUMENTATION = "documentation"
    CODE = "code"
    ACADEMIC = "academic"
    EXPERT = "expert"
    COMMUNITY = "community"
    PROPRIETARY = "proprietary"


class SourceStatus(str, Enum):
    """Lifecycle states of a source."""
    REGISTERED = "registered"
    ACTIVE = "active"
    SYNCING = "syncing"
    ERROR = "error"
    INACTIVE = "inactive"
    REMOVED = "removed"


class Source(TimestampedModel):
    """
    A knowledge source (documentation, code repository, academic paper, etc.)
    
    As defined in Knowledge Platform Specification v1.0, Section 8.2.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    type: SourceType = Field(
        description="Source type (documentation, code, academic, expert, community, proprietary)"
    )
    name: str = Field(
        description="Source name"
    )
    description: str = Field(
        description="Source description"
    )
    url: str = Field(
        description="Source URL or location"
    )
    connector_type: str = Field(
        description="Connector type for this source"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source-specific configuration"
    )
    trust_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall trust score (0.0-1.0)"
    )
    authority_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Authority score (0.0-1.0)"
    )
    freshness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Freshness score (0.0-1.0)"
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score (0.0-1.0)"
    )
    historical_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Historical accuracy (0.0-1.0)"
    )
    last_sync_at: Optional[datetime] = Field(
        default=None,
        description="Last synchronization time"
    )
    last_validated_at: Optional[datetime] = Field(
        default=None,
        description="Last validation time"
    )
    status: SourceStatus = Field(
        default=SourceStatus.REGISTERED,
        description="Source status (active, inactive, error)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )