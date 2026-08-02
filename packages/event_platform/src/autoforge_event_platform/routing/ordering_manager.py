"""
Ordering Manager (Section 7.1, 16).

Preserve event ordering.
Assign sequence numbers.
Detect ordering violations.
Handle ordering guarantees.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from autoforge_event_platform.interfaces import IOrderingManager
from autoforge_event_platform.models.event import Event, OrderingGuarantee


class OrderingManager(IOrderingManager):
    """
    Ordering Manager implementation (Section 7.1, 16).

    Ordering Guarantees (Section 16.1):
    - None: No ordering guarantee
    - Per-Aggregate: Events for the same aggregate are ordered
    - Per-Stream: Events for the same stream are ordered
    - Global: All events are globally ordered

    Sequence Numbers (Section 16.2):
    - Per-Aggregate: Sequence number per aggregate
    - Per-Stream: Sequence number per stream
    - Global: Global sequence number
    """

    def __init__(self):
        """Initialize the ordering manager."""
        self._global_counter: int = 0
        self._aggregate_counters: dict[uuid.UUID, int] = {}
        self._stream_counters: dict[str, int] = {}
        self._lock = threading.RLock()

    def assign_sequence_number(
        self, event: Event, guarantee: OrderingGuarantee
    ) -> Event:
        """
        Assign a sequence number to an event (Section 16.2).

        Returns a new event with the sequence number assigned.
        Events are immutable, so we create a new event.
        """
        with self._lock:
            if guarantee == OrderingGuarantee.NONE:
                return event

            data = event.model_dump()

            if guarantee == OrderingGuarantee.PER_AGGREGATE:
                counter = self._aggregate_counters.get(event.aggregate_id, 0) + 1
                self._aggregate_counters[event.aggregate_id] = counter
                data["sequence_number"] = counter

            elif guarantee == OrderingGuarantee.PER_STREAM:
                stream_key = f"{event.event_type.value}:{event.aggregate_id}"
                counter = self._stream_counters.get(stream_key, 0) + 1
                self._stream_counters[stream_key] = counter
                data["sequence_number"] = counter

            elif guarantee == OrderingGuarantee.GLOBAL:
                self._global_counter += 1
                data["sequence_number"] = self._global_counter

            return Event.model_validate(data)

    def check_ordering(self, event: Event, guarantee: OrderingGuarantee) -> bool:
        """
        Check if an event maintains ordering (Section 16.3).

        Returns True if ordering is maintained.
        """
        with self._lock:
            if guarantee == OrderingGuarantee.NONE:
                return True

            if event.sequence_number is None:
                return False

            if guarantee == OrderingGuarantee.PER_AGGREGATE:
                expected = self._aggregate_counters.get(event.aggregate_id, 0)
                return event.sequence_number == expected + 1

            elif guarantee == OrderingGuarantee.PER_STREAM:
                stream_key = f"{event.event_type.value}:{event.aggregate_id}"
                expected = self._stream_counters.get(stream_key, 0)
                return event.sequence_number == expected + 1

            elif guarantee == OrderingGuarantee.GLOBAL:
                expected = self._global_counter
                return event.sequence_number == expected + 1

            return True

    def get_next_sequence_number(
        self, guarantee: OrderingGuarantee, aggregate_id: uuid.UUID | None = None
    ) -> int:
        """Get the next sequence number for a given ordering guarantee."""
        with self._lock:
            if guarantee == OrderingGuarantee.PER_AGGREGATE and aggregate_id:
                return self._aggregate_counters.get(aggregate_id, 0) + 1
            elif guarantee == OrderingGuarantee.GLOBAL:
                return self._global_counter + 1
            return 0

    def reset(self) -> None:
        """Reset all counters (for testing)."""
        with self._lock:
            self._global_counter = 0
            self._aggregate_counters.clear()
            self._stream_counters.clear()
