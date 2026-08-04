"""
Research Brief Model

Represents a structured research brief as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from autoforge_models.base import IdentifiedModel


class ResearchBriefStatus(str, Enum):
    """Lifecycle states of a research brief."""
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class ResearchBrief(IdentifiedModel):
    """
    A structured research brief produced by the Knowledge Platform.
    
    As defined in Knowledge Platform Specification v1.0, Section 8.8.
    """
    
    model_config = ConfigDict(use_enum_values=True)
    
    query_id: uuid.UUID = Field(
        description="Query identifier"
    )
    topic: str = Field(
        description="Research topic"
    )
    executive_summary: str = Field(
        description="Executive summary of findings"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="Key findings from research"
    )
    supporting_evidence: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Supporting evidence with citations"
    )
    conflicting_views: List[str] = Field(
        default_factory=list,
        description="Conflicting information with source attribution"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations based on research"
    )
    knowledge_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps in knowledge"
    )
    sources: List[uuid.UUID] = Field(
        default_factory=list,
        description="Sources consulted"
    )
    citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Citations for all claims"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence (0.0-1.0)"
    )
    trust_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Trust scores for sources"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When brief was created"
    )
    valid_until: datetime = Field(
        description="When brief expires"
    )
    status: ResearchBriefStatus = Field(
        default=ResearchBriefStatus.CREATED,
        description="Current lifecycle status"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata"
    )