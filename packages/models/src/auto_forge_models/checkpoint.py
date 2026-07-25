"""
Checkpoint model — a snapshot of execution state for resumability.

Checkpoints capture the full state of an execution session at a point in time,
enabling pause/resume and failure recovery workflows.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import CheckpointType


class Checkpoint(TimestampedModel):
    """
    A snapshot of execution state for resumability.

    Checkpoints allow the platform to pause and resume execution sessions,
    recover from failures, and provide milestone-based progress tracking.
    """

    execution_session_id: uuid.UUID = Field(
        ...,
        description="UUID of the ExecutionSession this checkpoint belongs to.",
    )
    checkpoint_type: CheckpointType = Field(
        ...,
        description="The type or trigger for this checkpoint.",
    )
    label: str = Field(
        default="",
        max_length=256,
        description="Optional human-readable label for this checkpoint.",
    )
    state_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialised execution state at the time of the checkpoint.",
    )
    artifact_snapshots: list[uuid.UUID] = Field(
        default_factory=list,
        description="UUIDs of artifacts captured in this checkpoint.",
    )
    task_states: dict[uuid.UUID, str] = Field(
        default_factory=dict,
        description="Mapping of task UUIDs to their status strings at checkpoint time.",
    )
    size_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Total size of the checkpoint data in bytes.",
    )
    is_recovery_point: bool = Field(
        default=False,
        description="Whether this checkpoint is designated as a recovery point.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )