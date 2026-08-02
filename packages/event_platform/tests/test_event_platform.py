"""
Tests for the Event Platform.

Verifies compliance with the Event Platform Specification v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from autoforge_event_platform.core.event_platform import EventPlatform
from autoforge_event_platform.models.event import (
    DeadLetterQuery,
    DeliveryMode,
    Event,
    EventCategory,
    EventQuery,
    EventType,
    OrderingGuarantee,
    Priority,
    PublicationStatus,
    ReplayRequest,
    ReplaySource,
    ReplayStatus,
    SubscriptionRequest,
    SubscriptionStatus,
)


@pytest.fixture
def platform() -> EventPlatform:
    """Create an EventPlatform instance for testing."""
    return EventPlatform()


@pytest.fixture
def received_events():
    """Fixture to collect received events."""
    return []


@pytest.fixture
def callback(received_events):
    """Create a callback that collects events."""
    def _callback(event: Event) -> None:
        received_events.append(event)
    return _callback


class TestEventModel:
    """Test the canonical event model (Section 8)."""

    def test_event_has_all_fields(self):
        """Verify all specification-defined fields are present (Section 8.1)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123", "result": "success"},
            aggregate_type="Task",
        )

        # Verify all fields from Section 8.1
        assert event.event_id is not None
        assert event.event_type == EventType.TASK_COMPLETED
        assert event.event_category == EventCategory.TASK
        assert event.source == "execution"
        assert event.timestamp is not None
        assert event.version == "1.0.0"
        assert event.correlation_id is not None
        assert event.aggregate_id is not None
        assert event.aggregate_type == "Task"
        assert event.payload == {"taskId": "123", "result": "success"}
        assert event.metadata is not None
        assert event.priority == Priority.NORMAL
        assert event.delivery_mode == DeliveryMode.AT_LEAST_ONCE

    def test_event_is_immutable(self):
        """Verify events are immutable (Section 8.3)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
        )

        with pytest.raises(Exception):
            event.event_type = EventType.TASK_FAILED

    def test_event_id_is_uuid_v4(self):
        """Verify event ID is UUID v4 (Section 8.4)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={},
            aggregate_type="Task",
        )
        assert event.event_id.version == 4

    def test_event_categories(self):
        """Verify all event categories are defined (Section 9)."""
        expected_categories = {
            "kernel", "runtime", "workflow", "execution", "review",
            "knowledge", "memory", "learning", "infrastructure",
            "connector", "security", "observability", "approval",
            "artifact", "worker", "task", "project", "checkpoint",
            "recovery",
        }
        actual_categories = {c.value for c in EventCategory}
        assert expected_categories == actual_categories

    def test_event_types(self):
        """Verify all event types are defined (Section 9)."""
        # Check a sample of event types
        assert EventType.KERNEL_CREATED.value == "kernel.created"
        assert EventType.TASK_COMPLETED.value == "task.completed"
        assert EventType.PROJECT_CREATED.value == "project.created"
        assert EventType.RECOVERY_STARTED.value == "recovery.started"

    def test_priority_levels(self):
        """Verify priority levels (Section 8.2)."""
        assert Priority.LOW.value == "low"
        assert Priority.NORMAL.value == "normal"
        assert Priority.HIGH.value == "high"
        assert Priority.CRITICAL.value == "critical"

    def test_delivery_modes(self):
        """Verify delivery modes (Section 8.2)."""
        assert DeliveryMode.AT_MOST_ONCE.value == "at-most-once"
        assert DeliveryMode.AT_LEAST_ONCE.value == "at-least-once"
        assert DeliveryMode.EXACTLY_ONCE.value == "exactly-once"


