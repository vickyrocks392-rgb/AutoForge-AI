# Services

> **⚠️ TRANSITIONAL PLACEHOLDER**
>
> This directory reflects the previous SDLC-based service architecture (Planner, Research, Requirements, Architecture, UI, Backend, Frontend, Testing, Deployment, Documentation).
>
> Architecture v1.0 (`architecture/ARCHITECTURE.md`) replaces this model with Kernel, Platform Engines, Shared Platform Services, and Workers.
>
> These service directories are retained as transitional placeholders. Future implementation will replace them with the Architecture v1.0 structure.

## Purpose

This directory contains the AI agent services that implement each phase of the Software Development Life Cycle (SDLC). Each service is an independent, self-contained module with a single responsibility.

## Responsibility

- Implement SDLC phase logic as autonomous AI agents
- Communicate through well-defined, versioned contracts
- Produce artifacts consumed by downstream services
- Handle errors gracefully and report state to the workflow engine

## Current Contents

- `planner/` — Task decomposition and planning
- `research/` — Context gathering and research
- `requirements/` — Requirements analysis and specification
- `architecture/` — System design and architecture
- `ui/` — UI/UX generation
- `backend/` — Backend code generation
- `frontend/` — Frontend code generation
- `testing/` — Test generation and execution
- `deployment/` — Deployment and infrastructure
- `documentation/` — Documentation generation