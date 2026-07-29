# Technical Debt

## Purpose

This document records intentional technical debt, known limitations, future refactoring opportunities, deprecated APIs, engineering improvements, and architectural cleanup items across the AutoForge AI platform.

It serves as a living record for the engineering team to track, prioritise, and eventually resolve items that are not bugs but represent quality, maintainability, or correctness improvements.

## What Belongs Here

- Deprecated API usage that still works but should be migrated
- Known design limitations or trade-offs accepted for delivery
- Code that violates current coding standards or conventions
- Missing test coverage for edge cases
- Configuration or packaging improvements
- Architectural inconsistencies between components
- Future-proofing changes (e.g., compatibility with upcoming dependency versions)

## What Does NOT Belong Here

- Bug reports — use the issue tracker
- Feature requests — use the roadmap or feature request template
- Roadmap items — documented in the Long-Term Roadmap section of `README.md`
- Architecture decisions — documented in `docs/adr/ADR.md`
- Day-to-day tasks — use the project board

---

## Priority Levels

| Priority | Definition |
|----------|------------|
| **Critical** | Blocks development, causes incorrect behaviour, or creates security risk |
| **High** | Significant quality, performance, or maintainability impact |
| **Medium** | Notable improvement with moderate effort |
| **Low** | Nice-to-have cleanup, cosmetic, or future-proofing |

## Status

| Status | Definition |
|--------|------------|
| **Open** | Identified but not yet scheduled |
| **Planned** | Scheduled for a specific phase or milestone |
| **In Progress** | Actively being addressed |
| **Resolved** | Fixed, verified, and closed |

---

## Entry Template

```
### TECH-{NNN}: {Title}

| Field | Value |
|-------|-------|
| **Priority** | Critical / High / Medium / Low |
| **Status** | Open / Planned / In Progress / Resolved |
| **Area** | Affected component or subsystem |
| **Reason** | Why this debt exists |
| **Current Impact** | What happens if this is not addressed |
| **Recommended Solution** | How to resolve it |
| **Target Phase** | When this should be addressed |
| **Owner** | (optional) |
| **Created** | YYYY-MM-DD |
| **Resolved** | (optional) YYYY-MM-DD |
```

---

## Debt Register

### TECH-001: Migrate deprecated Pydantic `json_encoders` to serializer decorators

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Status** | Open |
| **Area** | Core Models (`packages/models/src/autoforge_models/base.py`) |
| **Reason** | The project uses Pydantic's deprecated `json_encoders` configuration in `AutoForgeBaseModel.model_config`. This API is scheduled for removal in Pydantic v3. |
| **Current Impact** | No runtime impact. All 80 tests pass. Only deprecation warnings appear in test output (107 warnings, all from `json_encoders`). |
| **Recommended Solution** | Replace `json_encoders` in `ConfigDict` with Pydantic v2's modern `@field_serializer` and `@model_serializer` decorators on the relevant fields (`id` as UUID, `created_at`/`updated_at` as datetime). |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-002: Remove `json_encoders` deprecation warnings from test output

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Status** | Open |
| **Area** | Test Suite (`tests/models/`) |
| **Reason** | The 107 deprecation warnings in test output (all `PydanticDeprecatedSince20: json_encoders is deprecated`) clutter test results and can mask real warnings. |
| **Current Impact** | Test output is noisy. Real deprecation or future warnings could be missed among the 107 expected warnings. |
| **Recommended Solution** | Resolve TECH-001 first, then verify warnings are eliminated. Optionally add a `filterwarnings` config in `pyproject.toml` as an interim measure. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-003: Add `__version__` attribute to `autoforge_models` package

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Status** | Open |
| **Area** | Package Configuration (`packages/models/src/autoforge_models/__init__.py`) |
| **Reason** | The package does not expose a `__version__` attribute. Standard Python convention is to read the version from `pyproject.toml` and expose it at the package level. |
| **Current Impact** | Consumers cannot programmatically determine the installed package version via `autoforge_models.__version__`. |
| **Recommended Solution** | Use `importlib.metadata` to read the version from the installed package metadata, or use a tool like `importlib_metadata` for broader compatibility. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-004: Standardise pytest configuration at repository root

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Status** | Open |
| **Area** | Build & Test Configuration |
| **Reason** | The `pytest.ini` files in `packages/models/` and `tests/models/` were removed during packaging fixes. The project currently relies on editable installation for test discovery. A root-level `pyproject.toml` `[tool.pytest.ini_options]` section would provide a single source of truth. |
| **Current Impact** | Tests run correctly via editable install but lack centralised pytest configuration (e.g., `testpaths`, `filterwarnings`, `markers`). |
| **Recommended Solution** | Add a `[tool.pytest.ini_options]` section to the root `pyproject.toml` with `testpaths = ["tests/models"]` and any shared configuration. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-005: Remove `from __future__ import annotations` from model files

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Status** | Open |
| **Area** | Core Models (all `packages/models/src/autoforge_models/*.py` files) |
| **Reason** | The project targets Python 3.12+. The `from __future__ import annotations` import was added during initial development but is unnecessary since PEP 563 behaviour (postponed evaluation of annotations) is the default starting from Python 3.14, and the project already uses `|` syntax for unions which is supported natively in 3.12+. |
| **Current Impact** | No functional impact. The import is harmless but adds noise. |
| **Recommended Solution** | Remove `from __future__ import annotations` from all model files. Verify no type-checking or runtime issues arise. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-006: Align KnowledgeNode tests with graph architecture

