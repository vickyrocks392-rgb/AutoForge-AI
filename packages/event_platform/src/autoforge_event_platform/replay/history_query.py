"""
History Query (Section 7.4, 17.2).

Queries event history.
Supports complex queries.
Filters events for replay.
Orders events for replay.
Returns event streams.
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
    ReplayRequest,
)
from autoforge_event_platform.persistence.event_history_store import EventHistoryStore


class HistoryQuery:
    """
    History Query implementation (Section 7.4, 17.2).

    Queries event history for replay.
    Supports filtering by:
    - Time range
    - Event types
    - Event categories
    - Project ID
    - Correlation ID
    - Source
    """

    def __init__(self, history_store: EventHistoryStore | None = None):
        """
        Initialize the history query.

        Args:
            history_store: Event history store for querying.
        """
        self._history_store = history_store or EventHistoryStore()
        self._lock = threading.RLock()

    def query_for_replay(self, request: ReplayRequest) -> list[Event]:
        """
        Query events for replay (Section 17.2 Step 2).

        Process:
        1. Query event history based on source
        2. Apply filters (event types, categories, project ID, etc.)
        3. Order events by timestamp or sequence
        4. Paginate events
        5. Return event stream

        Returns:
            List of events matching the replay request.
        """
        with self._lock:
            query = EventQuery(
                event_types=request.event_types,
                event_categories=request.event_categories,
                project_id=request.project_id,
                correlation_id=request.correlation_id,
                limit=10000,
                offset=0,
                order_by="timestamp",
            )

            # Apply source-based filtering
            if request.source == "from_timestamp" and request.from_timestamp:
                query = EventQuery(
                    event_types=request.event_types,
                    event_categories=request.event_categories,
                    project_id=request.project_id,
                    correlation_id=request.correlation_id,
                    time_range=(request.from_timestamp, datetime.max.replace(tzinfo=request.from_timestamp.tzinfo)),
                    limit=10000,
                    offset=0,
                    order_by="timestamp",
                )
            elif request.source == "from_event_id" and request.from_event_id:
                # Query from a specific event ID — get all events after that event's timestamp
                from_event = self._history_store.get(request.from_event_id)
                if from_event:
                    query = EventQuery(
                        event_types=request.event_types,
                        event_categories=request.event_categories,
                        project_id=request.project_id,
                        correlation_id=request.correlation_id,
                        time_range=(from_event.timestamp, datetime.max.replace(tzinfo=from_event.timestamp.tzinfo)),
                        limit=10000,
                        offset=0,
                        order_by="timestamp",
                    )
            elif request.source == "from_checkpoint" and request.from_checkpoint:
                # Query from a checkpoint — use checkpoint timestamp
                # In a real implementation, this would load the checkpoint
                # For now, we query all events
                pass
            elif request.source == "from_beginning":
                # Query all events
                pass

            result = self._history_store.query(query)
            return result.events

    def query_events(self, query: EventQuery) -> EventQueryResult:
        """Query events from history (Section 19.2)."""
        with self._lock:
            return self._history_store.query(query)

    def get_event(self, event_id: uuid.UUID) -> Event | None:
        """Get a single event by ID."""
        with self._lock:
            return self._history_store.get(event_id)
