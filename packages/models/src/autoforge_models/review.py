"""
Review model — a quality review of an artifact or task.

Reviews are the mechanism by which the platform ensures quality.
They can be applied to artifacts, tasks, or any other work product.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_models.base import TimestampedModel
from autoforge_models.enums import ReviewStatus


class Review(TimestampedModel):
    """
    A quality review of an artifact or task.

    Reviews capture the evaluation of work products against quality
    standards. They include feedback, ratings, and a final disposition.
    """

    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent Project.",
    )
    artifact_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Artifact being reviewed (if reviewing an artifact).",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Task being reviewed (if reviewing a task).",
    )
    reviewer_id: uuid.UUID = Field(
        ...,
        description="UUID of the Employee performing the review.",
    )
    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING,
        description="Current status of the review.",
    )
    score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Numerical score (0-100) assigned by the reviewer.",
    )
    comments: str = Field(
        default="",
        max_length=32768,
        description="Detailed review comments and feedback.",
    )
    checklist_results: dict[str, bool] = Field(
        default_factory=dict,
        description="Results of a review checklist (item name -> passed).",
    )
    requested_changes: list[str] = Field(
        default_factory=list,
        description="List of specific changes requested by the reviewer.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when the review was started.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when the review was completed.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )