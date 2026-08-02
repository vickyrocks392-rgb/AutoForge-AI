"""
Event Persistence Layer (Section 7.3, 18).

Persist events to durable storage.
Ensure event durability.
Manage event retention.
Archive events.
Delete events according to retention policy.
Optimize storage for performance and cost.
Backup event data for disaster recovery.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import IEventPersistence
from autoforge_event_platform.models.event import (
    Event,
    EventQuery,
    EventQueryResult,
)
from autoforge_event_platform.persistence.event_archiver import EventArchiver
from autoforge_event_platform.persistence.event_reader import EventReader
from autoforge_event_platform.persistence.event_writer import EventWriter


class EventPersistence(IEventPersistence):
    """
    Event Persistence implementation (Section 7.3, 18).

    Multi-tier persistence model (Section 18.1):
    - Hot Storage (SSD): Recent events (last 30 days), fast access, full indexing
    - Warm Storage (HDD): Older events (30 days - 1 year), slower access, compressed
    - Cold Storage (Archive): Old events (1+ years), slowest access, highly compressed

    Write Path (Section 18.2):
    1. Event is accepted
    2. Event is validated
    3. Event is enriched
    4. Event is written to hot storage
    5. Write is confirmed
    6. Event is routed to subscribers

    Write Guarantees (Section 18.2):
    - Event is durably written before routing
    - Write is atomic
    - Write is recoverable
    - Write is confirmed
    """

    def __init__(
        self,
        hot_storage_days: int = 30,
        warm_storage_days: int = 365,
    ):
        """
        Initialize the event persistence layer.

        Args:
            hot_storage_days: Days to keep events in hot storage (Section 18.4).
            warm_storage_days: Days to keep events in warm storage (Section 18.4).
        """
        self._writer = EventWriter()
        self._reader = EventReader(self._writer)
        self._archiver = EventArchiver(
            hot_storage_days=hot_storage_days,
            warm_storage_days=warm_storage_days,
        )
        self._lock = threading.RLock()

    def write(self, event: Event) -> bool:
        """
        Write an event to persistent storage (Section 18.2).

        Write Guarantees:
        - Event is durably written before routing
        - Write is atomic
        - Write is recoverable
        - Write is confirmed

        Returns:
            True if write succeeded.
        """
        with self._lock:
            # Write to hot storage
            success = self._writer.write(event)

            # Also store in archiver's hot storage for tiering
            self._archiver._hot_storage[event.event_id] = event

            # Clear reader cache for this event
            self._reader.clear_cache()

            return success

    def write_batch(self, events: list[Event]) -> bool:
        """
        Batch write events for performance (Section 18.2).

        Returns:
            True if all writes succeeded.
        """
        with self._lock:
            success = self._writer.write_batch(events)
            for event in events:
                self._archiver._hot_storage[event.event_id] = event
            self._reader.clear_cache()
            return success

    def read(self, event_id: uuid.UUID) -> Event | None:
        """
        Read an event by ID (Section 18.2).

        Returns:
            The event, or None if not found.
        """
        with self._lock:
            # Try reader first (with cache)
            event = self._reader.read(event_id)
            if event is not None:
                return event

            # Try archiver (warm/cold storage)
            return self._archiver.retrieve(event_id)

    def query(self, query: EventQuery) -> EventQueryResult:
        """
        Query events from storage (Section 18.2, 19).

        Returns:
            EventQueryResult with events, total_count, and has_more.
        """
        with self._lock:
            return self._reader.query(query)

    def archive(self, event_id: uuid.UUID) -> bool:
        """
        Archive an event (Section 18.3, 11.2 Stage 7).

        Returns:
            True if archival succeeded.
        """
        with self._lock:
            event = self._writer.get_all()
            event_obj = next((e for e in event if e.event_id == event_id), None)
            if event_obj is None:
                return False

            return self._archiver.archive(event_obj)

    def run_retention_job(self, now: datetime | None = None) -> int:
        """
        Run the daily retention job (Section 18.4).

        Returns:
            Number of events archived.
        """
        with self._lock:
            return self._archiver.run_retention_job(now)

    def get_stats(self) -> dict[str, int]:
        """Get persistence statistics."""
        with self._lock:
            return {
                "hot_storage": self._writer.count(),
                "warm_storage": self._archiver.get_stats()["warm_storage"],
                "cold_storage": self._archiver.get_stats()["cold_storage"],
            }
