"""
Artifact repository interface for the AutoForge AI platform.

Defines the contract for persisting and querying ``Artifact`` entities.
Extends the generic ``Repository`` with artifact-specific query methods
for type filtering, project scoping, and task association.
"""

from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Sequence

from autoforge_models.artifact import Artifact
from autoforge_models.enums import ArtifactType

from autoforge_persistence.repository import Repository


class ArtifactRepository(Repository[Artifact]):
    """
    Repository interface for ``Artifact`` entities.

    Provides domain-specific queries for artifact management, including
    type-based filtering, project scoping, and task association lookups.
    """

    @abstractmethod
    async def get_by_project(
        self,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Artifact]:
        """
        Retrieve all artifacts belonging to a specific project.

        Args:
            project_id: The UUID of the parent project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``Artifact`` instances within the project.
        """
        ...

    @abstractmethod
    async def get_by_task(
        self,
        task_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Artifact]:
        """
        Retrieve all artifacts produced by a specific task.

        Args:
            task_id: The UUID of the producing task.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``Artifact`` instances produced by the task.
        """
        ...

    @abstractmethod
    async def get_by_type(
        self,
        artifact_type: ArtifactType,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Artifact]:
        """
        Retrieve artifacts filtered by their type.

        Args:
            artifact_type: The ``ArtifactType`` to filter by.
            project_id: If provided, only return artifacts within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``Artifact`` instances.
        """
        ...

    @abstractmethod
    async def get_by_execution_session(
        self,
        execution_session_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Artifact]:
        """
        Retrieve all artifacts produced during a specific execution session.

        Args:
            execution_session_id: The UUID of the execution session.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``Artifact`` instances from the session.
        """
        ...

    @abstractmethod
    async def search_by_name(
        self,
        name_pattern: str,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Artifact]:
        """
        Search artifacts by name using a pattern match.

        Args:
            name_pattern: A substring or pattern to match against artifact names.
            project_id: If provided, only search within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``Artifact`` instances.
        """
        ...