| Field | Value |
|-------|-------|
| **Priority** | Low |
| **Status** | Resolved |
| **Area** | Knowledge Graph |
| **Reason** | A unit test incorrectly expected `KnowledgeNode` to contain a `weight` field. The architecture defines relationship weights on `KnowledgeEdge`, not `KnowledgeNode`. |
| **Current Impact** | None. |
| **Recommended Solution** | No model changes required. The unit test was updated to match the architecture. |
| **Target Phase** | Completed |
| **Created** | 2026-07-25 |
| **Resolved** | 2026-07-25 |

---

### TECH-007: Rename `Employee.model_config` to `Employee.model` to avoid Pydantic reserved attribute conflict

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Status** | Resolved |
| **Area** | Employee Model (`packages/models/src/autoforge_models/employee.py`) |
| **Reason** | The `Employee` model had a field named `model_config` which conflicts with Pydantic's reserved `model_config` class attribute. This caused a `TypeError: 'FieldInfo' object is not iterable` on Python 3.14 + Pydantic 2.13.4. |
| **Current Impact** | Resolved. The field was renamed to `model` and all references updated. |
| **Recommended Solution** | N/A — resolved. Any future model should avoid using `model_config`, `model_fields`, or other Pydantic reserved names as field names. |
| **Target Phase** | N/A |
| **Created** | 2026-07-25 |
| **Resolved** | 2026-07-25 |

---

### TECH-008: Remove `ClassVar` annotation from `model_config` in `AutoForgeBaseModel`

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Status** | Resolved |
| **Area** | Base Models (`packages/models/src/autoforge_models/base.py`) |
| **Reason** | The `model_config` was annotated with `ClassVar[ConfigDict]` which caused Pydantic's metaclass to misinterpret it as a `FieldInfo` on Python 3.14. The `ClassVar` annotation is unnecessary — Pydantic v2 recognises `model_config` as a special attribute regardless of annotation. |
| **Current Impact** | Resolved. The `ClassVar` annotation and import were removed. |
| **Recommended Solution** | N/A — resolved. Follow Pydantic v2 convention: `model_config = ConfigDict(...)` without `ClassVar`. |
| **Target Phase** | N/A |
| **Created** | 2026-07-25 |
| **Resolved** | 2026-07-25 |

---

### TECH-009: Establish Python packaging convention for all future packages

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Status** | Open |
| **Area** | Repository-wide packaging |
| **Reason** | The `packages/models/` package was the first Python package in the repository. Its packaging setup (`pyproject.toml`, `src` layout, editable install) should serve as the template for all future Python packages. However, no convention document exists yet. |
| **Current Impact** | Future Python packages may diverge in structure, leading to inconsistent build, test, and deployment workflows. |
| **Recommended Solution** | Document the Python package convention in `docs/standards/CODING_STANDARDS.md` or a new `docs/PYTHON_PACKAGING.md`. Include: `src` layout, `pyproject.toml` structure, editable install workflow, test configuration, and naming conventions. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |

---

### TECH-010: Audit all models for Pydantic reserved attribute name conflicts

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Status** | Open |
| **Area** | Core Models (all `packages/models/src/autoforge_models/*.py`) |
| **Reason** | The `Employee.model_config` conflict (TECH-007) revealed that Pydantic has several reserved attribute names. Other models may have similar conflicts that are latent (not triggered by current Python/Pydantic versions but may break in the future). |
| **Current Impact** | No current impact. All models pass tests. But latent conflicts could surface with Python or Pydantic upgrades. |
| **Recommended Solution** | Audit all model field names against Pydantic's reserved names: `model_config`, `model_fields`, `model_computed_fields`, `model_extra`, `model_post_init`, `model_validate`, `model_dump`, etc. Rename any conflicting fields. |
| **Target Phase** | Platform Stabilisation |
| **Created** | 2026-07-25 |