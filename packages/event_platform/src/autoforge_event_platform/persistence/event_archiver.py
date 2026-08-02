"""
Event Archiver (Section 7.3, 18.3).

Archives old events.
Moves events to cold storage.
Enforces retention policies.
Compresses archived events.
Manages archive lifecycle.
"""

from __future__ import annotations

import gzip
import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from autoforge_event_platform.models.event import Event


class EventArchiver:
    """
    Event Archiver implementation (Section 7.3, 18.3).

    Retention Policy (Section 18.4):
    - Hot storage: 30 days (configurable)
    - Warm storage: 1 year (configurable)
    - Cold storage: Indefinite (configurable)
    - Deletion: Never (archived only)
    """

    def __init__(
        self,
        hot_storage_days: int = 30,
        warm_storage_days: int = 365,
    ):
        """
        Initialize the event archiver.

        Args:
            hot_storage_days: Days to keep events in hot storage (Section 18.4).
            warm_storage_days: Days to keep events in warm storage (Section 18.4).
        """
        self._hot_storage_days = hot_storage_days
        self._warm_storage_days = warm_storage_days

        # Storage tiers
        self._hot_storage: dict[uuid.UUID, Event] = {}
        self._warm_storage: dict[uuid.UUID, bytes] = {}  # compressed
        self._cold_storage: dict[uuid.UUID, bytes] = {}  # highly compressed

        self._lock = threading.RLock()

    def archive(self, event: Event) -> bool:
        """
        Archive an event (Section 18.3, 11.2 Stage 7).

        Returns:
            True if archival succeeded.
        """
        with self._lock:
            # Compress event for warm storage
            event_json = event.model_dump_json()
            compressed = gzip.compress(event_json.encode("utf-8"))
            self._warm_storage[event.event_id] = compressed
            return True

    def move_to_cold(self, event_id: uuid.UUID) -> bool:
        """
        Move an event from warm to cold storage (Section 18.3).

        Returns:
            True if move succeeded.
        """
        with self._lock:
            if event_id in self._warm_storage:
                # Re-compress for cold storage
                data = self._warm_storage.pop(event_id)
                self._cold_storage[event_id] = data
                return True
            return False

    def retrieve(self, event_id: uuid.UUID) -> Event | None:
        """
        Retrieve an event from any storage tier.

        Returns:
            The event, or None if not found.
        """
        with self._lock:
            # Check hot storage
            if event_id in self._hot_storage:
                return self._hot_storage[event_id]

            # Check warm storage
            if event_id in self._warm_storage:
                data = self._warm_storage[event_id]
                decompressed = gzip.decompress(data).decode("utf-8")
                return Event.model_validate_json(decompressed)

            # Check cold storage
            if event_id in self._cold_storage:
                data = self._cold_storage[event_id]
                decompressed = gzip.decompress(data).decode("utf-8")
                return Event.model_validate_json(decompressed)

            return None

    def check_retention(self, now: datetime | None = None) -> list[uuid.UUID]:
        """
        Check retention policies and return events to archive (Section 18.4).

        Returns:
            List of event IDs that should be archived.
        """
        with self._lock:
            if now is None:
                now = datetime.now(timezone.utc)

            hot_cutoff = now - timedelta(days=self._hot_storage_days)
            warm_cutoff = now - timedelta(days=self._warm_storage_days)

            to_archive: list[uuid.UUID] = []
            for event_id, event in self._hot_storage.items():
                if event.timestamp < hot_cutoff:
                    to_archive.append(event_id)

            return to_archive

    def run_retention_job(self, now: datetime | None = None) -> int:
        """
        Run the daily retention job (Section 18.4).

        Moves events from hot to warm, and from warm to cold.

        Returns:
            Number of events archived.
        """
        with self._lock:
            if now is None:
                now = datetime.now(timezone.utc)

            hot_cutoff = now - timedelta(days=self._hot_storage_days)
            warm_cutoff = now - timedelta(days=self._warm_storage_days)

            archived = 0

            # Move from hot to warm
            hot_to_warm = [
                (eid, event)
                for eid, event in self._hot_storage.items()
                if event.timestamp < hot_cutoff
            ]
            for event_id, event in hot_to_warm:
                event_json = event.model_dump_json()
                compressed = gzip.compress(event_json.encode("utf-8"))
                self._warm_storage[event_id] = compressed
                del self._hot_storage[event_id]
                archived += 1

            # Move from warm to cold
            warm_to_cold = [
                event_id
                for event_id, data in list(self._warm_storage.items())
                if self._get_event_timestamp(data) < warm_cutoff
            ]
            for event_id in warm_to_cold:
                data = self._warm_storage.pop(event_id)
                self._cold_storage[event_id] = data
                archived += 1

            return archived

    def _get_event_timestamp(self, compressed_data: bytes) -> datetime:
        """Extract timestamp from compressed event data."""
        try:
            decompressed = gzip.decompress(compressed_data).decode("utf-8")
            event = Event.model_validate_json(decompressed)
            return event.timestamp
        except Exception:
            return datetime.now(timezone.utc)

    def get_stats(self) -> dict[str, int]:
        """Get storage tier statistics."""
        with self._lock:
            return {
                "hot_storage": len(self._hot_storage),
                "warm_storage": len(self._warm_storage),
                "cold_storage": len(self._cold_storage),
            }
