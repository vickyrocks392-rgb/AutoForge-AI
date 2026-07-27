"""
Protocol definitions for the AutoForge AI persistence layer.

This module defines structural typing protocols that describe the shape
of repository implementations without requiring explicit inheritance.
Protocols enable duck-typing and make it easier to write test doubles
or alternative implementations that conform to the same interface.
"""

from __future__ import annotations

import uuid
from typing import (
    Any,
    AsyncIterator,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)

from autoforge_models.base import AutoForgeBaseModel

T = TypeVar("T", bound=AutoForgeBaseModel, contravariant=True)


@runtime_checkable
class RepositoryProtocol(Protocol[T]):
    """
    Structural protocol for a generic repository.

    Any object that provides ``get``, ``list``, ``add``, ``update``,
    ``remove``, and ``exists`` methods with the correct signatures
    satisfies this protocol, regardless of its inheritance hierarchy.
    """

    async def get(self, id: uuid.UUID) -> T:
        """Retrieve a single entity by its unique identifier."""
        ...

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> Sequence[T]:
        """List entities with optional pagination and filtering."""
        ...

    async def add(self, entity: T) -> T:
        """Persist a new entity and return it with any generated state."""
        ...

    async def update(self, entity: T) -> T:
        """Update an existing entity and return the updated state."""
        ...

    async def remove(self, id: uuid.UUID) -> None:
        """Delete an entity by its unique identifier."""
        ...

    async def exists(self, id: uuid.UUID) -> bool:
        """Check whether an entity with the given identifier exists."""
        ...


@runtime_checkable
class AsyncIterableRepositoryProtocol(RepositoryProtocol[T], Protocol[T]):
    """
    Extension of ``RepositoryProtocol`` that supports async iteration.

    Repositories that back large collections may benefit from providing
    an async iterator over all entities, enabling memory-efficient
    streaming of results.
    """

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over all entities asynchronously."""
        ...
        yield  # pragma: no cover