# AutoForge AI OS — Glossary

> **Canonical terminology for all architecture documents.**
> This document defines the authoritative vocabulary. It is not an implementation document and not a user guide.

---

## Artifact

A named, versioned output produced or consumed during execution. Artifacts are immutable once written and are identified by a content-addressable digest. They form the data dependencies between tasks in a task graph.

## Canonical Event Model

A schema-enforced, versioned structure that every event in the system must conform to. It defines mandatory fields (id, type, source, timestamp, payload, metadata) and ensures that all producers and consumers agree on the shape of event data. The model is the contract between event producers and the event bus.

## Connector

A pluggable adapter that bridges the platform to an external system. Connectors translate between the platform's internal protocols and external APIs, databases, or services. They are registered at startup and invoked by the engine when a task requires interaction with an external resource.

## Dashboard

A read-only projection of platform state, metrics, and observability data intended for human operators. Dashboards aggregate signals from the observability subsystem and present them as visual summaries. They have no write path into the platform's operational state.

## Engine

A major platform subsystem responsible for a specific domain of behaviour.

An engine owns a well-defined set of responsibilities, exposes explicit interfaces, and collaborates with other engines through documented contracts.

Examples include the Execution Engine, Research Engine, Learning Engine, and Review Engine.

## Event

A discrete, immutable record of something that has happened within the platform. Each event carries a type, a source, a timestamp, and a payload conforming to the canonical event model. Events are the sole mechanism for communicating state changes across subsystems.

## Event Bus

An internal publish-subscribe channel that routes events from producers to consumers. The event bus decouples subsystems by allowing them to communicate without direct references. It guarantees at-least-once delivery and preserves event ordering within a partition.

## Execution

A runtime instance of a task graph.

Each execution has its own state, context, memory, artifacts, event history, and lifecycle.

## Execution Loop

The iterative cycle in which the engine selects a ready task, dispatches it to a worker, collects the result, and advances the task graph. The execution loop continues until no ready tasks remain or a terminal condition is reached. It is the inner mechanism of the engine's runtime behavior.

## Knowledge

Structured, queryable information that persists across executions and projects. Knowledge is derived from artifacts, reviews, and external sources, and is stored in a form that supports retrieval and reasoning. It is distinct from memory in that it is explicitly curated and versioned.

## Memory

A contextual store that captures the state and history of a specific execution or session. Memory is ephemeral by default and is used by workers and the engine to maintain continuity within a single execution. It may be promoted to knowledge through an explicit curation process.

## Model Router

A dispatch layer that selects which language model or inference endpoint handles a given task. The model router evaluates task requirements, model capabilities, cost, and latency to make a routing decision. It abstracts the underlying model infrastructure from the rest of the platform.

## Observability

The subsystem responsible for collecting, processing, and exposing telemetry data (logs, metrics, traces) from all platform components. Observability enables operators to understand system behaviour, diagnose failures, and measure performance. It is a read-only concern with no influence on execution logic.

## Platform

The complete software system encompassing all subsystems, services, and components that collectively provide the AutoForge AI OS capabilities. The platform includes the engine, runtime, services, persistence layer, event infrastructure, and all supporting machinery. It is the bounded context within which all architectural definitions apply.

## Project

A top-level organisational unit that groups related task graphs, executions, artifacts, and configuration. Projects provide isolation boundaries for resources and define the scope within which policies, permissions, and retention rules apply. Every execution belongs to exactly one project.

## Repository

A storage abstraction that provides CRUD operations for a specific entity type (e.g., task repository, artifact repository). Repositories encapsulate the underlying persistence technology and expose a consistent interface to the rest of the platform. They are the building blocks of the persistence plane.

## Research

A specialised workflow type whose purpose is information gathering and synthesis. Research workflows produce knowledge artifacts rather than executable outputs. They are typically invoked when a task requires external context that does not yet exist within the platform.

## Review

A structured evaluation of an artifact or execution outcome against a set of quality criteria. Reviews are performed by designated workers or automated gates and produce a pass/fail decision with supporting evidence. They are the mechanism by which quality policies are enforced.

## Runtime

The operational environment responsible for managing executions, workers, resources, state, and lifecycle coordination.

The runtime provides the execution infrastructure upon which platform engines operate while enforcing isolation, recovery, scheduling, and execution policies.

## Service

A long-lived software component that provides a focused capability to one or more engines.

Services encapsulate implementation details behind stable interfaces and may be local or distributed. Unlike engines, services do not own platform-level orchestration.

## State

A snapshot of all relevant properties of an entity (task, execution, project) at a point in time. State is managed by the state manager and is persisted to enable recovery, audit, and query. It is the single source of truth for the current condition of any tracked entity.

## Subsystem

A major architectural component of the platform with clearly defined responsibilities, interfaces, and boundaries.

Subsystems may consist of one or more engines, services, repositories, and supporting components.

## Task

The smallest unit of work schedulable by the engine. A task has a type, input artifacts, output artifacts, and a state machine that governs its lifecycle. Tasks are the nodes in a task graph and are executed by workers.

## Task Graph

A directed acyclic graph (DAG) whose nodes are tasks and whose edges represent data or control dependencies. The task graph defines the order of execution and the flow of artifacts between tasks. It is the primary structure submitted to the engine for execution.

## Worker

An execution unit responsible for performing a single task.

Workers receive execution context, perform the assigned work, produce artifacts, and report results back to the runtime.

The underlying implementation may be a local process, container, remote service, or another execution environment.

## Workforce

The collection of workers currently available to execute tasks.

The workforce represents the execution capacity of the platform and may consist of heterogeneous worker types operating across multiple execution environments.

## Workflow

A declarative description of a business or automation process.

A workflow defines the desired outcome, while the platform transforms it into one or more executable task graphs.