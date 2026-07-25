# Coding Standards

## Purpose

This document defines the coding standards, conventions, and best practices for all code written within the AutoForge AI project. Adherence to these standards ensures consistency, maintainability, and readability across the entire codebase.

---

## General Principles

- **Readability over cleverness** — Code is written for humans first, machines second.
- **Consistency** — Follow existing patterns in the codebase.
- **Simplicity** — Prefer simple, obvious solutions over complex abstractions.
- **Testability** — Every piece of code should be testable in isolation.
- **Documentation** — Code should be self-documenting; comments explain why, not what.

---

## Language Standards

### TypeScript / JavaScript
- Use TypeScript for all new code. Strict mode is required.
- Use ES2022+ syntax. Target Node.js LTS.
- Prefer `const` over `let`. Never use `var`.
- Use arrow functions over `function` declarations where appropriate.
- Use async/await over raw promises. Avoid callbacks.
- Use named exports over default exports.

### Naming Conventions
- **Classes, interfaces, types, enums** — PascalCase
- **Functions, variables, parameters, properties** — camelCase
- **Constants (truly immutable)** — UPPER_SNAKE_CASE
- **Files** — kebab-case for files, PascalCase for class/component files
- **Directories** — kebab-case

### File Organization
- One logical concept per file.
- Maximum 300 lines per file. Split into modules if larger.
- Related files are grouped in directories by feature or domain.

---

## Project Structure Standards

- Each package and service follows a consistent internal structure:
  ```
  src/
    index.ts          # Public API exports
    types/            # Type definitions
    schemas/          # Validation schemas
    services/         # Business logic
    utils/            # Utilities
    __tests__/        # Unit tests
  ```
- Index files re-export public API only. Internal modules are not exposed.

---

## Documentation Standards

- All public APIs must have JSDoc or TSDoc comments.
- README files exist in every package and service directory.
- Architecture decisions are documented in ADRs (Architecture Decision Records).
- Inline comments explain non-obvious logic, edge cases, and workarounds.

---

## Testing Standards

- **Unit tests** — Required for all business logic. Minimum 80% coverage.
- **Integration tests** — Required for all service boundaries and contracts.
- **E2E tests** — Required for critical user workflows.
- Test files are co-located with source files in `__tests__/` directories.
- Use descriptive test names following the pattern: `should [expected behavior] when [condition]`.

---

## Error Handling

- Use typed errors. Extend a base `AppError` class.
- Never swallow errors silently. Log context and rethrow or handle explicitly.
- Use early returns and guard clauses to avoid deep nesting.
- Validate inputs at service boundaries.

---

## Version Control

- **Branch naming** — `feature/description`, `fix/description`, `chore/description`
- **Commit messages** — Conventional Commits format: `type(scope): description`
- **Pull requests** — Include description, testing notes, and links to related issues.

---

## Code Review

- All code must be reviewed before merging.
- Reviews focus on correctness, design, test coverage, and adherence to standards.
- Automated checks (lint, type check, tests) must pass before review.

---

## Tooling

- **Linter** — ESLint with strict configuration
- **Formatter** — Prettier with consistent settings
- **Type Checker** — TypeScript strict mode
- **Test Runner** — Vitest or Jest
- **Pre-commit Hooks** — Husky with lint-staged