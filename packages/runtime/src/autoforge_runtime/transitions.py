"""
State transition validation for the AutoForge AI Runtime State Manager.

Defines allowed state transitions for Task and ExecutionSession statuses,
and provides validation helpers to enforce them at runtime.
"""

from __future__ import annotations

from autoforge_models.enums import ExecutionStatus, TaskStatus

from autoforge_runtime.exceptions import InvalidTransitionError

# ── Task Status Transitions ──────────────────────────────────────────────
#
# Allowed transitions for TaskStatus:
#
#   PENDING  ──► READY
#   PENDING  ──► CANCELLED
#   READY    ──► RUNNING
#   READY    ──► CANCELLED
#   RUNNING  ──► COMPLETED
#   RUNNING  ──► FAILED
#   RUNNING  ──► CANCELLED
#   RUNNING  ──► PAUSED
#   PAUSED   ──► RUNNING
#   PAUSED   ──► CANCELLED
#   COMPLETED  (terminal)
#   FAILED     (terminal)
#   CANCELLED  (terminal)
#   BLOCKED  ──► READY
#   BLOCKED  ──► CANCELLED
#

_TASK_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.READY, TaskStatus.CANCELLED},
    TaskStatus.READY: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.PAUSED},
    TaskStatus.PAUSED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
    TaskStatus.BLOCKED: {TaskStatus.READY, TaskStatus.CANCELLED},
}

# ── Execution Session Status Transitions ─────────────────────────────────
#
# Allowed transitions for ExecutionStatus:
#
#   PENDING   ──► RUNNING
#   PENDING   ──► CANCELLED
#   RUNNING   ──► COMPLETED
#   RUNNING   ──► FAILED
#   RUNNING   ──► CANCELLED
#   RUNNING   ──► PAUSED
#   PAUSED    ──► RUNNING
#   PAUSED    ──► CANCELLED
#   COMPLETED   (terminal)
#   FAILED      (terminal)
#   CANCELLED   (terminal)
#   TIMED_OUT   (terminal)
#

_EXECUTION_TRANSITIONS: dict[ExecutionStatus, set[ExecutionStatus]] = {
    ExecutionStatus.PENDING: {ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED},
    ExecutionStatus.RUNNING: {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.PAUSED,
    },
    ExecutionStatus.PAUSED: {ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED},
    ExecutionStatus.COMPLETED: set(),
    ExecutionStatus.FAILED: set(),
    ExecutionStatus.CANCELLED: set(),
    ExecutionStatus.TIMED_OUT: set(),
}


def validate_task_transition(
    current: TaskStatus,
    target: TaskStatus,
    *,
    task_id: str | None = None,
) -> None:
    """
    Validate a Task status transition.

    Args:
        current: The current TaskStatus.
        target: The desired TaskStatus.
        task_id: Optional task identifier for error messages.

    Raises:
        InvalidTransitionError: If the transition is not allowed.
    """
    allowed = _TASK_TRANSITIONS.get(current, set())
    if target not in allowed:
        label = f" for task {task_id}" if task_id else ""
        raise InvalidTransitionError(
            f"Invalid Task status transition: {current.value!r} -> {target.value!r}{label}",
            details={
                "current": current.value,
                "target": target.value,
                "entity_type": "task",
                "entity_id": task_id,
            },
        )


def validate_execution_transition(
    current: ExecutionStatus,
    target: ExecutionStatus,
    *,
    session_id: str | None = None,
) -> None:
    """
    Validate an ExecutionSession status transition.

    Args:
        current: The current ExecutionStatus.
        target: The desired ExecutionStatus.
        session_id: Optional session identifier for error messages.

    Raises:
        InvalidTransitionError: If the transition is not allowed.
    """
    allowed = _EXECUTION_TRANSITIONS.get(current, set())
    if target not in allowed:
        label = f" for session {session_id}" if session_id else ""
        raise InvalidTransitionError(
            f"Invalid Execution status transition: {current.value!r} -> {target.value!r}{label}",
            details={
                "current": current.value,
                "target": target.value,
                "entity_type": "execution_session",
                "entity_id": session_id,
            },
        )


def get_allowed_task_transitions(status: TaskStatus) -> frozenset[TaskStatus]:
    """
    Return the set of allowed target statuses from a given TaskStatus.

    Args:
        status: The current TaskStatus.

    Returns:
        A frozenset of allowed target TaskStatus values.
    """
    return frozenset(_TASK_TRANSITIONS.get(status, set()))


def get_allowed_execution_transitions(status: ExecutionStatus) -> frozenset[ExecutionStatus]:
    """
    Return the set of allowed target statuses from a given ExecutionStatus.

    Args:
        status: The current ExecutionStatus.

    Returns:
        A frozenset of allowed target ExecutionStatus values.
    """
    return frozenset(_EXECUTION_TRANSITIONS.get(status, set()))


def is_terminal(status: TaskStatus | ExecutionStatus) -> bool:
    """
    Check whether a status is terminal (no further transitions allowed).

    Args:
        status: A TaskStatus or ExecutionStatus value.

    Returns:
        True if the status is terminal, False otherwise.
    """
    if isinstance(status, TaskStatus):
        return status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
    if isinstance(status, ExecutionStatus):
        return status in {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.TIMED_OUT,
        }
    return False