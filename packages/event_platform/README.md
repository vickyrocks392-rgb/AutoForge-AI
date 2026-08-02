# AutoForge Event Platform

This is the Event Platform implementation for AutoForge AI OS, implementing the Event Platform Specification v1.0.

Key Features:
- Event publication and subscription management
- Event routing and delivery
- Dead letter queue handling
- Event replay and history queries
- Schema registry and validation

Usage:
```python
from autoforge_event_platform import EventPlatform

platform = EventPlatform()
platform.publish(event_type=EventType.TASK_COMPLETED, source="execution", payload={"taskId": "123"})