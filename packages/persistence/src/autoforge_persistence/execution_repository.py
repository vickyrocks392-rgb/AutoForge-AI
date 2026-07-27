"""
Execution session repository interface for the AutoForge AI platform.

Defines the contract for persisting and querying ``ExecutionSession``
entities. Extends the generic ``Repository`` with execution-specific
query methods for status tracking, project scoping, and task association.
"""

from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Sequence

from autoforge_models.enums import ExecutionStatus
from autoforge_models.execution_session import ExecutionSession

from autoforge_persistence.repository import Repository


class ExecutionRepository(Repository[ExecutionSession]):
    """
    Repository interface for ``ExecutionSession`` entities.

    Provides domain-specific queries for execution lifecycle management,
    including status filtering, project scoping, and running session
    discovery.
    """

    @abstractmethod
    async def get_running_sessions(
        self,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve all currently running execution sessions.

        A session is considered running when its status is
        ``ExecutionStatus.RUNNING``.

        Args:
            project_id: If provided, only return sessions within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of running ``ExecutionSession`` instances.
        """
        ...

    @abstractmethod
    async def get_by_status(
        self,
        status: ExecutionStatus,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve execution sessions filtered by their status.

        Args:
            status: The ``ExecutionStatus`` to filter by.
            project_id: If provided, only return sessions within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``ExecutionSession`` instances.
        """
        ...

    @abstractmethod
    async def get_by_project(
        self,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve all execution sessions belonging to a specific project.

        Args:
            project_id: The UUID of the parent project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``ExecutionSession`` instances within the project.
        """
        ...

    @abstractmethod
    async def get_by_task(
        self,
        task_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve all execution sessions for a specific task.

        Args:
            task_id: The UUID of the task.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``ExecutionSession`` instances for the task.
        """
        ...

    @abstractmethod
    async def get_recent_failures(
        self,
        project_id: uuid.UUID | None = None,
        *,
        since_hours: int = 24,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve execution sessions that failed within a recent time window.

        Args:
            project_id: If provided, only return sessions within this project.
            since_hours: Number of hours to look back from now.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of failed ``ExecutionSession`` instances.
        """
        ...

    @abstractmethod
    async def get_stale_sessions(
        self,
        *,
        older_than_minutes: int = 30,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ExecutionSession]:
        """
        Retrieve sessions that have been running longer than expected.

        Stale sessions are those in a non-terminal state (e.g. ``RUNNING``
        or ``PENDING``) that have not been updated within the specified
        time window.

        Args:
            older_than_minutes: Age threshold in minutes.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of stale ``ExecutionSession`` instances.
        """
        ...