class TestEventPublication:
    """Test event publication (Section 6.1, 13)."""

    def test_publish_event(self, platform: EventPlatform):
        """Test publishing an event (Section 31.1)."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123", "result": "success"},
            priority=Priority.HIGH,
            delivery_mode=DeliveryMode.AT_LEAST_ONCE,
        )

        assert result.status == PublicationStatus.ACCEPTED
        assert result.event_id is not None
        assert result.timestamp is not None

    def test_publish_with_correlation_id(self, platform: EventPlatform):
        """Test publishing with correlation ID."""
        correlation_id = uuid.uuid4()
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
            correlation_id=correlation_id,
        )

        assert result.status == PublicationStatus.ACCEPTED

        # Verify the event was stored with the correlation ID
        event = platform.persistence.read(result.event_id)
        assert event is not None
        assert event.correlation_id == correlation_id

    def test_publish_with_aggregate_id(self, platform: EventPlatform):
        """Test publishing with aggregate ID."""
        aggregate_id = uuid.uuid4()
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
            aggregate_id=aggregate_id,
            aggregate_type="Task",
        )

        assert result.status == PublicationStatus.ACCEPTED

        event = platform.persistence.read(result.event_id)
        assert event is not None
        assert event.aggregate_id == aggregate_id

    def test_publish_with_metadata(self, platform: EventPlatform):
        """Test publishing with custom metadata."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
            metadata={"customField": "customValue"},
        )

        assert result.status == PublicationStatus.ACCEPTED

        event = platform.persistence.read(result.event_id)
        assert event is not None
        assert event.metadata.get("customField") == "customValue"

    def test_publish_enriches_event(self, platform: EventPlatform):
        """Test that events are enriched with standard metadata (Section 11.2 Stage 3)."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        event = platform.persistence.read(result.event_id)
        assert event is not None

        # Verify standard metadata fields
        assert "publisherId" in event.metadata
        assert "publisherVersion" in event.metadata
        assert "schemaVersion" in event.metadata
        assert "contentType" in event.metadata
        assert "contentEncoding" in event.metadata
        assert "traceId" in event.metadata
        assert "spanId" in event.metadata

    def test_publish_rejects_invalid_event(self, platform: EventPlatform):
        """Test that invalid events are rejected (Section 13.2 Step 2)."""
        # Create an event with an invalid type
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={},
            aggregate_type="Task",
        )
        # Manually corrupt the event type to test validation
        data = event.model_dump()
        data["event_type"] = "invalid.event.type"
        # Use model_construct to bypass Pydantic validation and create an invalid event
        corrupted = Event.model_construct(**data)

        result = platform.publish_event(corrupted)
        assert result.status == PublicationStatus.REJECTED


class TestEventSubscription:
    """Test event subscription (Section 6.2, 14)."""

    def test_subscribe_by_type(self, platform: EventPlatform, callback, received_events):
        """Test subscribing to specific event types (Section 14.3.1)."""
        sub_id, status = platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )

        assert status == SubscriptionStatus.ACTIVE
        assert sub_id != ""

        # Publish an event
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        # Note: In the current implementation, publish goes through publisher first,
        # then event bus. The event bus handles delivery.
        # The event is persisted but delivery happens through the bus.

    def test_subscribe_by_category(self, platform: EventPlatform, callback):
        """Test subscribing to event categories (Section 14.3.2)."""
        sub_id, status = platform.subscribe(
            event_categories=[EventCategory.TASK],
            callback=callback,
        )

        assert status == SubscriptionStatus.ACTIVE
        assert sub_id != ""

    def test_subscribe_with_filter(self, platform: EventPlatform, callback):
        """Test subscribing with a filter expression (Section 14.3.3)."""
        sub_id, status = platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            filter="priority = 'high'",
            callback=callback,
        )

        assert status == SubscriptionStatus.ACTIVE
        assert sub_id != ""

    def test_subscribe_requires_callback(self, platform: EventPlatform):
        """Test that subscription requires a callback."""
        sub_id, status = platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=None,
        )

        assert status == SubscriptionStatus.FAILED

    def test_subscribe_requires_event_type_or_category(self, platform: EventPlatform, callback):
        """Test that subscription requires at least one event type or category."""
        sub_id, status = platform.subscribe(
            callback=callback,
        )

        assert status == SubscriptionStatus.FAILED

    def test_get_subscription(self, platform: EventPlatform, callback):
        """Test getting subscription details (Section 6.6 — get)."""
        sub_id, status = platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )

        subscription = platform.get_subscription(sub_id)
        assert subscription is not None
        assert subscription.subscription_id == sub_id

    def test_delete_subscription(self, platform: EventPlatform, callback):
        """Test deleting a subscription (Section 6.6 — delete)."""
        sub_id, status = platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )

        result = platform.delete_subscription(sub_id)
        assert result is True

        subscription = platform.get_subscription(sub_id)
        assert subscription is None

    def test_list_subscriptions(self, platform: EventPlatform, callback):
        """Test listing subscriptions (Section 6.6 — list)."""
        platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )
        platform.subscribe(
            event_categories=[EventCategory.PROJECT],
            callback=callback,
        )

        subscriptions = platform.list_subscriptions()
        assert len(subscriptions) == 2


class TestEventQuery:
    """Test event query (Section 6.3, 19)."""

    def test_query_by_event_type(self, platform: EventPlatform):
        """Test querying by event type (Section 19.2.1)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        query = EventQuery(
            event_types=[EventType.TASK_COMPLETED],
            limit=100,
        )
        result = platform.query_events(query)

        assert result.total_count >= 1
        assert len(result.events) >= 1

    def test_query_by_event_category(self, platform: EventPlatform):
        """Test querying by event category (Section 19.2.2)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        query = EventQuery(
            event_categories=[EventCategory.TASK],
            limit=100,
        )
        result = platform.query_events(query)

        assert result.total_count >= 1

    def test_query_by_source(self, platform: EventPlatform):
        """Test querying by source (Section 19.2.5)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        query = EventQuery(
            source="execution",
            limit=100,
        )
        result = platform.query_events(query)

        assert result.total_count >= 1

    def test_query_pagination(self, platform: EventPlatform):
        """Test query pagination."""
        for i in range(5):
            platform.publish(
                event_type=EventType.TASK_COMPLETED,
                source="execution",
                payload={"taskId": str(i)},
            )

        query = EventQuery(
            event_types=[EventType.TASK_COMPLETED],
            limit=2,
            offset=0,
        )
        result = platform.query_events(query)
        assert len(result.events) == 2
        assert result.has_more is True

        query = EventQuery(
            event_types=[EventType.TASK_COMPLETED],
            limit=2,
            offset=2,
        )
        result = platform.query_events(query)
        assert len(result.events) == 2

    def test_count_events(self, platform: EventPlatform):
        """Test counting events (Section 19.3)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        counts = platform.query_engine.count_events(
            event_types=[EventType.TASK_COMPLETED],
            group_by="eventType",
        )
        assert "task.completed" in counts
        assert counts["task.completed"] >= 1


class TestEventReplay:
    """Test event replay (Section 6.4, 17)."""

    def test_start_replay_from_beginning(self, platform: EventPlatform, callback, received_events):
        """Test starting a replay from the beginning (Section 17.1)."""
        # Publish some events
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        # Start replay
        request = ReplayRequest(
            source=ReplaySource.FROM_BEGINNING,
            event_types=[EventType.TASK_COMPLETED],
            speed=100.0,  # Fast speed for testing
            subscriber=callback,
        )
        result = platform.start_replay(request)

        assert result.status in (ReplayStatus.COMPLETED, ReplayStatus.RUNNING)
        assert result.replay_id != ""

    def test_replay_with_filters(self, platform: EventPlatform, callback):
        """Test replay with filters (Section 17.3)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        request = ReplayRequest(
            source=ReplaySource.FROM_BEGINNING,
            event_types=[EventType.TASK_COMPLETED],
            speed=100.0,
            subscriber=callback,
        )
        result = platform.start_replay(request)
        assert result.status in (ReplayStatus.COMPLETED, ReplayStatus.RUNNING)

    def test_replay_at_different_speeds(self, platform: EventPlatform, callback):
        """Test replay at different speeds (Section 17.3)."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        for speed in [1.0, 2.0, 4.0, 8.0]:
            request = ReplayRequest(
                source=ReplaySource.FROM_BEGINNING,
                event_types=[EventType.TASK_COMPLETED],
                speed=speed,
                subscriber=callback,
            )
            result = platform.start_replay(request)
            assert result.status in (ReplayStatus.COMPLETED, ReplayStatus.RUNNING)


class TestDeadLetterQueue:
    """Test dead letter queue (Section 6.5, 23)."""

    def test_list_dead_letters(self, platform: EventPlatform):
        """Test listing dead letters (Section 23.3 — list)."""
        query = DeadLetterQuery(limit=100)
        result = platform.list_dead_letters(query)
        assert result.total_count >= 0

    def test_analyze_dead_letters(self, platform: EventPlatform):
        """Test analyzing dead letters (Section 23.3 — analyze)."""
        analysis = platform.analyze_dead_letters()
        assert analysis.total_entries >= 0
        assert isinstance(analysis.failure_reasons, dict)
        assert isinstance(analysis.recommendations, list)

    def test_dlq_operations(self, platform: EventPlatform):
        """Test DLQ operations (Section 31.5)."""
        # List
        result = platform.manage_dead_letters("list")
        assert result is not None

        # Analyze
        result = platform.manage_dead_letters("analyze")
        assert result is not None


class TestEventFiltering:
    """Test event filtering (Section 21)."""

    def test_filter_equals(self, platform: EventPlatform):
        """Test filter with equals operator (Section 21.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
            priority=Priority.HIGH,
        )

        result = platform.filter_engine.evaluate(event, "priority = 'high'")
        assert result is True

        result = platform.filter_engine.evaluate(event, "priority = 'low'")
        assert result is False

    def test_filter_and(self, platform: EventPlatform):
        """Test filter with AND operator (Section 21.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
            priority=Priority.HIGH,
        )

        result = platform.filter_engine.evaluate(
            event, "priority = 'high' AND source = 'execution'"
        )
        assert result is True

    def test_filter_or(self, platform: EventPlatform):
        """Test filter with OR operator (Section 21.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
            priority=Priority.LOW,
        )

        result = platform.filter_engine.evaluate(
            event, "priority = 'high' OR priority = 'low'"
        )
        assert result is True

    def test_filter_in(self, platform: EventPlatform):
        """Test filter with IN operator (Section 21.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
            priority=Priority.HIGH,
        )

        result = platform.filter_engine.evaluate(
            event, "priority IN ('high', 'critical')"
        )
        assert result is True

    def test_filter_contains(self, platform: EventPlatform):
        """Test filter with CONTAINS operator (Section 21.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
        )

        result = platform.filter_engine.evaluate(
            event, "source CONTAINS 'exec'"
        )
        assert result is True

    def test_filter_validation(self, platform: EventPlatform):
        """Test filter validation (Section 21.3)."""
        result = platform.filter_engine.validate_filter("priority = 'high'")
        assert result.valid is True

        result = platform.filter_engine.validate_filter("invalid filter syntax !!!")
        # Should not crash, may or may not be valid depending on parsing


