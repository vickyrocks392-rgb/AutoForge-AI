"""
AutoForge Runtime — In-memory Runtime State Manager.

This package provides the authoritative in-memory state management subsystem
for the AutoForge AI platform. It maintains the live runtime state of all
active entities and provides concurrent-safe CRUD operations, snapshot/restore,
and state transition validation.

Key components:
    - RuntimeStateManager: The main entry point for all state operations.
    - RuntimeSnapshot: Immutable point-in-time captures of runtime state.
    - Transition validation: Enforces valid state transitions for Tasks and
      ExecutionSessions.
    - Exceptions: Runtime-specific error hierarchy.
"""

from __future__ import annotations

from autoforge_runtime.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidTransitionError,
    RuntimeError,
    SnapshotError,
    StateError,
)
from autoforge_runtime.snapshots import RuntimeSnapshot
from autoforge_runtime.state_manager import RuntimeStateManager
from autoforge_runtime.transitions import (
    get_allowed_execution_transitions,
    get_allowed_task_transitions,
    is_terminal,
    validate_execution_transition,
    validate_task_transition,
)

__all__ = [
    # Main class
    "RuntimeStateManager",
    # Snapshot
    "RuntimeSnapshot",
    # Exceptions
    "RuntimeError",
    "StateError",
    "InvalidTransitionError",
    "SnapshotError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    # Transition helpers
    "validate_task_transition",
    "validate_execution_transition",
    "get_allowed_task_transitions",
    "get_allowed_execution_transitions",
    "is_terminal",
]