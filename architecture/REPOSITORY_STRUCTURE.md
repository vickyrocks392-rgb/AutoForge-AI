# AutoForge AI OS — Repository Structure

**Canonical Repository Governance Document**

**Version:** 1.0  
**Status:** Frozen  
**Last Updated:** 2026-07-30  

This document is the canonical definition of the AutoForge AI OS repository layout. Every future contributor, AI agent, and developer must follow the rules defined herein.

---

## Table of Contents

1. [Repository Philosophy](#1-repository-philosophy)
2. [Top-Level Directory Structure](#2-top-level-directory-structure)
3. [Directory Responsibilities and Ownership](#3-directory-responsibilities-and-ownership)
4. [Documentation Rules](#4-documentation-rules)
5. [Package Rules](#5-package-rules)
6. [Application Rules](#6-application-rules)
7. [Naming Conventions](#7-naming-conventions)
8. [Architectural Governance](#8-architectural-governance)
9. [Documentation Lifecycle](#9-documentation-lifecycle)
10. [Repository Lifecycle](#10-repository-lifecycle)
11. [Future Expansion Guidelines](#11-future-expansion-guidelines)
12. [Repository Governance Summary](#12-repository-governance-summary)

---

## 1. Repository Philosophy

### 1.1 Single Source of Truth

The repository is organized around a single source of truth: `architecture/ARCHITECTURE.md`. Every document, package, application, and service in this repository derives from or supports this canonical architecture. No document may redefine, contradict, or duplicate the architecture.

### 1.2 Separation by Purpose

Every file in this repository has a clearly defined location based on its purpose:

- **Canonical architecture** → `architecture/`
- **Supporting documentation** → `docs/`
- **Reusable platform modules** → `packages/`
- **Deployable applications** → `apps/`
- **Executable services** → `services/`
- **Cross-package testing** → `tests/`
- **Automation** → `scripts/`
- **Sample projects** → `examples/`
- **Containerization** → `docker/`
- **GitHub configuration** → `.github/`

### 1.3 No Duplication

No document exists in multiple locations. If a document's content is needed in multiple contexts, create references (links) rather than copies.

### 1.4 Scalability by Convention

The repository is designed to scale to hundreds of packages and documents without becoming disorganized. Convention replaces configuration. Every future file has a clearly defined location. No future contributor should need to guess where a new file belongs.

---

## 2. Top-Level Directory Structure

```
/
├── architecture/          # Canonical architecture documentation
├── docs/                  # Supporting documentation
├── apps/                  # Deployable applications
├── packages/              # Reusable platform modules
├── services/              # Executable services
├── tests/                 # Cross-package and integration testing
├── scripts/               # Automation and utility scripts
├── examples/              # Sample projects and usage examples
├── docker/                # Containerization assets
└── .github/               # GitHub configuration
```

### Root-Level Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, and documentation index |
| `LICENSE` | Project license (MIT) |
| `Makefile` | Top-level build and automation targets |
| `package.json` | Monorepo workspace configuration (npm/pnpm workspaces) |
| `tsconfig.base.json` | Base TypeScript configuration shared across packages |
| `.editorconfig` | Editor configuration for consistent formatting |
| `.gitattributes` | Git attribute configuration |
| `.gitignore` | Git ignore patterns |
| `.nvmrc` | Node.js version specification |
| `docker-compose.yml` | Local development infrastructure |

---

## 3. Directory Responsibilities and Ownership

### 3.1 `architecture/` — Canonical Architecture Documentation

**Purpose:** Contains only canonical architecture documentation that defines the platform's fundamental design, principles, and specifications.

**Ownership:** Architecture Team / Platform Architects

**Contents:**

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | **Single source of truth.** The canonical architectural blueprint. Defines subsystems, boundaries, responsibilities, and interactions. |
| `VISION.md` | Long-term vision and aspirational direction of the platform. |
| `PRINCIPLES.md` | Core engineering and design principles that govern all decisions. |
| `MANIFEST.md` | The platform manifesto — what AutoForge AI OS is and is not. |
| `GLOSSARY.md` | Canonical glossary of terms used across the platform. |
| `REPOSITORY_STRUCTURE.md` | **This document.** Canonical repository governance. |

**Rules:**

- `architecture/` contains **only** canonical architecture documentation.
- `architecture/` **never** contains implementation details.
- `architecture/` **never** contains subsystem specifications (those belong in `docs/subsystems/`).
- `architecture/` **never** contains standards, guides, reports, or ADRs.
- Every file in `architecture/` is considered frozen once approved. Changes require an ADR.

### 3.2 `docs/` — Supporting Documentation

**Purpose:** Contains all supporting documentation that derives from or supports the canonical architecture.

**Ownership:** Documentation Team / All Contributors

**Subdirectories:**

| Directory | Purpose |
|-----------|---------|
| `docs/subsystems/` | Subsystem specifications — detailed design documents for each subsystem |
| `docs/standards/` | Coding standards, data contracts, quality gates, and other standards |
| `docs/guides/` | How-to guides, tutorials, and operational guides |
| `docs/reports/` | Reports, audits, sync reports, and analysis documents |
| `docs/adr/` | Architecture Decision Records |

**Rules:**

- `docs/` contains **supporting documentation only**.
- `docs/` **never** contains canonical architecture (that belongs in `architecture/`).
- `docs/` **never** contains implementation code.
- Subsystem specifications must reference `architecture/ARCHITECTURE.md` and must not redefine architectural boundaries.

### 3.3 `apps/` — Deployable Applications

**Purpose:** Contains deployable, executable applications that are products of the platform or tools for interacting with it.

**Ownership:** Application Team

**Contents:**

| Directory | Purpose |
|-----------|---------|
| `apps/api/` | Public API gateway — the external API surface of the platform |
| `apps/web/` | Web interface — the user-facing dashboard and management UI |

**Rules:**

- Each application is a self-contained deployable unit.
- Applications may depend on `packages/` but must not depend on other `apps/`.
- Applications must have their own `README.md` describing purpose, setup, and usage.
- Future applications follow the same convention: `apps/<name>/`.

### 3.4 `packages/` — Reusable Platform Modules

**Purpose:** Contains reusable, versioned platform modules that provide shared capabilities across applications and services.

**Ownership:** Platform Engineering Team

**Contents:**

| Directory | Purpose |
|-----------|---------|
| `packages/events/` | Event types, event bus interfaces, and event publishing utilities |
| `packages/execution/` | Execution runtime, task dispatch, and execution lifecycle management |
| `packages/memory/` | State management, persistence interfaces, and memory abstractions |
| `packages/models/` | Data models, schemas, enums, and type definitions |
| `packages/persistence/` | Repository implementations, unit of work, and data access layer |
| `packages/prompts/` | Prompt templates, prompt management, and prompt versioning |
| `packages/runtime/` | Runtime state manager, state transitions, and snapshot management |
| `packages/shared/` | Common types, utilities, constants, and shared infrastructure |
| `packages/tools/` | Shared tool definitions, tool integrations, and tool registries |
| `packages/workflows/` | Workflow engine, workflow definitions, and orchestration logic |

**Rules:**

- Each package is independently versioned and reusable.
- Packages may depend on other `packages/` but must not depend on `apps/` or `services/`.
- Packages must follow the [Package Structure](#52-package-structure) defined in this document.
- New packages must be proposed and reviewed before creation.

### 3.5 `services/` — Executable Services

**Purpose:** Contains executable services that implement platform capabilities. Services are deployable units that may be composed into larger systems.

**Ownership:** Service Engineering Team

**Contents:**

| Directory | Purpose |
|-----------|---------|
| `services/architecture/` | Architecture design service |
| `services/backend/` | Backend code generation service |
| `services/deployment/` | Deployment and infrastructure service |
| `services/documentation/` | Documentation generation service |
| `services/frontend/` | Frontend code generation service |
| `services/planner/` | Task decomposition and planning service |
| `services/requirements/` | Requirements analysis and specification service |
| `services/research/` | Context gathering and research service |
| `services/testing/` | Test generation and execution service |
| `services/ui/` | UI/UX generation service |

**Rules:**

- Each service is independently deployable.
- Services may depend on `packages/` but must not depend on other `services/`.
- Services must have their own `README.md` describing purpose, API, and usage.
- Services are expected to evolve as the platform matures.

### 3.6 `tests/` — Cross-Package and Integration Testing

**Purpose:** Contains tests that span multiple packages or test integration between components.

**Ownership:** Quality Engineering Team

**Contents:**

| Directory | Purpose |
|-----------|---------|
| `tests/models/` | Integration tests for model layer across packages |

**Rules:**

- Unit tests live within their respective `packages/<name>/tests/` directories.
- `tests/` contains only cross-package, integration, and end-to-end tests.
- Tests must be organized by the component or layer they test.

### 3.7 `scripts/` — Automation and Utility Scripts

**Purpose:** Contains build scripts, utility scripts, automation tools, and development helpers.

**Ownership:** DevOps / Platform Engineering Team

**Rules:**

- Scripts must be documented with a comment header describing purpose and usage.
- Scripts should be idempotent where possible.
- Large or complex scripts should be implemented as packages rather than standalone scripts.

### 3.8 `examples/` — Sample Projects and Usage Examples

**Purpose:** Contains sample projects, demonstration code, and usage examples that show how to use the platform.

**Ownership:** Developer Experience Team

**Rules:**

- Each example must have its own `README.md` describing what it demonstrates and how to run it.
- Examples should be kept minimal and focused on demonstrating specific capabilities.
- Examples are not production code and should not be used as dependencies.

### 3.9 `docker/` — Containerization Assets

**Purpose:** Contains Dockerfiles, Docker Compose overrides, and container configuration.

**Ownership:** DevOps Team

**Rules:**

- The root `docker-compose.yml` is for local development infrastructure.
- Service-specific Dockerfiles live within their respective service directories.
- `docker/` contains shared or base container configurations.

### 3.10 `.github/` — GitHub Configuration

**Purpose:** Contains GitHub-specific configuration including issue templates, pull request templates, and CI/CD workflow definitions.

**Ownership:** DevOps Team

**Contents:**

| Directory | Purpose |
|-----------|---------|
| `.github/ISSUE_TEMPLATE/` | Issue templates for bug reports, feature requests, etc. |
| `.github/workflows/` | GitHub Actions CI/CD workflow definitions |

**Rules:**

- CI/CD workflows must be defined in `.github/workflows/`.
- Issue and PR templates must be defined in `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`.
- GitHub-specific configuration only — no application or service code.

---

## 4. Documentation Rules

### 4.1 Document Type Classification

Every document in the repository belongs to exactly one of the following categories:

| Category | Location | Examples |
|----------|----------|----------|
| **Architecture** | `architecture/` | `ARCHITECTURE.md`, `VISION.md`, `PRINCIPLES.md` |
| **Vision** | `architecture/` | `VISION.md` |
| **Principles** | `architecture/` | `PRINCIPLES.md` |
| **Roadmap** | `architecture/` | (future) `ROADMAP.md` |
| **Manifest** | `architecture/` | `MANIFEST.md` |
| **Glossary** | `architecture/` | `GLOSSARY.md` |
| **Repository Governance** | `architecture/` | `REPOSITORY_STRUCTURE.md` |
| **Subsystem Specifications** | `docs/subsystems/` | `EXECUTION_ENGINE.md`, `EVENT_BUS.md` |
| **Standards** | `docs/standards/` | `CODING_STANDARDS.md`, `DATA_CONTRACTS.md` |
| **Guides** | `docs/guides/` | How-to guides, tutorials, operational guides |
| **Reports** | `docs/reports/` | `ARCHITECTURE_SYNC_REPORT.md` |
| **Architecture Decision Records** | `docs/adr/` | `ADR.md` |
| **Project Documentation** | `docs/` | `PROJECT_DASHBOARD.md`, `TECH_DEBT.md` |

### 4.2 Document Placement Rules

1. **Architecture documents** → `architecture/`
   - Includes: Architecture, Vision, Principles, Roadmap, Manifest, Glossary, Repository Structure
   - These are canonical. They define the platform. They are frozen once approved.

2. **Subsystem specifications** → `docs/subsystems/`
   - Detailed design documents for individual subsystems
   - Must reference `architecture/ARCHITECTURE.md` as the canonical source
   - Must not redefine architectural boundaries or responsibilities

3. **Standards** → `docs/standards/`
   - Coding standards, data contracts, quality gates, style guides
   - Enforceable rules that govern implementation

4. **Guides** → `docs/guides/`
   - How-to guides, tutorials, operational runbooks
   - Instructional content that helps contributors use the platform

5. **Reports** → `docs/reports/`
   - Analysis documents, audit reports, sync reports
   - Time-bound documents that capture findings and recommendations

6. **Architecture Decision Records** → `docs/adr/`
   - Records of architectural decisions, including context, options, and rationale
   - Immutable once written (new ADRs supersede old ones)

7. **Project documentation** → `docs/`
   - Project-level documents that don't fit the above categories
   - Examples: `PROJECT_DASHBOARD.md`, `TECH_DEBT.md`

### 4.3 Cardinal Rule

**No document exists in multiple locations.**

If a document's content is needed in multiple contexts, use Markdown links to reference the canonical location. Never copy content between documents.

---

## 5. Package Rules

### 5.1 Package Naming

- Python packages use `snake_case` naming: `autoforge_events`, `autoforge_models`
- Directory names use `kebab-case`: `packages/event-bus/`, `packages/model-router/`
- Package source code lives under `src/<package_name>/`

### 5.2 Package Structure

Every package must follow this consistent structure:

```
packages/<name>/
├── README.md              # Package description, API, and usage
├── pyproject.toml         # Python package configuration (or package.json for TS)
├── src/                   # Source code
│   └── <package_name>/    # Python package directory
│       ├── __init__.py    # Package exports
│       └── ...            # Module files
└── tests/                 # Unit tests
    ├── __init__.py
    └── ...                # Test files
```

### 5.3 Package Requirements

- **README.md** is required. It must describe the package's purpose, API, and usage.
- **pyproject.toml** (or equivalent) is required. It defines the package metadata, dependencies, and build configuration.
- **src/** layout is required. Source code must be in a `src/` directory to separate it from project configuration.
- **tests/** is required. Unit tests must be co-located with the package.
- Additional files (e.g., `CHANGELOG.md`, `LICENSE`, `Makefile`) are permitted only where justified.

### 5.4 Package Dependency Rules

- Packages may depend on other `packages/` in the monorepo.
- Packages must not depend on `apps/` or `services/`.
- Circular dependencies between packages are prohibited.
- Dependencies should be explicit and minimal.

---

## 6. Application Rules

### 6.1 Application Structure

Every application must follow this structure:

```
apps/<name>/
├── README.md              # Application description, setup, and usage
├── package.json           # Application configuration and dependencies
├── src/                   # Source code
├── tests/                 # Application tests
└── ...                    # Additional files only where justified
```

### 6.2 Application Requirements

- **README.md** is required. It must describe the application's purpose, how to set it up, and how to use it.
- Applications are **executable products**. They must be runnable.
- Applications may depend on `packages/` but must not depend on other `apps/`.
- Applications should be independently deployable.

### 6.3 Current Applications

| Application | Purpose |
|-------------|---------|
| `apps/api/` | Public API gateway — external API surface of the platform |
| `apps/web/` | Web interface — user-facing dashboard and management UI |

### 6.4 Future Applications

Future applications follow the same convention: `apps/<name>/`. Examples of potential future applications:

- `apps/cli/` — Command-line interface for the platform
- `apps/worker/` — Standalone worker process
- `apps/admin/` — Administrative interface

---

## 7. Naming Conventions

### 7.1 Directory Naming

| Context | Convention | Example |
|---------|------------|---------|
| Top-level directories | Lowercase, no separator | `architecture/`, `docs/`, `packages/` |
| Package directories | `kebab-case` | `packages/event-bus/`, `packages/model-router/` |
| Application directories | `kebab-case` | `apps/api/`, `apps/web/` |
| Service directories | `kebab-case` | `services/backend/`, `services/frontend/` |
| Documentation subdirectories | Lowercase, no separator | `docs/subsystems/`, `docs/standards/` |

### 7.2 File Naming

| Context | Convention | Example |
|---------|------------|---------|
| Markdown documents | `UPPER_SNAKE_CASE.md` | `ARCHITECTURE.md`, `CODING_STANDARDS.md` |
| Python modules | `snake_case.py` | `event_types.py`, `task_repository.py` |
| Python packages | `snake_case` | `autoforge_events`, `autoforge_models` |
| TypeScript/JavaScript | `camelCase.ts` | `eventBus.ts`, `stateManager.ts` |
| Configuration files | As required by tool | `pyproject.toml`, `package.json` |
| Test files | `test_<name>.py` | `test_events.py`, `test_state_manager.py` |

### 7.3 Naming Rules

- **No inconsistent capitalization.** All directory names are lowercase. Markdown files use `UPPER_SNAKE_CASE`.
- **No abbreviations** unless the abbreviation is more widely recognized than the full name (e.g., `ADR`, `API`, `CI/CD`).
- **Python packages** use `snake_case` and should be prefixed with `autoforge_` to avoid naming conflicts.
- **Test files** are prefixed with `test_` for Python or end with `.test.ts` for TypeScript.
- **README files** are always `README.md` (uppercase).

---

## 8. Architectural Governance

### 8.1 Architecture.md is the Single Source of Truth

`architecture/ARCHITECTURE.md` is the canonical architectural specification for AutoForge AI OS. It defines:

- Subsystem boundaries and responsibilities
- Architectural principles
- Dependency rules
- Communication patterns
- Lifecycle definitions

### 8.2 Subsystem Specifications Must Never Redefine Architecture

Subsystem specifications in `docs/subsystems/`:

- Must reference `architecture/ARCHITECTURE.md` as the canonical source.
- May provide additional detail within the boundaries established by the architecture.
- Must remain consistent with the architectural principles, relationships, and responsibilities defined in `architecture/ARCHITECTURE.md`.
- Must not redefine, contradict, or extend architectural boundaries.

### 8.3 Architecture Change Process

If implementation reveals an architectural issue:

1. **Create an ADR** — Document the issue, context, options, and proposed resolution in `docs/adr/`.
2. **Review the architecture** — The ADR is reviewed by the Architecture Team.
3. **Modify Architecture.md only if necessary** — If the ADR is approved and requires architectural changes, update `architecture/ARCHITECTURE.md` accordingly.
4. **Update subsystem specifications** — Ensure all affected subsystem specifications are updated to remain consistent.

### 8.4 Prohibited Practices

- **No ad-hoc architectural changes.** All architectural changes must go through the ADR process.
- **No architecture in implementation.** Implementation code must not define or redefine architectural boundaries.
- **No duplicate architecture.** No document other than `architecture/ARCHITECTURE.md` may define the platform architecture.
- **No bypassing governance.** Changes that affect subsystem boundaries, introduce new dependencies, or modify architectural principles require an ADR.

---

## 9. Documentation Lifecycle

Every subsystem specification follows this lifecycle:

```
Specification
     ↓
    Review
     ↓
    Freeze
     ↓
Implementation
     ↓
  Validation
     ↓
Production Ready
```

### 9.1 Specification

- The subsystem is documented in `docs/subsystems/<NAME>.md`.
- The specification must reference `architecture/ARCHITECTURE.md` and remain consistent with it.
- The specification defines the subsystem's purpose, responsibilities, interfaces, and behavior.

### 9.2 Review

- The specification is reviewed by the Architecture Team and relevant stakeholders.
- Feedback is incorporated and the specification is revised as needed.
- The review confirms that the specification is consistent with the canonical architecture.

### 9.3 Freeze

- The specification is frozen. No further changes are permitted without an ADR.
- The frozen specification becomes the authoritative reference for implementation.

### 9.4 Implementation

- The subsystem is implemented according to the frozen specification.
- Implementation must conform to the specification. Deviations are considered technical debt.

### 9.5 Validation

- The implementation is validated against the specification.
- Validation confirms that the implementation meets the specified requirements and remains consistent with the architecture.

### 9.6 Production Ready

- The subsystem is declared production ready.
- The specification and implementation are considered stable.
- Future changes follow the same lifecycle from Specification.

---

## 10. Repository Lifecycle

Every completed subsystem follows this lifecycle:

```
Specification
     ↓
Implementation
     ↓
   Testing
     ↓
Documentation
     ↓
  Git Commit
     ↓
Next Subsystem
```

### 10.1 Specification

- The subsystem specification is written and reviewed (see [Documentation Lifecycle](#9-documentation-lifecycle)).

### 10.2 Implementation

- The subsystem is implemented in the appropriate location:
  - Platform module → `packages/<name>/`
  - Application → `apps/<name>/`
  - Service → `services/<name>/`

### 10.3 Testing

- Unit tests are added to the package's `tests/` directory.
- Integration tests are added to `tests/` if the subsystem spans multiple packages.
- All tests must pass before the subsystem is considered complete.

### 10.4 Documentation

- The subsystem specification is finalized in `docs/subsystems/`.
- README files are updated as needed.
- The documentation index in `README.md` is updated.

### 10.5 Git Commit

- All changes are committed with a descriptive commit message.
- The commit message should reference the subsystem being completed.

### 10.6 Next Subsystem

- Work begins on the next subsystem, following the same lifecycle.

---

## 11. Future Expansion Guidelines

### 11.1 Adding a New Package

1. Create `packages/<name>/` following the [Package Structure](#52-package-structure).
2. Add a `README.md` describing the package's purpose and API.
3. Add the package to the monorepo workspace configuration.
4. Ensure no circular dependencies are introduced.

### 11.2 Adding a New Application

1. Create `apps/<name>/` following the [Application Structure](#61-application-structure).
2. Add a `README.md` describing the application's purpose and usage.
3. Ensure the application is independently deployable.

### 11.3 Adding a New Service

1. Create `services/<name>/` with a `README.md`.
2. Ensure the service depends only on `packages/`, not on other services.

### 11.4 Adding New Documentation

1. Determine the document type using the [Document Type Classification](#41-document-type-classification) table.
2. Place the document in the appropriate directory.
3. Update the documentation index in `README.md` if the document is of general interest.

### 11.5 Adding a New Top-Level Directory

New top-level directories should be rare and must be justified. Proposals for new top-level directories must:

1. Demonstrate that the content does not fit in any existing directory.
2. Demonstrate that the content is significant enough to warrant a new top-level entry.
3. Be reviewed and approved by the Architecture Team.
4. Be documented in this file.

### 11.6 Scaling Guidelines

- **Packages** can scale to hundreds. Each package is self-contained and independently versioned.
- **Applications** remain few. Each application is a product, not a library.
- **Services** can scale as the platform grows. Each service is independently deployable.
- **Documentation** scales through the subdirectory structure. New categories can be added under `docs/` as needed.
- **Tests** scale by mirroring the structure they test. Integration tests in `tests/` mirror the package structure.

---

## 12. Repository Governance Summary

### 12.1 Repository Philosophy

- **Single source of truth:** `architecture/ARCHITECTURE.md` is the canonical architecture.
- **Separation by purpose:** Every file has a clearly defined location based on its purpose.
- **No duplication:** No document exists in multiple locations.
- **Scalability by convention:** Convention replaces configuration. The structure scales without reorganization.

### 12.2 Directory Responsibilities

| Directory | Contains | Never Contains |
|-----------|----------|----------------|
| `architecture/` | Canonical architecture documentation | Implementation details, subsystem specs |
| `docs/` | Supporting documentation | Canonical architecture, implementation code |
| `apps/` | Deployable applications | Reusable libraries |
| `packages/` | Reusable platform modules | Deployable applications |
| `services/` | Executable services | Reusable libraries |
| `tests/` | Cross-package and integration tests | Unit tests (belong in packages) |
| `scripts/` | Automation and utility scripts | Application code |
| `examples/` | Sample projects and usage examples | Production code |
| `docker/` | Containerization assets | Application code |
| `.github/` | GitHub configuration | Application or service code |

### 12.3 Documentation Rules

- Architecture, Vision, Principles, Roadmap, Manifest, Glossary → `architecture/`
- Subsystem specifications → `docs/subsystems/`
- Standards → `docs/standards/`
- Guides → `docs/guides/`
- Reports → `docs/reports/`
- Architecture Decision Records → `docs/adr/`
- No document exists in multiple locations.

### 12.4 Package Rules

- Every package has: `README.md`, `pyproject.toml`, `src/`, `tests/`.
- Packages use `src/` layout.
- Packages may depend on other packages but not on apps or services.
- Circular dependencies are prohibited.

### 12.5 Governance Rules

- `architecture/ARCHITECTURE.md` is the single source of truth.
- Subsystem specifications must not redefine architecture.
- Architectural changes require an ADR.
- Implementation must conform to the architecture.
- Deviations are technical debt and must be documented.

### 12.6 Future Expansion Guidelines

- New packages → `packages/<name>/`
- New applications → `apps/<name>/`
- New services → `services/<name>/`
- New documentation → appropriate `docs/` subdirectory
- New top-level directories require Architecture Team approval

---

*This document is canonical. It defines the permanent organizational standard for the AutoForge AI OS repository. Every future contributor, AI agent, and developer must follow the rules defined herein.*