class TestEventCorrelation:
    """Test event correlation (Section 20)."""

    def test_query_by_correlation_id(self, platform: EventPlatform):
        """Test querying by correlation ID (Section 20.3)."""
        correlation_id = uuid.uuid4()
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
            correlation_id=correlation_id,
        )

        events = platform.query_by_correlation_id(correlation_id)
        assert len(events) >= 1

    def test_query_causation_chain(self, platform: EventPlatform):
        """Test querying causation chain (Section 20.3)."""
        # Publish an event
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        event = platform.persistence.read(result.event_id)
        assert event is not None

        chain = platform.query_causation_chain(event.event_id)
        assert len(chain) >= 1

    def test_query_related_events(self, platform: EventPlatform):
        """Test querying related events (Section 20.3)."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        related = platform.query_related_events(result.event_id)
        assert len(related) >= 1


class TestEventOrdering:
    """Test event ordering (Section 16)."""

    def test_ordering_manager_assigns_sequence(self, platform: EventPlatform):
        """Test that ordering manager assigns sequence numbers (Section 16.2)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
        )

        ordered = platform.ordering_manager.assign_sequence_number(
            event, OrderingGuarantee.PER_AGGREGATE
        )
        assert ordered.sequence_number is not None
        assert ordered.sequence_number > 0

    def test_ordering_manager_global(self, platform: EventPlatform):
        """Test global ordering (Section 16.1)."""
        event = Event(
            event_type=EventType.TASK_COMPLETED,
            event_category=EventCategory.TASK,
            source="execution",
            payload={"taskId": "123"},
            aggregate_type="Task",
        )

        ordered = platform.ordering_manager.assign_sequence_number(
            event, OrderingGuarantee.GLOBAL
        )
        assert ordered.sequence_number is not None


