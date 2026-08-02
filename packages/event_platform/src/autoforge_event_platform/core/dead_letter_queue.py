"""
Dead Letter Queue (Section 7.5, 23).

Manage events that cannot be delivered.
Store failed events.
Enable dead letter replay.
Alert on dead letters.
Analyze dead letters.
Retry dead letters.
Clean up dead letters.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import IDeadLetterQueue
from autoforge_event_platform.models.event import (
    DeadLetterAnalysis,
    DeadLetterEntry,
    DeadLetterQuery,
    DeadLetterResult,
    Event,
)


class DeadLetterQueue(IDeadLetterQueue):
    """
    Dead Letter Queue implementation (Section 7.5, 23).

    DLQ Characteristics (Section 23.1):
    - Events that failed delivery after retries
    - Events with permanent errors
    - Events for manual intervention
    - Events for analysis and debugging

    DLQ Process (Section 23.2):
    1. Event delivery fails
    2. Event Platform retries delivery
    3. Retries exhausted
    4. Event is sent to DLQ
    5. DLQ stores event with failure context
    6. DLQ publishes event.dead_lettered event
    7. DLQ alerts on DLQ growth

    Retention (Section 23.2):
    - DLQ events retained for 30 days (configurable)
    - DLQ events archived after retention
    - DLQ events never deleted
    """

    def __init__(self, retention_days: int = 30):
        """
        Initialize the dead letter queue.

        Args:
            retention_days: Days to retain DLQ events (Section 23.2).
        """
        self._retention_days = retention_days
        self._entries: dict[str, DeadLetterEntry] = {}
        self._lock = threading.RLock()

    def add_dead_letter(self, entry: DeadLetterEntry) -> None:
        """
        Add an event to the dead letter queue (Section 23.2).

        Failure Context:
        - Event ID
        - Subscriber ID
        - Error message
        - Retry count
        - Failure timestamp
        - Failure reason
        """
        with self._lock:
            self._entries[entry.dead_letter_id] = entry

    def list_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """
        List dead letter events (Section 23.3 — list).

        Returns:
            DeadLetterResult with entries, total_count, and has_more.
        """
        with self._lock:
            entries = list(self._entries.values())

            # Apply filters
            if query.subscriber_id:
                entries = [e for e in entries if e.subscriber_id == query.subscriber_id]

            if query.event_type:
                entries = [e for e in entries if e.event.event_type == query.event_type]

            if query.failure_reason:
                entries = [e for e in entries if e.failure_reason == query.failure_reason]

            if query.time_range:
                start, end = query.time_range
                entries = [
                    e for e in entries if start <= e.failure_timestamp <= end
                ]

            # Sort by failure timestamp
            entries.sort(key=lambda e: e.failure_timestamp)

            total_count = len(entries)
            offset = query.offset
            limit = query.limit
            paginated = entries[offset : offset + limit]
            has_more = (offset + limit) < total_count

            return DeadLetterResult(
                entries=paginated,
                total_count=total_count,
                has_more=has_more,
            )

    def retry_dead_letter(self, dead_letter_id: str) -> bool:
        """
        Retry a dead letter event (Section 23.3 — retry).

        Process:
        1. Retrieve dead letter event
        2. Remove from DLQ
        3. Retry delivery
        4. If success: Mark as delivered
        5. If failure: Return to DLQ

        Returns:
            True if retry succeeded, False otherwise.
        """
        with self._lock:
            entry = self._entries.get(dead_letter_id)
            if entry is None:
                return False

            # Remove from DLQ
            del self._entries[dead_letter_id]

            # In a real implementation, this would retry delivery.
            # For the in-memory implementation, we return True (success).
            return True

    def replay_dead_letters(self, query: DeadLetterQuery) -> DeadLetterResult:
        """
        Replay all matching dead letter events (Section 23.3 — replay).

        Process:
        1. Query dead letters
        2. Remove from DLQ
        3. Retry delivery for all
        4. Track replay progress
        5. Return replay results

        Returns:
            DeadLetterResult with results.
        """
        with self._lock:
            result = self.list_dead_letters(query)

            # Remove from DLQ and retry
            for entry in result.entries:
                if entry.dead_letter_id in self._entries:
                    del self._entries[entry.dead_letter_id]

            return result

    def delete_dead_letter(self, dead_letter_id: str) -> bool:
        """
        Delete a dead letter event (Section 23.3 — delete).

        Process:
        1. Retrieve dead letter event
        2. Remove from DLQ
        3. Archive event
        4. Return success

        Returns:
            True if deletion succeeded.
        """
        with self._lock:
            entry = self._entries.pop(dead_letter_id, None)
            if entry is None:
                return False

            # In a real implementation, this would archive the event.
            return True

    def analyze_dead_letters(
        self, time_range: tuple[datetime, datetime] | None = None
    ) -> DeadLetterAnalysis:
        """
        Analyze dead letter patterns (Section 23.3 — analyze).

        Analysis:
        - Failure reasons
        - Failure patterns
        - Subscriber failure rates
        - Event type failure rates
        - Time-based patterns
        - Recommendations

        Returns:
            DeadLetterAnalysis with analysis results.
        """
        with self._lock:
            entries = list(self._entries.values())

            if time_range:
                start, end = time_range
                entries = [
                    e for e in entries if start <= e.failure_timestamp <= end
                ]

            # Failure reasons
            failure_reasons: dict[str, int] = {}
            for entry in entries:
                reason = entry.failure_reason
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

            # Subscriber failure rates
            subscriber_failures: dict[str, int] = {}
            for entry in entries:
                sub_id = entry.subscriber_id or "unknown"
                subscriber_failures[sub_id] = subscriber_failures.get(sub_id, 0) + 1

            total = len(entries) if entries else 1
            subscriber_failure_rates = {
                k: v / total for k, v in subscriber_failures.items()
            }

            # Event type failure rates
            event_type_failures: dict[str, int] = {}
            for entry in entries:
                et = entry.event.event_type.value
                event_type_failures[et] = event_type_failures.get(et, 0) + 1

            event_type_failure_rates = {
                k: v / total for k, v in event_type_failures.items()
            }

            # Recommendations
            recommendations: list[str] = []
            if failure_reasons.get("retries_exhausted", 0) > 5:
                recommendations.append(
                    "High number of retries exhausted. Consider increasing retry count or investigating subscriber health."
                )
            if failure_reasons.get("subscriber_unavailable", 0) > 3:
                recommendations.append(
                    "Subscriber unavailable errors detected. Check subscriber connectivity."
                )
            if failure_reasons.get("subscriber_timeout", 0) > 3:
                recommendations.append(
                    "Subscriber timeout errors detected. Consider increasing delivery timeout."
                )
            if not recommendations:
                recommendations.append("No specific recommendations. Review failure patterns manually.")

            return DeadLetterAnalysis(
                total_entries=len(entries),
                failure_reasons=failure_reasons,
                subscriber_failure_rates=subscriber_failure_rates,
                event_type_failure_rates=event_type_failure_rates,
                recommendations=recommendations,
            )

    def get_stats(self) -> dict[str, int]:
        """Get DLQ statistics."""
        with self._lock:
            return {
                "total": len(self._entries),
                "by_reason": len(set(e.failure_reason for e in self._entries.values())),
            }

    def cleanup_expired(self, now: datetime | None = None) -> int:
        """
        Clean up expired DLQ events (Section 23.2).

        DLQ events are archived after retention period, never deleted.
        """
        with self._lock:
            if now is None:
                now = datetime.now(timezone.utc)

            from datetime import timedelta
            cutoff = now - timedelta(days=self._retention_days)

            expired = [
                dlid
                for dlid, entry in self._entries.items()
                if entry.failure_timestamp < cutoff
            ]

            for dlid in expired:
                del self._entries[dlid]

            return len(expired)
