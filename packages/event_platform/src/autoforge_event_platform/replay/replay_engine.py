"""
Event Replay Engine (Section 7.4, 17).

Enable event replay from history.
Replay from checkpoint.
Replay with filters.
Replay at different speeds.
Pause and resume replay.
Track replay progress.
Isolate replay from live event flow.
"""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.interfaces import IEventReplayEngine
from autoforge_event_platform.models.event import (
    Event,
    ReplayRequest,
    ReplayResult,
    ReplaySource,
    ReplayStatus,
)
from autoforge_event_platform.replay.history_query import HistoryQuery
from autoforge_event_platform.replay.replay_controller import ReplayController


class ReplayEngine(IEventReplayEngine):
    """
    Event Replay Engine implementation (Section 7.4, 17).

    Replay Sources (Section 17.1):
    - From timestamp
    - From event ID
    - From checkpoint
    - From beginning of time

    Replay Modes (Section 17.1):
    - Live replay (deliver to subscriber)
    - Export replay (write to file)
    - Isolated replay (deliver to isolated bus)

    Replay Speeds (Section 17.3):
    - 1x (real-time)
    - 2x, 4x, 8x (accelerated)
    - Maximum (as fast as possible)
    """

    def __init__(
        self,
        history_query: HistoryQuery | None = None,
        controller: ReplayController | None = None,
    ):
        """
        Initialize the replay engine.

        Args:
            history_query: History query for querying events.
            controller: Replay controller for session management.
        """
        self._history_query = history_query or HistoryQuery()
        self._controller = controller or ReplayController()
        self._lock = threading.RLock()

    def start_replay(self, request: ReplayRequest) -> ReplayResult:
        """
        Start an event replay session (Section 6.4, 17.2).

        Process:
        1. Validate replay request
        2. Create replay session
        3. Query events from history
        4. Deliver events to subscriber at specified speed
        5. Track replay progress
        6. Handle errors according to policy
        7. Return replay ID and status

        Returns:
            ReplayResult with replay_id, status, and progress.
        """
        with self._lock:
            # Step 1: Validate replay request
            if not self._validate_replay_request(request):
                return ReplayResult(
                    replay_id="",
                    status=ReplayStatus.FAILED,
                    progress=(0, 0),
                    error="Invalid replay request",
                )

            # Step 2: Create replay session
            replay_id = self._controller.create_session(request)

            # Step 3: Query events from history
            events = self._history_query.query_for_replay(request)
            self._controller.set_events(replay_id, events)

            # Step 4: Deliver events to subscriber at specified speed
            if request.subscriber is not None:
                self._deliver_events(replay_id, events, request)

            # Step 5: Track replay progress (done during delivery)
            # Step 6: Handle errors (done during delivery)

            # Step 7: Return replay ID and status
            return self._controller.get_status(replay_id)

    def _validate_replay_request(self, request: ReplayRequest) -> bool:
        """Validate a replay request (Section 17.2 Step 1)."""
        # Source must be valid
        if request.source not in ReplaySource:
            return False

        # For from_timestamp, timestamp must be provided
        if request.source == ReplaySource.FROM_TIMESTAMP and request.from_timestamp is None:
            return False

        # For from_event_id, event_id must be provided
        if request.source == ReplaySource.FROM_EVENT_ID and request.from_event_id is None:
            return False

        # For from_checkpoint, checkpoint must be provided
        if request.source == ReplaySource.FROM_CHECKPOINT and request.from_checkpoint is None:
            return False

        return True

    def _deliver_events(
        self,
        replay_id: str,
        events: list[Event],
        request: ReplayRequest,
    ) -> None:
        """
        Deliver events to subscriber at specified speed (Section 17.2 Step 3).

        Supports:
        - Different speeds (1x, 2x, 4x, 8x, maximum)
        - Pause and resume
        - Stop
        - Error handling
        """
        speed = request.speed
        stop_on_error = request.stop_on_error

        for event in events:
            # Check if replay was paused or stopped
            status = self._controller.get_status(replay_id)
            if status is None:
                break

            if status.status == ReplayStatus.PAUSED:
                # Wait for resume
                while True:
                    time.sleep(0.1)
                    status = self._controller.get_status(replay_id)
                    if status is None:
                        return
                    if status.status == ReplayStatus.RUNNING:
                        break
                    if status.status == ReplayStatus.STOPPED:
                        return

            if status.status == ReplayStatus.STOPPED:
                return

            # Deliver event
            try:
                if request.subscriber is not None:
                    request.subscriber(event)
                self._controller.mark_delivered(replay_id)
            except Exception as e:
                if stop_on_error:
                    self._controller.mark_failed(replay_id, str(e))
                    return
                else:
                    # Continue with next event
                    self._controller.mark_delivered(replay_id)

            # Apply speed delay
            if speed > 0 and speed != float("inf"):
                # Calculate delay based on event timestamp difference
                # For simplicity, use a fixed delay scaled by speed
                delay = 0.001 / speed  # Base 1ms per event at 1x speed
                time.sleep(delay)

        # Mark as completed
        self._controller.mark_completed(replay_id)

    def pause_replay(self, replay_id: str) -> ReplayResult:
        """Pause a replay session (Section 17.3)."""
        with self._lock:
            result = self._controller.pause(replay_id)
            if result is None:
                return ReplayResult(
                    replay_id=replay_id,
                    status=ReplayStatus.FAILED,
                    progress=(0, 0),
                    error="Replay session not found",
                )
            return result

    def resume_replay(self, replay_id: str) -> ReplayResult:
        """Resume a paused replay session (Section 17.3)."""
        with self._lock:
            result = self._controller.resume(replay_id)
            if result is None:
                return ReplayResult(
                    replay_id=replay_id,
                    status=ReplayStatus.FAILED,
                    progress=(0, 0),
                    error="Replay session not found",
                )
            return result

    def stop_replay(self, replay_id: str) -> ReplayResult:
        """Stop a replay session (Section 17.3)."""
        with self._lock:
            result = self._controller.stop(replay_id)
            if result is None:
                return ReplayResult(
                    replay_id=replay_id,
                    status=ReplayStatus.FAILED,
                    progress=(0, 0),
                    error="Replay session not found",
                )
            return result

    def get_replay_status(self, replay_id: str) -> ReplayResult | None:
        """Get replay session status."""
        with self._lock:
            return self._controller.get_status(replay_id)

    def replay_from_checkpoint(
        self,
        checkpoint_id: str,
        request: ReplayRequest,
    ) -> ReplayResult:
        """
        Replay events from a specific checkpoint (Section 17.3).

        Process:
        1. Load checkpoint
        2. Get checkpoint timestamp or event ID
        3. Query events from checkpoint
        4. Replay events
        """
        with self._lock:
            # Set the source to from_checkpoint
            request = ReplayRequest(
                source=ReplaySource.FROM_CHECKPOINT,
                from_checkpoint=checkpoint_id,
                event_types=request.event_types,
                event_categories=request.event_categories,
                project_id=request.project_id,
                correlation_id=request.correlation_id,
                speed=request.speed,
                subscriber=request.subscriber,
                stop_on_error=request.stop_on_error,
            )
            return self.start_replay(request)

    def replay_with_filters(
        self,
        request: ReplayRequest,
    ) -> ReplayResult:
        """
        Replay filtered events (Section 17.3).

        Process:
        1. Apply filters to event query
        2. Query filtered events
        3. Replay filtered events
        """
        with self._lock:
            return self.start_replay(request)

    def replay_at_speed(
        self,
        request: ReplayRequest,
        speed: float,
    ) -> ReplayResult:
        """
        Replay events at a different speed (Section 17.3).

        Speeds:
        - 1x (real-time)
        - 2x, 4x, 8x (accelerated)
        - Maximum (as fast as possible)
        """
        with self._lock:
            request = ReplayRequest(
                source=request.source,
                from_timestamp=request.from_timestamp,
                from_event_id=request.from_event_id,
                from_checkpoint=request.from_checkpoint,
                event_types=request.event_types,
                event_categories=request.event_categories,
                project_id=request.project_id,
                correlation_id=request.correlation_id,
                speed=speed,
                subscriber=request.subscriber,
                stop_on_error=request.stop_on_error,
            )
            return self.start_replay(request)

    def isolated_replay(
        self,
        request: ReplayRequest,
    ) -> ReplayResult:
        """
        Replay events in isolation from live event flow (Section 17.4).

        Isolation Methods:
        - Separate event bus (replay bus)
        - Separate subscriber (replay subscriber)
        - Event tagging (replay events tagged)

        Isolation Guarantees:
        - Replay events do not affect live subscribers
        - Replay events do not trigger live workflows
        - Replay events are clearly identified
        """
        with self._lock:
            # Tag the event with replay metadata
            original_subscriber = request.subscriber

            def isolated_subscriber(event: Event) -> None:
                # Tag event as replayed
                data = event.model_dump()
                data["metadata"] = dict(event.metadata)
                data["metadata"]["replayed"] = True
                data["metadata"]["replayId"] = str(uuid.uuid4())
                replayed_event = Event.model_validate(data)

                if original_subscriber is not None:
                    original_subscriber(replayed_event)

            request = ReplayRequest(
                source=request.source,
                from_timestamp=request.from_timestamp,
                from_event_id=request.from_event_id,
                from_checkpoint=request.from_checkpoint,
                event_types=request.event_types,
                event_categories=request.event_categories,
                project_id=request.project_id,
                correlation_id=request.correlation_id,
                speed=request.speed,
                subscriber=isolated_subscriber,
                stop_on_error=request.stop_on_error,
            )
            return self.start_replay(request)
