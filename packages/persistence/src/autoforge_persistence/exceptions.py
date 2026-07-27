"""
Persistence exception hierarchy for the AutoForge AI platform.

Defines the canonical set of exceptions that repository implementations
may raise. Consumers of the repository layer should catch these exceptions
rather than storage-technology-specific errors.

All exceptions inherit from ``RepositoryError``, which itself inherits
from the built-in ``Exception`` class.
"""

from __future__ import annotations

from typing import Any


class RepositoryError(Exception):
    """
    Base exception for all persistence-layer errors.

    All repository-related exceptions inherit from this class, allowing
    consumers to catch a single base type when they do not need fine-grained
    error handling.
    """

    def __init__(
        self,
        message: str = "An unexpected repository error occurred.",
        *,
        original: Exception | None = None,
    ) -> None:
        self.original = original
        super().__init__(message)


class EntityNotFoundError(RepositoryError):
    """
    Raised when a requested entity does not exist in the data store.

    Typically raised by ``get()`` or ``update()`` when the given identifier
    does not match any persisted record.
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        *,
        original: Exception | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = f"{entity_type} with id {entity_id!r} was not found."
        super().__init__(message, original=original)


class DuplicateEntityError(RepositoryError):
    """
    Raised when an attempt is made to create an entity that already exists.

    Typically raised by ``add()`` when the entity's identifier or a unique
    constraint is already present in the data store.
    """

    def __init__(
        self,
        entity_type: str,
        key: str,
        value: Any,
        *,
        original: Exception | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.key = key
        self.value = value
        message = f"{entity_type} with {key}={value!r} already exists."
        super().__init__(message, original=original)


class ConcurrencyError(RepositoryError):
    """
    Raised when a concurrent modification is detected.

    This occurs when two processes attempt to modify the same entity
    simultaneously and the data store detects a conflict (e.g. via
    optimistic locking or version checks).
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        *,
        original: Exception | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = (
            f"Concurrency conflict detected for {entity_type} "
            f"with id {entity_id!r}. The entity was modified by another process."
        )
        super().__init__(message, original=original)


class TransactionError(RepositoryError):
    """
    Raised when a unit of work transaction fails.

    This may occur during ``commit()`` or ``rollback()`` if the underlying
    data store encounters an error that prevents the transaction from
    completing successfully.
    """

    def __init__(
        self,
        message: str = "The transaction failed.",
        *,
        original: Exception | None = None,
    ) -> None:
        super().__init__(message, original=original)