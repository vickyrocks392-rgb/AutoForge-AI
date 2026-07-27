"""
Memory entry repository interface for the AutoForge AI platform.

Defines the contract for persisting and querying ``MemoryEntry`` entities.
Extends the generic ``Repository`` with memory-specific query methods
for semantic search, type filtering, and importance-based retrieval.
"""

from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Sequence

from autoforge_models.enums import MemoryType
from autoforge_models.memory_entry import MemoryEntry

from autoforge_persistence.repository import Repository


class MemoryRepository(Repository[MemoryEntry]):
    """
    Repository interface for ``MemoryEntry`` entities.

    Provides domain-specific queries for the memory system, including
    semantic search, type-based filtering, and importance-based retrieval.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        *,
        memory_type: MemoryType | None = None,
        project_id: uuid.UUID | None = None,
        min_importance: float = 0.0,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[MemoryEntry]:
        """
        Search memory entries by content.

        Performs a text-based search against memory entry content, title,
        and summary fields. The exact search semantics (e.g. full-text
        search, fuzzy matching) are implementation-defined.

        Args:
            query: The search query string.
            memory_type: If provided, only return entries of this type.
            project_id: If provided, only return entries within this project.
            min_importance: Minimum importance score threshold (0.0 to 1.0).
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``MemoryEntry`` instances.
        """
        ...

    @abstractmethod
    async def get_by_type(
        self,
        memory_type: MemoryType,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[MemoryEntry]:
        """
        Retrieve memory entries filtered by their type.

        Args:
            memory_type: The ``MemoryType`` to filter by.
            project_id: If provided, only return entries within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``MemoryEntry`` instances.
        """
        ...

    @abstractmethod
    async def get_by_project(
        self,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[MemoryEntry]:
        """
        Retrieve all memory entries belonging to a specific project.

        Args:
            project_id: The UUID of the related project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``MemoryEntry`` instances for the project.
        """
        ...

    @abstractmethod
    async def get_by_key(
        self,
        key: str,
        project_id: uuid.UUID | None = None,
    ) -> MemoryEntry | None:
        """
        Retrieve a memory entry by its unique key.

        Args:
            key: The unique key of the memory entry.
            project_id: If provided, scope the lookup to this project.

        Returns:
            The matching ``MemoryEntry`` if found, or ``None``.
        """
        ...

    @abstractmethod
    async def get_most_important(
        self,
        project_id: uuid.UUID | None = None,
        *,
        limit: int = 10,
    ) -> Sequence[MemoryEntry]:
        """
        Retrieve the most important memory entries.

        Importance is determined by the ``importance_score`` field.
        Entries are returned in descending order of importance.

        Args:
            project_id: If provided, only return entries within this project.
            limit: Maximum number of records to return.

        Returns:
            A sequence of the most important ``MemoryEntry`` instances.
        """
        ...

    @abstractmethod
    async def get_recently_accessed(
        self,
        project_id: uuid.UUID | None = None,
        *,
        limit: int = 10,
    ) -> Sequence[MemoryEntry]:
        """
        Retrieve the most recently accessed memory entries.

        Args:
            project_id: If provided, only return entries within this project.
            limit: Maximum number of records to return.

        Returns:
            A sequence of recently accessed ``MemoryEntry`` instances.
        """
        ...

    @abstractmethod
    async def increment_access_count(
        self,
        memory_entry_id: uuid.UUID,
    ) -> None:
        """
        Increment the access count for a memory entry.

        This is a specialised operation that updates only the access
        tracking fields without requiring a full entity update.

        Args:
            memory_entry_id: The UUID of the memory entry to update.

        Raises:
            EntityNotFoundError: If no entry with the given ``id`` exists.
        """
        ...