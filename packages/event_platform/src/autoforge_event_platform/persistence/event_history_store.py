"""
Event History Store (Section 7.3, 19).

Maintain complete history of all events.
Query event history.
Filter event history by criteria.
Aggregate event history for analytics.
Correlate event history.
Visualize event history.
Export event history for analysis.
"""

from __future__ import annotations

import csv
import io
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import IEventHistoryStore
from autoforge_event_platform.models.event import (
    Event,
    EventCategory,
    EventQuery,
    EventQueryResult,
    EventType,
)
from autoforge_event_platform.persistence.event_persistence import EventPersistence


class EventHistoryStore(IEventHistoryStore):
    """
    Event History Store implementation (Section 7.3, 19).

    History Characteristics (Section 19.1):
    - Complete: All events are recorded
    - Immutable: Events cannot be modified or deleted
    - Ordered: Events are ordered by timestamp and sequence
    - Indexed: Events are indexed for efficient querying
    - Durable: Events are persisted durably
    """

    def __init__(self, persistence: EventPersistence | None = None):
        """
        Initialize the event history store.

        Args:
            persistence: Event persistence layer for storage.
        """
        self._persistence = persistence or EventPersistence()
        self._lock = threading.RLock()

    def store(self, event: Event) -> bool:
        """
        Store an event in history (Section 19.1).

        Returns:
            True if storage succeeded.
        """
        with self._lock:
            return self._persistence.write(event)

    def get(self, event_id: uuid.UUID) -> Event | None:
        """
        Retrieve an event from history by ID (Section 19.1).

        Returns:
            The event, or None if not found.
        """
        with self._lock:
            return self._persistence.read(event_id)

    def query(self, query: EventQuery) -> EventQueryResult:
        """
        Query event history (Section 19.2).

        Supports queries by:
        - Event type (Section 19.2.1)
        - Event category (Section 19.2.2)
        - Project ID (Section 19.2.3)
        - Correlation ID (Section 19.2.4)
        - Source (Section 19.2.5)
        - Time range

        Returns:
            EventQueryResult with events, total_count, and has_more.
        """
        with self._lock:
            return self._persistence.query(query)

    def count_events(
        self,
        event_types: list[EventType] | None = None,
        event_categories: list[EventCategory] | None = None,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, int]:
        """
        Count events with optional grouping (Section 19.3).

        Returns:
            Dictionary of counts, grouped by the specified dimension.
        """
        with self._lock:
            query = EventQuery(
                event_types=event_types,
                event_categories=event_categories,
                time_range=time_range,
                limit=10000,
                offset=0,
            )
            result = self._persistence.query(query)

            if group_by is None:
                return {"total": result.total_count}

            counts: dict[str, int] = {}
            for event in result.events:
                if group_by == "eventType":
                    key = event.event_type.value
                elif group_by == "eventCategory":
                    key = event.event_category.value
                elif group_by == "source":
                    key = event.source
                elif group_by == "priority":
                    key = event.priority.value
                elif group_by == "deliveryMode":
                    key = event.delivery_mode.value
                elif group_by == "day":
                    key = event.timestamp.strftime("%Y-%m-%d")
                else:
                    key = "unknown"

                counts[key] = counts.get(key, 0) + 1

            return counts

    def aggregate_metrics(
        self,
        metric: str,
        time_range: tuple[datetime, datetime] | None = None,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate metrics from event history (Section 19.3).

        Returns:
            Dictionary of aggregated metrics.
        """
        with self._lock:
            query = EventQuery(
                time_range=time_range,
                limit=10000,
                offset=0,
            )
            result = self._persistence.query(query)

            if group_by is None:
                return {"total": result.total_count}

            groups: dict[str, list[Event]] = {}
            for event in result.events:
                if group_by == "day":
                    key = event.timestamp.strftime("%Y-%m-%d")
                elif group_by == "eventType":
                    key = event.event_type.value
                elif group_by == "eventCategory":
                    key = event.event_category.value
                else:
                    key = "unknown"

                if key not in groups:
                    groups[key] = []
                groups[key].append(event)

            return {key: len(events) for key, events in groups.items()}

    def export_events(
        self,
        query: EventQuery,
        format: str = "json",
    ) -> str:
        """
        Export event history (Section 19.4).

        Export Formats:
        - JSON
        - CSV
        - Parquet (simulated as JSON for in-memory implementation)

        Returns:
            Export location or data as string.
        """
        with self._lock:
            result = self._persistence.query(query)

            if format == "json":
                return json.dumps(
                    [event.model_dump() for event in result.events],
                    default=str,
                    indent=2,
                )
            elif format == "csv":
                output = io.StringIO()
                if result.events:
                    fieldnames = [
                        "event_id",
                        "event_type",
                        "event_category",
                        "source",
                        "timestamp",
                        "version",
                        "correlation_id",
                        "causation_id",
                        "aggregate_id",
                        "aggregate_type",
                        "priority",
                        "delivery_mode",
                    ]
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    for event in result.events:
                        writer.writerow(
                            {
                                "event_id": str(event.event_id),
                                "event_type": event.event_type.value,
                                "event_category": event.event_category.value,
                                "source": event.source,
                                "timestamp": event.timestamp.isoformat(),
                                "version": event.version,
                                "correlation_id": str(event.correlation_id),
                                "causation_id": str(event.causation_id) if event.causation_id else "",
                                "aggregate_id": str(event.aggregate_id),
                                "aggregate_type": event.aggregate_type,
                                "priority": event.priority.value,
                                "delivery_mode": event.delivery_mode.value,
                            }
                        )
                return output.getvalue()
            elif format == "parquet":
                # Simulated parquet export (returns JSON for in-memory implementation)
                return json.dumps(
                    [event.model_dump() for event in result.events],
                    default=str,
                )
            else:
                raise ValueError(f"Unsupported export format: {format}")
