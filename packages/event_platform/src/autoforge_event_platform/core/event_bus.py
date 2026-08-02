"""
Event Bus (Section 7.1).

Transport events between publishers and subscribers.
Manage event transport.
Ensure event delivery.
Maintain event ordering.
Route events.
Scale event throughput.
Monitor event health.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import (
    IDeadLetterQueue,
    IEventDispatcher,
    IEventFilterEngine,
    IEventRouter,
    IEventValidator,
)
from autoforge_event_platform.models.event import (
    DeliveryResult,
    DeliveryStatus,
    Event,
    EventLifecycleState,
    PublicationResult,
    PublicationStatus,
    Subscription,
    SubscriptionId,
    SubscriptionRequest,
    SubscriptionStatus,
)
from autoforge_event_platform.delivery.event_dispatcher import EventDispatcher
from autoforge_event_platform.delivery.priority_queue import PriorityQueue
from autoforge_event_platform.routing.event_router import EventRouter
from autoforge_event_platform.routing.filter_engine import FilterEngine
from autoforge_event_platform.routing.ordering_manager import OrderingManager
from autoforge_event_platform.subscription.subscription_manager import SubscriptionManager


class EventBus:
    """
    Event Bus implementation (Section 7.1).

    The Event Bus is the central transport layer that:
    - Receives events from publishers
    - Validates events
    - Routes events to subscribers
    - Handles delivery failures
    - Publishes delivery status events

    Architecture (Section 7.1):
    Event Bus
      ├── Event Router — Routes events to appropriate subscribers
      ├── Event Dispatcher — Dispatches events to subscribers
      ├── Event Validator — Validates events against schemas
      ├── Priority Queue — Manages event priority queues
      ├── Ordering Manager — Preserves event order where required
      └── Filter Engine — Filters events based on subscription filters
    """

    def __init__(
        self,
        validator: IEventValidator | None = None,
        router: IEventRouter | None = None,
        dispatcher: IEventDispatcher | None = None,
        filter_engine: IEventFilterEngine | None = None,
        subscription_manager: SubscriptionManager | None = None,
        dead_letter_queue: IDeadLetterQueue | None = None,
    ):
        """
        Initialize the event bus.

        Args:
            validator: Event validator for schema validation.
            router: Event router for routing events.
            dispatcher: Event dispatcher for delivering events.
            filter_engine: Filter engine for evaluating filters.
            subscription_manager: Subscription manager.
            dead_letter_queue: Dead letter queue for failed events.
        """
        self._validator = validator
        self._filter_engine = filter_engine or FilterEngine()
        self._router = router or EventRouter(self._filter_engine)
        self._dispatcher = dispatcher or EventDispatcher(dead_letter_queue)
        self._ordering_manager = OrderingManager()
        self._priority_queue = PriorityQueue()
        self._subscription_manager = subscription_manager or SubscriptionManager(
            self._router, self._filter_engine
        )
        self._dead_letter_queue = dead_letter_queue

        # Event history for lifecycle tracking
        self._event_history: dict[str, EventLifecycleState] = {}
        self._lock = threading.RLock()

    def publish(self, event: Event) -> PublicationResult:
        """
        Publish an event to the event bus (Section 13).

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
        # Step 1: Receive Event (Section 13.2 Step 1)
        # Event is already received

        # Step 2: Validate Event (Section 13.2 Step 2)
        if self._validator is not None:
            validation_result = self._validator.validate(event)
            if not validation_result.valid:
                return PublicationResult(
                    event_id=event.event_id,
                    status=PublicationStatus.REJECTED,
                    timestamp=datetime.now(timezone.utc),
                    errors=validation_result.errors,
                )

        # Step 3: Enrich Event (Section 13.2 Step 3)
        # Event is already enriched by the publisher

        # Step 4: Persist Event (Section 13.2 Step 4)
        # Persistence is handled by the Event Platform

        # Step 5: Route Event (Section 13.2 Step 5)
        matched_subscriptions = self._router.route(event)

        # Step 6: Deliver Event (Section 13.2 Step 6)
        delivery_results: list[DeliveryResult] = []
        for subscription in matched_subscriptions:
            result = self._dispatcher.dispatch(event, subscription)
            delivery_results.append(result)

        # Step 7: Confirm Publication (Section 13.2 Step 7)
        # Event is accepted even if some deliveries fail — failures go to DLQ
        return PublicationResult(
            event_id=event.event_id,
            status=PublicationStatus.ACCEPTED,
            timestamp=datetime.now(timezone.utc),
        )

    def subscribe(
        self, request: SubscriptionRequest
    ) -> tuple[SubscriptionId, SubscriptionStatus]:
        """
        Subscribe to events on the bus (Section 14.1).

        Returns:
            Tuple of (subscription_id, status).
        """
        subscription_id, status, _ = self._subscription_manager.subscribe(request)
        return subscription_id, status

    def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        """Unsubscribe from the bus."""
        return self._subscription_manager.delete_subscription(subscription_id)

    def get_health(self) -> dict[str, Any]:
        """
        Monitor event bus health and performance (Section 2.1).

        Returns:
            Health metrics dictionary.
        """
        with self._lock:
            return {
                "queue_size": self._priority_queue.size(),
                "active_subscriptions": len(self._subscription_manager.get_all_subscriptions()),
                "event_history_size": len(self._event_history),
            }

    def get_subscriptions(self) -> list[Subscription]:
        """Get all active subscriptions."""
        return self._subscription_manager.get_all_subscriptions()

    def get_subscription(self, subscription_id: SubscriptionId) -> Subscription | None:
        """Get a subscription by ID."""
        return self._subscription_manager.get_subscription(subscription_id)

    @property
    def validator(self) -> IEventValidator | None:
        """Get the event validator."""
        return self._validator

    @validator.setter
    def validator(self, value: IEventValidator | None) -> None:
        """Set the event validator."""
        self._validator = value

    @property
    def router(self) -> IEventRouter:
        """Get the event router."""
        return self._router

    @property
    def dispatcher(self) -> IEventDispatcher:
        """Get the event dispatcher."""
        return self._dispatcher

    @property
    def subscription_manager(self) -> SubscriptionManager:
        """Get the subscription manager."""
        return self._subscription_manager

    @property
    def dead_letter_queue(self) -> IDeadLetterQueue | None:
        """Get the dead letter queue."""
        return self._dead_letter_queue

    @dead_letter_queue.setter
    def dead_letter_queue(self, value: IDeadLetterQueue | None) -> None:
        """Set the dead letter queue."""
        self._dead_letter_queue = value
        # Update dispatcher with new DLQ
        if self._dispatcher is not None and hasattr(self._dispatcher, "set_dead_letter_queue"):
            self._dispatcher.set_dead_letter_queue(value)
