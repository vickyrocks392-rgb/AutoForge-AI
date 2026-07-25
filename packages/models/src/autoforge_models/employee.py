"""
Employee model — an AI agent or human participant.

Employees represent the actors in the platform. They can be AI agents
with specific model configurations, or human participants with their
own capabilities and preferences.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from autoforge_models.base import AutoForgeBaseModel, TimestampedModel
from autoforge_models.enums import EmployeeRole, ModelProvider


class ModelConfig(AutoForgeBaseModel):
    """
    Configuration for an AI model used by an employee.

    Specifies which model provider, model name, and parameters
    to use when this employee performs work.
    """

    provider: ModelProvider = Field(
        ...,
        description="The AI model provider.",
    )
    model_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The specific model name/identifier (e.g. 'gpt-4', 'claude-3-opus').",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for the model.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=1_000_000,
        description="Maximum tokens to generate.",
    )
    top_p: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Top-p nucleus sampling parameter.",
    )
    api_base_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Custom API base URL (for local/custom providers).",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific parameters.",
    )


class Employee(TimestampedModel):
    """
    An AI agent or human participant in the platform.

    Employees are the actors that perform work — planning, coding,
    reviewing, testing, and operating. Each employee has a role,
    capabilities, and optionally a model configuration.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Human-readable name of the employee.",
    )
    role: EmployeeRole = Field(
        ...,
        description="Primary role of the employee.",
    )
    is_ai: bool = Field(
        default=True,
        description="Whether this employee is an AI agent (True) or human (False).",
    )
    model: ModelConfig | None = Field(
        default=None,
        description="AI model configuration (required for AI employees, null for humans).",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="List of skills or capabilities this employee possesses.",
    )
    max_concurrent_tasks: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Maximum number of tasks this employee can handle concurrently.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this employee is currently active and available.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )