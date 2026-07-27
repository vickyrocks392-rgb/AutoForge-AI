"""
Unit of Work interface for the AutoForge AI platform.

Defines the contract for transactional access to repositories. The
Unit of Work pattern ensures that multiple repository operations can
be composed into a single atomic transaction with begin, commit, and
rollback semantics.

This module defines **contracts only**. No transaction implementation
or storage technology is referenced.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from autoforge_persistence.artifact_repository import ArtifactRepository
from autoforge_persistence.execution_repository import ExecutionRepository
from autoforge_persistence.memory_repository import MemoryRepository
from autoforge_persistence.project_repository import ProjectRepository
from autoforge_persistence.task_repository import TaskRepository


class UnitOfWork(ABC):
    """
    Abstract unit of work that provides transactional access to all
    domain repositories.

    A UnitOfWork instance acts as a single transactional boundary.
    All repository operations performed within the unit of work are
    committed atomically when ``commit()`` is called, or discarded
    when ``rollback()`` is called.

    Usage::

        async with unit_of_work:
            project = await unit_of_work.projects.get(project_id)
            project = project.model_copy(update={"name": "New Name"})
            await unit_of_work.projects.update(project)
            await unit_of_work.commit()

    Concrete implementations must provide the actual transaction
    management and repository bindings.
    """

    @property
    @abstractmethod
    def projects(self) -> ProjectRepository:
        """Repository for ``Project`` entities."""
        ...

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Repository for ``Task`` entities."""
        ...

    @property
    @abstractmethod
    def artifacts(self) -> ArtifactRepository:
        """Repository for ``Artifact`` entities."""
        ...

    @property
    @abstractmethod
    def executions(self) -> ExecutionRepository:
        """Repository for ``ExecutionSession`` entities."""
        ...

    @property
    @abstractmethod
    def memories(self) -> MemoryRepository:
        """Repository for ``MemoryEntry`` entities."""
        ...

    @abstractmethod
    async def begin(self) -> None:
        """
        Begin a new transaction.

        All subsequent repository operations will be part of this
        transaction until ``commit()`` or ``rollback()`` is called.

        Raises:
            TransactionError: If a transaction is already in progress.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit the current transaction.

        All changes made through the repositories since ``begin()``
        will be persisted atomically.

        Raises:
            TransactionError: If the commit fails.
        """
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """
        Roll back the current transaction.

        All changes made through the repositories since ``begin()``
        will be discarded.

        Raises:
            TransactionError: If the rollback fails.
        """
        ...

    async def __aenter__(self) -> UnitOfWork:
        """Enter async context manager, beginning a transaction."""
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """
        Exit async context manager.

        If an exception occurred, the transaction is rolled back.
        Otherwise, it is committed.
        """
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()