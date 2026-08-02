"""Runtime Lifecycle — manages the Runtime State Manager process lifecycle.

Implements the Runtime Lifecycle from Runtime State Manager Specification v1.0, Section 16.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from autoforge_runtime.exceptions import LifecycleError
from autoforge_runtime.models import RuntimeMetadata, RuntimeStatus


class RuntimeLifecycle:
    """Manages the Runtime State Manager lifecycle.

    Implements the runtime state machine from Specification Section 16.1:
        Created → Starting → Ready → Processing → Ready
                                    → Paused → Ready
                                    → Stopping → Stopped
    """

    def __init__(
        self,
        runtime_id: uuid.UUID | None = None,
        *,
        event_callback: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize the runtime lifecycle.

        Args:
            runtime_id: Optional runtime ID. Defaults to a new UUID.
            event_callback: Callback to publish lifecycle events.
        """
        self._runtime_id = runtime_id or uuid.uuid4()
        self._event_callback = event_callback
        self._started_at: datetime | None = None
        self._metadata = RuntimeMetadata(
            runtime_id=self._runtime_id,
            status=RuntimeStatus.CREATED,
        )

    @property
    def runtime_id(self) -> uuid.UUID:
        """Get the runtime ID."""
        return self._runtime_id

    @property
    def status(self) -> RuntimeStatus:
        """Get the current runtime status."""
        return self._metadata.status

    def initialize(self) -> None:
        """Begin initialization (Created → Starting)."""
        self._transition(RuntimeStatus.STARTING, "runtime.starting")

    def start(self) -> None:
        """Complete initialization (Starting → Ready)."""
        self._started_at = datetime.now(timezone.utc)
        self._metadata = self._metadata.model_copy(
            update={
                "status": RuntimeStatus.READY,
                "started_at": self._started_at,
            }
        )
        self._publish("runtime.started", {"timestamp": self._started_at.isoformat()})

    def process(self) -> None:
        """Begin processing operations (Ready → Processing)."""
        self._transition(RuntimeStatus.PROCESSING, "runtime.processing")

    def complete_processing(self) -> None:
        """Complete processing (Processing → Ready)."""
        self._transition(RuntimeStatus.READY, "runtime.ready")

    def pause(self, reason: str = "user_requested") -> None:
        """Pause the runtime (Ready/Processing → Paused)."""
        self._transition(RuntimeStatus.PAUSED, "runtime.pausing", {"reason": reason})
        self._publish("runtime.paused", {"timestamp": datetime.now(timezone.utc).isoformat()})

    def resume(self) -> None:
        """Resume the runtime (Paused → Ready)."""
        self._transition(RuntimeStatus.READY, "runtime.resuming")
        self._publish("runtime.ready", {"timestamp": datetime.now(timezone.utc).isoformat()})

    def stop(self, reason: str = "shutdown") -> None:
        """Stop the runtime (Ready/Processing/Paused → Stopping → Stopped)."""
        self._transition(RuntimeStatus.STOPPING, "runtime.stopping", {"reason": reason})
        self._metadata = self._metadata.model_copy(update={"status": RuntimeStatus.STOPPED})
        uptime = None
        if self._started_at:
            uptime = datetime.now(timezone.utc) - self._started_at
        self._publish(
            "runtime.stopped",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime": str(uptime) if uptime else None,
            },
        )

    def recover(self, recovery_type: str = "checkpoint") -> None:
        """Publish a recovery event."""
        self._publish("runtime.recovered", {"recovery_type": recovery_type})

    def _transition(self, new_status: RuntimeStatus, event_name: str, metadata: dict[str, Any] | None = None) -> None:
        """Transition to a new runtime status."""
        current = self._metadata.status
        if not self._is_valid_transition(current, new_status):
            raise LifecycleError(
                f"Invalid runtime transition: {current.value} -> {new_status.value}",
                details={"current": current.value, "target": new_status.value},
            )
        self._metadata = self._metadata.model_copy(update={"status": new_status})
        self._publish(event_name, metadata or {})

    def _is_valid_transition(self, current: RuntimeStatus, target: RuntimeStatus) -> bool:
        """Check if a runtime transition is valid."""
        transitions = {
            RuntimeStatus.CREATED: {RuntimeStatus.STARTING},
            RuntimeStatus.STARTING: {RuntimeStatus.READY, RuntimeStatus.STOPPED},
            RuntimeStatus.READY: {RuntimeStatus.PROCESSING, RuntimeStatus.PAUSED, RuntimeStatus.STOPPING},
            RuntimeStatus.PROCESSING: {RuntimeStatus.READY, RuntimeStatus.PAUSED, RuntimeStatus.STOPPING},
            RuntimeStatus.PAUSED: {RuntimeStatus.READY, RuntimeStatus.STOPPING},
            RuntimeStatus.STOPPING: {RuntimeStatus.STOPPED},
            RuntimeStatus.STOPPED: set(),
        }
        return target in transitions.get(current, set())

    def _publish(self, event_name: str, metadata: dict[str, Any]) -> None:
        """Publish a lifecycle event."""
        if self._event_callback:
            self._event_callback(
                event_name,
                {
                    "runtime_id": str(self._runtime_id),
                    **metadata,
                },
            )

    def get_metadata(self) -> RuntimeMetadata:
        """Get the current runtime metadata."""
        return self._metadata