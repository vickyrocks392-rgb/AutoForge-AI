"""
Priority Queue (Section 7.1, 15.2).

Manage event priority queues.
Order events by priority.
Handle priority-based delivery.
"""

from __future__ import annotations

import heapq
import threading
import uuid
from typing import Any

from autoforge_event_platform.models.event import Event, Priority


class PriorityQueue:
    """
    Priority Queue implementation (Section 7.1, 15.2).

    Priority Levels (Section 15.2):
    - Critical: Delivered immediately
    - High: Delivered before normal and low
    - Normal: Default priority
    - Low: Delivered last

    Queue Behavior:
    - Events are ordered by priority
    - Within the same priority, events are ordered by timestamp
    - Critical events are always delivered first
    """

    _PRIORITY_ORDER = {
        Priority.CRITICAL: 0,
        Priority.HIGH: 1,
        Priority.NORMAL: 2,
        Priority.LOW: 3,
    }

    def __init__(self):
        """Initialize the priority queue."""
        self._queue: list[tuple[int, float, uuid.UUID, Event]] = []
        self._lock = threading.RLock()

    def enqueue(self, event: Event) -> None:
        """
        Add an event to the priority queue (Section 15.2).

        Events are ordered by:
        1. Priority (critical first)
        2. Timestamp (earlier first)
        3. Event ID (for tie-breaking)
        """
        with self._lock:
            priority_rank = self._PRIORITY_ORDER.get(event.priority, 2)
            timestamp_rank = event.timestamp.timestamp()
            heapq.heappush(
                self._queue,
                (priority_rank, timestamp_rank, event.event_id, event),
            )

    def dequeue(self) -> Event | None:
        """
        Remove and return the highest-priority event (Section 15.2).

        Returns:
            The highest-priority event, or None if queue is empty.
        """
        with self._lock:
            if not self._queue:
                return None
            _, _, _, event = heapq.heappop(self._queue)
            return event

    def peek(self) -> Event | None:
        """
        Return the highest-priority event without removing it.

        Returns:
            The highest-priority event, or None if queue is empty.
        """
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][3]

    def size(self) -> int:
        """Return the number of events in the queue."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        with self._lock:
            return len(self._queue) == 0

    def clear(self) -> None:
        """Clear all events from the queue."""
        with self._lock:
            self._queue.clear()

    def get_all(self) -> list[Event]:
        """Return all events in priority order without removing them."""
        with self._lock:
            sorted_queue = sorted(self._queue)
            return [item[3] for item in sorted_queue]
