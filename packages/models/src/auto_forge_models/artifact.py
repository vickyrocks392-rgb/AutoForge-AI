"""
Artifact model — a file or data output produced during execution.

Artifacts represent any output produced by a task or execution session.
They can be source code, documentation, test results, configuration files,
or any other deliverable.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import ArtifactType


class Artifact(TimestampedModel):
    """
    A file or data output produced during execution.

    Artifacts are the tangible outputs of the platform. They are produced
    by tasks, reviewed by employees, and stored for later use.
    """

    project_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent Project.",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the Task that produced this artifact.",
    )
    execution_session_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the ExecutionSession that produced this artifact.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Human-readable name of the artifact.",
    )
    artifact_type: ArtifactType = Field(
        ...,
        description="Type or category of the artifact.",
    )
    file_path: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Relative or absolute path to the artifact file.",
    )
    mime_type: str = Field(
        default="application/octet-stream",
        max_length=128,
        description="MIME type of the artifact content.",
    )
    size_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Size of the artifact in bytes.",
    )
    checksum: str | None = Field(
        default=None,
        max_length=128,
        description="Content hash (e.g. SHA-256) for integrity verification.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering the artifact.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )