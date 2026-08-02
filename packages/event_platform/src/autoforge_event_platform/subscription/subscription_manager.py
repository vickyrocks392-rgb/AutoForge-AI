"""
Event Subscription Manager (Section 14, 6.6).

Manage event subscriptions.
Validate subscriptions.
Route events to subscribers.
Manage subscription lifecycle.
Support subscription filters.
Handle subscriber failures.
Manage subscription state.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from autoforge_event_platform.interfaces import (
    IEventFilterEngine,
    IEventRouter,
    IEventSubscriptionManager,
)
from autoforge_event_platform.models.event import (
    Event,
    EventCategory,
    EventType,
    Subscription,
    SubscriptionId,
    SubscriptionRequest,
    SubscriptionStatus,
)
from autoforge_event_platform.routing.filter_engine import FilterEngine


class SubscriptionManager(IEventSubscriptionManager):
    """
    Event Subscription Manager implementation (Section 14, 6.6).

    Subscription Flow (Section 14.1):
    1. Subscriber creates subscription
    2. Event Platform validates subscription
    3. Event Platform registers subscription
    4. Event Platform begins delivering events
    5. Event Platform delivers matching events
    6. Subscriber processes events
    7. Subscriber returns confirmations

    Subscription Types (Section 14.3):
    - Type-Based Subscription: Subscribe to specific event types
    - Category-Based Subscription: Subscribe to event category
    - Filtered Subscription: Subscribe with filter expression
    """

    def __init__(
        self,
        router: IEventRouter | None = None,
        filter_engine: IEventFilterEngine | None = None,
    ):
        """
        Initialize the subscription manager.

        Args:
            router: Event router for registering subscriptions.
            filter_engine: Filter engine for validating filters.
        """
        self._router = router
        self._filter_engine = filter_engine or FilterEngine()
        self._subscriptions: dict[SubscriptionId, Subscription] = {}
        self._lock = threading.RLock()

    def subscribe(
        self, request: SubscriptionRequest
    ) -> tuple[SubscriptionId, SubscriptionStatus, datetime]:
        """
        Subscribe to events from the event bus (Section 6.2, 14.2).

        Behavior:
        1. Validate subscription request
        2. Create subscription record
        3. Register subscription with router
        4. Begin delivering matching events
        5. Return subscription ID and status

        Returns:
            Tuple of (subscription_id, status, timestamp).
        """
        with self._lock:
            # Step 1: Validate subscription request (Section 14.2 Step 2)
            validation_errors = request.validate_request()
            if validation_errors:
                return (
                    "",
                    SubscriptionStatus.FAILED,
                    datetime.now(timezone.utc),
                )

            # Validate filter expression (Section 14.2 Step 2)
            if request.filter:
                filter_result = self._filter_engine.validate_filter(request.filter)
                if not filter_result.valid:
                    return (
                        "",
                        SubscriptionStatus.FAILED,
                        datetime.now(timezone.utc),
                    )

            # Step 2: Create subscription record (Section 14.2 Step 3)
            subscription_id = str(uuid.uuid4())
            subscription = Subscription(
                subscription_id=subscription_id,
                event_types=request.event_types,
                event_categories=request.event_categories,
                filter=request.filter,
                delivery_mode=request.delivery_mode,
                ordering_guarantee=request.ordering_guarantee,
                status=SubscriptionStatus.ACTIVE,
                callback=request.callback,
            )

            # Step 3: Store subscription
            self._subscriptions[subscription_id] = subscription

            # Step 4: Register with router
            if self._router is not None:
                self._router.register_subscription(subscription)

            # Step 5: Begin delivering events (handled by Event Bus)

            return (
                subscription_id,
                SubscriptionStatus.ACTIVE,
                datetime.now(timezone.utc),
            )

    def get_subscription(self, subscription_id: SubscriptionId) -> Subscription | None:
        """Get subscription details (Section 6.6 — get)."""
        with self._lock:
            return self._subscriptions.get(subscription_id)

    def update_subscription(
        self, subscription_id: SubscriptionId, request: SubscriptionRequest
    ) -> Subscription | None:
        """Update subscription (Section 6.6 — update)."""
        with self._lock:
            existing = self._subscriptions.get(subscription_id)
            if existing is None:
                return None

            # Validate the update
            validation_errors = request.validate_request()
            if validation_errors:
                return None

            # Create updated subscription
            updated = Subscription(
                subscription_id=subscription_id,
                event_types=request.event_types,
                event_categories=request.event_categories,
                filter=request.filter,
                delivery_mode=request.delivery_mode,
                ordering_guarantee=request.ordering_guarantee,
                status=existing.status,
                callback=request.callback,
            )

            self._subscriptions[subscription_id] = updated

            # Update router registration
            if self._router is not None:
                self._router.unregister_subscription(subscription_id)
                self._router.register_subscription(updated)

            return updated

    def delete_subscription(self, subscription_id: SubscriptionId) -> bool:
        """
        Delete subscription (Section 6.6 — delete, 14.4).

        Process:
        1. Look up subscription
        2. Stop delivering events
        3. Remove subscription from registry
        4. Publish subscription.deleted event
        5. Return success
        """
        with self._lock:
            subscription = self._subscriptions.pop(subscription_id, None)
            if subscription is None:
                return False

            # Unregister from router
            if self._router is not None:
                self._router.unregister_subscription(subscription_id)

            return True

    def list_subscriptions(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[EventCategory] | None = None,
    ) -> list[Subscription]:
        """List subscriptions (Section 6.6 — list)."""
        with self._lock:
            results = list(self._subscriptions.values())

            if event_types:
                results = [
                    s
                    for s in results
                    if s.event_types and any(et in s.event_types for et in event_types)
                ]

            if event_categories:
                results = [
                    s
                    for s in results
                    if s.event_categories
                    and any(ec in s.event_categories for ec in event_categories)
                ]

            return results

    def get_all_subscriptions(self) -> list[Subscription]:
        """Get all subscriptions."""
        with self._lock:
            return list(self._subscriptions.values())

    def get_subscriptions_for_event(self, event: Event) -> list[Subscription]:
        """Get all subscriptions that match an event."""
        with self._lock:
            results: list[Subscription] = []
            for subscription in self._subscriptions.values():
                if subscription.status.value != "active":
                    continue

                # Check type match
                if subscription.event_types and event.event_type in subscription.event_types:
                    results.append(subscription)
                    continue

                # Check category match
                if subscription.event_categories and event.event_category in subscription.event_categories:
                    results.append(subscription)
                    continue

            return results
