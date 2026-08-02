"""
Schema Transformer (Section 7.2, 10.3).

Transforms events between schema versions.
Handles schema evolution.
Applies backward compatibility rules.
Applies forward compatibility rules.
Migrates event data.
"""

from __future__ import annotations

from typing import Any

from autoforge_event_platform.models.event import Event, EventSchema


class SchemaTransformer:
    """
    Schema Transformer implementation (Section 7.2, 10.3).

    Handles schema evolution by transforming events between versions.
    """

    def __init__(self, schema_registry):
        """
        Initialize the schema transformer.

        Args:
            schema_registry: The schema registry for looking up schemas.
        """
        self._registry = schema_registry

    def transform(self, event: Event, target_version: str) -> Event:
        """
        Transform an event to the target schema version (Section 10.3).

        Returns a new event with the target version.
        Events are immutable, so we create a new event.
        """
        source_schema = self._registry.get_schema(event.event_type, event.version)
        target_schema = self._registry.get_schema(event.event_type, target_version)

        if target_schema is None:
            return event

        if source_schema is None:
            # No source schema — just update version
            data = event.model_dump()
            data["version"] = target_version
            return Event.model_validate(data)

        # Transform payload
        new_payload = self._transform_payload(
            event.payload,
            source_schema.payload_schema,
            target_schema.payload_schema,
        )

        # Transform metadata
        new_metadata = self._transform_metadata(
            event.metadata,
            source_schema.metadata_schema,
            target_schema.metadata_schema,
        )

        # Create new event with transformed data
        data = event.model_dump()
        data["version"] = target_version
        data["payload"] = new_payload
        data["metadata"] = new_metadata
        return Event.model_validate(data)

    def _transform_payload(
        self,
        payload: dict[str, Any],
        source_schema: dict[str, Any],
        target_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Transform payload between schema versions."""
        source_props = source_schema.get("properties", {})
        target_props = target_schema.get("properties", {})

        result: dict[str, Any] = {}

        # Copy fields that exist in both schemas
        for field_name, field_value in payload.items():
            if field_name in target_props:
                result[field_name] = field_value

        # Add default values for new fields in target schema
        for field_name, field_schema in target_props.items():
            if field_name not in result and "default" in field_schema:
                result[field_name] = field_schema["default"]

        return result

    def _transform_metadata(
        self,
        metadata: dict[str, Any],
        source_schema: dict[str, Any],
        target_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Transform metadata between schema versions."""
        if not target_schema:
            return dict(metadata)

        source_props = source_schema.get("properties", {})
        target_props = target_schema.get("properties", {})

        result: dict[str, Any] = {}

        # Copy fields that exist in both schemas
        for field_name, field_value in metadata.items():
            if field_name in target_props or not target_props:
                result[field_name] = field_value

        # Add default values for new fields in target schema
        for field_name, field_schema in target_props.items():
            if field_name not in result and "default" in field_schema:
                result[field_name] = field_schema["default"]

        return result

    def migrate_history(
        self,
        events: list[Event],
        target_version: str,
    ) -> list[Event]:
        """
        Migrate historical events to a new schema version (Section 2.14).

        Returns a list of transformed events.
        """
        return [self.transform(event, target_version) for event in events]
