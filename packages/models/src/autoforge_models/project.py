"""
Project model — the top-level container for a software project being built.

A Project represents a complete software development effort. It contains
tasks, artifacts, employees, and all other domain objects that participate
in the project's lifecycle.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from autoforge_models.base import AuditableModel


class Project(AuditableModel):
    """
    A top-level software project within the AutoForge AI platform.

    A Project is the root aggregate that owns all other entities within
    a development effort. It defines the project's goals, constraints,
    and configuration.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Human-readable name of the project.",
    )
    description: str = Field(
        default="",
        max_length=4096,
        description="Detailed description of the project's purpose and goals.",
    )
    version: str = Field(
        default="0.1.0",
        max_length=32,
        description="Current version of the project (semver).",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering the project.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store for project-specific data.",
    )
    is_archived: bool = Field(
        default=False,
        description="Whether the project has been archived (read-only).",
    )