"""
Runtime-specific exceptions for the AutoForge AI Runtime State Manager.

Defines a hierarchy of exceptions raised by the runtime state management
subsystem. All runtime exceptions inherit from RuntimeError.
"""

from __future__ import annotations

from typing import Any


class RuntimeError(Exception):
    """Base exception for all Runtime State Manager errors."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.details = details or {}
        super().__init__(message)


class StateError(RuntimeError):
    """
    Raised when an operation attempts to manipulate state in an invalid way.

    Examples:
        - Registering an entity with a duplicate ID
        - Updating an entity that does not exist
        - Removing an entity that does not exist
    """


class InvalidTransitionError(RuntimeError):
    """
    Raised when an invalid state transition is attempted.

    Examples:
        - Transitioning a Task from PENDING directly to COMPLETED
        - Transitioning an ExecutionSession from CANCELLED to RUNNING
    """


class SnapshotError(RuntimeError):
    """
    Raised when a snapshot operation fails.

    Examples:
        - Attempting to restore a corrupted snapshot
        - Creating a snapshot when the runtime is in an inconsistent state
    """


class EntityNotFoundError(RuntimeError):
    """
    Raised when a requested entity is not found in the runtime state.

    Examples:
        - Looking up a Project by an ID that does not exist
        - Attempting to update a Task that was never registered
    """


class DuplicateEntityError(RuntimeError):
    """
    Raised when attempting to register an entity that already exists.

    Examples:
        - Registering a Project with an ID that is already in use
        - Registering a Task with a duplicate ID
    """