"""
Event Platform (top-level facade).

The Event Platform is the canonical communication backbone of AutoForge AI OS.
It is the single, authoritative system for event transport, delivery, and management.

This facade combines all Event Platform components:
- Event Bus (transport layer)
- Event Publisher (publication)
- Event Subscription Manager (subscription management)
- Event Query Engine (history queries)
- Event Replay Engine (replay)
- Dead Letter Queue (failed event management)
- Event Schema Registry (schema management)
- Event Validator (validation)
- Event Persistence (durable storage)
- Event History Store (history)
- Event Correlation Engine (correlation)
- Event Filter Engine (filtering)
- Event Router (routing)
- Event Dispatcher (delivery)
- Priority Queue (priority management)
- Ordering Manager (ordering)
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from autoforge_event_platform.interfaces import (
    IDeadLetterQueue,
    IEventBus,
    IEventCorrelationEngine,
    IEventDispatcher,
    IEventFilterEngine,
    IEventHistoryStore,
    IEventPersistence,
    IEventPublisher,
    IEventQueryEngine,
    IEventReplayEngine,
    IEventRouter,
    IEventSchemaRegistry,
    IEventSubscriptionManager,
    IEventValidator,
    IEventPlatform,
)
from autoforge_event_platform.models.event import (
    DeadLetterAnalysis,
    DeadLetterQuery,
    DeadLetterResult,
    DeliveryMode,
    Event,
    EventCategory,
    EventQuery,
    EventQueryResult,
    EventType,
    OrderingGuarantee,
    Priority,
    PublicationResult,
    PublicationStatus,
    ReplayRequest,
    ReplayResult,
    ReplaySource,
    ReplayStatus,
    Subscription,
    SubscriptionId,
    SubscriptionRequest,
    SubscriptionStatus,
)
from autoforge_event_platform.core.dead_letter_queue import DeadLetterQueue
from autoforge_event_platform.core.event_bus import EventBus
from autoforge_event_platform.core.event_publisher import EventPublisher
from autoforge_event_platform.delivery.event_dispatcher import EventDispatcher
from autoforge_event_platform.delivery.priority_queue import PriorityQueue
from autoforge_event_platform.persistence.event_history_store import EventHistoryStore
from autoforge_event_platform.persistence.event_persistence import EventPersistence
from autoforge_event_platform.persistence.event_validator import EventValidator
from autoforge_event_platform.persistence.schema_registry import SchemaRegistry
from autoforge_event_platform.replay.correlation_engine import CorrelationEngine
from autoforge_event_platform.replay.event_query_engine import EventQueryEngine
from autoforge_event_platform.replay.history_query import HistoryQuery
from autoforge_event_platform.replay.replay_engine import ReplayEngine
from autoforge_event_platform.routing.event_router import EventRouter
from autoforge_event_platform.routing.filter_engine import FilterEngine
from autoforge_event_platform.routing.ordering_manager import OrderingManager
from autoforge_event_platform.subscription.subscription_manager import SubscriptionManager


class EventPlatform(IEventPlatform):
    """
    Event Platform facade (Section 6).

    Provides the public API surface defined in Section 6 and Section 31.

    Public Interfaces (Section 6):
    - 6.1 Event Publication Interface
    - 6.2 Event Subscription Interface
    - 6.3 Event Query Interface
    - 6.4 Event Replay Interface
    - 6.5 Dead Letter Queue Interface
    - 6.6 Event Subscription Management Interface

    Internal Components (Section 7):
    - 7.1 Event Bus (Router, Dispatcher, Validator, Priority Queue, Ordering Manager, Filter Engine)
    - 7.2 Event Schema Registry (Schema Registry, Schema Validator, Schema Transformer)
    - 7.3 Event Persistence (Event Writer, Event Reader, Event Archiver)
    - 7.4 Event Replay Engine (Replay Controller, History Query, Correlation Engine)
    - 7.5 Dead Letter Queue (DLQ Writer, DLQ Reader, DLQ Analyzer)
    """

    def __init__(
        self,
        schema_registry: IEventSchemaRegistry | None = None,
        validator: IEventValidator | None = None,
        persistence: IEventPersistence | None = None,
        history_store: IEventHistoryStore | None = None,
        filter_engine: IEventFilterEngine | None = None,
        router: IEventRouter | None = None,
        dispatcher: IEventDispatcher | None = None,
        subscription_manager: IEventSubscriptionManager | None = None,
        replay_engine: IEventReplayEngine | None = None,
        query_engine: IEventQueryEngine | None = None,
        correlation_engine: IEventCorrelationEngine | None = None,
        dead_letter_queue: IDeadLetterQueue | None = None,
    ):
        """
        Initialize the Event Platform with dependency injection.

        All components are injectable to maintain interface-first architecture
        and avoid circular dependencies (Section 5.4).
        """
        # Core components
        self._schema_registry = schema_registry or SchemaRegistry()
        self._validator = validator or EventValidator(self._schema_registry)
        self._persistence = persistence or EventPersistence()
        self._history_store = history_store or EventHistoryStore(self._persistence)
        self._filter_engine = filter_engine or FilterEngine()
        self._router = router or EventRouter(self._filter_engine)
        self._dead_letter_queue = dead_letter_queue or DeadLetterQueue()
        self._dispatcher = dispatcher or EventDispatcher(self._dead_letter_queue)
        self._subscription_manager = subscription_manager or SubscriptionManager(
            self._router, self._filter_engine
        )
        self._replay_engine = replay_engine or ReplayEngine(
            HistoryQuery(self._history_store)
        )
        self._query_engine = query_engine or EventQueryEngine(self._history_store)
        self._correlation_engine = correlation_engine or CorrelationEngine(self._history_store)

        # Event Bus (combines router, dispatcher, validator, priority queue, ordering manager, filter engine)
        self._event_bus = EventBus(
            validator=self._validator,
            router=self._router,
            dispatcher=self._dispatcher,
            filter_engine=self._filter_engine,
            subscription_manager=self._subscription_manager,
            dead_letter_queue=self._dead_letter_queue,
        )

        # Event Publisher
        self._publisher = EventPublisher(
            validator=self._validator,
            schema_registry=self._schema_registry,
            persistence=self._persistence,
            router=self._router,
        )

        # Additional components
        self._priority_queue = PriorityQueue()
        self._ordering_manager = OrderingManager()

        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Section 6.1 — Event Publication Interface
    # ------------------------------------------------------------------

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

        Publication Flow (Section 13.1):
        1. Receive Event
        2. Validate Event
        3. Enrich Event
        4. Persist Event
        5. Route Event
        6. Deliver Event
        7. Confirm Publication

        Returns:
            PublicationResult with event_id, status, and timestamp.
        """
        # Step 1-4: Create, validate, enrich, and persist event
        result = self._publisher.publish(
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

        if result.status == PublicationStatus.REJECTED:
            return result

        # Step 5-7: Route, deliver, and confirm via Event Bus
        # Get the enriched event from persistence
        event = self._persistence.read(result.event_id)
        if event is None:
            return result

        # Route and deliver through the event bus
        bus_result = self._event_bus.publish(event)

        return bus_result

    def publish_event(self, event: Event) -> PublicationResult:
        """
        Publish a pre-constructed event (Section 13.2).

        Returns:
            PublicationResult with event_id, status, and timestamp.
        """
        return self._publisher.publish_event(event)

    # ------------------------------------------------------------------
    # Section 6.2 — Event Subscription Interface
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[EventCategory] | None = None,
        filter: str | None = None,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
        ordering_guarantee: OrderingGuarantee = OrderingGuarantee.NONE,
        callback: Callable[[Event], None] | None = None,
    ) -> tuple[SubscriptionId, SubscriptionStatus]:
        """
        Subscribe to events from the event bus (Section 31.2).

        Returns:
            Tuple of (subscription_id, status).
        """
        request = SubscriptionRequest(
            event_types=event_types,
            event_categories=event_categories,
            filter=filter,
            delivery_mode=delivery_mode,
            ordering_guarantee=ordering_guarantee,
            callback=callback,
        )
        return self._event_bus.subscribe(request)

    # ------------------------------------------------------------------
    # Section 6.3 — Event Query Interface
    # ------------------------------------------------------------------

    def query_events(self, query: EventQuery) -> EventQueryResult:
        """
        Query historical events (Section 31.3).

        Returns:
            EventQueryResult with events, total_count, and has_more.
        """
        return self._query_engine.query_events(query)

    # ------------------------------------------------------------------
    # Section 6.4 — Event Replay Interface
    # ------------------------------------------------------------------

    def start_replay(self, request: ReplayRequest) -> ReplayResult:
        """
        Start an event replay session (Section 31.4).

        Returns:
            ReplayResult with replay_id, status, and progress.
        """
        return self._replay_engine.start_replay(request)

    def pause_replay(self, replay_id: str) -> ReplayResult:
        """Pause a replay session (Section 17.3)."""
        return self._replay_engine.pause_replay(replay_id)

    def resume_replay(self, replay_id: str) -> ReplayResult:
        """Resume a paused replay session (Section 17.3)."""
        return self._replay_engine.resume_replay(replay_id)

    def stop_replay(self, replay_id: str) -> ReplayResult:
        """Stop a replay session (Section 17.3)."""
        return self._replay_engine.stop_replay(replay_id)

    def get_replay_status(self, replay_id: str) -> ReplayResult | None:
        """Get replay session status."""
        return self._replay_engine.get_replay_status(replay_id)

    # ------------------------------------------------------------------
    # Section 6.5 — Dead Letter Queue Interface
    # ------------------------------------------------------------------

    def manage_dead_letters(self, operation: str, **kwargs: Any) -> Any:
        """
        Manage dead letter events (Section 31.5).

        Operations:
        - list: List dead letter events
        - retry: Retry dead letter event
        - replay: Replay all dead letter events
        - delete: Delete dead letter event
        - analyze: Analyze dead letter patterns
        """
        if operation == "list":
            query = kwargs.get("query", DeadLetterQuery())
            return self._dead_letter_queue.list_dead_letters(query)
        elif operation == "retry":
            dead_letter_id = kwargs.get("dead_letter_id")
            return self._dead_letter_queue.retry_dead_letter(dead_letter_id)
        elif operation == "replay":
            query = kwargs.get("query", DeadLetterQuery())
            return self._dead_letter_queue.replay_dead_letters(query)
        elif operation == "delete":
            dead_letter_id = kwargs.get("dead_letter_id")
            return self._dead_letter_queue.delete_dead_letter(dead_letter_id)
        elif operation == "analyze":
            time_range = kwargs.get("time_range")
            return self._dead_letter_queue.analyze_dead_letters(time_range)
        else:
            raise ValueError(f"Unknown DLQ operation: {operation}")

    def list_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """List dead letter events (Section 23.3 — list)."""
        return self._dead_letter_queue.list_dead_letters(query)

    def retry_dead_letter(self, dead_letter_id: str) -> bool:
        """Retry a dead letter event (Section 23.3 — retry)."""
        return self._dead_letter_queue.retry_dead_letter(dead_letter_id)

    def replay_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """Replay all matching dead letter events (Section 23.3 — replay)."""
        return self._dead_letter_queue.replay_dead_letters(query)

    def delete_dead_letter(self, dead_letter_id: str) -> bool:
        """Delete a dead letter event (Section 23.3 — delete)."""
        return self._dead_letter_queue.delete_dead_letter(dead_letter_id)

    def analyze_dead_letters(
        self, time_range: tuple[datetime, datetime] | None = None
    ) -> DeadLetterAnalysis:
        """Analyze dead letter patterns (Section 23.3 — analyze)."""
        return self._dead_letter_queue.analyze_dead_letters(time_range)

    # ------------------------------------------------------------------
    # Section 6.6 — Event Subscription Management Interface
    # ------------------------------------------------------------------

    def manage_subscriptions(self, operation: str, **kwargs: Any) -> Any:
        """
        Manage event subscriptions (Section 31.6).

        Operations:
        - create: Create subscription
        - get: Get subscription details
        - update: Update subscription
        - delete: Delete subscription
        - list: List subscriptions
        """
        if operation == "create":
            request = kwargs.get("request")
            if request is None:
                raise ValueError("request is required for create operation")
            return self._subscription_manager.subscribe(request)
        elif operation == "get":
            subscription_id = kwargs.get("subscription_id")
            return self._subscription_manager.get_subscription(subscription_id)
        elif operation == "update":
            subscription_id = kwargs.get("subscription_id")
            request = kwargs.get("request")
            return self._subscription_manager.update_subscription(subscription_id, request)
        elif operation == "delete":
            subscription_id = kwargs.get("subscription_id")
            return self._subscription_manager.delete_subscription(subscription_id)
        elif operation == "list":
            event_types = kwargs.get("event_types")
            event_categories = kwargs.get("event_categories")
            return self._subscription_manager.list_subscriptions(
                event_types=event_types,
                event_categories=event_categories,
            )
        else:
            raise ValueError(f"Unknown subscription operation: {operation}")

    def get_subscription(self, subscription_id: SubscriptionId) -> Subscription | None:
        """Get subscription details (Section 6.6 — get)."""
        return self._subscription_manager.get_subscription(subscription_id)

    def update_subscription(
        self, subscription_id: SubscriptionId, request: SubscriptionRequest
    ) -> Subscription | None:
        """Update subscription (Section 6.6 — update)."""
        return self._subscription_manager.update_subscription(subscription_id, request)

    def delete_subscription(self, subscription_id: SubscriptionId) -> bool:
        """Delete subscription (Section 6.6 — delete)."""
        return self._subscription_manager.delete_subscription(subscription_id)

    def list_subscriptions(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[EventCategory] | None = None,
    ) -> list[Subscription]:
        """List subscriptions (Section 6.6 — list)."""
        return self._subscription_manager.list_subscriptions(
            event_types=event_types,
            event_categories=event_categories,
        )

    # ------------------------------------------------------------------
    # Section 7.2 — Schema Registry
    # ------------------------------------------------------------------

    def register_schema(self, schema: Any) -> bool:
        """Register a new event schema (Section 10.4)."""
        return self._schema_registry.register_schema(schema)

    def get_schema(self, event_type: EventType, version: str | None = None) -> Any:
        """Retrieve a schema for an event type (Section 10.4)."""
        return self._schema_registry.get_schema(event_type, version)

    def get_latest_schema_version(self, event_type: EventType) -> str | None:
        """Get the latest schema version for an event type."""
        return self._schema_registry.get_latest_version(event_type)

    def list_schemas(self) -> list[Any]:
        """List all registered schemas."""
        return self._schema_registry.list_schemas()

    def check_schema_compatibility(self, event_type: EventType, schema: Any) -> Any:
        """Check compatibility of a new schema version (Section 10.3)."""
        return self._schema_registry.check_compatibility(event_type, schema)

    def transform_event(self, event: Event, target_version: str) -> Event:
        """Transform an event between schema versions (Section 10.3)."""
        return self._schema_registry.transform_event(event, target_version)

    # ------------------------------------------------------------------
    # Section 7.4 — Correlation Engine
    # ------------------------------------------------------------------

    def query_by_correlation_id(self, correlation_id: uuid.UUID) -> list[Event]:
        """Query all events with a correlation ID (Section 20.3)."""
        return self._correlation_engine.query_by_correlation_id(correlation_id)

    def query_causation_chain(self, event_id: uuid.UUID) -> list[Event]:
        """Query the causation chain for an event (Section 20.3)."""
        return self._correlation_engine.query_causation_chain(event_id)

    def query_related_events(self, event_id: uuid.UUID) -> list[Event]:
        """Query all related events (Section 20.3)."""
        return self._correlation_engine.query_related_events(event_id)

    def group_by_aggregate(self, aggregate_id: uuid.UUID) -> list[Event]:
        """Group events by aggregate (Section 20.2)."""
        return self._correlation_engine.group_by_aggregate(aggregate_id)

    # ------------------------------------------------------------------
    # Section 7.1 — Event Bus
    # ------------------------------------------------------------------

    def get_event_bus(self) -> EventBus:
        """Get the event bus."""
        return self._event_bus

    def get_health(self) -> dict[str, Any]:
        """Monitor event bus health and performance (Section 2.1)."""
        return self._event_bus.get_health()

    # ------------------------------------------------------------------
    # Component accessors
    # ------------------------------------------------------------------

    @property
    def event_bus(self) -> EventBus:
        """Get the event bus."""
        return self._event_bus

    @property
    def publisher(self) -> EventPublisher:
        """Get the event publisher."""
        return self._publisher

    @property
    def router(self) -> IEventRouter:
        """Get the event router."""
        return self._router

    @property
    def dispatcher(self) -> IEventDispatcher:
        """Get the event dispatcher."""
        return self._dispatcher

    @property
    def validator(self) -> IEventValidator:
        """Get the event validator."""
        return self._validator

    @property
    def schema_registry(self) -> IEventSchemaRegistry:
        """Get the schema registry."""
        return self._schema_registry

    @property
    def persistence(self) -> IEventPersistence:
        """Get the event persistence."""
        return self._persistence

    @property
    def history_store(self) -> IEventHistoryStore:
        """Get the event history store."""
        return self._history_store

    @property
    def query_engine(self) -> IEventQueryEngine:
        """Get the event query engine."""
        return self._query_engine

    @property
    def replay_engine(self) -> IEventReplayEngine:
        """Get the event replay engine."""
        return self._replay_engine

    @property
    def correlation_engine(self) -> IEventCorrelationEngine:
        """Get the event correlation engine."""
        return self._correlation_engine

    @property
    def filter_engine(self) -> IEventFilterEngine:
        """Get the event filter engine."""
        return self._filter_engine

    @property
    def dead_letter_queue(self) -> IDeadLetterQueue:
        """Get the dead letter queue."""
        return self._dead_letter_queue

    @property
    def subscription_manager(self) -> IEventSubscriptionManager:
        """Get the subscription manager."""
        return self._subscription_manager

    @property
    def priority_queue(self) -> PriorityQueue:
        """Get the priority queue."""
        return self._priority_queue

    @property
    def ordering_manager(self) -> OrderingManager:
        """Get the ordering manager."""
        return self._ordering_manager
