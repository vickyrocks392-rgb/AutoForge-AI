"""
Event Schema Registry (Section 7.2, 10).

Register event schemas.
Retrieve schemas for event types.
Manage schema versions.
Check schema compatibility.
Transform events between schema versions.
"""

from __future__ import annotations

import threading
from typing import Any

from autoforge_event_platform.interfaces import IEventSchemaRegistry
from autoforge_event_platform.models.event import (
    Event,
    EventCategory,
    EventSchema,
    EventType,
)
from autoforge_event_platform.persistence.schema_transformer import SchemaTransformer


class SchemaRegistry(IEventSchemaRegistry):
    """
    Schema Registry implementation (Section 7.2, 10).

    Schema Registry Responsibilities (Section 10.1):
    - Register schemas for event types
    - Retrieve schemas by event type and version
    - Manage schema versions
    - Check schema compatibility
    - Transform events between versions

    Schema Registration (Section 10.4):
    1. Validate schema structure
    2. Check compatibility with existing versions
    3. Register schema
    4. Publish schema.registered event
    5. Return success
    """

    def __init__(self):
        """Initialize the schema registry and register default schemas."""
        self._schemas: dict[EventType, dict[str, EventSchema]] = {}
        self._latest_versions: dict[EventType, str] = {}
        self._transformer = SchemaTransformer(self)
        self._lock = threading.RLock()
        # Register default schemas for all event types (Section 10.4)
        self.register_default_schemas()

    def register_schema(self, schema: EventSchema) -> bool:
        """
        Register a new event schema (Section 10.4).

        Process:
        1. Validate schema structure
        2. Check compatibility with existing versions
        3. Register schema
        4. Publish schema.registered event
        5. Return success

        Returns:
            True if registration succeeded.
        """
        with self._lock:
            event_type = schema.event_type
            version = schema.version

            # Step 1: Validate schema structure
            if not self._validate_schema_structure(schema):
                return False

            # Step 2: Check compatibility
            if event_type in self._schemas:
                existing_versions = self._schemas[event_type]
                if version in existing_versions:
                    # Version already exists — update
                    pass
                else:
                    # Check compatibility with latest version
                    latest = self._latest_versions.get(event_type)
                    if latest and latest in existing_versions:
                        latest_schema = existing_versions[latest]
                        if not self._check_compatibility(latest_schema, schema):
                            return False

            # Step 3: Register schema
            if event_type not in self._schemas:
                self._schemas[event_type] = {}
            self._schemas[event_type][version] = schema

            # Update latest version
            if event_type not in self._latest_versions or self._is_newer_version(version, self._latest_versions[event_type]):
                self._latest_versions[event_type] = version

            return True

    def get_schema(self, event_type: EventType, version: str | None = None) -> EventSchema | None:
        """
        Retrieve a schema for an event type (Section 10.4).

        Returns:
            The schema, or None if not found.
        """
        with self._lock:
            if event_type not in self._schemas:
                return None

            if version is None:
                version = self._latest_versions.get(event_type)
                if version is None:
                    return None

            return self._schemas[event_type].get(version)

    def get_latest_version(self, event_type: EventType) -> str | None:
        """Get the latest schema version for an event type."""
        with self._lock:
            return self._latest_versions.get(event_type)

    def list_schemas(self) -> list[EventSchema]:
        """List all registered schemas."""
        with self._lock:
            result: list[EventSchema] = []
            for event_type_schemas in self._schemas.values():
                for schema in event_type_schemas.values():
                    result.append(schema)
            return result

    def check_compatibility(self, event_type: EventType, schema: EventSchema) -> bool:
        """
        Check compatibility of a new schema version (Section 10.3).

        Returns:
            True if compatible.
        """
        with self._lock:
            latest = self._latest_versions.get(event_type)
            if latest is None:
                return True

            latest_schema = self._schemas.get(event_type, {}).get(latest)
            if latest_schema is None:
                return True

            return self._check_compatibility(latest_schema, schema)

    def transform_event(self, event: Event, target_version: str) -> Event:
        """Transform an event between schema versions (Section 10.3)."""
        return self._transformer.transform(event, target_version)

    def _validate_schema_structure(self, schema: EventSchema) -> bool:
        """Validate the structure of a schema."""
        if not schema.schema_id:
            return False
        if not schema.version:
            return False
        if not schema.event_type:
            return False
        if not schema.category:
            return False
        return True

    def _check_compatibility(self, existing: EventSchema, new: EventSchema) -> bool:
        """Check if a new schema is compatible with an existing one."""
        # Check backward compatibility
        existing_props = set(existing.payload_schema.get("properties", {}).keys())
        new_props = set(new.payload_schema.get("properties", {}).keys())

        # New schema must not remove required fields
        existing_required = set(existing.payload_schema.get("required", []))
        new_required = set(new.payload_schema.get("required", []))

        if not new_required.issubset(existing_required | new_props):
            return False

        return True

    def _is_newer_version(self, version: str, current: str) -> bool:
        """Check if a version is newer than the current version."""
        try:
            v_parts = [int(x) for x in version.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            return v_parts > c_parts
        except (ValueError, AttributeError):
            return version > current

    def register_default_schemas(self) -> None:
        """Register default schemas for all event types (Section 10.4)."""
        with self._lock:
            for event_type in EventType:
                category = self._get_category_for_type(event_type)
                schema = EventSchema(
                    schema_id=f"{event_type.value}.v1.0.0",
                    version="1.0.0",
                    description=f"Schema for {event_type.value}",
                    category=category,
                    event_type=event_type,
                    payload_schema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                    metadata_schema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                )
                self.register_schema(schema)

    def _get_category_for_type(self, event_type: EventType) -> EventCategory:
        """Determine the event category from the event type."""
        type_to_category: dict[EventType, EventCategory] = {
            EventType.KERNEL_CREATED: EventCategory.KERNEL,
            EventType.KERNEL_STARTING: EventCategory.KERNEL,
            EventType.KERNEL_STARTED: EventCategory.KERNEL,
            EventType.KERNEL_PAUSING: EventCategory.KERNEL,
            EventType.KERNEL_PAUSED: EventCategory.KERNEL,
            EventType.KERNEL_RESUMING: EventCategory.KERNEL,
            EventType.KERNEL_READY: EventCategory.KERNEL,
            EventType.KERNEL_STOPPING: EventCategory.KERNEL,
            EventType.KERNEL_STOPPED: EventCategory.KERNEL,
            EventType.STATE_TRANSITIONED: EventCategory.RUNTIME,
            EventType.STATE_CREATED: EventCategory.RUNTIME,
            EventType.STATE_UPDATED: EventCategory.RUNTIME,
            EventType.STATE_DELETED: EventCategory.RUNTIME,
            EventType.STATE_RESTORED: EventCategory.RUNTIME,
            EventType.WORKFLOW_CREATED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_STARTED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_COMPLETED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_FAILED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_PAUSED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_RESUMED: EventCategory.WORKFLOW,
            EventType.WORKFLOW_CANCELLED: EventCategory.WORKFLOW,
            EventType.EXECUTION_STARTED: EventCategory.EXECUTION,
            EventType.EXECUTION_COMPLETED: EventCategory.EXECUTION,
            EventType.EXECUTION_FAILED: EventCategory.EXECUTION,
            EventType.EXECUTION_PAUSED: EventCategory.EXECUTION,
            EventType.EXECUTION_RESUMED: EventCategory.EXECUTION,
            EventType.EXECUTION_CANCELLED: EventCategory.EXECUTION,
            EventType.EXECUTION_TIMED_OUT: EventCategory.EXECUTION,
            EventType.REVIEW_STARTED: EventCategory.REVIEW,
            EventType.REVIEW_COMPLETED: EventCategory.REVIEW,
            EventType.REVIEW_APPROVED: EventCategory.REVIEW,
            EventType.REVIEW_REJECTED: EventCategory.REVIEW,
            EventType.REVIEW_CHANGES_REQUESTED: EventCategory.REVIEW,
            EventType.REVIEW_ESCALATED: EventCategory.REVIEW,
            EventType.KNOWLEDGE_QUERIED: EventCategory.KNOWLEDGE,
            EventType.KNOWLEDGE_RESEARCHED: EventCategory.KNOWLEDGE,
            EventType.KNOWLEDGE_PROMOTED: EventCategory.KNOWLEDGE,
            EventType.KNOWLEDGE_UPDATED: EventCategory.KNOWLEDGE,
            EventType.KNOWLEDGE_DELETED: EventCategory.KNOWLEDGE,
            EventType.MEMORY_STORED: EventCategory.MEMORY,
            EventType.MEMORY_UPDATED: EventCategory.MEMORY,
            EventType.MEMORY_DELETED: EventCategory.MEMORY,
            EventType.MEMORY_RETRIEVED: EventCategory.MEMORY,
            EventType.MEMORY_CONTEXT_LOADED: EventCategory.MEMORY,
            EventType.LEARNING_ANALYZED: EventCategory.LEARNING,
            EventType.LEARNING_VALIDATED: EventCategory.LEARNING,
            EventType.LEARNING_PROMOTED: EventCategory.LEARNING,
            EventType.LEARNING_DISCARDED: EventCategory.LEARNING,
            EventType.SERVICE_STARTED: EventCategory.INFRASTRUCTURE,
            EventType.SERVICE_STOPPED: EventCategory.INFRASTRUCTURE,
            EventType.SERVICE_HEALTHY: EventCategory.INFRASTRUCTURE,
            EventType.SERVICE_DEGRADED: EventCategory.INFRASTRUCTURE,
            EventType.SERVICE_RECOVERED: EventCategory.INFRASTRUCTURE,
            EventType.SERVICE_FAILED: EventCategory.INFRASTRUCTURE,
            EventType.CONNECTOR_CONNECTED: EventCategory.CONNECTOR,
            EventType.CONNECTOR_DISCONNECTED: EventCategory.CONNECTOR,
            EventType.CONNECTOR_EXECUTED: EventCategory.CONNECTOR,
            EventType.CONNECTOR_FAILED: EventCategory.CONNECTOR,
            EventType.CONNECTOR_RETRYING: EventCategory.CONNECTOR,
            EventType.SECURITY_AUTHENTICATED: EventCategory.SECURITY,
            EventType.SECURITY_AUTHORIZED: EventCategory.SECURITY,
            EventType.SECURITY_DENIED: EventCategory.SECURITY,
            EventType.SECURITY_POLICY_VIOLATED: EventCategory.SECURITY,
            EventType.SECURITY_AUDIT: EventCategory.SECURITY,
            EventType.OBSERVABILITY_METRIC: EventCategory.OBSERVABILITY,
            EventType.OBSERVABILITY_LOG: EventCategory.OBSERVABILITY,
            EventType.OBSERVABILITY_TRACE: EventCategory.OBSERVABILITY,
            EventType.OBSERVABILITY_SPAN: EventCategory.OBSERVABILITY,
            EventType.OBSERVABILITY_ALERT: EventCategory.OBSERVABILITY,
            EventType.APPROVAL_REQUIRED: EventCategory.APPROVAL,
            EventType.APPROVAL_DECIDED: EventCategory.APPROVAL,
            EventType.APPROVAL_TIMEOUT: EventCategory.APPROVAL,
            EventType.APPROVAL_ESCALATED: EventCategory.APPROVAL,
            EventType.APPROVAL_CANCELLED: EventCategory.APPROVAL,
            EventType.ARTIFACT_CREATED: EventCategory.ARTIFACT,
            EventType.ARTIFACT_UPDATED: EventCategory.ARTIFACT,
            EventType.ARTIFACT_DELETED: EventCategory.ARTIFACT,
            EventType.ARTIFACT_PUBLISHED: EventCategory.ARTIFACT,
            EventType.ARTIFACT_ARCHIVED: EventCategory.ARTIFACT,
            EventType.WORKER_REGISTERED: EventCategory.WORKER,
            EventType.WORKER_DISPATCHED: EventCategory.WORKER,
            EventType.WORKER_STARTED: EventCategory.WORKER,
            EventType.WORKER_COMPLETED: EventCategory.WORKER,
            EventType.WORKER_FAILED: EventCategory.WORKER,
            EventType.WORKER_RETIRED: EventCategory.WORKER,
            EventType.TASK_CREATED: EventCategory.TASK,
            EventType.TASK_UPDATED: EventCategory.TASK,
            EventType.TASK_QUEUED: EventCategory.TASK,
            EventType.TASK_READY: EventCategory.TASK,
            EventType.TASK_STARTED: EventCategory.TASK,
            EventType.TASK_PAUSED: EventCategory.TASK,
            EventType.TASK_RESUMED: EventCategory.TASK,
            EventType.TASK_COMPLETED: EventCategory.TASK,
            EventType.TASK_FAILED: EventCategory.TASK,
            EventType.TASK_CANCELLED: EventCategory.TASK,
            EventType.TASK_BLOCKED: EventCategory.TASK,
            EventType.TASK_DELETED: EventCategory.TASK,
            EventType.TASK_DISPATCHED: EventCategory.TASK,
            EventType.TASK_RETRYING: EventCategory.TASK,
            EventType.TASK_WAITING: EventCategory.TASK,
            EventType.PROJECT_CREATED: EventCategory.PROJECT,
            EventType.PROJECT_UPDATED: EventCategory.PROJECT,
            EventType.PROJECT_STARTED: EventCategory.PROJECT,
            EventType.PROJECT_PLANNING: EventCategory.PROJECT,
            EventType.PROJECT_RUNNING: EventCategory.PROJECT,
            EventType.PROJECT_REVIEWING: EventCategory.PROJECT,
            EventType.PROJECT_PAUSED: EventCategory.PROJECT,
            EventType.PROJECT_RESUMED: EventCategory.PROJECT,
            EventType.PROJECT_COMPLETING: EventCategory.PROJECT,
            EventType.PROJECT_FINISHED: EventCategory.PROJECT,
            EventType.PROJECT_FAILED: EventCategory.PROJECT,
            EventType.PROJECT_CANCELLED: EventCategory.PROJECT,
            EventType.PROJECT_ARCHIVED: EventCategory.PROJECT,
            EventType.PROJECT_DELETED: EventCategory.PROJECT,
            EventType.CHECKPOINT_CREATED: EventCategory.CHECKPOINT,
            EventType.CHECKPOINT_RESTORED: EventCategory.CHECKPOINT,
            EventType.CHECKPOINT_DELETED: EventCategory.CHECKPOINT,
            EventType.CHECKPOINT_ARCHIVED: EventCategory.CHECKPOINT,
            EventType.FAILURE_DETECTED: EventCategory.RECOVERY,
            EventType.RECOVERY_STARTED: EventCategory.RECOVERY,
            EventType.RECOVERY_COMPLETED: EventCategory.RECOVERY,
            EventType.RECOVERY_FAILED: EventCategory.RECOVERY,
            EventType.RECOVERY_ABORTED: EventCategory.RECOVERY,
            EventType.LOOP_STARTED: EventCategory.WORKFLOW,
            EventType.LOOP_PLANNING: EventCategory.WORKFLOW,
            EventType.LOOP_EXECUTING: EventCategory.WORKFLOW,
            EventType.LOOP_REVIEWING: EventCategory.WORKFLOW,
            EventType.LOOP_COMPLETED: EventCategory.WORKFLOW,
            EventType.LOOP_REMEDIATING: EventCategory.WORKFLOW,
            EventType.LOOP_ESCALATED: EventCategory.WORKFLOW,
            EventType.LOOP_FAILED: EventCategory.WORKFLOW,
            EventType.PLAN_CREATED: EventCategory.WORKFLOW,
            EventType.PLAN_UPDATED: EventCategory.WORKFLOW,
            EventType.RESEARCH_COMPLETED: EventCategory.KNOWLEDGE,
            EventType.INTENT_ANALYZED: EventCategory.KERNEL,
            EventType.MODEL_SELECTED: EventCategory.KNOWLEDGE,
            EventType.MODEL_FAILED: EventCategory.KNOWLEDGE,
            EventType.MODEL_SWITCHED: EventCategory.KNOWLEDGE,
            EventType.EVENT_CREATED: EventCategory.OBSERVABILITY,
            EventType.EVENT_VALIDATED: EventCategory.OBSERVABILITY,
            EventType.EVENT_ENRICHED: EventCategory.OBSERVABILITY,
            EventType.EVENT_PERSISTED: EventCategory.OBSERVABILITY,
            EventType.EVENT_ROUTED: EventCategory.OBSERVABILITY,
            EventType.EVENT_DELIVERED: EventCategory.OBSERVABILITY,
            EventType.EVENT_DELIVERY_FAILED: EventCategory.OBSERVABILITY,
            EventType.EVENT_DEAD_LETTERED: EventCategory.OBSERVABILITY,
            EventType.EVENT_ARCHIVED: EventCategory.OBSERVABILITY,
            EventType.SCHEMA_REGISTERED: EventCategory.OBSERVABILITY,
            EventType.SCHEMA_UPDATED: EventCategory.OBSERVABILITY,
            EventType.SUBSCRIPTION_CREATED: EventCategory.OBSERVABILITY,
            EventType.SUBSCRIPTION_DELETED: EventCategory.OBSERVABILITY,
            EventType.REPLAY_STARTED: EventCategory.OBSERVABILITY,
            EventType.REPLAY_COMPLETED: EventCategory.OBSERVABILITY,
            EventType.REPLAY_FAILED: EventCategory.OBSERVABILITY,
            EventType.ORDERING_VIOLATION: EventCategory.OBSERVABILITY,
        }

        return type_to_category.get(event_type, EventCategory.OBSERVABILITY)
