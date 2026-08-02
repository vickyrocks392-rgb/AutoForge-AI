"""
Schema Validator (Section 7.2, 22).

Validates events against schemas.
Checks data types.
Validates required fields.
Validates field constraints.
Returns validation errors.
"""

from __future__ import annotations

from typing import Any

from autoforge_event_platform.models.event import (
    Event,
    EventSchema,
    EventType,
    ValidationError,
    ValidationResult,
)


class SchemaValidator:
    """
    Schema Validator implementation (Section 7.2, 22).

    Validation Process (Section 22.1):
    1. Schema Lookup — Look up schema for event type
    2. Structure Validation — Validate event structure
    3. Payload Validation — Validate payload against schema
    """

    def validate(self, event: Event, schema: EventSchema | None = None) -> ValidationResult:
        """
        Validate an event against its schema (Section 22.1).

        Returns:
            ValidationResult with valid flag and errors.
        """
        if schema is None:
            return ValidationResult(
                valid=False,
                errors=[
                    ValidationError(
                        field="eventType",
                        error="schema_not_found",
                        message=f"Schema not found for event type: {event.event_type}",
                    )
                ],
            )

        errors: list[ValidationError] = []

        # Step 1: Schema Lookup already done — schema is provided
        # Step 2: Structure Validation (Section 22.1 Step 2)
        errors.extend(self._validate_structure(event, schema))

        # Step 3: Payload Validation (Section 22.1 Step 3)
        errors.extend(self._validate_payload(event.payload, schema.payload_schema, "payload"))

        # Step 4: Metadata Validation
        if schema.metadata_schema:
            errors.extend(
                self._validate_payload(event.metadata, schema.metadata_schema, "metadata")
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _validate_structure(self, event: Event, schema: EventSchema) -> list[ValidationError]:
        """Validate event structure (Section 22.1 Step 2)."""
        errors: list[ValidationError] = []

        # Event type matches schema (Section 22.1)
        if event.event_type != schema.event_type:
            errors.append(
                ValidationError(
                    field="eventType",
                    error="invalid_value",
                    message=f"Event type '{event.event_type}' does not match schema event type '{schema.event_type}'.",
                )
            )

        # Event category matches schema (Section 22.1)
        if event.event_category != schema.category:
            errors.append(
                ValidationError(
                    field="eventCategory",
                    error="invalid_value",
                    message=f"Event category '{event.event_category}' does not match schema category '{schema.category}'.",
                )
            )

        # Required fields present (Section 22.1)
        if not event.source:
            errors.append(
                ValidationError(
                    field="source",
                    error="required_field_missing",
                    message="Field 'source' is required.",
                )
            )

        if not event.aggregate_type:
            errors.append(
                ValidationError(
                    field="aggregateType",
                    error="required_field_missing",
                    message="Field 'aggregateType' is required.",
                )
            )

        # Field constraints (Section 22.1)
        if len(event.source) > 256:
            errors.append(
                ValidationError(
                    field="source",
                    error="constraint_violation",
                    message="Field 'source' must be max 256 characters.",
                )
            )

        if len(event.aggregate_type) > 64:
            errors.append(
                ValidationError(
                    field="aggregateType",
                    error="constraint_violation",
                    message="Field 'aggregateType' must be max 64 characters.",
                )
            )

        return errors

    def _validate_payload(
        self, data: dict[str, Any], schema: dict[str, Any], prefix: str
    ) -> list[ValidationError]:
        """Validate payload against JSON Schema (Section 22.1 Step 3)."""
        errors: list[ValidationError] = []

        if not schema:
            return errors

        # Check type
        expected_type = schema.get("type")
        if expected_type and expected_type != "object":
            if not isinstance(data, dict):
                errors.append(
                    ValidationError(
                        field=prefix,
                        error="invalid_type",
                        message=f"Field '{prefix}' must be of type '{expected_type}'.",
                    )
                )
                return errors

        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        # Check required fields (Section 22.1)
        for field in required_fields:
            if field not in data:
                errors.append(
                    ValidationError(
                        field=f"{prefix}.{field}",
                        error="required_field_missing",
                        message=f"Field '{field}' is required in {prefix}.",
                    )
                )

        # Check field types and constraints (Section 22.1)
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = properties[field_name]
                field_type = field_schema.get("type")

                if field_type and not self._check_type(field_value, field_type):
                    errors.append(
                        ValidationError(
                            field=f"{prefix}.{field_name}",
                            error="invalid_type",
                            message=f"Field '{field_name}' must be of type '{field_type}'.",
                        )
                    )

                # Check format constraints
                field_format = field_schema.get("format")
                if field_format == "uuid" and isinstance(field_value, str):
                    try:
                        import uuid
                        uuid.UUID(field_value)
                    except (ValueError, AttributeError):
                        errors.append(
                            ValidationError(
                                field=f"{prefix}.{field_name}",
                                error="invalid_value",
                                message=f"Field '{field_name}' must be a valid UUID.",
                            )
                        )

        return errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if a value matches the expected JSON Schema type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
            "null": type(None),
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        if expected_type == "integer" and isinstance(value, bool):
            return False
        return isinstance(value, expected)
