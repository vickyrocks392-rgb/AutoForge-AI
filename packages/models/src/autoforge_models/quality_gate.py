"""
QualityGate model — a quality threshold that must be satisfied.

Quality gates define the criteria that work products must meet before
they can proceed to the next stage. They are the mechanism by which
the platform enforces quality standards and prevents regressions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from autoforge_models.base import TimestampedModel
from autoforge_models.enums import QualityGateStatus


class QualityGate(TimestampedModel):
    """
    A quality threshold that must be satisfied.

    Quality gates are checkpoints that enforce quality standards.
    They define criteria (e.g. test coverage, code style, review approval)
    that must be met before work can proceed. Each gate evaluation
    produces a status and detailed results.
    """

    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent Project.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Human-readable name of this quality gate.",
    )
    description: str = Field(
        default="",
        max_length=2048,
        description="Detailed description of what this gate checks.",
    )
    gate_type: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The type/category of quality gate (e.g. 'test_coverage', 'code_review', 'lint').",
    )
    status: QualityGateStatus = Field(
        default=QualityGateStatus.PENDING,
        description="Current status of the quality gate check.",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this gate is required (must pass) or optional.",
    )
    is_blocking: bool = Field(
        default=True,
        description="Whether a failure of this gate blocks further progress.",
    )
    threshold_value: float | None = Field(
        default=None,
        description="Numerical threshold that must be met (e.g. 80.0 for 80% coverage).",
    )
    actual_value: float | None = Field(
        default=None,
        description="The actual measured value from the latest evaluation.",
    )
    evaluated_by: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Employee or service that performed the evaluation.",
    )
    evaluated_at: datetime | None = Field(
        default=None,
        description="Timestamp of the latest evaluation.",
    )
    results: dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed results from the latest evaluation.",
    )
    failure_reason: str | None = Field(
        default=None,
        max_length=4096,
        description="Reason for failure, if the gate is failing.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering quality gates.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )