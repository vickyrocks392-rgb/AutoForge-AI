"""
Event Platform Public Interfaces (Section 6, 7).

All public interfaces are defined here to maintain interface-first architecture.
Components depend on interfaces, not concrete implementations.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable

from autoforge_event_platform.models.event import (
    DeadLetterAnalysis,
    DeadLetterEntry,
    DeadLetterQuery,
    DeadLetterResult,
    DeliveryResult,
    Event,
    EventQuery,
    EventQueryResult,
    EventSchema,
    EventType,
    OrderingGuarantee,
    PublicationResult,
    ReplayRequest,
    ReplayResult,
    Subscription,
    SubscriptionId,
    SubscriptionRequest,
    SubscriptionStatus,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# Section 6.1 — Event Publication Interface
# ---------------------------------------------------------------------------


class IEventPublisher(ABC):
    """Interface for event publication (Section 6.1)."""

    @abstractmethod
    def publish(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        correlation_id: uuid.UUID | None = None,
        aggregate_id: uuid.UUID | None = None,
        aggregate_type: str | None = None,
        priority: Any = None,
        delivery_mode: Any = None,
        metadata: dict[str, Any] | None = None,
        causation_id: uuid.UUID | None = None,
    ) -> PublicationResult:
        """Publish an event to the event bus (Section 31.1)."""
        ...

    @abstractmethod
    def publish_event(self, event: Event) -> PublicationResult:
        """Publish a pre-constructed event (Section 13.2)."""
        ...


# ---------------------------------------------------------------------------
# Section 6.2 — Event Subscription Interface
# ---------------------------------------------------------------------------


class IEventSubscriptionManager(ABC):
    """Interface for event subscription management (Section 6.2, 14)."""

    @abstractmethod
    def subscribe(
        self, request: SubscriptionRequest
    ) -> tuple[SubscriptionId, SubscriptionStatus, datetime]:
        """Subscribe to events from the event bus (Section 14.2)."""
        ...

    @abstractmethod
    def get_subscription(self, subscription_id: SubscriptionId) -> Subscription | None:
        """Get subscription details (Section 6.6 — get)."""
        ...

    @abstractmethod
    def update_subscription(
        self, subscription_id: SubscriptionId, request: SubscriptionRequest
    ) -> Subscription | None:
        """Update subscription (Section 6.6 — update)."""
        ...

    @abstractmethod
    def delete_subscription(self, subscription_id: SubscriptionId) -> bool:
        """Delete subscription (Section 6.6 — delete)."""
        ...

    @abstractmethod
    def list_subscriptions(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[Any] | None = None,
    ) -> list[Subscription]:
        """List subscriptions (Section 6.6 — list)."""
        ...


# ---------------------------------------------------------------------------
# Section 6.3 — Event Query Interface
# ---------------------------------------------------------------------------


class IEventQueryEngine(ABC):
    """Interface for event query (Section 6.3, 19)."""

    @abstractmethod
    def query_events(self, query: EventQuery) -> EventQueryResult:
        """Query historical events (Section 19.2)."""
        ...

    @abstractmethod
    def count_events(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[Any] | None = None,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, int]:
        """Count events with optional grouping (Section 19.3)."""
        ...

    @abstractmethod
    def aggregate_metrics(
        self,
        metric: str,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate metrics from event history (Section 19.3)."""
        ...

    @abstractmethod
    def export_events(self, query: EventQuery, format: str = "json") -> str:
        """Export event history (Section 19.4)."""
        ...


# ---------------------------------------------------------------------------
# Section 6.4 — Event Replay Interface
# ---------------------------------------------------------------------------


class IEventReplayEngine(ABC):
    """Interface for event replay (Section 6.4, 17)."""

    @abstractmethod
    def start_replay(self, request: ReplayRequest) -> ReplayResult:
        """Start an event replay session (Section 17.2)."""
        ...

    @abstractmethod
    def pause_replay(self, replay_id: str) -> ReplayResult:
        """Pause a replay session (Section 17.3)."""
        ...

    @abstractmethod
    def resume_replay(self, replay_id: str) -> ReplayResult:
        """Resume a paused replay session (Section 17.3)."""
        ...

    @abstractmethod
    def stop_replay(self, replay_id: str) -> ReplayResult:
        """Stop a replay session (Section 17.3)."""
        ...

    @abstractmethod
    def get_replay_status(self, replay_id: str) -> ReplayResult | None:
        """Get replay session status."""
        ...


# ---------------------------------------------------------------------------
# Section 6.5 — Dead Letter Queue Interface
# ---------------------------------------------------------------------------


