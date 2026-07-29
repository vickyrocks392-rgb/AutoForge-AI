# AI Organization

> **Note:** This document uses terminology consistent with Architecture v1.0 (`architecture/ARCHITECTURE.md`). The canonical architecture describes Engineering Workers under the AI Workforce, where each worker is a specialised agent responsible for a specific engineering domain.

## Purpose

This document describes the organizational model for AI workers within the AutoForge AI platform. It defines how workers are structured, how they collaborate, and how they are managed as a virtual engineering workforce.

## Scope

This document covers the conceptual organization of AI workers, their roles, responsibilities, and communication patterns. It does not cover implementation details of individual worker services.

---

## Overview

AutoForge AI treats its AI workers as a virtual engineering organization. Each worker is an "AI employee" with a specific role, set of responsibilities, and expected outputs. The organization is structured to mirror a high-functioning software engineering team, with specialization, collaboration, and review built into the workflow.

## Worker Roles

| Role | Service | Responsibility |
|---|---|---|
| **Strategic Engine** | `services/planner` | Strategic reasoning, requirement analysis, research, architecture design, implementation planning |
| **Research Engineer** | `services/research` | Technical research, documentation research, framework research, best practice research, technology comparisons |
| **Software Architect** | `services/architecture` | Designs system architecture, defines component boundaries, selects architectural patterns |
| **Product Planner** | `services/requirements` | Defines product requirements, user stories, acceptance criteria, and prioritisation |
| **Backend Engineer** | `services/backend` | Generates server-side code and APIs |
| **Frontend Engineer** | `services/frontend` | Generates client-side code and interfaces |
| **Database Engineer** | `services/database` | Designs and implements data storage schemas, queries, and data migration strategies |
| **DevOps Engineer** | `services/deployment` | Manages infrastructure, deployment pipelines, and operational tooling |
| **Security Engineer** | `services/security` | Implements security controls, vulnerability assessments, and compliance measures |
| **QA Engineer** | `services/testing` | Generates and executes test suites, verifies quality |
| **Performance Engineer** | `services/performance` | Implements performance benchmarks, identifies bottlenecks, optimises system behaviour |
| **Documentation Engineer** | `services/documentation` | Produces technical documentation, API references, and user guides |

## Organizational Structure

- **Flat hierarchy** — All workers are peers. No worker manages another worker.
- **Orchestrated collaboration** — The Kernel, Workflow Engine, and Execution Engine coordinate worker interactions.
- **Contract-based communication** — Workers communicate through structured inputs and outputs, not free-form messages.
- **Human management** — Humans act as the product owner and engineering manager, defining goals and reviewing outputs.

## Collaboration Model

1. A human defines a goal or task.
2. The Kernel determines whether the Strategic Engine is required for strategic reasoning.
3. The Workflow Engine transforms plans into executable workflows.
4. The Execution Engine dispatches tasks to workers and manages the engineering loops.
5. Each worker receives structured input, performs its work, and produces structured output.
6. Downstream workers consume the outputs of upstream workers.
7. The Review Engine evaluates artifacts against quality criteria.
8. The human reviews the final output and provides feedback.

## Future Topics

- Worker specialization and sub-roles
- Multi-worker collaboration patterns (debate, review, ensemble)
- Worker performance evaluation and feedback loops
- Worker memory and learning from past projects
- Scaling the organization with additional worker roles
- Human-worker interaction patterns and approval workflows