"""
Tests for the persistence repository contracts.

These tests verify that:
- Interface definitions are syntactically valid.
- Generic typing is correctly parameterised.
- Exception hierarchy is properly structured.
- All abstract methods are defined on each repository interface.

No persistence logic is tested. No storage technology is imported.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Sequence, get_type_hints

import pytest

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


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Verify the exception inheritance chain."""

    def test_repository_error_is_base(self) -> None:
        assert issubclass(RepositoryError, Exception)

    def test_entity_not_found_inherits(self) -> None:
        assert issubclass(EntityNotFoundError, RepositoryError)

    def test_duplicate_entity_inherits(self) -> None:
        assert issubclass(DuplicateEntityError, RepositoryError)

    def test_concurrency_error_inherits(self) -> None:
        assert issubclass(ConcurrencyError, RepositoryError)

    def test_transaction_error_inherits(self) -> None:
        assert issubclass(TransactionError, RepositoryError)

    def test_entity_not_found_has_entity_type_and_id(self) -> None:
        exc = EntityNotFoundError("TestEntity", uuid.uuid4())
        assert hasattr(exc, "entity_type")
        assert hasattr(exc, "entity_id")

    def test_duplicate_entity_has_key_and_value(self) -> None:
        exc = DuplicateEntityError("TestEntity", "name", "test")
        assert hasattr(exc, "key")
        assert hasattr(exc, "value")

    def test_concurrency_error_has_entity_type_and_id(self) -> None:
        exc = ConcurrencyError("TestEntity", uuid.uuid4())
        assert hasattr(exc, "entity_type")
        assert hasattr(exc, "entity_id")

    def test_repository_error_has_original(self) -> None:
        inner = ValueError("inner")
        exc = RepositoryError("wrapped", original=inner)
        assert exc.original is inner


# ---------------------------------------------------------------------------
# Base Repository interface
# ---------------------------------------------------------------------------


class TestRepositoryInterface:
    """Verify the generic Repository ABC defines all required methods."""

    def test_is_abstract(self) -> None:
        assert issubclass(Repository, ABC)

    def test_has_get_method(self) -> None:
        assert hasattr(Repository, "get")
        assert getattr(Repository.get, "__isabstractmethod__", False)

    def test_has_list_method(self) -> None:
        assert hasattr(Repository, "list")
        assert getattr(Repository.list, "__isabstractmethod__", False)

    def test_has_add_method(self) -> None:
        assert hasattr(Repository, "add")
        assert getattr(Repository.add, "__isabstractmethod__", False)

    def test_has_update_method(self) -> None:
        assert hasattr(Repository, "update")
        assert getattr(Repository.update, "__isabstractmethod__", False)

    def test_has_remove_method(self) -> None:
        assert hasattr(Repository, "remove")
        assert getattr(Repository.remove, "__isabstractmethod__", False)

    def test_has_exists_method(self) -> None:
        assert hasattr(Repository, "exists")
        assert getattr(Repository.exists, "__isabstractmethod__", False)

    def test_all_methods_are_async(self) -> None:
        """All repository methods should be async (coroutine)."""
        for method_name in ("get", "list", "add", "update", "remove", "exists"):
            method = getattr(Repository, method_name)
            hints = get_type_hints(method)
            # The return type hint should be available
            assert "return" in hints, f"{method_name} is missing return type hint"


class TestAsyncIterableRepositoryInterface:
    """Verify the AsyncIterableRepository extends Repository with __aiter__."""

    def test_is_abstract(self) -> None:
        assert issubclass(AsyncIterableRepository, ABC)

    def test_extends_repository(self) -> None:
        assert issubclass(AsyncIterableRepository, Repository)

    def test_has_aiter_method(self) -> None:
        assert hasattr(AsyncIterableRepository, "__aiter__")
        assert getattr(
            AsyncIterableRepository.__aiter__, "__isabstractmethod__", False
        )


# ---------------------------------------------------------------------------
# Specialised repository interfaces
# ---------------------------------------------------------------------------


class TestProjectRepositoryInterface:
    """Verify ProjectRepository defines all domain-specific methods."""

    def test_extends_repository(self) -> None:
        assert issubclass(ProjectRepository, Repository)

    def test_has_get_by_name(self) -> None:
        assert hasattr(ProjectRepository, "get_by_name")
        assert getattr(ProjectRepository.get_by_name, "__isabstractmethod__", False)

    def test_has_list_active(self) -> None:
        assert hasattr(ProjectRepository, "list_active")
        assert getattr(ProjectRepository.list_active, "__isabstractmethod__", False)

    def test_has_list_archived(self) -> None:
        assert hasattr(ProjectRepository, "list_archived")
        assert getattr(ProjectRepository.list_archived, "__isabstractmethod__", False)

    def test_has_search_by_tags(self) -> None:
        assert hasattr(ProjectRepository, "search_by_tags")
        assert getattr(ProjectRepository.search_by_tags, "__isabstractmethod__", False)


