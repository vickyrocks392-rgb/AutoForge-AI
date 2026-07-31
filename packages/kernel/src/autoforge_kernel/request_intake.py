"""
Request Intake Module

Responsible for accepting, validating, and normalizing incoming requests.
This module implements the Request Intake component of the Kernel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_models.project import Project
from autoforge_models.task import Task

from autoforge_events.base import BaseEvent as DomainBaseEvent
from autoforge_events.event_types import EventCategory, EventType

from autoforge_kernel.interfaces import (
    Request,
    RequestValidator,
    RequestNormalizer,
    ProjectInitializer,
    IdentifierGenerator,
    IntentAnalysisResult,
    EventBus,
)
from autoforge_kernel.event_utils import publish_event, make_timestamp


class DefaultRequestValidator(RequestValidator):
    """
    Default implementation of request validation.

    Validates request completeness, clarity, and feasibility.
    """

    async def validate(self, request: Request) -> tuple[bool, list[str]]:
        """
        Validate a request.

        Args:
            request: The request to validate.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate request text
        if not request.request_text or len(request.request_text.strip()) == 0:
            errors.append("Request text cannot be empty")

        if len(request.request_text) > 10000:
            errors.append("Request text exceeds maximum length of 10000 characters")

        # Validate context
        if not isinstance(request.context, dict):
            errors.append("Context must be a dictionary")

        # Validate configuration
        if not isinstance(request.configuration, dict):
            errors.append("Configuration must be a dictionary")

        # Validate metadata
        if not isinstance(request.metadata, dict):
            errors.append("Metadata must be a dictionary")

        return len(errors) == 0, errors


class DefaultRequestNormalizer(RequestNormalizer):
    """
    Default implementation of request normalization.

    Transforms diverse request formats into canonical internal representation.
    """

    async def normalize(self, request: Request) -> Request:
        """
        Normalize a request to canonical format.

        Args:
            request: The request to normalize.

        Returns:
            Normalized request.
        """
        # Normalize request text (strip whitespace, normalize line endings)
        normalized_text = request.request_text.strip()
        normalized_text = normalized_text.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize context (ensure all keys are lowercase)
        normalized_context = {k.lower(): v for k, v in request.context.items()}

        # Normalize configuration (ensure all keys are lowercase)
        normalized_config = {k.lower(): v for k, v in request.configuration.items()}

        # Normalize metadata (ensure all keys are lowercase)
        normalized_metadata = {k.lower(): v for k, v in request.metadata.items()}

        # Create normalized request
        normalized_request = Request(
            user_id=request.user_id,
            request_text=normalized_text,
            context=normalized_context,
            configuration=normalized_config,
            metadata=normalized_metadata,
        )

        return normalized_request


class DefaultProjectInitializer(ProjectInitializer):
    """
    Default implementation of project initialization.

    Creates project records and initializes state.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
    ):
        """
        Initialize the project initializer.

        Args:
            event_bus: Event bus for publishing events.
        """
        self.event_bus = event_bus

    async def initialize(self, request: Request) -> Project:
        """
        Initialize a new project from a request.

        Args:
            request: The request to initialize from.

        Returns:
            Initialized project.
        """
        # Create project from request
        project = Project(
            name=self._extract_project_name(request),
            description=request.request_text,
            version="0.1.0",
            tags=self._extract_tags(request),
            metadata={
                "user_id": str(request.user_id) if request.user_id else None,
                "configuration": request.configuration,
                "original_request": request.request_text,
            },
        )

        # Publish project.created event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_CREATED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project.id,
            aggregate_type="Project",
            metadata={
                "project_name": project.name,
                "request_text": request.request_text[:100],
            },
        )

        return project

    def _extract_project_name(self, request: Request) -> str:
        """
        Extract a project name from the request.

        Args:
            request: The request.

        Returns:
            Project name.
        """
        # Use first line or first 50 characters as project name
        lines = request.request_text.strip().split("\n")
        first_line = lines[0].strip()

        # Truncate to 50 characters
        if len(first_line) > 50:
            first_line = first_line[:47] + "..."

        return first_line

    def _extract_tags(self, request: Request) -> list[str]:
        """
        Extract tags from the request.

        Args:
            request: The request.

        Returns:
            List of tags.
        """
        tags = []

        # Extract from context
        if "tags" in request.context:
            tags.extend(request.context["tags"])

        # Extract from metadata
        if "tags" in request.metadata:
            tags.extend(request.metadata["tags"])

        # Deduplicate
        tags = list(set(tags))

        return tags


class DefaultIdentifierGenerator(IdentifierGenerator):
    """
    Default implementation of identifier generation.

    Generates unique project, workflow, and correlation IDs.
    """

    def generate_project_id(self) -> uuid.UUID:
        """Generate a new project ID."""
        return uuid.uuid4()

    def generate_workflow_id(self) -> uuid.UUID:
        """Generate a new workflow ID."""
        return uuid.uuid4()

    def generate_correlation_id(self) -> uuid.UUID:
        """Generate a new correlation ID."""
        return uuid.uuid4()


class RequestIntakeModule:
    """
    Request Intake Module.

    Coordinates request validation, normalization, and project initialization.
    """

    def __init__(
        self,
        validator: RequestValidator | None = None,
        normalizer: RequestNormalizer | None = None,
        initializer: ProjectInitializer | None = None,
        identifier_generator: IdentifierGenerator | None = None,
        event_bus: EventBus | None = None,
    ):
        """
        Initialize the request intake module.

        Args:
            validator: Request validator.
            normalizer: Request normalizer.
            initializer: Project initializer.
            identifier_generator: Identifier generator.
            event_bus: Event bus for publishing events.
        """
        self.validator = validator or DefaultRequestValidator()
        self.normalizer = normalizer or DefaultRequestNormalizer()
        self.initializer = initializer or DefaultProjectInitializer(event_bus=event_bus)
        self.identifier_generator = identifier_generator or DefaultIdentifierGenerator()
        self.event_bus = event_bus

    async def process_request(self, request: Request) -> dict[str, Any]:
        """
        Process an incoming request.

        Args:
            request: The incoming request.

        Returns:
            Dictionary containing project_id, correlation_id, workflow_id, project.
        """
        # Step 1: Validate request
        is_valid, errors = await self.validator.validate(request)
        if not is_valid:
            raise ValueError(f"Invalid request: {', '.join(errors)}")

        # Step 2: Normalize request
        normalized_request = await self.normalizer.normalize(request)

        # Step 3: Initialize project
        project = await self.initializer.initialize(normalized_request)

        # Step 4: Generate identifiers
        correlation_id = self.identifier_generator.generate_correlation_id()
        workflow_id = self.identifier_generator.generate_workflow_id()

        # Step 5: Publish project.created event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_CREATED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project.id,
            aggregate_type="Project",
            correlation_id=correlation_id,
            metadata={
                "project_name": project.name,
                "workflow_id": str(workflow_id),
                "request_text": normalized_request.request_text[:100],
            },
        )

        return {
            "project_id": project.id,
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "project": project,
            "normalized_request": normalized_request,
        }