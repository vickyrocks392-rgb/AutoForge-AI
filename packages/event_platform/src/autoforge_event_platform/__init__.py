"""
AutoForge Event Platform.

The canonical event platform for AutoForge AI OS.
Implements the Event Platform Specification v1.0.

Public API:
    from autoforge_event_platform import EventPlatform

    platform = EventPlatform()
    result = platform.publish(
        event_type=EventType.TASK_COMPLETED,
        source="execution",
        payload={"taskId": "123"},
    )
"""

from autoforge_event_platform.core.event_platform import EventPlatform
from autoforge_event_platform.models.event import (
    DeliveryMode,
    Event,
    EventCategory,
    EventType,
    OrderingGuarantee,
    Priority,
    PublicationResult,
    PublicationStatus,
    ReplayRequest,
    ReplayResult,
    ReplaySource,
    ReplayStatus,
    Subscription,
    SubscriptionRequest,
    SubscriptionStatus,
)

__all__ = [
    "EventPlatform",
    "Event",
    "EventType",
    "EventCategory",
    "Priority",
    "DeliveryMode",
    "OrderingGuarantee",
    "PublicationResult",
    "PublicationStatus",
    "Subscription",
    "SubscriptionRequest",
    "SubscriptionStatus",
    "ReplayRequest",
    "ReplayResult",
    "ReplaySource",
    "ReplayStatus",
]

__version__ = "1.0.0"
