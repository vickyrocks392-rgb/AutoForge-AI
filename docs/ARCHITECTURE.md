# Architecture

## Purpose

This document describes the architectural principles, patterns, and decisions that guide the design and evolution of the AutoForge AI platform.

---

## Architectural Principles

### 1. Service-Oriented Architecture
Each SDLC phase is owned by an independent service with a single responsibility. Services communicate through defined interfaces and are independently deployable.

### 2. Contract-First Design
All inter-service communication is governed by versioned contracts. Contracts define inputs, outputs, error states, and behavioral guarantees.

### 3. Stateless Services, Stateful Workflows
Services are stateless to enable horizontal scaling. Workflow state is managed externally by the workflow engine and persisted in the memory layer.

### 4. Event-Driven Orchestration
Services communicate asynchronously through events. The workflow engine coordinates execution order, handles failures, and manages retries.

### 5. Layered Isolation
- **Apps** — Presentation and API layer
- **Services** — Business logic and agent execution
- **Packages** — Shared infrastructure and domain models

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Apps                             │
│  ┌──────────────┐          ┌──────────────────────┐     │
│  │   API        │          │   Web                │     │
│  └──────┬───────┘          └──────────┬───────────┘     │
└─────────┼─────────────────────────────┼─────────────────┘
          │                             │
          └──────────┬──────────────────┘
                     │
          ┌──────────▼──────────┐
          │  Workflow Engine    │
          │  (packages/workflows)│
          └──────────┬──────────┘
                     │
     ┌───────────────┼───────────────────┐
     │               │                   │
┌────▼────┐   ┌─────▼─────┐   ┌─────────▼─────────┐
│ Planner │   │ Research  │   │ Requirements      │
└────┬────┘   └─────┬─────┘   └─────────┬─────────┘
     │               │                   │
┌────▼────┐   ┌─────▼─────┐   ┌─────────▼─────────┐
│Architect│   │    UI     │   │ Backend           │
└────┬────┘   └─────┬─────┘   └─────────┬─────────┘
     │               │                   │
┌────▼────┐   ┌─────▼─────┐   ┌─────────▼─────────┐
│Frontend │   │  Testing  │   │ Deployment        │
└────┬────┘   └─────┬─────┘   └─────────┬─────────┘
     │               │                   │
     └───────────────┼───────────────────┘
                     │
          ┌──────────▼──────────┐
          │ Documentation       │
          └─────────────────────┘
```

---

## Service Contract Model

Each service exposes:
- **Input Schema** — The data structure required to invoke the service
- **Output Schema** — The data structure produced by the service
- **Error Schema** — The data structure for error states
- **Lifecycle Hooks** — Pre-execution, post-execution, and error recovery callbacks

---

## Workflow Engine

The workflow engine in `packages/workflows` provides:
- **Directed Acyclic Graph (DAG) Execution** — Define workflows as a series of steps with dependencies
- **State Persistence** — Workflow state is persisted for recovery and audit
- **Error Handling** — Configurable retry policies, fallback paths, and dead-letter queues
- **Observability** — Every workflow step emits events for monitoring and debugging

---

## Data Layer

### Memory & State
- **Short-term memory** — In-memory cache for active workflow state
- **Long-term memory** — Persistent storage for completed workflows, artifacts, and context
- **Vector memory** — Semantic search over past decisions and artifacts

### Storage
- **Relational** — Structured data, service state, user data
- **Document** — Unstructured artifacts, generated code, specifications
- **Vector** — Embeddings for semantic retrieval

---

## Security Architecture

- **Authentication** — API keys, OAuth2, or SSO at the app layer
- **Authorization** — Role-based access control (RBAC) for service invocation
- **Audit** — All service invocations and workflow steps are logged
- **Secrets Management** — External secrets manager for API keys and credentials

---

## Deployment Architecture

- **Development** — Local Docker Compose with hot-reload
- **Staging** — Kubernetes namespace with production-like configuration
- **Production** — Kubernetes cluster with auto-scaling, monitoring, and HA