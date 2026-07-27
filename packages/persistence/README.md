# AutoForge AI — Persistence Repository Contracts

## Purpose

This package defines the **repository abstraction layer** for the AutoForge AI platform. It contains **contracts only** — abstract base classes, structural typing protocols, and exception definitions — with **zero storage technology dependencies**.

The persistence contracts serve as the boundary between domain logic and data storage. Every subsystem that needs to persist or retrieve domain entities depends on these interfaces, not on concrete implementations. This ensures that storage backends can be swapped, tested, or replaced without affecting business logic.

## Design Philosophy

### Clean Architecture

The repository contracts sit at the **interface adapter** layer of Clean Architecture. Domain logic (use cases, services) depends on these interfaces **inward**, never on concrete storage implementations **outward**.

### SOLID Principles

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | Each repository interface manages exactly one aggregate root. |
| **Open/Closed** | New query methods can be added to repository interfaces without modifying callers. |
| **Liskov Substitution** | Any implementation of a repository interface can be substituted without breaking consumers. |
| **Interface Segregation** | Specialised repository interfaces expose only domain-relevant query methods. |
| **Dependency Inversion** | High-level modules depend on abstract repository interfaces, not on concrete storage. |

### Generic Typing

The base `Repository[T]` is generic over the entity type `T`, which must be a subclass of `AutoForgeBaseModel`. This provides compile-time type safety across all repository operations.

### Async by Default

All repository methods are asynchronous (`async def`). This supports non-blocking I/O for production storage backends without imposing synchronous overhead on callers.

## Why Repository Contracts Exist

1. **Decoupling**: Domain logic is isolated from storage technology choices (SQL, NoSQL, file-based, etc.).
2. **Testability**: Use cases can be tested with lightweight test doubles that implement the same interfaces.
3. **Evolvability**: Storage backends can be upgraded or replaced without touching business logic.
4. **Clarity**: The interface explicitly documents every operation the domain layer needs from persistence.

## Package Structure

```
packages/persistence/
├── README.md
├── pyproject.toml
├── src/
│   └── autoforge_persistence/
│       ├── __init__.py              # Public API exports
│       ├── repository.py            # Generic base Repository[T] ABC
│       ├── protocols.py             # Structural typing protocols
│       ├── exceptions.py            # Persistence exception hierarchy
│       ├── project_repository.py    # ProjectRepository interface
│       ├── task_repository.py       # TaskRepository interface
│       ├── artifact_repository.py   # ArtifactRepository interface
│       ├── execution_repository.py  # ExecutionRepository interface
│       ├── memory_repository.py     # MemoryRepository interface
│       └── unit_of_work.py          # UnitOfWork ABC
└── tests/
    └── test_contracts.py            # Interface definition tests
```

## Interfaces Defined

### Base Repository

```python
class Repository(ABC, Generic[T]):
    async def get(self, id: uuid.UUID) -> T: ...
    async def list(self, *, skip: int = 0, limit: int = 100, **filters: Any) -> Sequence[T]: ...
    async def add(self, entity: T) -> T: ...
    async def update(self, entity: T) -> T: ...
    async def remove(self, id: uuid.UUID) -> None: ...
    async def exists(self, id: uuid.UUID) -> bool: ...
```

### Specialised Repositories

| Interface | Entity | Domain-Specific Queries |
|-----------|--------|------------------------|
| `ProjectRepository` | `Project` | `get_by_name()`, `list_active()`, `list_archived()`, `search_by_tags()` |
| `TaskRepository` | `Task` | `get_ready_tasks()`, `get_by_status()`, `get_by_project()`, `get_by_priority()`, `get_blocked_tasks()`, `get_dependents()`, `get_subtasks()` |
| `ArtifactRepository` | `Artifact` | `get_by_project()`, `get_by_task()`, `get_by_type()`, `get_by_execution_session()`, `search_by_name()` |
| `ExecutionRepository` | `ExecutionSession` | `get_running_sessions()`, `get_by_status()`, `get_by_project()`, `get_by_task()`, `get_recent_failures()`, `get_stale_sessions()` |
| `MemoryRepository` | `MemoryEntry` | `search()`, `get_by_type()`, `get_by_project()`, `get_by_key()`, `get_most_important()`, `get_recently_accessed()`, `increment_access_count()` |

### Unit of Work

```python
class UnitOfWork(ABC):
    @property
    def projects(self) -> ProjectRepository: ...
    @property
    def tasks(self) -> TaskRepository: ...
    @property
    def artifacts(self) -> ArtifactRepository: ...
    @property
    def executions(self) -> ExecutionRepository: ...
    @property
    def memories(self) -> MemoryRepository: ...

    async def begin(self) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

The `UnitOfWork` also supports async context manager usage:

```python
async with unit_of_work:
    project = await unit_of_work.projects.get(project_id)
    # ... make changes ...
    # Auto-commits on success, auto-rollbacks on exception
```

### Exceptions

| Exception | When Raised |
|-----------|-------------|
| `RepositoryError` | Base for all persistence errors |
| `EntityNotFoundError` | Entity not found by `get()` or `update()` |
| `DuplicateEntityError` | Duplicate on `add()` |
| `ConcurrencyError` | Concurrent modification detected |
| `TransactionError` | Transaction begin/commit/rollback failure |

### Protocols

Structural typing protocols (`RepositoryProtocol`, `AsyncIterableRepositoryProtocol`) are provided for duck-typing scenarios, enabling test doubles and alternative implementations without requiring explicit inheritance.

## How Implementations Will Plug In

Concrete implementations live in **separate packages** (e.g., `autoforge-persistence-sql`, `autoforge-persistence-memory`). Each implementation:

1. **Inherits** from the appropriate repository ABC(s).
2. **Implements** all abstract methods using its chosen storage technology.
3. **Extends** `UnitOfWork` to provide transaction management.
4. **Is registered** with the dependency injection container at application startup.

Example implementation package structure:

```
autoforge-persistence-sql/
├── src/
│   └── autoforge_persistence_sql/
│       ├── repositories/
│       │   ├── sql_project_repository.py
│       │   ├── sql_task_repository.py
│       │   └── ...
│       ├── sql_unit_of_work.py
│       └── ...
```

## Dependencies

- **Runtime**: `autoforge-models` (for domain entity types)
- **No storage libraries**: This package imports no SQL, NoSQL, or caching libraries.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=autoforge_persistence