"""
ModelProfile model — configuration for an AI model provider.

ModelProfiles define how the platform connects to and interacts with
various AI model providers. They encapsulate provider-specific settings
such as API endpoints, authentication, and model parameters.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import ModelProvider


class ModelProfile(TimestampedModel):
    """
    Configuration for an AI model provider.

    A ModelProfile defines the connection details and default parameters
    for interacting with a specific AI model provider. Multiple profiles
    can exist for the same provider (e.g. different API keys or endpoints).
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Human-readable name for this profile.",
    )
    provider: ModelProvider = Field(
        ...,
        description="The AI model provider.",
    )
    model_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The specific model name/identifier.",
    )
    api_base_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Base URL for the provider's API.",
    )
    api_key_identifier: str | None = Field(
        default=None,
        max_length=256,
        description="Identifier for the API key (stored securely elsewhere, not in this model).",
    )
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default sampling temperature.",
    )
    default_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=1_000_000,
        description="Default maximum tokens to generate.",
    )
    max_context_length: int = Field(
        default=128_000,
        ge=1,
        le=10_000_000,
        description="Maximum context length supported by this model.",
    )
    supports_streaming: bool = Field(
        default=True,
        description="Whether the provider supports streaming responses.",
    )
    supports_functions: bool = Field(
        default=True,
        description="Whether the provider supports function/tool calling.",
    )
    cost_per_input_token: float | None = Field(
        default=None,
        ge=0.0,
        description="Cost per input token (in USD).",
    )
    cost_per_output_token: float | None = Field(
        default=None,
        ge=0.0,
        description="Cost per output token (in USD).",
    )
    rate_limit_requests_per_minute: int | None = Field(
        default=None,
        ge=1,
        description="Rate limit in requests per minute.",
    )
    rate_limit_tokens_per_minute: int | None = Field(
        default=None,
        ge=1,
        description="Rate limit in tokens per minute.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this profile is active and can be used.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering profiles.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )