"""
Shared Event Publishing Utilities

Centralizes event publishing logic to eliminate duplication across modules.
Provides strongly-typed event publishing with proper correlation IDs.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_events.base import BaseEvent as DomainBaseEvent
from autoforge_events.event_types import EventCategory, EventType

from autoforge_kernel.interfaces import EventBus


async def publish_event(
    event_bus: EventBus | None,
    event_type: EventType,
    event_category: EventCategory,
    aggregate_id: uuid.UUID,
    aggregate_type: str,
    correlation_id: uuid.UUID | None = None,
    causation_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Publish a strongly-typed event to the Event Bus.

    This is the single canonical event publishing function used by all Kernel modules.
    It does NOT use string-to-enum mapping. Event types are always passed as
    proper EventType enum values.

    Args:
        event_bus: The event bus instance (None = skip).
        event_type: The strongly-typed event type enum value.
        event_category: The event category enum value.
        aggregate_id: The ID of the aggregate this event relates to.
        aggregate_type: The type of the aggregate.
        correlation_id: Optional correlation ID for event tracing.
        causation_id: Optional causation ID for event chain tracing.
        metadata: Optional metadata payload.
    """
    if not event_bus:
        return

    event = DomainBaseEvent(
        event_type=event_type,
        event_category=event_category,
        aggregate_id=aggregate_id,
        aggregate_type=aggregate_type,
        correlation_id=correlation_id,
        causation_id=causation_id,
        metadata=metadata or {},
    )

    await event_bus.publish(event)


def make_timestamp() -> str:
    """Generate a proper ISO-8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()