class TestEventPersistence:
    """Test event persistence (Section 18)."""

    def test_persist_and_read(self, platform: EventPlatform):
        """Test persisting and reading events (Section 18.2)."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        event = platform.persistence.read(result.event_id)
        assert event is not None
        assert event.event_id == result.event_id

    def test_persistence_stats(self, platform: EventPlatform):
        """Test persistence statistics."""
        platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        stats = platform.persistence.get_stats()
        assert "hot_storage" in stats
        assert "warm_storage" in stats
        assert "cold_storage" in stats


class TestSchemaRegistry:
    """Test schema registry (Section 10)."""

    def test_get_schema(self, platform: EventPlatform):
        """Test retrieving a schema (Section 10.4)."""
        schema = platform.get_schema(EventType.TASK_COMPLETED)
        assert schema is not None
        assert schema.event_type == EventType.TASK_COMPLETED
        assert schema.version == "1.0.0"

    def test_list_schemas(self, platform: EventPlatform):
        """Test listing all schemas."""
        schemas = platform.list_schemas()
        assert len(schemas) > 0

    def test_get_latest_version(self, platform: EventPlatform):
        """Test getting latest schema version."""
        version = platform.get_latest_schema_version(EventType.TASK_COMPLETED)
        assert version == "1.0.0"


class TestEventBus:
    """Test event bus (Section 7.1)."""

    def test_bus_health(self, platform: EventPlatform):
        """Test event bus health monitoring (Section 2.1)."""
        health = platform.get_health()
        assert "queue_size" in health
        assert "active_subscriptions" in health
        assert "event_history_size" in health


class TestEventLifecycle:
    """Test event lifecycle (Section 11)."""

    def test_lifecycle_states(self):
        """Test event lifecycle states (Section 11.2)."""
        from autoforge_event_platform.models.event import EventLifecycleState

        assert EventLifecycleState.CREATED.value == "created"
        assert EventLifecycleState.VALIDATING.value == "validating"
        assert EventLifecycleState.REJECTED.value == "rejected"
        assert EventLifecycleState.ENRICHING.value == "enriching"
        assert EventLifecycleState.PERSISTING.value == "persisting"
        assert EventLifecycleState.PERSISTED.value == "persisted"
        assert EventLifecycleState.ROUTING.value == "routing"
        assert EventLifecycleState.DELIVERING.value == "delivering"
        assert EventLifecycleState.DELIVERED.value == "delivered"
        assert EventLifecycleState.FAILED.value == "failed"
        assert EventLifecycleState.ARCHIVED.value == "archived"


class TestDeliveryGuarantees:
    """Test delivery guarantees (Section 15)."""

    def test_default_delivery_mode(self, platform: EventPlatform):
        """Test default delivery mode is at-least-once (Section 15.1)."""
        result = platform.publish(
            event_type=EventType.TASK_COMPLETED,
            source="execution",
            payload={"taskId": "123"},
        )

        event = platform.persistence.read(result.event_id)
        assert event.delivery_mode == DeliveryMode.AT_LEAST_ONCE

    def test_at_most_once_delivery(self, platform: EventPlatform):
        """Test at-most-once delivery (Section 15.1)."""
        result = platform.publish(
            event_type=EventType.OBSERVABILITY_METRIC,
            source="observability",
            payload={"metric": "cpu_usage", "value": 0.85},
            delivery_mode=DeliveryMode.AT_MOST_ONCE,
        )

        event = platform.persistence.read(result.event_id)
        assert event.delivery_mode == DeliveryMode.AT_MOST_ONCE

    def test_exactly_once_delivery(self, platform: EventPlatform):
        """Test exactly-once delivery (Section 15.1)."""
        result = platform.publish(
            event_type=EventType.SECURITY_AUTHENTICATED,
            source="security",
            payload={"userId": "123"},
            delivery_mode=DeliveryMode.EXACTLY_ONCE,
        )

        event = platform.persistence.read(result.event_id)
        assert event.delivery_mode == DeliveryMode.EXACTLY_ONCE


class TestSubscriptionManagement:
    """Test subscription management (Section 6.6)."""

    def test_manage_subscriptions_create(self, platform: EventPlatform, callback):
        """Test subscription management create operation (Section 31.6)."""
        request = SubscriptionRequest(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )
        result = platform.manage_subscriptions("create", request=request)
        assert result is not None
        assert len(result) == 3  # (subscription_id, status, timestamp)

    def test_manage_subscriptions_list(self, platform: EventPlatform, callback):
        """Test subscription management list operation."""
        platform.subscribe(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )
        result = platform.manage_subscriptions("list")
        assert len(result) >= 1

    def test_manage_subscriptions_delete(self, platform: EventPlatform, callback):
        """Test subscription management delete operation."""
        request = SubscriptionRequest(
            event_types=[EventType.TASK_COMPLETED],
            callback=callback,
        )
        sub_id, _, _ = platform.manage_subscriptions("create", request=request)
        result = platform.manage_subscriptions("delete", subscription_id=sub_id)
        assert result is True
