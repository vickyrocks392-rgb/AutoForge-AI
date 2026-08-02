"""
Event Reader (Section 7.3, 18).

Reads events from persistent storage.
Supports queries.
Handles read failures.
Caches frequently accessed events.
Returns event data.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Any

from autoforge_event_platform.models.event import (
    Event,
    EventCategory,
    EventQuery,
    EventQueryResult,
    EventType,
)


class EventReader:
    """
    Event Reader implementation (Section 7.3, 18).

    Read Guarantees (Section 18.2):
    - Read is consistent
    - Read reflects all persisted events
    - Read is recoverable
    """

    def __init__(self, event_writer: Any):
        """
        Initialize the event reader.

        Args:
            event_writer: The event writer to read from.
        """
        self._writer = event_writer
        self._cache: dict[uuid.UUID, Event] = {}
        self._lock = threading.RLock()

    def read(self, event_id: uuid.UUID) -> Event | None:
        """
        Read an event by ID (Section 18.2).

        Returns:
            The event, or None if not found.
        """
        with self._lock:
            # Check cache first
            if event_id in self._cache:
                return self._cache[event_id]

            # Read from storage
            events = self._writer.get_all()
            for event in events:
                if event.event_id == event_id:
                    self._cache[event_id] = event
                    return event

            return None

    def query(self, query: EventQuery) -> EventQueryResult:
        """
        Query events from storage (Section 18.2, 19).

        Supports filtering by:
        - Event types
        - Event categories
        - Project ID
        - Correlation ID
        - Source
        - Time range

        Returns:
            EventQueryResult with events, total_count, and has_more.
        """
        with self._lock:
            events = self._writer.get_all()

            # Apply filters
            filtered = self._apply_filters(events, query)

            # Apply sorting
            filtered = self._apply_sorting(filtered, query.order_by)

            # Get total count before pagination
            total_count = len(filtered)

            # Apply pagination
            offset = query.offset
            limit = query.limit
            paginated = filtered[offset : offset + limit]
            has_more = (offset + limit) < total_count

            return EventQueryResult(
                events=paginated,
                total_count=total_count,
                has_more=has_more,
            )

    def _apply_filters(self, events: list[Event], query: EventQuery) -> list[Event]:
        """Apply query filters to events."""
        result = events

        # Filter by event types
        if query.event_types:
            result = [e for e in result if e.event_type in query.event_types]

        # Filter by event categories
        if query.event_categories:
            result = [e for e in result if e.event_category in query.event_categories]

        # Filter by project ID (from payload or metadata)
        if query.project_id:
            result = [
                e
                for e in result
                if e.payload.get("projectId") == str(query.project_id)
                or e.metadata.get("projectId") == str(query.project_id)
            ]

        # Filter by correlation ID
        if query.correlation_id:
            result = [e for e in result if e.correlation_id == query.correlation_id]

        # Filter by source
        if query.source:
            result = [e for e in result if e.source == query.source]

        # Filter by time range
        if query.time_range:
            start_time, end_time = query.time_range
            result = [
                e
                for e in result
                if start_time <= e.timestamp <= end_time
            ]

        return result

    def _apply_sorting(self, events: list[Event], order_by: str) -> list[Event]:
        """Apply sorting to events."""
        if order_by == "timestamp":
            return sorted(events, key=lambda e: e.timestamp)
        elif order_by == "-timestamp":
            return sorted(events, key=lambda e: e.timestamp, reverse=True)
        elif order_by == "eventType":
            return sorted(events, key=lambda e: e.event_type.value)
        elif order_by == "priority":
            priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
            return sorted(events, key=lambda e: priority_order.get(e.priority.value, 2))
        return events

    def clear_cache(self) -> None:
        """Clear the read cache."""
        with self._lock:
            self._cache.clear()
