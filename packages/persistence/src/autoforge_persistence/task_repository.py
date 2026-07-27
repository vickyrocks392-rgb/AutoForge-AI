"""
Task repository interface for the AutoForge AI platform.

Defines the contract for persisting and querying ``Task`` entities.
Extends the generic ``Repository`` with task-specific query methods
for status filtering, dependency resolution, and project scoping.
"""

from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Sequence

from autoforge_models.enums import TaskPriority, TaskStatus
from autoforge_models.task import Task

from autoforge_persistence.repository import Repository


class TaskRepository(Repository[Task]):
    """
    Repository interface for ``Task`` entities.

    Provides domain-specific queries for task lifecycle management,
    including readiness checks, status filtering, and project scoping.
    """

    @abstractmethod
    async def get_ready_tasks(
        self,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve tasks that are ready to execute within a project.

        A task is considered ready when all of its dependencies have been
        completed and its own status is ``TaskStatus.READY``.

        Args:
            project_id: The UUID of the parent project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ready ``Task`` instances.
        """
        ...

    @abstractmethod
    async def get_by_status(
        self,
        status: TaskStatus,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve tasks filtered by their lifecycle status.

        Args:
            status: The ``TaskStatus`` to filter by.
            project_id: If provided, only return tasks within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``Task`` instances.
        """
        ...

    @abstractmethod
    async def get_by_project(
        self,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve all tasks belonging to a specific project.

        Args:
            project_id: The UUID of the parent project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``Task`` instances within the project.
        """
        ...

    @abstractmethod
    async def get_by_priority(
        self,
        priority: TaskPriority,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve tasks filtered by priority level.

        Args:
            priority: The ``TaskPriority`` to filter by.
            project_id: If provided, only return tasks within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of matching ``Task`` instances.
        """
        ...

    @abstractmethod
    async def get_blocked_tasks(
        self,
        project_id: uuid.UUID | None = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve tasks that are currently blocked.

        Blocked tasks have unresolved dependencies or conditions that
        prevent them from being executed.

        Args:
            project_id: If provided, only return tasks within this project.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of blocked ``Task`` instances.
        """
        ...

    @abstractmethod
    async def get_dependents(
        self,
        task_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve tasks that depend on the specified task.

        Args:
            task_id: The UUID of the task whose dependents to find.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of ``Task`` instances that depend on the given task.
        """
        ...

    @abstractmethod
    async def get_subtasks(
        self,
        parent_task_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """
        Retrieve the direct subtasks of a parent task.

        Args:
            parent_task_id: The UUID of the parent task.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A sequence of child ``Task`` instances.
        """
        ...