class IDeadLetterQueue(ABC):
    """Interface for dead letter queue (Section 6.5, 23)."""

    @abstractmethod
    def add_dead_letter(self, entry: DeadLetterEntry) -> None:
        """Add an event to the dead letter queue (Section 23.2)."""
        ...

    @abstractmethod
    def list_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """List dead letter events (Section 23.3 — list)."""
        ...

    @abstractmethod
    def retry_dead_letter(self, dead_letter_id: str) -> bool:
        """Retry a dead letter event (Section 23.3 — retry)."""
        ...

    @abstractmethod
    def replay_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """Replay all matching dead letter events (Section 23.3 — replay)."""
        ...

    @abstractmethod
    def delete_dead_letter(self, dead_letter_id: str) -> bool:
        """Delete a dead letter event (Section 23.3 — delete)."""
        ...

    @abstractmethod
    def analyze_dead_letters(
        self, time_range: tuple[datetime, datetime] | None = None
    ) -> DeadLetterAnalysis:
        """Analyze dead letter patterns (Section 23.3 — analyze)."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Event Bus Interface
# ---------------------------------------------------------------------------


class IEventBus(ABC):
    """Interface for the event bus (Section 7.1)."""

    @abstractmethod
    def publish(self, event: Event) -> PublicationResult:
        """Publish an event to the event bus."""
        ...

    @abstractmethod
    def subscribe(
        self, request: SubscriptionRequest
    ) -> tuple[SubscriptionId, SubscriptionStatus]:
        """Subscribe to events on the bus."""
        ...

    @abstractmethod
    def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        """Unsubscribe from the bus."""
        ...

    @abstractmethod
    def get_health(self) -> dict[str, Any]:
        """Monitor event bus health and performance."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Event Router Interface
# ---------------------------------------------------------------------------


class IEventRouter(ABC):
    """Interface for the event router (Section 7.1, 12)."""

    @abstractmethod
    def register_subscription(self, subscription: Subscription) -> None:
        """Register a subscription with the router."""
        ...

    @abstractmethod
    def unregister_subscription(self, subscription_id: str) -> None:
        """Unregister a subscription from the router."""
        ...

    @abstractmethod
    def route(self, event: Event) -> list[Subscription]:
        """Route an event to matching subscriptions."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Event Dispatcher Interface
# ---------------------------------------------------------------------------


class IEventDispatcher(ABC):
    """Interface for the event dispatcher (Section 7.1, 15)."""

    @abstractmethod
    def dispatch(self, event: Event, subscription: Subscription) -> DeliveryResult:
        """Dispatch an event to a subscriber."""
        ...

    @abstractmethod
    def dispatch_batch(
        self, events: list[Event], subscription: Subscription
    ) -> list[DeliveryResult]:
        """Batch dispatch events to a subscriber."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Event Filter Engine Interface
# ---------------------------------------------------------------------------


class IEventFilterEngine(ABC):
    """Interface for the event filter engine (Section 7.1, 21)."""

    @abstractmethod
    def evaluate(self, event: Event, filter_expression: str) -> bool:
        """Evaluate a filter expression against an event."""
        ...

    @abstractmethod
    def validate_filter(self, filter_expression: str) -> ValidationResult:
        """Validate a filter expression."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Ordering Manager Interface
# ---------------------------------------------------------------------------


class IOrderingManager(ABC):
    """Interface for the ordering manager (Section 7.1, 16)."""

    @abstractmethod
    def assign_sequence_number(
        self, event: Event, guarantee: OrderingGuarantee
    ) -> Event:
        """Assign a sequence number to an event."""
        ...

    @abstractmethod
    def check_ordering(self, event: Event, guarantee: OrderingGuarantee) -> bool:
        """Check if an event maintains ordering."""
        ...


# ---------------------------------------------------------------------------
# Section 7.2 — Schema Registry Interface
# ---------------------------------------------------------------------------


class IEventSchemaRegistry(ABC):
    """Interface for the schema registry (Section 7.2, 10)."""

    @abstractmethod
    def register_schema(self, schema: EventSchema) -> bool:
        """Register a new event schema."""
        ...

    @abstractmethod
    def get_schema(self, event_type: EventType, version: str | None = None) -> EventSchema | None:
        """Retrieve a schema for an event type."""
        ...

    @abstractmethod
    def get_latest_version(self, event_type: EventType) -> str | None:
        """Get the latest schema version for an event type."""
        ...

    @abstractmethod
    def list_schemas(self) -> list[EventSchema]:
        """List all registered schemas."""
        ...

    @abstractmethod
    def check_compatibility(self, event_type: EventType, schema: EventSchema) -> bool:
        """Check compatibility of a new schema version."""
        ...

    @abstractmethod
    def transform_event(self, event: Event, target_version: str) -> Event:
        """Transform an event between schema versions."""
        ...


# ---------------------------------------------------------------------------
# Section 7.1 — Event Validator Interface
# ---------------------------------------------------------------------------


class IEventValidator(ABC):
    """Interface for the event validator (Section 7.1, 22)."""

    @abstractmethod
    def validate(self, event: Event) -> ValidationResult:
        """Validate an event against its schema."""
        ...


# ---------------------------------------------------------------------------
# Section 7.3 — Event Persistence Interface
# ---------------------------------------------------------------------------


class IEventPersistence(ABC):
    """Interface for event persistence (Section 7.3, 18)."""

    @abstractmethod
    def write(self, event: Event) -> bool:
        """Write an event to persistent storage."""
        ...

    @abstractmethod
    def write_batch(self, events: list[Event]) -> bool:
        """Batch write events for performance."""
        ...

    @abstractmethod
    def read(self, event_id: uuid.UUID) -> Event | None:
        """Read an event by ID."""
        ...

    @abstractmethod
    def query(self, query: EventQuery) -> EventQueryResult:
        """Query events from storage."""
        ...

    @abstractmethod
    def archive(self, event_id: uuid.UUID) -> bool:
        """Archive an event."""
        ...

    @abstractmethod
    def run_retention_job(self, now: datetime | None = None) -> int:
        """Run the daily retention job."""
        ...

    @abstractmethod
    def get_stats(self) -> dict[str, int]:
        """Get persistence statistics."""
        ...


# ---------------------------------------------------------------------------
# Section 7.3 — Event History Store Interface
# ---------------------------------------------------------------------------


class IEventHistoryStore(ABC):
    """Interface for the event history store (Section 7.3, 19)."""

    @abstractmethod
    def store(self, event: Event) -> bool:
        """Store an event in history."""
        ...

    @abstractmethod
    def get(self, event_id: uuid.UUID) -> Event | None:
        """Retrieve an event from history by ID."""
        ...

    @abstractmethod
    def query(self, query: EventQuery) -> EventQueryResult:
        """Query event history."""
        ...

    @abstractmethod
    def count_events(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[Any] | None = None,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, int]:
        """Count events with optional grouping."""
        ...

    @abstractmethod
    def aggregate_metrics(
        self,
        metric: str,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate metrics from event history."""
        ...

    @abstractmethod
    def export_events(self, query: EventQuery, format: str = "json") -> str:
        """Export event history."""
        ...


