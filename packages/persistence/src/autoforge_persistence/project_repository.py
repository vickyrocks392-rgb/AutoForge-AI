"""
Project repository interface for the AutoForge AI platform.

Defines the contract for persisting and querying ``Project`` entities.
Extends the generic ``Repository`` with project-specific query methods.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Sequence

from autoforge_models.project import Project

from autoforge_persistence.repository import Repository


class ProjectRepository(Repository[Project]):
    """
    Repository interface for ``Project`` entities.

    In addition to the standard CRUD operations inherited from
    ``Repository``, this interface exposes project-specific queries
    such as searching by name or listing active projects.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Project | None:
        """
        Retrieve a project by its exact name.

        Args:
            name: The exact project name to search for.

        Returns:
            The matching ``Project`` if found, or ``None``.
        """
        ...

    @abstractmethod
    async def list_active(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Project]:
        """
        List all projects that are not archived.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of active ``Project`` instances.
        """
        ...

    @abstractmethod
    async def list_archived(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Project]:
        """
        List all projects that have been archived.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of archived ``Project`` instances.
        """
        ...

    @abstractmethod
    async def search_by_tags(
        self,
        tags: set[str],
        *,
        match_all: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Project]:
        """
        Search projects by their associated tags.

        Args:
            tags: The set of tags to match against.
            match_all: If ``True``, only projects containing all specified
                tags are returned. If ``False``, projects containing any
                of the specified tags are returned.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``Project`` instances.
        """
        ...