"""
Event Query Engine (Section 7.4, 19).

Query event history.
Support complex queries.
Filter events for replay.
Order events for replay.
Return event streams.
"""

from __future__ import annotations

import threading
from typing import Any

from autoforge_event_platform.interfaces import IEventQueryEngine
from autoforge_event_platform.models.event import (
    Event,
    EventCategory,
    EventQuery,
    EventQueryResult,
    EventType,
)
from autoforge_event_platform.persistence.event_history_store import EventHistoryStore


class EventQueryEngine(IEventQueryEngine):
    """
    Event Query Engine implementation (Section 7.4, 19).

    Provides rich query APIs for event history (Section 19.2).
    """

    def __init__(self, history_store: EventHistoryStore | None = None):
        """
        Initialize the event query engine.

        Args:
            history_store: Event history store for querying.
        """
        self._history_store = history_store or EventHistoryStore()
        self._lock = threading.RLock()

    def query_events(self, query: EventQuery) -> EventQueryResult:
        """
        Query historical events (Section 6.3, 19.2).

        Behavior:
        1. Parse and validate query
        2. Execute query against event history
        3. Apply filters and sorting
        4. Paginate results
        5. Return events and metadata

        Returns:
            EventQueryResult with events, total_count, and has_more.
        """
        with self._lock:
            return self._history_store.query(query)

    def query_by_event_type(
        self,
        event_types: list[EventType],
        time_range: tuple[Any, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventQueryResult:
        """Query by event type (Section 19.2.1)."""
        query = EventQuery(
            event_types=event_types,
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        return self.query_events(query)

    def query_by_event_category(
        self,
        event_categories: list[EventCategory],
        time_range: tuple[Any, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventQueryResult:
        """Query by event category (Section 19.2.2)."""
        query = EventQuery(
            event_categories=event_categories,
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        return self.query_events(query)

    def query_by_project(
        self,
        project_id: Any,
        time_range: tuple[Any, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventQueryResult:
        """Query by project ID (Section 19.2.3)."""
        import uuid as uuid_module
        query = EventQuery(
            project_id=project_id if isinstance(project_id, uuid_module.UUID) else uuid_module.UUID(str(project_id)),
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        return self.query_events(query)

    def query_by_correlation_id(
        self,
        correlation_id: Any,
        time_range: tuple[Any, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventQueryResult:
        """Query by correlation ID (Section 19.2.4)."""
        import uuid as uuid_module
        query = EventQuery(
            correlation_id=correlation_id if isinstance(correlation_id, uuid_module.UUID) else uuid_module.UUID(str(correlation_id)),
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        return self.query_events(query)

    def query_by_source(
        self,
        source: str,
        time_range: tuple[Any, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventQueryResult:
        """Query by source (Section 19.2.5)."""
        query = EventQuery(
            source=source,
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
        return self.query_events(query)

    def count_events(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[EventCategory] | None = None,
        time_range: tuple[Any, Any] | None = None,
        group_by: str | None = None,
    ) -> dict[str, int]:
        """Count events with optional grouping (Section 19.3)."""
        with self._lock:
            return self._history_store.count_events(
                event_types=event_types,
                event_categories=event_categories,
                time_range=time_range,
                group_by=group_by,
            )

    def aggregate_metrics(
        self,
        metric: str,
        time_range: tuple[Any, Any] | None = None,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate metrics from event history (Section 19.3)."""
        with self._lock:
            return self._history_store.aggregate_metrics(
                metric=metric,
                time_range=time_range,
                group_by=group_by,
            )

    def export_events(
        self,
        query: EventQuery,
        format: str = "json",
    ) -> str:
        """Export event history (Section 19.4)."""
        with self._lock:
            return self._history_store.export_events(query, format)
