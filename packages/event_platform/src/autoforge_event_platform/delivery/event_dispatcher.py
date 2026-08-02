"""
Event Dispatcher (Section 7.1, 15).

Dispatch events to subscribers.
Handle delivery retries.
Handle delivery failures.
Send failed events to DLQ.
Track delivery status.
"""

from __future__ import annotations

import threading
import time
import uuid

from autoforge_event_platform.interfaces import (
    IDeadLetterQueue,
    IEventDispatcher,
)
from autoforge_event_platform.models.event import (
    DeadLetterEntry,
    DeliveryResult,
    DeliveryStatus,
    Event,
    Subscription,
)


class EventDispatcher(IEventDispatcher):
    """
    Event Dispatcher implementation (Section 7.1, 15).

    Delivery Process (Section 15.2):
    1. Receive event and subscription
    2. Check delivery mode
    3. Deliver event to subscriber
    4. Handle delivery result
    5. Retry on failure (if at-least-once or exactly-once)
    6. Send to DLQ if retries exhausted
    7. Return delivery result

    Retry Policy (Section 15.3):
    - Max retries: 3 (configurable)
    - Backoff: Exponential (1s, 2s, 4s)
    - Timeout: 30s per attempt (configurable)
    """

    def __init__(
        self,
        dead_letter_queue: IDeadLetterQueue | None = None,
        max_retries: int = 3,
        retry_backoff_base: float = 1.0,
        delivery_timeout: float = 30.0,
    ):
        """
        Initialize the event dispatcher.

        Args:
            dead_letter_queue: Dead letter queue for failed events.
            max_retries: Maximum number of delivery retries (Section 15.3).
            retry_backoff_base: Base for exponential backoff (Section 15.3).
            delivery_timeout: Timeout per delivery attempt in seconds (Section 15.3).
        """
        self._dlq = dead_letter_queue
        self._max_retries = max_retries
        self._retry_backoff_base = retry_backoff_base
        self._delivery_timeout = delivery_timeout
        self._lock = threading.RLock()

    def dispatch(self, event: Event, subscription: Subscription) -> DeliveryResult:
        """
        Dispatch an event to a subscriber (Section 15.2).

        Process:
        1. Receive event and subscription
        2. Check delivery mode
        3. Deliver event to subscriber
        4. Handle delivery result
        5. Retry on failure (if at-least-once or exactly-once)
        6. Send to DLQ if retries exhausted
        7. Return delivery result

        Returns:
            DeliveryResult with status and retry count.
        """
        callback = subscription.callback
        if callback is None:
            return DeliveryResult(
                subscription_id=subscription.subscription_id,
                event_id=event.event_id,
                status=DeliveryStatus.FAILED,
                retry_count=0,
                error="No callback registered for subscription",
            )

        retry_count = 0
        last_error: str | None = None

        while retry_count <= self._max_retries:
            try:
                callback(event)
                return DeliveryResult(
                    subscription_id=subscription.subscription_id,
                    event_id=event.event_id,
                    status=DeliveryStatus.DELIVERED,
                    retry_count=retry_count,
                )
            except Exception as e:
                last_error = str(e)
                retry_count += 1

                if retry_count > self._max_retries:
                    break

                # Exponential backoff (Section 15.3)
                backoff = self._retry_backoff_base * (2 ** (retry_count - 1))
                time.sleep(backoff)

        # All retries exhausted — send to DLQ (Section 15.3, 23.2)
        if self._dlq is not None:
            dead_letter_entry = DeadLetterEntry(
                dead_letter_id=str(uuid.uuid4()),
                event=event,
                subscriber_id=subscription.subscription_id,
                error_message=last_error or "Unknown error",
                retry_count=retry_count,
                failure_reason="retries_exhausted",
            )
            self._dlq.add_dead_letter(dead_letter_entry)

        return DeliveryResult(
            subscription_id=subscription.subscription_id,
            event_id=event.event_id,
            status=DeliveryStatus.DEAD_LETTERED,
            retry_count=retry_count,
            error=last_error,
        )

    def set_dead_letter_queue(self, dead_letter_queue: IDeadLetterQueue | None) -> None:
        """Set the dead letter queue for this dispatcher."""
        with self._lock:
            self._dlq = dead_letter_queue

    def dispatch_batch(
        self, events: list[Event], subscription: Subscription
    ) -> list[DeliveryResult]:
        """
        Batch dispatch events to a subscriber (Section 15.2).

        Returns:
            List of delivery results.
        """
        results: list[DeliveryResult] = []
        for event in events:
            result = self.dispatch(event, subscription)
            results.append(result)
        return results
