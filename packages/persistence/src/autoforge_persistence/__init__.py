"""
AutoForge AI — Persistence Repository Contracts.

This package defines the repository abstraction layer for the AutoForge AI
platform. It contains **contracts only** — abstract base classes, protocols,
and exception definitions — with no storage technology dependencies.

Every subsystem that needs to persist or retrieve domain entities should
depend on these interfaces, not on concrete implementations. This ensures
that storage backends can be swapped without affecting business logic.
"""

from autoforge_persistence.artifact_repository import ArtifactRepository
from autoforge_persistence.exceptions import (
    ConcurrencyError,
    DuplicateEntityError,
    EntityNotFoundError,
    RepositoryError,
    TransactionError,
)
from autoforge_persistence.execution_repository import ExecutionRepository
from autoforge_persistence.memory_repository import MemoryRepository
from autoforge_persistence.project_repository import ProjectRepository
from autoforge_persistence.protocols import (
    AsyncIterableRepositoryProtocol,
    RepositoryProtocol,
)
from autoforge_persistence.repository import AsyncIterableRepository, Repository
from autoforge_persistence.task_repository import TaskRepository
from autoforge_persistence.unit_of_work import UnitOfWork

__all__ = [
    # Base repository
    "Repository",
    "AsyncIterableRepository",
    # Protocols
    "RepositoryProtocol",
    "AsyncIterableRepositoryProtocol",
    # Specialised repositories
    "ProjectRepository",
    "TaskRepository",
    "ArtifactRepository",
    "ExecutionRepository",
    "MemoryRepository",
    # Unit of Work
    "UnitOfWork",
    # Exceptions
    "RepositoryError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "ConcurrencyError",
    "TransactionError",
]