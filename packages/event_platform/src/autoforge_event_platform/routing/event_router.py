"""
Event Router (Section 7.1, 12).

Route events to appropriate subscribers.
Match events to subscriptions.
Apply routing rules.
Handle routing failures.
Optimize routing performance.
"""

from __future__ import annotations

import threading
from typing import Any

from autoforge_event_platform.interfaces import IEventFilterEngine, IEventRouter
from autoforge_event_platform.models.event import Event, Subscription


class EventRouter(IEventRouter):
    """
    Event Router implementation (Section 7.1, 12).

    Routing Process (Section 12.1):
    1. Receive event
    2. Match event to subscriptions
    3. Apply filters
    4. Return matched subscriptions
    """

    def __init__(self, filter_engine: IEventFilterEngine | None = None):
        """
        Initialize the event router.

        Args:
            filter_engine: Filter engine for evaluating subscription filters.
        """
        self._filter_engine = filter_engine
        self._subscriptions: list[Subscription] = []
        self._lock = threading.RLock()

    def register_subscription(self, subscription: Subscription) -> None:
        """Register a subscription with the router (Section 12.1 Step 2)."""
        with self._lock:
            self._subscriptions.append(subscription)

    def unregister_subscription(self, subscription_id: str) -> None:
        """Unregister a subscription from the router (Section 12.1 Step 2)."""
        with self._lock:
            self._subscriptions = [
                s for s in self._subscriptions if s.subscription_id != subscription_id
            ]

    def route(self, event: Event) -> list[Subscription]:
        """
        Route an event to matching subscriptions (Section 12.1).

        Process:
        1. Receive event
        2. Match event to subscriptions
        3. Apply filters
        4. Return matched subscriptions

        Returns:
            List of subscriptions that match the event.
        """
        with self._lock:
            matched: list[Subscription] = []

            for subscription in self._subscriptions:
                if not self._matches_subscription(event, subscription):
                    continue

                # Apply filter if present
                if subscription.filter and self._filter_engine is not None:
                    if not self._filter_engine.evaluate(event, subscription.filter):
                        continue

                matched.append(subscription)

            return matched

    def _matches_subscription(self, event: Event, subscription: Subscription) -> bool:
        """Check if an event matches a subscription's type/category criteria."""
        # Check event types
        if subscription.event_types:
            if event.event_type not in subscription.event_types:
                return False

        # Check event categories
        if subscription.event_categories:
            if event.event_category not in subscription.event_categories:
                return False

        return True

    def get_subscriptions(self) -> list[Subscription]:
        """Get all registered subscriptions."""
        with self._lock:
            return list(self._subscriptions)