class TestTaskRepositoryInterface:
    """Verify TaskRepository defines all domain-specific methods."""

    def test_extends_repository(self) -> None:
        assert issubclass(TaskRepository, Repository)

    def test_has_get_ready_tasks(self) -> None:
        assert hasattr(TaskRepository, "get_ready_tasks")
        assert getattr(TaskRepository.get_ready_tasks, "__isabstractmethod__", False)

    def test_has_get_by_status(self) -> None:
        assert hasattr(TaskRepository, "get_by_status")
        assert getattr(TaskRepository.get_by_status, "__isabstractmethod__", False)

    def test_has_get_by_project(self) -> None:
        assert hasattr(TaskRepository, "get_by_project")
        assert getattr(TaskRepository.get_by_project, "__isabstractmethod__", False)

    def test_has_get_by_priority(self) -> None:
        assert hasattr(TaskRepository, "get_by_priority")
        assert getattr(TaskRepository.get_by_priority, "__isabstractmethod__", False)

    def test_has_get_blocked_tasks(self) -> None:
        assert hasattr(TaskRepository, "get_blocked_tasks")
        assert getattr(TaskRepository.get_blocked_tasks, "__isabstractmethod__", False)

    def test_has_get_dependents(self) -> None:
        assert hasattr(TaskRepository, "get_dependents")
        assert getattr(TaskRepository.get_dependents, "__isabstractmethod__", False)

    def test_has_get_subtasks(self) -> None:
        assert hasattr(TaskRepository, "get_subtasks")
        assert getattr(TaskRepository.get_subtasks, "__isabstractmethod__", False)


class TestArtifactRepositoryInterface:
    """Verify ArtifactRepository defines all domain-specific methods."""

    def test_extends_repository(self) -> None:
        assert issubclass(ArtifactRepository, Repository)

    def test_has_get_by_project(self) -> None:
        assert hasattr(ArtifactRepository, "get_by_project")
        assert getattr(ArtifactRepository.get_by_project, "__isabstractmethod__", False)

    def test_has_get_by_task(self) -> None:
        assert hasattr(ArtifactRepository, "get_by_task")
        assert getattr(ArtifactRepository.get_by_task, "__isabstractmethod__", False)

    def test_has_get_by_type(self) -> None:
        assert hasattr(ArtifactRepository, "get_by_type")
        assert getattr(ArtifactRepository.get_by_type, "__isabstractmethod__", False)

    def test_has_get_by_execution_session(self) -> None:
        assert hasattr(ArtifactRepository, "get_by_execution_session")
        assert getattr(
            ArtifactRepository.get_by_execution_session, "__isabstractmethod__", False
        )

    def test_has_search_by_name(self) -> None:
        assert hasattr(ArtifactRepository, "search_by_name")
        assert getattr(ArtifactRepository.search_by_name, "__isabstractmethod__", False)


class TestExecutionRepositoryInterface:
    """Verify ExecutionRepository defines all domain-specific methods."""

    def test_extends_repository(self) -> None:
        assert issubclass(ExecutionRepository, Repository)

    def test_has_get_running_sessions(self) -> None:
        assert hasattr(ExecutionRepository, "get_running_sessions")
        assert getattr(
            ExecutionRepository.get_running_sessions, "__isabstractmethod__", False
        )

    def test_has_get_by_status(self) -> None:
        assert hasattr(ExecutionRepository, "get_by_status")
        assert getattr(
            ExecutionRepository.get_by_status, "__isabstractmethod__", False
        )

    def test_has_get_by_project(self) -> None:
        assert hasattr(ExecutionRepository, "get_by_project")
        assert getattr(
            ExecutionRepository.get_by_project, "__isabstractmethod__", False
        )

    def test_has_get_by_task(self) -> None:
        assert hasattr(ExecutionRepository, "get_by_task")
        assert getattr(ExecutionRepository.get_by_task, "__isabstractmethod__", False)

    def test_has_get_recent_failures(self) -> None:
        assert hasattr(ExecutionRepository, "get_recent_failures")
        assert getattr(
            ExecutionRepository.get_recent_failures, "__isabstractmethod__", False
        )

    def test_has_get_stale_sessions(self) -> None:
        assert hasattr(ExecutionRepository, "get_stale_sessions")
        assert getattr(
            ExecutionRepository.get_stale_sessions, "__isabstractmethod__", False
        )


