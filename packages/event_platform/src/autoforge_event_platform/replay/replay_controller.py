"""
Replay Controller (Section 7.4, 17.2).

Controls replay sessions.
Manages replay state.
Handles replay control (pause, resume, stop).
Tracks replay progress.
Handles replay errors.
"""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_event_platform.models.event import (
    Event,
    ReplayRequest,
    ReplayResult,
    ReplayStatus,
)


class ReplayController:
    """
    Replay Controller implementation (Section 7.4, 17.2).

    Manages replay sessions with the following states (Section 30.3):
    - Idle: No replay in progress
    - Starting: Replay session starting
    - Running: Replay in progress
    - Paused: Replay paused
    - Completed: Replay completed
    - Failed: Replay failed
    - Stopped: Replay stopped
    """

    def __init__(self):
        """Initialize the replay controller."""
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def create_session(self, request: ReplayRequest) -> str:
        """
        Create a replay session (Section 17.2 Step 1).

        Process:
        1. Validate replay request
        2. Create replay session
        3. Query events from history
        4. Calculate total event count
        5. Return replay ID and status

        Returns:
            Replay ID.
        """
        with self._lock:
            replay_id = str(uuid.uuid4())
            self._sessions[replay_id] = {
                "request": request,
                "status": ReplayStatus.RUNNING,
                "events_delivered": 0,
                "total_events": 0,
                "events": [],
                "current_index": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "error": None,
            }
            return replay_id

    def set_events(self, replay_id: str, events: list[Event]) -> None:
        """Set the events to replay for a session."""
        with self._lock:
            if replay_id in self._sessions:
                self._sessions[replay_id]["events"] = events
                self._sessions[replay_id]["total_events"] = len(events)
                self._sessions[replay_id]["updated_at"] = datetime.now(timezone.utc)

    def get_session(self, replay_id: str) -> dict[str, Any] | None:
        """Get a replay session by ID."""
        with self._lock:
            return self._sessions.get(replay_id)

    def get_status(self, replay_id: str) -> ReplayResult | None:
        """Get the status of a replay session."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return None

            return ReplayResult(
                replay_id=replay_id,
                status=session["status"],
                progress=(session["events_delivered"], session["total_events"]),
                error=session.get("error"),
            )

    def pause(self, replay_id: str) -> ReplayResult | None:
        """Pause a replay session (Section 17.3)."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return None

            session["status"] = ReplayStatus.PAUSED
            session["updated_at"] = datetime.now(timezone.utc)
            return self.get_status(replay_id)

    def resume(self, replay_id: str) -> ReplayResult | None:
        """Resume a paused replay session (Section 17.3)."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return None

            if session["status"] == ReplayStatus.PAUSED:
                session["status"] = ReplayStatus.RUNNING
                session["updated_at"] = datetime.now(timezone.utc)
            return self.get_status(replay_id)

    def stop(self, replay_id: str) -> ReplayResult | None:
        """Stop a replay session (Section 17.3)."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return None

            session["status"] = ReplayStatus.STOPPED
            session["updated_at"] = datetime.now(timezone.utc)
            return self.get_status(replay_id)

    def mark_delivered(self, replay_id: str) -> None:
        """Mark an event as delivered in the replay session."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return

            session["events_delivered"] += 1
            session["current_index"] += 1
            session["updated_at"] = datetime.now(timezone.utc)

    def mark_completed(self, replay_id: str) -> None:
        """Mark a replay session as completed."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return

            session["status"] = ReplayStatus.COMPLETED
            session["updated_at"] = datetime.now(timezone.utc)

    def mark_failed(self, replay_id: str, error: str) -> None:
        """Mark a replay session as failed."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return

            session["status"] = ReplayStatus.FAILED
            session["error"] = error
            session["updated_at"] = datetime.now(timezone.utc)

    def get_next_event(self, replay_id: str) -> Event | None:
        """Get the next event to deliver in a replay session."""
        with self._lock:
            session = self._sessions.get(replay_id)
            if session is None:
                return None

            if session["status"] != ReplayStatus.RUNNING:
                return None

            events = session["events"]
            index = session["current_index"]
            if index >= len(events):
                return None

            return events[index]

    def cleanup(self, replay_id: str) -> None:
        """Clean up a replay session (Section 30.3)."""
        with self._lock:
            self._sessions.pop(replay_id, None)
