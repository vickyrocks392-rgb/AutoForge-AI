"""
Event Correlation Engine (Section 7.4, 20).

Correlate related events.
Trace event chains.
Group events by aggregate.
Detect event patterns.
Build correlation graphs.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from autoforge_event_platform.interfaces import IEventCorrelationEngine
from autoforge_event_platform.models.event import Event, EventType
from autoforge_event_platform.persistence.event_history_store import EventHistoryStore


class CorrelationEngine(IEventCorrelationEngine):
    """
    Event Correlation Engine implementation (Section 7.4, 20).

    Correlation Model (Section 20.1):
    - Correlation ID: Groups related events, set by publisher, spans subsystems
    - Causation ID: Traces event causation, set by Event Platform, forms event chain

    Correlation Patterns (Section 20.2):
    - Project Correlation: All events for a project
    - Workflow Correlation: All events for a workflow
    - Task Correlation: All events for a task
    - Causation Chain: Events linked in causation chain
    """

    def __init__(self, history_store: EventHistoryStore | None = None):
        """
        Initialize the correlation engine.

        Args:
            history_store: Event history store for querying.
        """
        self._history_store = history_store or EventHistoryStore()
        self._lock = threading.RLock()

    def query_by_correlation_id(self, correlation_id: uuid.UUID) -> list[Event]:
        """
        Query all events with a correlation ID (Section 20.3).

        Returns:
            All events with the given correlation ID.
        """
        with self._lock:
            from autoforge_event_platform.models.event import EventQuery

            query = EventQuery(
                correlation_id=correlation_id,
                limit=10000,
                offset=0,
            )
            result = self._history_store.query(query)
            return result.events

    def query_causation_chain(self, event_id: uuid.UUID) -> list[Event]:
        """
        Query the causation chain for an event (Section 20.3).

        Traces the chain of events that caused this event.

        Returns:
            Event causation chain (ordered from root cause to the event).
        """
        with self._lock:
            chain: list[Event] = []
            visited: set[uuid.UUID] = set()

            current_id = event_id
            while current_id is not None and current_id not in visited:
                visited.add(current_id)
                event = self._history_store.get(current_id)
                if event is None:
                    break

                chain.insert(0, event)
                current_id = event.causation_id

            return chain

    def query_related_events(self, event_id: uuid.UUID) -> list[Event]:
        """
        Query all related events (correlated and caused) (Section 20.3).

        Returns:
            All related events (correlated and caused).
        """
        with self._lock:
            event = self._history_store.get(event_id)
            if event is None:
                return []

            related: list[Event] = []
            visited: set[uuid.UUID] = set()

            # Get causation chain
            chain = self.query_causation_chain(event_id)
            for e in chain:
                if e.event_id not in visited:
                    related.append(e)
                    visited.add(e.event_id)

            # Get correlated events
            correlated = self.query_by_correlation_id(event.correlation_id)
            for e in correlated:
                if e.event_id not in visited:
                    related.append(e)
                    visited.add(e.event_id)

            return related

    def group_by_aggregate(self, aggregate_id: uuid.UUID) -> list[Event]:
        """
        Group events by aggregate (Section 20.2).

        Returns:
            All events for the given aggregate, ordered by timestamp.
        """
        with self._lock:
            from autoforge_event_platform.models.event import EventQuery

            query = EventQuery(
                limit=10000,
                offset=0,
            )
            result = self._history_store.query(query)

            # Filter by aggregate_id
            return [e for e in result.events if e.aggregate_id == aggregate_id]

    def detect_patterns(self, events: list[Event]) -> list[dict[str, Any]]:
        """
        Detect patterns in event streams (Section 20.2).

        Returns:
            List of detected patterns.
        """
        with self._lock:
            patterns: list[dict[str, Any]] = []

            # Detect failure patterns
            failure_events = [e for e in events if e.event_type == EventType.FAILURE_DETECTED]
            if failure_events:
                patterns.append({
                    "pattern": "failure_detected",
                    "count": len(failure_events),
                    "events": [str(e.event_id) for e in failure_events],
                })

            # Detect recovery patterns
            recovery_events = [e for e in events if e.event_type == EventType.RECOVERY_STARTED]
            if recovery_events:
                patterns.append({
                    "pattern": "recovery_started",
                    "count": len(recovery_events),
                    "events": [str(e.event_id) for e in recovery_events],
                })

            # Detect task completion patterns
            task_completed = [e for e in events if e.event_type == EventType.TASK_COMPLETED]
            if task_completed:
                patterns.append({
                    "pattern": "task_completed",
                    "count": len(task_completed),
                    "events": [str(e.event_id) for e in task_completed],
                })

            return patterns

    def build_correlation_graph(self, events: list[Event]) -> dict[str, list[str]]:
        """
        Build a correlation graph from events (Section 20.2).

        Returns:
            Adjacency list representing the correlation graph.
        """
        with self._lock:
            graph: dict[str, list[str]] = {}

            for event in events:
                event_id_str = str(event.event_id)
                if event_id_str not in graph:
                    graph[event_id_str] = []

                # Add causation edge
                if event.causation_id:
                    causation_str = str(event.causation_id)
                    if causation_str not in graph:
                        graph[causation_str] = []
                    graph[causation_str].append(event_id_str)

            return graph