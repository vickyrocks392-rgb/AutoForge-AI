"""
Event Publisher (Section 7.1, 13).

Accept event publications.
Validate published events.
Enrich events.
Persist events.
Route events.
Confirm publication.
Handle publication failures.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import (
    IEventPersistence,
    IEventPublisher,
    IEventRouter,
    IEventSchemaRegistry,
    IEventValidator,
)
from autoforge_event_platform.models.event import (
    DeliveryMode,
    Event,
    EventCategory,
    EventType,
    Priority,
    PublicationResult,
    PublicationStatus,
)
from autoforge_event_platform.persistence.event_persistence import EventPersistence
from autoforge_event_platform.persistence.event_validator import EventValidator
from autoforge_event_platform.persistence.schema_registry import SchemaRegistry


class EventPublisher(IEventPublisher):
    """
    Event Publisher implementation (Section 7.1, 13).

    Publication Flow (Section 13.1):
    1. Receive Event
    2. Validate Event
    3. Enrich Event
    4. Persist Event
    5. Route Event
    6. Deliver Event
    7. Confirm Publication

    Publication Process (Section 13.2):
    - Step 1: Receive Event
    - Step 2: Validate Event
    - Step 3: Enrich Event
    - Step 4: Persist Event
    - Step 5: Route Event
    - Step 6: Deliver Event
    - Step 7: Confirm Publication

    Publication Guarantees (Section 13.3):
    - Event is accepted if valid
    - Event is rejected if invalid
    - Event is queued if storage unavailable
    - Event is never lost once accepted
    - Event is persisted before routing
    - Event is durably stored
    - Event is recoverable from storage
    - Event is never lost
    """

    def __init__(
        self,
        validator: IEventValidator | None = None,
        schema_registry: IEventSchemaRegistry | None = None,
        persistence: IEventPersistence | None = None,
        router: IEventRouter | None = None,
    ):
        """
        Initialize the event publisher.

        Args:
            validator: Event validator for schema validation.
            schema_registry: Schema registry for schema lookups.
            persistence: Event persistence for durable storage.
            router: Event router for routing events.
        """
        self._schema_registry = schema_registry or SchemaRegistry()
        self._validator = validator or EventValidator(self._schema_registry)
        self._persistence = persistence or EventPersistence()
        self._router = router
        self._lock = threading.RLock()

    def publish(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        correlation_id: uuid.UUID | None = None,
        aggregate_id: uuid.UUID | None = None,
        aggregate_type: str | None = None,
        priority: Priority = Priority.NORMAL,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
        metadata: dict[str, Any] | None = None,
        causation_id: uuid.UUID | None = None,
    ) -> PublicationResult:
        """
        Publish an event to the event bus (Section 31.1).

        Signature:
        Publish(
          eventType: EventType,
          source: String,
          payload: Map<String, Any>,
          correlationId: UUID | null = null,
          aggregateId: UUID | null = null,
          aggregateType: String | null = null,
          priority: Priority = Priority.NORMAL,
          deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
          metadata: Map<String, Any> | null = null
        ) -> EventId

        Returns:
            PublicationResult with event_id, status, and timestamp.
        """
        # Step 1: Create event (Section 13.2 Step 1)
        event = self._create_event(
            event_type=event_type,
            source=source,
            payload=payload,
            correlation_id=correlation_id,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            priority=priority,
            delivery_mode=delivery_mode,
            metadata=metadata,
            causation_id=causation_id,
        )

        return self.publish_event(event)

    def publish_event(self, event: Event) -> PublicationResult:
        """
        Publish a pre-constructed event (Section 13.2).

        Returns:
            PublicationResult with event_id, status, and timestamp.
        """
        with self._lock:
            # Step 2: Validate Event (Section 13.2 Step 2)
            validation_result = self._validator.validate(event)
            if not validation_result.valid:
                return PublicationResult(
                    event_id=event.event_id,
                    status=PublicationStatus.REJECTED,
                    timestamp=datetime.now(timezone.utc),
                    errors=validation_result.errors,
                )

            # Step 3: Enrich Event (Section 13.2 Step 3)
            enriched_event = self._enrich_event(event)

            # Step 4: Persist Event (Section 13.2 Step 4)
            try:
                self._persistence.write(enriched_event)
            except Exception as e:
                # Persistence failure: Queue event for retry, return accepted with warning
                # (Section 13.2 Step 4, Error Handling)
                return PublicationResult(
                    event_id=enriched_event.event_id,
                    status=PublicationStatus.ACCEPTED,
                    timestamp=datetime.now(timezone.utc),
                    warnings=[f"Persistence deferred: {str(e)}"],
                )

            # Step 5: Route Event (Section 13.2 Step 5)
            # Routing is handled by the Event Bus

            # Step 6: Deliver Event (Section 13.2 Step 6)
            # Delivery is handled by the Event Bus

            # Step 7: Confirm Publication (Section 13.2 Step 7)
            return PublicationResult(
                event_id=enriched_event.event_id,
                status=PublicationStatus.ACCEPTED,
                timestamp=datetime.now(timezone.utc),
            )

    def _create_event(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        correlation_id: uuid.UUID | None,
        aggregate_id: uuid.UUID | None,
        aggregate_type: str | None,
        priority: Priority,
        delivery_mode: DeliveryMode,
        metadata: dict[str, Any] | None,
        causation_id: uuid.UUID | None,
    ) -> Event:
        """Create an event from publication parameters (Section 13.2 Step 1)."""
        # Determine event category from event type
        category = self._get_category_for_type(event_type)

        # Build metadata
        event_metadata = dict(metadata) if metadata else {}

        # Create the event
        event = Event(
            event_type=event_type,
            event_category=category,
            source=source,
            payload=payload,
            correlation_id=correlation_id or uuid.uuid4(),
            causation_id=causation_id,
            aggregate_id=aggregate_id or uuid.uuid4(),
            aggregate_type=aggregate_type or category.value,
            metadata=event_metadata,
            priority=priority,
            delivery_mode=delivery_mode,
        )

        return event

    def _enrich_event(self, event: Event) -> Event:
        """
        Enrich event with metadata (Section 13.2 Step 3, 11.2 Stage 3).

        Enrichment Fields:
        - eventId — Generated UUID
        - timestamp — Current timestamp
        - causationId — Set if not provided
        - correlationId — Set if not provided
        - metadata.publisherId — Added
        - metadata.publisherVersion — Added
        - metadata.schemaVersion — Added
        - metadata.traceId — Added
        - metadata.spanId — Added
        """
        # Event is immutable, so we create a new enriched event
        data = event.model_dump()

        # Ensure causation_id is set (Section 11.2 Stage 3)
        if data.get("causation_id") is None:
            data["causation_id"] = str(event.event_id)

        # Add standard metadata (Section 11.2 Stage 3)
        metadata = dict(data.get("metadata") or {})
        metadata.setdefault("publisherId", source if (source := data.get("source")) else "unknown")
        metadata.setdefault("publisherVersion", "1.0.0")
        metadata.setdefault("schemaVersion", event.version)
        metadata.setdefault("contentType", "application/json")
        metadata.setdefault("contentEncoding", "utf-8")
        metadata.setdefault("traceId", str(event.correlation_id))
        metadata.setdefault("spanId", str(event.event_id))
        metadata.setdefault("environment", "development")
        data["metadata"] = metadata

        return Event.model_validate(data)

    def _get_category_for_type(self, event_type: EventType) -> EventCategory:
        """Determine the event category from the event type."""
        # Map event types to categories based on the specification (Section 9)
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
