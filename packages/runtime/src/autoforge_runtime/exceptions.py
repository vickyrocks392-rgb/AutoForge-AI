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


class VersionConflictError(RuntimeError):
    """
    Raised when a state version conflict is detected (optimistic concurrency).

    Examples:
        - Two components attempt to update the same state with different versions
        - A transition is attempted with a stale version number
    """


class ValidationError(RuntimeError):
    """
    Raised when state data fails validation.

    Examples:
        - Project data is invalid
        - Required metadata is missing
    """


class PersistenceError(RuntimeError):
    """
    Raised when state cannot be persisted to durable storage.

    Examples:
        - Database write failure
        - Cache update failure
    """


class InvalidStateError(RuntimeError):
    """
    Raised when an entity is in an invalid state for an operation.

    Examples:
        - Attempting to restore a checkpoint that is not restorable
        - Attempting to transition from an invalid state
    """


class InvalidEntityTypeError(RuntimeError):
    """
    Raised when an invalid entity type is provided.

    Examples:
        - Subscribing to an unknown entity type
        - Querying an unknown entity type
    """


class CheckpointError(RuntimeError):
    """
    Raised when a checkpoint operation fails.

    Examples:
        - Checkpoint cannot be created
        - Checkpoint cannot be restored
        - Checkpoint integrity validation fails
    """


class RecoveryError(RuntimeError):
    """
    Raised when a recovery operation fails.

    Examples:
        - State cannot be restored from checkpoint
        - State reconstruction from events fails
    """


class LifecycleError(RuntimeError):
    """
    Raised when a runtime lifecycle operation fails.

    Examples:
        - Runtime cannot be started
        - Runtime cannot be stopped
        - Runtime is in an invalid state for the operation
    """
