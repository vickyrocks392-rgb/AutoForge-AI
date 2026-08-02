"""
Event Validator (Section 7.1, 22).

Validates events against schemas.
Rejects invalid events.
Reports validation errors.
Enforces schema contracts.
"""

from __future__ import annotations

from typing import Any

from autoforge_event_platform.interfaces import IEventSchemaRegistry, IEventValidator
from autoforge_event_platform.models.event import (
    Event,
    EventType,
    ValidationError,
    ValidationResult,
)
from autoforge_event_platform.persistence.schema_validator import SchemaValidator


class EventValidator(IEventValidator):
    """
    Event Validator implementation (Section 7.1, 22).

    Validation Process (Section 22.1):
    1. Schema Lookup — Look up schema for event type
    2. Structure Validation — Validate event structure
    3. Payload Validation — Validate payload against schema

    Validation Checks (Section 22.1):
    - Event type is valid
    - Event category matches event type
    - Required fields are present
    - Field types are correct
    - Field values are within constraints
    - Payload conforms to schema
    - Metadata conforms to schema
    """

    def __init__(self, schema_registry: IEventSchemaRegistry | None = None):
        """
        Initialize the event validator.

        Args:
            schema_registry: Schema registry for schema lookups.
        """
        self._schema_registry = schema_registry
        self._schema_validator = SchemaValidator()

    def validate(self, event: Event) -> ValidationResult:
        """
        Validate an event against its schema (Section 22.1).

        Returns:
            ValidationResult with valid flag and errors.
        """
        errors: list[ValidationError] = []

        # Step 1: Schema Lookup (Section 22.1 Step 1)
        schema = None
        if self._schema_registry is not None:
            schema = self._schema_registry.get_schema(event.event_type, event.version)

        if schema is None:
            errors.append(
                ValidationError(
                    field="eventType",
                    error="schema_not_found",
                    message=f"Schema not found for event type: {event.event_type} version: {event.version}",
                )
            )
            return ValidationResult(valid=False, errors=errors)

        # Step 2 & 3: Structure and Payload Validation
        result = self._schema_validator.validate(event, schema)
        errors.extend(result.errors)

        # Additional validation checks (Section 22.1)
        errors.extend(self._validate_event_type(event))
        errors.extend(self._validate_category_match(event))

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _validate_event_type(self, event: Event) -> list[ValidationError]:
        """Validate that the event type is a valid registered type (Section 22.1)."""
        errors: list[ValidationError] = []

        try:
            EventType(event.event_type)
        except ValueError:
            errors.append(
                ValidationError(
                    field="eventType",
                    error="invalid_value",
                    message=f"Event type '{event.event_type}' is not a valid registered event type.",
                )
            )

        return errors

    def _validate_category_match(self, event: Event) -> list[ValidationError]:
        """Validate that event category matches event type (Section 22.1)."""
        if self._schema_registry is None:
            return []

        schema = self._schema_registry.get_schema(event.event_type, event.version)
        if schema is not None and schema.category != event.event_category:
            return [
                ValidationError(
                    field="eventCategory",
                    error="invalid_value",
                    message=f"Event category '{event.event_category}' does not match expected category '{schema.category}' for event type '{event.event_type}'.",
                )
            ]

        return []