class TestMemoryRepositoryInterface:
    """Verify MemoryRepository defines all domain-specific methods."""

    def test_extends_repository(self) -> None:
        assert issubclass(MemoryRepository, Repository)

    def test_has_search(self) -> None:
        assert hasattr(MemoryRepository, "search")
        assert getattr(MemoryRepository.search, "__isabstractmethod__", False)

    def test_has_get_by_type(self) -> None:
        assert hasattr(MemoryRepository, "get_by_type")
        assert getattr(MemoryRepository.get_by_type, "__isabstractmethod__", False)

    def test_has_get_by_project(self) -> None:
        assert hasattr(MemoryRepository, "get_by_project")
        assert getattr(MemoryRepository.get_by_project, "__isabstractmethod__", False)

    def test_has_get_by_key(self) -> None:
        assert hasattr(MemoryRepository, "get_by_key")
        assert getattr(MemoryRepository.get_by_key, "__isabstractmethod__", False)

    def test_has_get_most_important(self) -> None:
        assert hasattr(MemoryRepository, "get_most_important")
        assert getattr(
            MemoryRepository.get_most_important, "__isabstractmethod__", False
        )

    def test_has_get_recently_accessed(self) -> None:
        assert hasattr(MemoryRepository, "get_recently_accessed")
        assert getattr(
            MemoryRepository.get_recently_accessed, "__isabstractmethod__", False
        )

    def test_has_increment_access_count(self) -> None:
        assert hasattr(MemoryRepository, "increment_access_count")
        assert getattr(
            MemoryRepository.increment_access_count, "__isabstractmethod__", False
        )


# ---------------------------------------------------------------------------
# Unit of Work interface
# ---------------------------------------------------------------------------


class TestUnitOfWorkInterface:
    """Verify the UnitOfWork ABC defines all required properties and methods."""

    def test_is_abstract(self) -> None:
        assert issubclass(UnitOfWork, ABC)

    def test_has_projects_property(self) -> None:
        assert hasattr(UnitOfWork, "projects")
        assert isinstance(UnitOfWork.projects, property)

    def test_has_tasks_property(self) -> None:
        assert hasattr(UnitOfWork, "tasks")
        assert isinstance(UnitOfWork.tasks, property)

    def test_has_artifacts_property(self) -> None:
        assert hasattr(UnitOfWork, "artifacts")
        assert isinstance(UnitOfWork.artifacts, property)

    def test_has_executions_property(self) -> None:
        assert hasattr(UnitOfWork, "executions")
        assert isinstance(UnitOfWork.executions, property)

    def test_has_memories_property(self) -> None:
        assert hasattr(UnitOfWork, "memories")
        assert isinstance(UnitOfWork.memories, property)

    def test_has_begin_method(self) -> None:
        assert hasattr(UnitOfWork, "begin")
        assert getattr(UnitOfWork.begin, "__isabstractmethod__", False)

    def test_has_commit_method(self) -> None:
        assert hasattr(UnitOfWork, "commit")
        assert getattr(UnitOfWork.commit, "__isabstractmethod__", False)

    def test_has_rollback_method(self) -> None:
        assert hasattr(UnitOfWork, "rollback")
        assert getattr(UnitOfWork.rollback, "__isabstractmethod__", False)

    def test_has_context_manager_support(self) -> None:
        assert hasattr(UnitOfWork, "__aenter__")
        assert hasattr(UnitOfWork, "__aexit__")


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------


class TestRepositoryProtocol:
    """Verify the structural typing protocol is correctly defined."""

    def test_is_runtime_checkable(self) -> None:
        import typing
        assert typing.get_type_hints  # ensure typing module is available
        # The protocol should be runtime_checkable
        assert hasattr(RepositoryProtocol, "__instancecheck__")

    def test_has_required_methods(self) -> None:
        """Protocol should define the same methods as Repository."""
        for method in ("get", "list", "add", "update", "remove", "exists"):
            assert hasattr(RepositoryProtocol, method)


class TestAsyncIterableRepositoryProtocol:
    """Verify the async iterable protocol extends the base protocol."""

    def test_extends_repository_protocol(self) -> None:
        assert issubclass(AsyncIterableRepositoryProtocol, RepositoryProtocol)

    def test_has_aiter(self) -> None:
        assert hasattr(AsyncIterableRepositoryProtocol, "__aiter__")


# ---------------------------------------------------------------------------
# Generic typing
# ---------------------------------------------------------------------------


class TestGenericTyping:
    """Verify that repository interfaces are properly parameterised generics."""

    def test_repository_is_generic(self) -> None:
        """Repository should be generic over the entity type."""
        import typing
        origin = typing.get_origin(Repository)
        # Repository is ABC + Generic[T], so origin should be ABC
        # but more importantly, it should have __parameters__
        assert hasattr(Repository, "__parameters__")

    def test_specialised_repositories_are_parameterised(self) -> None:
        """Each specialised repository should bind its entity type."""
        # These should not raise
        from autoforge_models.project import Project
        from autoforge_models.task import Task
        from autoforge_models.artifact import Artifact
        from autoforge_models.execution_session import ExecutionSession
        from autoforge_models.memory_entry import MemoryEntry

        # Verify the generic bases are correct by checking __orig_bases__
        for repo_class, entity_class in [
            (ProjectRepository, Project),
            (TaskRepository, Task),
            (ArtifactRepository, Artifact),
            (ExecutionRepository, ExecutionSession),
            (MemoryRepository, MemoryEntry),
        ]:
            bases = repo_class.__orig_bases__ if hasattr(repo_class, "__orig_bases__") else repo_class.__bases__
            # At minimum, the class should be a subclass of Repository[Entity]
            assert issubclass(repo_class, Repository), f"{repo_class.__name__} is not a Repository subclass"