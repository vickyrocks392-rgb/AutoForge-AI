# AutoForge AI — Canonical Domain Models

## Purpose

The `packages/models/` package defines the **canonical domain models** for the AutoForge AI platform. These models are the shared, universal language that every subsystem — services, APIs, execution engine, memory engine, control plane, data plane, and persistence plane — uses to communicate.

## Design Philosophy

### 1. Infrastructure‑Independent

These models contain **zero infrastructure concerns**. There is no:

- ORM mapping or SQLAlchemy
- FastAPI dependency or Pydantic model configuration tied to web frameworks
- Repository pattern or data access logic
- Serialization format assumptions beyond what Pydantic v2 provides natively

This independence means the models can be imported and used by **any** future subsystem without creating coupling to a particular database, framework, or runtime.

### 2. Strict Typing & Validation

Every field is strictly typed. Enums replace stringly‑typed fields. Pydantic v2 validators enforce invariants at construction time. UUIDs are used for all identities. `datetime` with timezone awareness is used for all timestamps.

### 3. Minimal Responsibilities

Each model has a single, clear responsibility. There is no business logic, no service methods, no behaviour — only **data** and **validation**. Behaviour belongs in services; these models are the contracts those services operate on.

### 4. Composition over Inheritance

Where appropriate, models compose shared value objects (e.g. `ResourceRequirements`, `ModelConfig`) rather than deep inheritance hierarchies. The common `BaseModel` provides only serialization, validation, and identity plumbing.

## Relationship with Other Platform Components

```
┌─────────────────────────────────────────────────────────┐
│                    Services / APIs                       │
│  (planner, research, requirements, architecture, etc.)  │
└──────────────────────┬──────────────────────────────────┘
                       │ depends on
┌──────────────────────▼──────────────────────────────────┐
│              Canonical Domain Models                     │
│              (packages/models/)                          │
└──────┬──────────────────────┬──────────────────┬────────┘
       │                      │                  │
       ▼                      ▼                  ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│  Persistence │   │  Execution Engine│   │  Memory      │
│  Plane       │   │  (services/)     │   │  Engine      │
└──────────────┘   └──────────────────┘   └──────────────┘
```

- **Services** import models to define their inputs, outputs, and internal state.
- **Persistence Plane** maps models to/from storage (the models themselves know nothing about storage).
- **Execution Engine** uses models to represent work units, checkpoints, and artifacts.
- **Memory Engine** uses models to represent knowledge graph nodes and edges.
- **Control Plane** uses models to represent projects, sessions, and quality gates.

## Why Infrastructure Independence Matters

1. **Testability** — Models can be instantiated and validated in isolation without a database or web server.
2. **Portability** — The same model package can be used by CLI tools, background workers, web APIs, and event processors.
3. **Evolvability** — Storage technology can change (PostgreSQL → ScyllaDB, file system → S3) without touching model definitions.
4. **Contract Clarity** — The models serve as the single source of truth for data contracts between subsystems.

## Models Overview

| Model              | Purpose                                                    |
|--------------------|------------------------------------------------------------|
| `Project`          | Top-level container for a software project being built     |
| `Task`             | A unit of work within a project                            |
| `Artifact`         | A file or data output produced by a task                   |
| `Checkpoint`       | A snapshot of execution state for resumability             |
| `ExecutionSession` | A single run of a task or workflow                         |
| `Employee`         | An AI agent or human participant                           |
| `Review`           | A quality review of an artifact or task                    |
| `Event`            | A domain event emitted during execution                    |
| `ModelProfile`     | Configuration for an AI model provider                     |
| `MemoryEntry`      | A stored memory item (episodic, semantic, procedural)      |
| `KnowledgeNode`    | A node in the knowledge graph                              |
| `KnowledgeEdge`    | A relationship between two knowledge nodes                 |
| `QualityGate`      | A quality threshold that must be satisfied                 |

## Enums Overview

| Enum                | Values                                                                 |
|---------------------|------------------------------------------------------------------------|
| `TaskStatus`        | pending, ready, running, paused, completed, failed, cancelled, blocked |
| `TaskPriority`      | low, medium, high, critical                                            |
| `ReviewStatus`      | pending, in_progress, approved, changes_requested, rejected            |
| `ArtifactType`      | specification, design, code, test, documentation, config, data, other  |
| `EmployeeRole`      | architect, developer, reviewer, tester, planner, researcher, operator  |
| `ExecutionStatus`   | pending, running, paused, completed, failed, cancelled, timed_out      |
| `CheckpointType`    | automatic, manual, milestone, recovery                                 |
| `EventType`         | created, updated, deleted, started, completed, failed, approved, ...   |
| `ModelProvider`     | openai, anthropic, google, local, custom                               |
| `MemoryType`        | episodic, semantic, procedural                                         |
| `KnowledgeEdgeType` | depends_on, produces, requires, relates_to, implements, extends        |
| `QualityGateStatus` | pending, passing, warning, failing, error                              |

## Future Dependencies

When the platform grows, these models will be consumed by:

- **`packages/persistence/`** — Repository implementations that map models to storage
- **`packages/events/`** — Event bus serialization/deserialization
- **`services/*/`** — All microservices for their input/output contracts
- **`apps/api/`** — Request/response schemas (via composition or inheritance)
- **`apps/web/`** — Type generation for frontend TypeScript types

The models themselves, however, will never depend on any of these.