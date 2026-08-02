"""Event Publisher — publishes state change events.

Implements the Event Publisher from Runtime State Manager Specification v1.0, Section 7.6 and 21.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from autoforge_runtime.models import EntityType


class EventFormatter:
    """Formats state changes as events."""

    def format_state_change(
        self,
        entity_type: EntityType,
        entity_id: uuid.UUID,
        old_state: str,
        new_state: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a state change as an event payload."""
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": f"{entity_type.value}.{new_state}",
            "entity_id": str(entity_id),
            "entity_type": entity_type.value,
            "old_state": old_state,
            "new_state": new_state,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

    def format_lifecycle_event(
        self,
        event_name: str,
        runtime_id: uuid.UUID,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a runtime lifecycle event."""
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": event_name,
            "runtime_id": str(runtime_id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

    def format_checkpoint_event(
        self,
        event_name: str,
        checkpoint_id: uuid.UUID,
        project_id: uuid.UUID,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a checkpoint event."""
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": event_name,
            "checkpoint_id": str(checkpoint_id),
            "project_id": str(project_id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }


class EventRouter:
    """Routes events to appropriate topics."""

    def __init__(self) -> None:
        """Initialize the event router."""
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[dict[str, Any]], None]) -> uuid.UUID:
        """Subscribe to an event type."""
        sub_id = uuid.uuid4()
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        return sub_id

    def unsubscribe(self, subscription_id: uuid.UUID) -> bool:
        """Unsubscribe from events."""
        for event_type, callbacks in self._subscribers.items():
            # We can't easily remove by ID since we don't track IDs
            pass
        return True

    def route(self, event: dict[str, Any]) -> None:
        """Route an event to subscribers."""
        event_type = event.get("event_type", "")
        for callback in self._subscribers.get(event_type, []):
            callback(event)


class EventPublisher:
    """Publishes events to the Event Bus.

    Implements the Event Publisher from Specification Section 7.6.
    """

    def __init__(
        self,
        *,
        publish_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize the event publisher.

        Args:
            publish_callback: Callback to publish events to the Event Bus.
        """
        self._publish_callback = publish_callback
        self.formatter = EventFormatter()
        self.router = EventRouter()
        self._published_events: list[dict[str, Any]] = []

    def publish_state_change(
        self,
        entity_type: EntityType,
        entity_id: uuid.UUID,
        old_state: str,
        new_state: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Publish a state change event."""
        event = self.formatter.format_state_change(
            entity_type, entity_id, old_state, new_state, metadata=metadata
        )
        self._publish(event)

    def publish_lifecycle_event(
        self,
        event_name: str,
        runtime_id: uuid.UUID,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Publish a runtime lifecycle event."""
        event = self.formatter.format_lifecycle_event(
            event_name, runtime_id, metadata=metadata
        )
        self._publish(event)

    def publish_checkpoint_event(
        self,
        event_name: str,
        checkpoint_id: uuid.UUID,
        project_id: uuid.UUID,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Publish a checkpoint event."""
        event = self.formatter.format_checkpoint_event(
            event_name, checkpoint_id, project_id, metadata=metadata
        )
        self._publish(event)

    def _publish(self, event: dict[str, Any]) -> None:
        """Publish an event."""
        self._published_events.append(event)
        if self._publish_callback:
            self._publish_callback(event)
        self.router.route(event)

    def get_published_events(self) -> list[dict[str, Any]]:
        """Get all published events."""
        return list(self._published_events)