# ---------------------------------------------------------------------------
# Section 7.4 — Event Correlation Engine Interface
# ---------------------------------------------------------------------------


class IEventCorrelationEngine(ABC):
    """Interface for the event correlation engine (Section 7.4, 20)."""

    @abstractmethod
    def query_by_correlation_id(self, correlation_id: uuid.UUID) -> list[Event]:
        """Query all events with a correlation ID."""
        ...

    @abstractmethod
    def query_causation_chain(self, event_id: uuid.UUID) -> list[Event]:
        """Query the causation chain for an event."""
        ...

    @abstractmethod
    def query_related_events(self, event_id: uuid.UUID) -> list[Event]:
        """Query all related events."""
        ...

    @abstractmethod
    def group_by_aggregate(self, aggregate_id: uuid.UUID) -> list[Event]:
        """Group events by aggregate."""
        ...

    @abstractmethod
    def detect_patterns(self, events: list[Event]) -> list[dict[str, Any]]:
        """Detect patterns in event streams."""
        ...

    @abstractmethod
    def build_correlation_graph(self, events: list[Event]) -> dict[str, list[str]]:
        """Build a correlation graph from events."""
        ...


# ---------------------------------------------------------------------------
# Section 6 — Event Platform Interface
# ---------------------------------------------------------------------------


class IEventPlatform(ABC):
    """Interface for the Event Platform facade (Section 6)."""

    @abstractmethod
    def publish(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        correlation_id: uuid.UUID | None = None,
        aggregate_id: uuid.UUID | None = None,
        aggregate_type: str | None = None,
        priority: Any = None,
        delivery_mode: Any = None,
        metadata: dict[str, Any] | None = None,
        causation_id: uuid.UUID | None = None,
    ) -> PublicationResult:
        """Publish an event to the event bus (Section 31.1)."""
        ...

    @abstractmethod
    def subscribe(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[Any] | None = None,
        filter: str | None = None,
        delivery_mode: Any = None,
        ordering_guarantee: OrderingGuarantee = OrderingGuarantee.NONE,
        callback: Callable[[Event], None] | None = None,
    ) -> tuple[SubscriptionId, SubscriptionStatus]:
        """Subscribe to events from the event bus (Section 31.2)."""
        ...

    @abstractmethod
    def query_events(self, query: EventQuery) -> EventQueryResult:
        """Query historical events (Section 31.3)."""
        ...

    @abstractmethod
    def start_replay(self, request: ReplayRequest) -> ReplayResult:
        """Start an event replay session (Section 31.4)."""
        ...

    @abstractmethod
    def manage_dead_letters(self, operation: str, **kwargs: Any) -> Any:
        """Manage dead letter events (Section 31.5)."""
        ...

    @abstractmethod
    def manage_subscriptions(self, operation: str, **kwargs: Any) -> Any:
        """Manage event subscriptions (Section 31.6)."""
        ...
