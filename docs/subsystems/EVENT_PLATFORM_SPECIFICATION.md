# Event Platform Specification v1.0

> **Status:** Frozen — Phase 4.1 Deliverable
> **Canonical Reference:** This document is the authoritative specification for the Event Platform subsystem. All implementation must conform to this specification.
> **Architecture Alignment:** This specification is consistent with `architecture/ARCHITECTURE.md` v1.0, `docs/subsystems/kernel/KERNEL_SPECIFICATION.md` v1.0, `docs/subsystems/RUNTIME_STATE_MANAGER_SPECIFICATION.md` v1.0, and all subsystem architecture documents.

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Responsibilities](#2-responsibilities)
3. [Non-Responsibilities](#3-non-responsibilities)
4. [Design Philosophy](#4-design-philosophy)
5. [Architectural Principles](#5-architectural-principles)
6. [Public Interfaces](#6-public-interfaces)
7. [Internal Components](#7-internal-components)
8. [Event Model](#8-event-model)
9. [Event Categories](#9-event-categories)
10. [Event Schema Model](#10-event-schema-model)
11. [Event Lifecycle](#11-event-lifecycle)
12. [Event Routing](#12-event-routing)
13. [Event Publication](#13-event-publication)
14. [Event Subscription](#14-event-subscription)
15. [Event Delivery Guarantees](#15-event-delivery-guarantees)
16. [Event Ordering](#16-event-ordering)
17. [Event Replay](#17-event-replay)
18. [Event Persistence](#18-event-persistence)
19. [Event History](#19-event-history)
20. [Event Correlation](#20-event-correlation)
21. [Event Filtering](#21-event-filtering)
22. [Event Validation](#22-event-validation)
23. [Dead Letter Queue](#23-dead-letter-queue)
24. [Failure Handling](#24-failure-handling)
25. [Kernel Interactions](#25-kernel-interactions)
26. [Runtime Interactions](#26-runtime-interactions)
27. [Platform Engine Interactions](#27-platform-engine-interactions)
28. [Shared Platform Service Interactions](#28-shared-platform-service-interactions)
29. [Sequence Diagrams](#29-sequence-diagrams)
30. [State Diagrams](#30-state-diagrams)
31. [Public API Reference](#31-public-api-reference)
32. [Internal Component Reference](#32-internal-component-reference)
33. [Extension Points](#33-extension-points)
34. [ADR Requirements](#34-adr-requirements)
35. [Glossary](#35-glossary)

---

## 1. Purpose

The Event Platform is the canonical communication backbone of AutoForge AI OS. It is the single, authoritative system for event transport, delivery, and management across the entire platform.

Every subsystem communicates through the Event Platform. The Event Platform owns event transport and delivery. It does NOT own orchestration, runtime state, or engineering work.

### What the Event Platform Is

- The **canonical communication backbone** for all platform subsystems
- The **owner** of event transport, delivery, and routing
- The **authority** for event schemas, validation, and contracts
- The **provider** of event persistence, history, and replay capabilities
- The **guarantor** of event delivery semantics and ordering
- The **coordinator** of event-driven communication patterns

### What the Event Platform Is Not

- The Event Platform is **NOT** an orchestration engine
- The Event Platform is **NOT** a state storage system
- The Event Platform is **NOT** a workflow execution engine
- The Event Platform is **NOT** a message queue (though it may use one)
- The Event Platform is **NOT** a logging system
- The Event Platform **NEVER** interprets event business meaning
- The Event Platform **NEVER** makes orchestration decisions
- The Event Platform **NEVER** performs engineering work

---

## 2. Responsibilities

The Event Platform owns the following responsibilities:

### 2.1 Event Bus

- **Own event bus** — Maintain the canonical event bus for the platform
- **Manage event transport** — Transport events between producers and consumers
- **Ensure event delivery** — Guarantee event delivery according to configured semantics
- **Maintain event ordering** — Preserve event ordering where required
- **Route events** — Route events to appropriate subscribers
- **Scale event throughput** — Handle platform-scale event volume
- **Monitor event health** — Monitor event bus health and performance

### 2.2 Event Contracts

- **Define event schemas** — Define canonical schemas for all platform events
- **Validate event schemas** — Validate events against schemas
- **Version event schemas** — Manage event schema versions
- **Enforce schema contracts** — Ensure all events conform to schemas
- **Document event contracts** — Maintain event contract documentation
- **Evolve schemas** — Manage schema evolution and backward compatibility

### 2.3 Event Routing

- **Route events by topic** — Route events to topic-based subscribers
- **Route events by category** — Route events to category-based subscribers
- **Support broadcast** — Broadcast events to all interested subscribers
- **Support directed events** — Route events to specific subscribers
- **Route internal events** — Route events within the platform
- **Route external events** — Route events to external systems
- **Filter events** — Filter events based on subscriber requirements

### 2.4 Event Publication

- **Accept event publications** — Accept events from publishers
- **Validate published events** — Validate events before acceptance
- **Enrich events** — Add metadata to events (timestamps, IDs, etc.)
- **Persist events** — Persist events to durable storage
- **Route events** — Route events to subscribers
- **Confirm publication** — Confirm event publication to publishers
- **Handle publication failures** — Handle publication failures gracefully

### 2.5 Event Subscription

- **Manage subscriptions** — Manage event subscriptions
- **Validate subscriptions** — Validate subscription requests
- **Route events to subscribers** — Deliver events to subscribers
- **Manage subscription lifecycle** — Handle subscription creation, updates, and deletion
- **Support subscription filters** — Support filtered subscriptions
- **Handle subscriber failures** — Handle subscriber failures gracefully
- **Manage subscription state** — Track subscription state and health

### 2.6 Event Delivery

- **Deliver events** — Deliver events to subscribers
- **Guarantee delivery semantics** — Implement at-most-once, at-least-once, exactly-once delivery
- **Handle delivery failures** — Retry failed deliveries
- **Confirm delivery** — Confirm event delivery to publishers
- **Track delivery status** — Track event delivery status
- **Manage delivery timing** — Control event delivery timing
- **Prioritize deliveries** — Prioritize event deliveries based on priority

### 2.7 Event Ordering

- **Preserve event order** — Preserve event order where required
- **Define ordering guarantees** — Define ordering guarantees per event stream
- **Handle out-of-order events** — Handle out-of-order events gracefully
- **Sequence events** — Assign sequence numbers to events
- **Detect ordering violations** — Detect and handle ordering violations
- **Support ordered replay** — Support ordered event replay

### 2.8 Event Replay

- **Support event replay** — Enable event replay from event history
- **Replay from checkpoint** — Replay events from specific checkpoints
- **Replay with filters** — Replay events with filters
- **Replay at different speeds** — Support accelerated and decelerated replay
- **Pause and resume replay** — Support replay control
- **Track replay progress** — Track replay progress and status
- **Isolate replay** — Isolate replay from live event flow

### 2.9 Event Persistence

- **Persist events** — Persist events to durable storage
- **Ensure event durability** — Ensure events are not lost
- **Manage event retention** — Manage event retention policies
- **Archive events** — Archive old events according to policy
- **Delete events** — Delete events according to retention policy
- **Optimize storage** — Optimize event storage for performance and cost
- **Backup events** — Backup event data for disaster recovery

### 2.10 Event History

- **Maintain event history** — Maintain complete history of all events
- **Query event history** — Provide APIs to query event history
- **Filter event history** — Filter event history by criteria
- **Aggregate event history** — Aggregate event history for analytics
- **Correlate event history** — Correlate related events in history
- **Visualize event history** — Support event history visualization
- **Export event history** — Export event history for analysis

### 2.11 Event Correlation

- **Correlate related events** — Correlate events using correlation IDs
- **Trace event chains** — Trace event causation chains
- **Group related events** — Group events by aggregate, project, or workflow
- **Detect event patterns** — Detect patterns in event streams
- **Support distributed tracing** — Support distributed tracing across subsystems
- **Maintain correlation context** — Maintain correlation context across event chains

### 2.12 Event Filtering

- **Filter events by type** — Filter events by event type
- **Filter events by category** — Filter events by event category
- **Filter events by source** — Filter events by source subsystem
- **Filter events by project** — Filter events by project ID
- **Filter events by time** — Filter events by time range
- **Filter events by content** — Filter events by payload content
- **Support complex filters** — Support complex filter expressions

### 2.13 Dead Letter Queue

- **Manage dead letter queue** — Manage events that cannot be delivered
- **Store failed events** — Store events that failed delivery
- **Enable dead letter replay** — Enable replay of dead letter events
- **Alert on dead letters** — Alert when events enter dead letter queue
- **Analyze dead letters** — Analyze patterns in dead letter events
- **Retry dead letters** — Retry dead letter events automatically or manually
- **Clean up dead letters** — Clean up dead letter events according to policy

### 2.14 Event Versioning

- **Version event schemas** — Version event schemas for evolution
- **Support schema evolution** — Support backward and forward compatibility
- **Transform event versions** — Transform events between schema versions
- **Deprecate old schemas** — Deprecate old event schemas gracefully
- **Document schema versions** — Document all event schema versions
- **Validate version compatibility** — Validate version compatibility
- **Migrate event history** — Migrate historical events to new schemas

### 2.15 Event Schema Validation

- **Validate event schemas** — Validate events against schemas
- **Enforce schema contracts** — Enforce schema contracts at publication and subscription
- **Report validation errors** — Report schema validation errors clearly
- **Support schema evolution** — Support schema evolution without breaking consumers
- **Validate event structure** — Validate event structure and data types
- **Validate event semantics** — Validate event semantic correctness
- **Provide validation feedback** — Provide clear feedback for validation failures

---

## 3. Non-Responsibilities

The Event Platform explicitly does NOT own the following:

### 3.1 Orchestration

- **Orchestration** — The Event Platform does not orchestrate execution
- **Planning** — The Event Platform does not plan work
- **Scheduling** — The Event Platform does not schedule tasks
- **Worker dispatch** — The Event Platform does not dispatch workers
- **Model selection** — The Event Platform does not select AI models
- **Retry logic** — The Event Platform does not implement business retry policies
- **Recovery logic** — The Event Platform does not implement recovery strategies

### 3.2 State Ownership

- **Project state** — The Event Platform publishes state change events but does not own project state
- **Runtime state** — The Event Platform publishes state change events but does not own runtime state
- **Workflow state** — The Event Platform publishes state change events but does not own workflow state
- **Task state** — The Event Platform publishes state change events but does not own task state
- **Memory** — The Event Platform publishes memory events but does not own memory
- **Knowledge** — The Event Platform publishes knowledge events but does not own knowledge

### 3.3 Execution

- **Engineering work** — The Event Platform does not perform engineering tasks
- **Code generation** — The Event Platform does not generate code
- **Research** — The Event Platform does not perform research
- **Review** — The Event Platform does not review artifacts
- **Testing** — The Event Platform does not execute tests
- **Deployment** — The Event Platform does not deploy applications

### 3.4 Business Logic

- **Event interpretation** — The Event Platform transports events but does not interpret business meaning
- **Event aggregation** — The Event Platform does not aggregate events for business logic
- **Event transformation** — The Event Platform does not transform events for business purposes
- **Event enrichment** — The Event Platform adds metadata but does not enrich events with business data
- **Event routing logic** — The Event Platform routes events but does not make business routing decisions

### 3.5 Infrastructure

- **Message queue implementation** — The Event Platform may use a message queue but does not implement one
- **Database implementation** — The Event Platform may use a database but does not implement one
- **Storage implementation** — The Event Platform may use storage but does not implement storage systems
- **Network implementation** — The Event Platform may use networks but does not implement network protocols

### 3.6 What the Event Platform Delegates

| Capability | Owner | Event Platform's Role |
|---|---|---|
| Orchestration | Kernel | Transport orchestration events |
| State management | Runtime State Manager | Transport state change events |
| Execution | Execution Engine | Transport execution events |
| Planning | Workflow Engine | Transport planning events |
| Memory operations | Memory Engine | Transport memory events |
| Knowledge retrieval | Knowledge Engine | Transport knowledge events |
| Model execution | Model Router | Transport model events |
| Recovery | Execution Continuity Manager | Transport recovery events |
| External access | Connector Layer | Transport connector events |
| Quality evaluation | Review Engine | Transport review events |
| Artifact management | Artifact Manager | Transport artifact events |
| Learning | Learning Engine | Transport learning events |

---

## 4. Design Philosophy

The Event Platform is designed around the following philosophical principles:

### 4.1 Events Are Immutable Facts

Events represent things that happened. They are immutable records of facts. Once an event is published, it can never be changed or deleted. This immutability enables auditability, replay, and reliable event-driven systems.

### 4.2 Events Are the Primary Communication Mechanism

All inter-subsystem communication flows through events. There are no backdoors, no direct invocations, no bypass mechanisms. This ensures that all communication is observable, debuggable, and recoverable.

### 4.3 Publishers and Subscribers Are Decoupled

Publishers know nothing about subscribers. Subscribers know nothing about publishers. The Event Platform mediates all communication. This enables independent evolution of subsystems and platform-wide extensibility.

### 4.4 Events Are First-Class Citizens

Events are not an afterthought. They are designed, documented, versioned, and managed with the same rigor as any other platform artifact. Every event has a schema, a contract, and a lifecycle.

### 4.5 Delivery Guarantees Are Explicit

The Event Platform makes explicit delivery guarantees and enforces them rigorously. Publishers and subscribers know exactly what guarantees they receive. There are no surprises, no hidden semantics, no ambiguous contracts.

### 4.6 Events Are Durable

Events are persisted durably. They are never lost. This enables replay, audit, recovery, and analysis. Event durability is non-negotiable.

### 4.7 Events Are Ordered Where Required

The Event Platform preserves event order where business logic requires it. Ordering is explicit, documented, and enforced. Where order doesn't matter, events can be delivered in parallel for performance.

### 4.8 Events Are Observable

Every event is observable. Every publication, delivery, and failure is logged and traceable. There are no black boxes. Event flows are visible, debuggable, and analyzable.

### 4.9 Events Are Schema-Validated

Every event is validated against its schema before publication and before delivery. Invalid events are rejected immediately. This prevents garbage-in, garbage-out scenarios and ensures data quality.

### 4.10 Events Are Local-First, Cloud-Capable

The Event Platform works locally for single-node deployments and scales to cloud deployments. The same event model, the same APIs, the same guarantees apply in both contexts. Deployment topology is transparent to event producers and consumers.

---

## 5. Architectural Principles

The Event Platform adheres to the following architectural principles:

### 5.1 Single Responsibility

The Event Platform has one responsibility: transport events. It does not attempt to do anything else. All event-related concerns are concentrated in the Event Platform.

### 5.2 Single Source of Truth

The Event Platform is the single source of truth for event transport. There is no alternative event bus, no shadow event channel, no backdoor communication. All events flow through the Event Platform.

### 5.3 Interface First

The Event Platform defines explicit interfaces for all event operations. Publishers and subscribers depend on interfaces, not implementations. This enables the Event Platform to evolve internally without affecting producers and consumers.

### 5.4 No Circular Dependencies

The Event Platform may depend on infrastructure services (persistence, monitoring), but no business component depends on the internal implementation of the Event Platform. The dependency graph is strictly hierarchical.

### 5.5 Event-Driven Communication

The Event Platform IS event-driven communication. It enables event-driven architectures but is not itself event-driven. It is the transport layer that makes event-driven architectures possible.

### 5.6 Immutability

All events are immutable. Once published, an event can never be modified or deleted. This immutability enables auditability, replay, and reliable event processing.

### 5.7 Loose Coupling

The Event Platform depends on contracts, not implementations. It knows what persistence providers can do, not how they do it. This enables infrastructure providers to evolve independently.

### 5.8 High Cohesion

All event transport logic resides in the Event Platform. There is no event transport logic scattered across other components. This makes the event model explicit, inspectable, and maintainable.

### 5.9 Idempotency

All Event Platform operations are idempotent. If an operation is invoked multiple times (due to retry or event replay), the result is the same as if it were invoked once. This enables safe retry and event replay.

### 5.10 Observability

Every Event Platform operation is observable. Every publication, delivery, failure, and retry is logged and traceable. There are no black boxes.

### 5.11 Schema-First Design

Every event type has a schema. Schemas are defined first, validated rigorously, versioned carefully, and documented completely. Event schemas are contracts that enable safe evolution.

### 5.12 Provider Agnostic

The Event Platform is provider agnostic. It can use different message queues, different persistence layers, different monitoring systems. Implementation providers are pluggable and replaceable.

### 5.13 Local-First

The Event Platform works locally without external dependencies. A single-node deployment uses local storage and in-memory transport. Cloud deployments add distributed capabilities transparently.

---

## 6. Public Interfaces

The Event Platform exposes the following public interfaces:

### 6.1 Event Publication Interface

**Purpose:** Publish events to the event bus.

**Input:**
- `event` — The event to publish (validated against schema)
- `deliveryMode` — Delivery guarantee (at-most-once, at-least-once, exactly-once)
- `priority` — Event priority (low, normal, high, critical)
- `metadata` — Optional publication metadata

**Output:**
- `eventId` — Unique identifier for the published event
- `status` — Publication status (accepted, rejected, failed)
- `timestamp` — When the event was published

**Behavior:**
1. Validate event against schema
2. Enrich event with metadata (event ID, timestamp, etc.)
3. Assign event to priority queue
4. Persist event to durable storage
5. Route event to matching subscribers
6. Confirm publication to publisher
7. Return event ID and status

**Error Handling:**
- Invalid schema: Reject event, return validation error
- Persistence failure: Queue event for retry, return accepted with warning
- Routing failure: Queue event for retry, return accepted with warning

### 6.2 Event Subscription Interface

**Purpose:** Subscribe to events from the event bus.

**Input:**
- `subscriptionRequest` — Subscription specification
  - `eventTypes` — List of event types to subscribe to
  - `eventCategories` — List of event categories to subscribe to
  - `filter` — Optional filter expression
  - `deliveryMode` — Required delivery guarantee
  - `callback` — Subscriber callback endpoint or handler
  - `orderingGuarantee` — Required ordering guarantee (if any)

**Output:**
- `subscriptionId` — Unique subscription identifier
- `status` — Subscription status (active, pending, failed)
- `timestamp` — When the subscription was created

**Behavior:**
1. Validate subscription request
2. Create subscription record
3. Register subscription with router
4. Begin delivering matching events
5. Return subscription ID and status

**Error Handling:**
- Invalid filter: Reject subscription, return validation error
- Invalid event types: Reject subscription, return validation error
- Callback unavailable: Queue subscription, retry callback registration

### 6.3 Event Query Interface

**Purpose:** Query historical events.

**Input:**
- `query` — Query specification
  - `eventTypes` — Filter by event types
  - `eventCategories` — Filter by event categories
  - `projectId` — Filter by project ID
  - `correlationId` — Filter by correlation ID
  - `timeRange` — Filter by time range
  - `source` — Filter by source
  - `limit` — Maximum results to return
  - `offset` — Pagination offset
  - `orderBy` — Sort order

**Output:**
- `events` — List of matching events
- `totalCount` — Total number of matching events
- `hasMore` — Whether more results are available

**Behavior:**
1. Parse and validate query
2. Execute query against event history
3. Apply filters and sorting
4. Paginate results
5. Return events and metadata

**Error Handling:**
- Invalid query: Return validation error
- Query timeout: Return partial results with timeout warning
- Storage unavailable: Return error, suggest retry

### 6.4 Event Replay Interface

**Purpose:** Replay events from history.

**Input:**
- `replayRequest` — Replay specification
  - `source` — Replay source (from timestamp, from event ID, from checkpoint)
  - `eventTypes` — Filter by event types
  - `eventCategories` — Filter by event categories
  - `projectId` — Filter by project ID
  - `speed` — Replay speed (1x, 2x, 4x, etc.)
  - `subscriber` — Subscriber to receive replayed events
  - `stopOnError` — Whether to stop on error

**Output:**
- `replayId` — Unique replay identifier
- `status` — Replay status (running, paused, completed, failed)
- `progress` — Replay progress (events replayed / total events)

**Behavior:**
1. Validate replay request
2. Create replay session
3. Query events from history
4. Deliver events to subscriber at specified speed
5. Track replay progress
6. Handle errors according to policy
7. Return replay ID and status

**Error Handling:**
- Invalid source: Return validation error
- No events found: Return error, suggest alternative source
- Subscriber unavailable: Pause replay, retry subscriber registration

### 6.5 Dead Letter Queue Interface

**Purpose:** Manage dead letter events.

**Input:**
- `operation` — Operation to perform
  - `list` — List dead letter events
  - `retry` — Retry dead letter event
  - `replay` — Replay all dead letter events
  - `delete` — Delete dead letter event
  - `analyze` — Analyze dead letter patterns

**Output:**
- Varies by operation

**Behavior:**
1. Validate operation
2. Execute operation on dead letter queue
3. Return results

**Error Handling:**
- Invalid operation: Return validation error
- Dead letter queue unavailable: Return error, suggest retry

### 6.6 Event Subscription Management Interface

**Purpose:** Manage event subscriptions.

**Input:**
- `operation` — Operation to perform
  - `create` — Create subscription
  - `get` — Get subscription details
  - `update` — Update subscription
  - `delete` — Delete subscription
  - `list` — List subscriptions

**Output:**
- Varies by operation

**Behavior:**
1. Validate operation
2. Execute operation on subscription
3. Return results

**Error Handling:**
- Invalid operation: Return validation error
- Subscription not found: Return error
- Subscription in use: Return error, suggest graceful shutdown

---

## 7. Internal Components

The Event Platform consists of the following internal components:

### Architecture Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    Event Platform                            │
│           (Canonical Communication Backbone)                 │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Bus                                 │
│              (Event Transport Layer)                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Event      │  │   Event      │  │   Event      │      │
│  │   Router     │  │  Dispatcher  │  │  Validator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Priority    │  │   Ordering   │  │   Filter     │      │
│  │   Queue       │  │   Manager    │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                Event Schema Registry                         │
│           (Event Contracts and Validation)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Schema      │  │   Schema      │  │   Schema      │      │
│  │   Registry    │  │   Validator   │  │   Transformer │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Persistence                         │
│              (Durable Event Storage)                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Event      │  │   Event      │  │   Event      │      │
│  │   Writer     │  │   Reader     │  │   Archiver   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Event Replay Engine                         │
│              (Event History and Replay)                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Replay      │  │   History     │  │   Correlation │      │
│  │   Controller  │  │   Query       │  │   Engine      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Dead Letter Queue                           │
│              (Failed Event Management)                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   DLQ        │  │   DLQ        │  │   DLQ        │      │
│  │   Writer     │  │   Reader     │  │   Analyzer   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 7.1 Event Bus

**Responsibility:** Transport events between publishers and subscribers.

**Sub-components:**

**Event Router**
- Routes events to appropriate subscribers
- Matches events to subscriptions
- Handles topic-based and category-based routing
- Supports broadcast and directed routing
- Manages routing tables

**Event Dispatcher**
- Dispatches events to subscribers
- Manages delivery timing
- Handles delivery failures
- Implements retry logic
- Tracks delivery status

**Event Validator**
- Validates events against schemas
- Rejects invalid events
- Reports validation errors
- Enforces schema contracts

**Priority Queue**
- Manages event priority queues
- Prioritizes event delivery
- Handles priority escalation
- Manages queue capacity

**Ordering Manager**
- Preserves event order where required
- Assigns sequence numbers
- Detects ordering violations
- Handles out-of-order events

**Filter Engine**
- Filters events based on subscription filters
- Evaluates filter expressions
- Optimizes filter performance
- Returns filtered events

**Interactions:**
- Receives events from publishers
- Validates events
- Routes events to subscribers
- Handles delivery failures
- Publishes delivery status events

### 7.2 Event Schema Registry

**Responsibility:** Manage event schemas and validation.

**Sub-components:**

**Schema Registry**
- Stores event schemas
- Manages schema versions
- Tracks schema dependencies
- Provides schema lookup
- Manages schema lifecycle

**Schema Validator**
- Validates events against schemas
- Checks data types
- Validates required fields
- Validates field constraints
- Returns validation errors

**Schema Transformer**
- Transforms events between schema versions
- Handles schema evolution
- Applies backward compatibility rules
- Applies forward compatibility rules
- Migrates event data

**Interactions:**
- Receives schema registration requests
- Validates schemas
- Stores schemas
- Provides schema validation for events
- Transforms events between versions

### 7.3 Event Persistence

**Responsibility:** Persist events to durable storage.

**Sub-components:**

**Event Writer**
- Writes events to persistent storage
- Ensures durability
- Handles write failures
- Batches writes for performance
- Confirms write completion

**Event Reader**
- Reads events from persistent storage
- Supports queries
- Handles read failures
- Caches frequently accessed events
- Returns event data

**Event Archiver**
- Archives old events
- Moves events to cold storage
- Enforces retention policies
- Compresses archived events
- Manages archive lifecycle

**Interactions:**
- Receives events from Event Bus
- Writes events to storage
- Supports event queries
- Archives old events
- Deletes expired events

### 7.4 Event Replay Engine

**Responsibility:** Enable event replay from history.

**Sub-components:**

**Replay Controller**
- Controls replay sessions
- Manages replay state
- Handles replay control (pause, resume, stop)
- Tracks replay progress
- Handles replay errors

**History Query**
- Queries event history
- Supports complex queries
- Filters events for replay
- Orders events for replay
- Returns event streams

**Correlation Engine**
- Correlates related events
- Traces event chains
- Groups events by aggregate
- Detects event patterns
- Builds correlation graphs

**Interactions:**
- Receives replay requests
- Queries event history
- Delivers replayed events
- Tracks replay progress
- Handles replay errors

### 7.5 Dead Letter Queue

**Responsibility:** Manage events that cannot be delivered.

**Sub-components:**

**DLQ Writer**
- Writes failed events to DLQ
- Captures failure context
- Stores failure metadata
- Prioritizes DLQ events
- Alerts on DLQ growth

**DLQ Reader**
- Reads events from DLQ
- Supports DLQ queries
- Returns DLQ statistics
- Identifies failure patterns

**DLQ Analyzer**
- Analyzes DLQ events
- Identifies failure patterns
- Generates failure reports
- Suggests remediation
- Tracks DLQ metrics

**Interactions:**
- Receives failed events from Event Bus
- Writes events to DLQ
- Supports DLQ queries
- Analyzes DLQ patterns
- Enables DLQ replay

---

## 8. Event Model

The Event Platform defines the canonical event model for the entire platform.

### 8.1 Event Structure

Every event in the platform conforms to the following structure:

```
Event
├── eventId (UUID) — Unique event identifier
├── eventType (EventType) — Specific event type
├── eventCategory (EventCategory) — High-level event category
├── source (String) — Component that emitted the event
├── timestamp (DateTime) — When the event occurred
├── version (String) — Event schema version
├── correlationId (UUID) — Correlation ID for related events
├── causationId (UUID) — Causation ID for event chain
├── aggregateId (UUID) — Aggregate root identifier
├── aggregateType (String) — Aggregate root type
├── payload (Object) — Event-specific data
├── metadata (Object) — Extensible metadata
├── priority (Enum) — Event priority
└── deliveryMode (Enum) — Delivery guarantee
```

### 8.2 Event Fields

#### eventId

- **Type:** UUID
- **Description:** Unique identifier for the event
- **Generated by:** Event Platform (at publication time)
- **Immutable:** Yes
- **Purpose:** Uniquely identify the event for deduplication, replay, and reference

#### eventType

- **Type:** EventType (Enum)
- **Description:** Specific event type (e.g., `project.created`, `task.completed`)
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Identify the specific occurrence that the event represents

#### eventCategory

- **Type:** EventCategory (Enum)
- **Description:** High-level event category (e.g., `project`, `task`, `execution`)
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Group related event types for routing, filtering, and subscription

#### source

- **Type:** String (max 256 characters)
- **Description:** Identifier of the subsystem or component that emitted the event
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Identify the event source for routing, filtering, and audit

#### timestamp

- **Type:** DateTime (ISO 8601)
- **Description:** When the event occurred
- **Generated by:** Event Platform (at publication time)
- **Immutable:** Yes
- **Purpose:** Record when the event occurred for ordering, audit, and replay

#### version

- **Type:** String (semantic version)
- **Description:** Event schema version (e.g., `1.0.0`, `1.1.0`)
- **Generated by:** Event Schema Registry
- **Immutable:** Yes
- **Purpose:** Enable schema evolution and backward compatibility

#### correlationId

- **Type:** UUID
- **Description:** Correlation ID for grouping related events
- **Generated by:** Event publisher (or Event Platform if not provided)
- **Immutable:** Yes
- **Purpose:** Correlate events that are part of the same logical operation or workflow

#### causationId

- **Type:** UUID
- **Description:** Causation ID of the event that caused this event
- **Generated by:** Event Platform (at publication time)
- **Immutable:** Yes
- **Purpose:** Trace event causation chains for debugging and audit

#### aggregateId

- **Type:** UUID
- **Description:** Aggregate root identifier
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Group events by aggregate for event sourcing and consistency

#### aggregateType

- **Type:** String (max 64 characters)
- **Description:** Aggregate root type (e.g., `Project`, `Task`, `Workflow`)
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Identify the aggregate type for routing and filtering

#### payload

- **Type:** Object (JSON)
- **Description:** Event-specific data
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Carry event-specific information to subscribers

#### metadata

- **Type:** Object (JSON)
- **Description:** Extensible metadata key-value store
- **Generated by:** Event Platform (enriched) and Event publisher (custom)
- **Immutable:** Yes
- **Purpose:** Carry additional context, routing information, and platform metadata

**Standard Metadata Fields:**
- `publisherId` — Unique identifier of the publisher
- `publisherVersion` — Version of the publisher
- `schemaVersion` — Event schema version
- `contentType` — Payload content type (default: `application/json`)
- `contentEncoding` — Payload encoding (default: `utf-8`)
- `traceId` — Distributed trace ID
- `spanId` — Distributed span ID
- `tenantId` — Tenant identifier (for multi-tenancy)
- `environment` — Deployment environment (dev, staging, prod)

#### priority

- **Type:** Priority (Enum)
- **Values:** `low`, `normal`, `high`, `critical`
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Prioritize event delivery and processing

**Priority Levels:**
- **low** — Background events, analytics, metrics
- **normal** — Standard events (default)
- **high** — Important events requiring fast delivery
- **critical** — Critical events requiring immediate delivery

#### deliveryMode

- **Type:** DeliveryMode (Enum)
- **Values:** `at-most-once`, `at-least-once`, `exactly-once`
- **Generated by:** Event publisher
- **Immutable:** Yes
- **Purpose:** Specify delivery guarantee for the event

**Delivery Modes:**
- **at-most-once** — Event may be lost but never delivered more than once
- **at-least-once** — Event will be delivered at least once, may be delivered multiple times
- **exactly-once** — Event will be delivered exactly once (where applicable)

### 8.3 Event Immutability

Events are **immutable**. Once an event is published, it can never be modified or deleted.

**Immutable Fields:**
- `eventId` — Never changes
- `eventType` — Never changes
- `eventCategory` — Never changes
- `source` — Never changes
- `timestamp` — Never changes
- `version` — Never changes
- `correlationId` — Never changes
- `causationId` — Never changes
- `aggregateId` — Never changes
- `aggregateType` — Never changes
- `payload` — Never changes
- `metadata` — Never changes
- `priority` — Never changes
- `deliveryMode` — Never changes

**Corrections:**
If an event contains incorrect information, a new correction event must be published. The correction event references the original event via `causationId` and contains the corrected information.

**Deletions:**
Events are never deleted. They are archived according to retention policies but remain available for audit and replay.

### 8.4 Event Identifiers

**Event ID**
- Format: UUID v4
- Generated by: Event Platform
- Uniqueness: Globally unique
- Purpose: Uniquely identify the event

**Correlation ID**
- Format: UUID v4
- Generated by: Event publisher (or Event Platform)
- Uniqueness: Unique per logical operation
- Purpose: Group related events
- Scope: Typically spans multiple subsystems and event types

**Causation ID**
- Format: UUID v4
- Generated by: Event Platform
- Uniqueness: Equals the event ID of the causing event
- Purpose: Trace event causation chains
- Scope: Direct cause-and-effect relationship

**Aggregate ID**
- Format: UUID v4
- Generated by: Event publisher
- Uniqueness: Unique per aggregate
- Purpose: Group events by aggregate
- Scope: All events for a specific aggregate instance

---

## 9. Event Categories

The Event Platform defines the following canonical event categories:

### 9.1 Category Hierarchy

```
EventCategory
├── KERNEL
│   └── Kernel lifecycle and orchestration events
├── RUNTIME
│   └── Runtime state management events
├── WORKFLOW
│   └── Workflow execution events
├── EXECUTION
│   └── Execution session events
├── REVIEW
│   └── Review engine events
├── KNOWLEDGE
│   └── Knowledge engine events
├── MEMORY
│   └── Memory engine events
├── LEARNING
│   └── Learning engine events
├── INFRASTRUCTURE
│   └── Infrastructure service events
├── CONNECTOR
│   └── Connector layer events
├── SECURITY
│   └── Security events
├── OBSERVABILITY
│   └── Observability events
├── APPROVAL
│   └── Human approval events
├── ARTIFACT
│   └── Artifact management events
├── WORKER
│   └── Worker lifecycle events
├── TASK
│   └── Task lifecycle events
├── PROJECT
│   └── Project lifecycle events
├── CHECKPOINT
│   └── Checkpoint events
└── RECOVERY
    └── Recovery events
```

### 9.2 Category Definitions

#### KERNEL

**Description:** Events related to Kernel lifecycle and orchestration.

**Event Types:**
- `kernel.created` — Kernel instance created
- `kernel.starting` — Kernel is starting up
- `kernel.started` — Kernel has started
- `kernel.pausing` — Kernel is pausing
- `kernel.paused` — Kernel is paused
- `kernel.resuming` — Kernel is resuming
- `kernel.ready` — Kernel is ready to accept requests
- `kernel.stopping` — Kernel is stopping
- `kernel.stopped` — Kernel has stopped

**Subscribers:**
- Observability (monitor kernel health)
- Infrastructure (manage kernel lifecycle)
- Security (audit kernel operations)

#### RUNTIME

**Description:** Events related to runtime state management.

**Event Types:**
- `state.transitioned` — State transition occurred
- `state.created` — State entity created
- `state.updated` — State entity updated
- `state.deleted` — State entity deleted
- `state.restored` — State restored from checkpoint

**Subscribers:**
- Kernel (monitor state changes)
- Observability (track state metrics)
- Recovery (detect state inconsistencies)

#### WORKFLOW

**Description:** Events related to workflow execution.

**Event Types:**
- `workflow.created` — Workflow created
- `workflow.started` — Workflow execution started
- `workflow.completed` — Workflow execution completed
- `workflow.failed` — Workflow execution failed
- `workflow.paused` — Workflow execution paused
- `workflow.resumed` — Workflow execution resumed
- `workflow.cancelled` — Workflow execution cancelled

**Subscribers:**
- Kernel (orchestrate workflow execution)
- Observability (track workflow metrics)
- Recovery (handle workflow failures)

#### EXECUTION

**Description:** Events related to execution sessions.

**Event Types:**
- `execution.started` — Execution session started
- `execution.completed` — Execution session completed
- `execution.failed` — Execution session failed
- `execution.paused` — Execution session paused
- `execution.resumed` — Execution session resumed
- `execution.cancelled` — Execution session cancelled
- `execution.timed_out` — Execution session timed out

**Subscribers:**
- Kernel (orchestrate execution)
- Observability (track execution metrics)
- Recovery (handle execution failures)

#### REVIEW

**Description:** Events related to review engine.

**Event Types:**
- `review.started` — Review started
- `review.completed` — Review completed
- `review.approved` — Artifact approved
- `review.rejected` — Artifact rejected
- `review.changes_requested` — Changes requested
- `review.escalated` — Review escalated to human

**Subscribers:**
- Kernel (coordinate review flow)
- Approval (manage approval gates)
- Observability (track review metrics)

#### KNOWLEDGE

**Description:** Events related to knowledge engine.

**Event Types:**
- `knowledge.queried` — Knowledge queried
- `knowledge.researched` — Research completed
- `knowledge.promoted` — Learning promoted to knowledge
- `knowledge.updated` — Knowledge updated
- `knowledge.deleted` — Knowledge deleted

**Subscribers:**
- Kernel (request knowledge)
- Learning (promote learning)
- Observability (track knowledge usage)

#### MEMORY

**Description:** Events related to memory engine.

**Event Types:**
- `memory.stored` — Memory entry stored
- `memory.updated` — Memory entry updated
- `memory.deleted` — Memory entry deleted
- `memory.retrieved` — Memory entry retrieved
- `memory.context_loaded` — Project context loaded

**Subscribers:**
- Kernel (load project context)
- Execution (persist execution state)
- Observability (track memory usage)

#### LEARNING

**Description:** Events related to learning engine.

**Event Types:**
- `learning.analyzed` — Learning analysis completed
- `learning.validated` — Learning validated
- `learning.promoted` — Learning promoted to knowledge
- `learning.discarded` — Learning discarded

**Subscribers:**
- Kernel (trigger learning analysis)
- Knowledge (promote validated learning)
- Observability (track learning metrics)

#### INFRASTRUCTURE

**Description:** Events related to infrastructure services.

**Event Types:**
- `service.started` — Service started
- `service.stopped` — Service stopped
- `service.healthy` — Service is healthy
- `service.degraded` — Service is degraded
- `service.recovered` — Service recovered
- `service.failed` — Service failed

**Subscribers:**
- Kernel (monitor service health)
- Recovery (handle service failures)
- Observability (track service metrics)

#### CONNECTOR

**Description:** Events related to connector layer.

**Event Types:**
- `connector.connected` — Connector connected
- `connector.disconnected` — Connector disconnected
- `connector.executed` — Connector operation executed
- `connector.failed` — Connector operation failed
- `connector.retrying` — Connector operation retrying

**Subscribers:**
- Kernel (coordinate connector operations)
- Recovery (handle connector failures)
- Observability (track connector metrics)

#### SECURITY

**Description:** Events related to security.

**Event Types:**
- `security.authenticated` — Authentication successful
- `security.authorized` — Authorization successful
- `security.denied` — Access denied
- `security.policy_violated` — Security policy violated
- `security.audit` — Security audit event

**Subscribers:**
- Security (enforce security policies)
- Observability (track security events)
- Audit (record security audit trail)

#### OBSERVABILITY

**Description:** Events related to observability.

**Event Types:**
- `observability.metric` — Metric emitted
- `observability.log` — Log event
- `observability.trace` — Trace created
- `observability.span` — Span recorded
- `observability.alert` — Alert triggered

**Subscribers:**
- Observability (collect telemetry)
- Monitoring (trigger alerts)
- Analytics (analyze metrics)

#### APPROVAL

**Description:** Events related to human approval flow.

**Event Types:**
- `approval.required` — Human approval needed
- `approval.decided` — Human made decision
- `approval.timeout` — Approval timeout
- `approval.escalated` — Approval escalated
- `approval.cancelled` — Approval cancelled

**Subscribers:**
- Kernel (coordinate approval flow)
- Approval (manage approval gates)
- Observability (track approval metrics)

#### ARTIFACT

**Description:** Events related to artifact management.

**Event Types:**
- `artifact.created` — Artifact created
- `artifact.updated` — Artifact updated
- `artifact.deleted` — Artifact deleted
- `artifact.published` — Artifact published
- `artifact.archived` — Artifact archived

**Subscribers:**
- Kernel (track artifacts)
- Artifact Manager (manage artifacts)
- Observability (track artifact metrics)

#### WORKER

**Description:** Events related to worker lifecycle.

**Event Types:**
- `worker.registered` — Worker registered
- `worker.dispatched` — Worker dispatched to task
- `worker.started` — Worker started task
- `worker.completed` — Worker completed task
- `worker.failed` — Worker failed
- `worker.retired` — Worker retired

**Subscribers:**
- Kernel (coordinate worker dispatch)
- Execution (execute tasks)
- Observability (track worker metrics)

#### TASK

**Description:** Events related to task lifecycle.

**Event Types:**
- `task.created` — Task created
- `task.updated` — Task updated
- `task.queued` — Task queued
- `task.ready` — Task ready to execute
- `task.started` — Task started
- `task.paused` — Task paused
- `task.resumed` — Task resumed
- `task.completed` — Task completed
- `task.failed` — Task failed
- `task.cancelled` — Task cancelled
- `task.blocked` — Task blocked
- `task.deleted` — Task deleted
- `task.dispatched` — Task dispatched to worker
- `task.retrying` — Task retrying
- `task.waiting` — Task waiting for approval

**Subscribers:**
- Kernel (orchestrate task execution)
- Execution (execute tasks)
- Observability (track task metrics)

#### PROJECT

**Description:** Events related to project lifecycle.

**Event Types:**
- `project.created` — Project created
- `project.updated` — Project updated
- `project.started` — Project execution started
- `project.planning` — Planning phase began
- `project.running` — Execution began
- `project.reviewing` — Awaiting human review
- `project.paused` — Execution paused
- `project.resumed` — Execution resumed
- `project.completing` — Validating completion
- `project.finished` — Project completed
- `project.failed` — Project failed
- `project.cancelled` — Project cancelled
- `project.archived` — Project archived
- `project.deleted` — Project deleted

**Subscribers:**
- Kernel (orchestrate project lifecycle)
- Observability (track project metrics)
- Audit (record project history)

#### CHECKPOINT

**Description:** Events related to checkpoints.

**Event Types:**
- `checkpoint.created` — Checkpoint created
- `checkpoint.restored` — Checkpoint restored
- `checkpoint.deleted` — Checkpoint deleted
- `checkpoint.archived` — Checkpoint archived

**Subscribers:**
- Recovery (restore from checkpoints)
- Observability (track checkpoint metrics)
- Audit (record checkpoint history)

#### RECOVERY

**Description:** Events related to recovery operations.

**Event Types:**
- `failure.detected` — Failure detected
- `recovery.started` — Recovery started
- `recovery.completed` — Recovery completed
- `recovery.failed` — Recovery failed
- `recovery.aborted` — Recovery aborted

**Subscribers:**
- Kernel (coordinate recovery)
- Recovery (execute recovery)
- Observability (track recovery metrics)

---

## 10. Event Schema Model

The Event Platform defines schemas for all platform events.

### 10.1 Schema Structure

Every event schema defines:

```json
{
  "schemaId": "project.created.v1",
  "version": "1.0.0",
  "description": "A new project was created",
  "category": "project",
  "eventType": "project.created",
  "payloadSchema": {
    "type": "object",
    "properties": {
      "projectId": {
        "type": "string",
        "format": "uuid"
      },
      "request": {
        "type": "object"
      },
      "configuration": {
        "type": "object"
      }
    },
    "required": ["projectId"]
  },
  "metadataSchema": {
    "type": "object",
    "properties": {
      "publisherId": {
        "type": "string"
      },
      "publisherVersion": {
        "type": "string"
      }
    }
  },
  "compatibility": {
    "backward": "1.0.0",
    "forward": "1.0.0"
  }
}
```

### 10.2 Schema Fields

#### schemaId

- **Type:** String
- **Description:** Unique schema identifier
- **Format:** `{eventType}.v{version}` (e.g., `project.created.v1`)
- **Purpose:** Uniquely identify the schema

#### version

- **Type:** String (semantic version)
- **Description:** Schema version
- **Format:** `major.minor.patch` (e.g., `1.0.0`)
- **Purpose:** Enable schema evolution

#### description

- **Type:** String
- **Description:** Human-readable description of the event
- **Purpose:** Document the event

#### category

- **Type:** EventCategory (Enum)
- **Description:** Event category
- **Purpose:** Group related events

#### eventType

- **Type:** EventType (Enum)
- **Description:** Specific event type
- **Purpose:** Identify the event type

#### payloadSchema

- **Type:** JSON Schema
- **Description:** Schema for event payload
- **Purpose:** Validate event payload

#### metadataSchema

- **Type:** JSON Schema
- **Description:** Schema for event metadata
- **Purpose:** Validate event metadata

#### compatibility

- **Type:** Object
- **Description:** Schema compatibility rules
- **Fields:**
  - `backward` — Minimum backward-compatible version
  - `forward` — Minimum forward-compatible version
- **Purpose:** Enable safe schema evolution

### 10.3 Schema Evolution

The Event Platform supports schema evolution with backward and forward compatibility.

#### Backward Compatibility

A new schema version is backward compatible if consumers using the old schema can read events written with the new schema.

**Rules:**
- New fields must be optional
- Removed fields must have been optional
- Field types must not change
- Field constraints must not be tightened

#### Forward Compatibility

A new schema version is forward compatible if consumers using the new schema can read events written with the old schema.

**Rules:**
- Removed fields must have been optional
- New fields must have default values
- Field types must not change
- Field constraints must not be tightened

#### Schema Versioning

**Major Version:** Breaking changes
- Field type changes
- Required field additions
- Field removals
- Constraint tightening

**Minor Version:** Backward-compatible changes
- Optional field additions
- Field deprecation
- Documentation updates

**Patch Version:** Non-breaking fixes
- Schema validation fixes
- Documentation fixes
- Metadata updates

### 10.4 Schema Registry

The Event Schema Registry maintains all event schemas.

**Schema Registration:**
1. Publisher submits schema for new event type
2. Schema Registry validates schema
3. Schema Registry checks compatibility with existing schemas
4. Schema Registry assigns version
5. Schema Registry stores schema
6. Schema Registry publishes `schema.registered` event

**Schema Retrieval:**
1. Publisher or subscriber requests schema
2. Schema Registry returns schema
3. Publisher or subscriber validates event against schema

**Schema Evolution:**
1. Publisher submits new schema version
2. Schema Registry validates schema
3. Schema Registry checks compatibility
4. Schema Registry stores new version
5. Schema Registry publishes `schema.updated` event
6. Schema Registry supports both old and new versions during migration

---

## 11. Event Lifecycle

The Event Platform manages the complete lifecycle of an event.

### 11.1 Lifecycle Overview

```
Event Creation
    │
    ▼
Event Validation
    │
    ▼
Event Enrichment
    │
    ▼
Event Persistence
    │
    ▼
Event Routing
    │
    ├──► Subscriber 1
    │   │
    │   ├──► Delivery Success
    │   │   │
    │   │   ▼
    │   │  Delivered
    │   │
    │   └──► Delivery Failure
    │       │
    │       ├──► Retry
    │       │   │
    │       │   ├──► Retry Success
    │       │   │   │
    │       │   │   ▼
    │       │   │  Delivered
    │       │   │
    │       │   └──► Retry Failure
    │       │       │
    │       │       ▼
    │       │      Dead Letter Queue
    │       │
    │       └──► Skip (at-most-once)
    │           │
    │           ▼
    │          Skipped
    │
    ├──► Subscriber 2
    │   └── (same as above)
    │
    └──► Subscriber N
        └── (same as above)

Event Archived
```

### 11.2 Lifecycle Stages

#### Stage 1: Event Creation

**Purpose:** Create a new event.

**Process:**
1. Publisher creates event with:
   - Event type
   - Event category
   - Source
   - Payload
   - Correlation ID (optional)
   - Aggregate ID (optional)
   - Priority (optional)
   - Delivery mode (optional)
2. Publisher submits event to Event Platform
3. Event Platform receives event

**Outputs:**
- Event object (unvalidated)

**Duration:** Typically < 1ms

#### Stage 2: Event Validation

**Purpose:** Validate event against schema.

**Process:**
1. Event Platform retrieves schema for event type
2. Event Platform validates event structure
3. Event Platform validates event payload against schema
4. Event Platform validates event metadata against schema
5. If valid: Proceed to enrichment
6. If invalid: Reject event, return validation error

**Validation Checks:**
- Event type is valid
- Event category matches event type
- Required fields are present
- Field types are correct
- Field values are within constraints
- Payload conforms to schema
- Metadata conforms to schema

**Outputs:**
- Valid event (proceed to enrichment)
- Validation error (reject event)

**Duration:** Typically < 1ms

#### Stage 3: Event Enrichment

**Purpose:** Enrich event with metadata.

**Process:**
1. Event Platform generates event ID
2. Event Platform sets timestamp
3. Event Platform sets causation ID (if not set)
4. Event Platform sets correlation ID (if not set)
5. Event Platform adds standard metadata:
   - Publisher ID
   - Publisher version
   - Schema version
   - Trace ID
   - Span ID
6. Event Platform assigns to priority queue
7. Event Platform assigns sequence number (if ordering required)

**Enrichment Fields:**
- `eventId` — Generated UUID
- `timestamp` — Current timestamp
- `causationId` — Set if not provided
- `correlationId` — Set if not provided
- `metadata.publisherId` — Added
- `metadata.publisherVersion` — Added
- `metadata.schemaVersion` — Added
- `metadata.traceId` — Added
- `metadata.spanId` — Added

**Outputs:**
- Enriched event

**Duration:** Typically < 1ms

#### Stage 4: Event Persistence

**Purpose:** Persist event to durable storage.

**Process:**
1. Event Platform writes event to persistent storage
2. Event Platform confirms write
3. If write succeeds: Proceed to routing
4. If write fails: Queue event for retry

**Persistence Guarantees:**
- Event is written durably before routing
- Event is not lost once accepted
- Event is recoverable from storage

**Outputs:**
- Persisted event

**Duration:** Typically < 10ms

#### Stage 5: Event Routing

**Purpose:** Route event to matching subscribers.

**Process:**
1. Event Platform queries subscription registry
2. Event Platform matches event to subscriptions:
   - Match by event type
   - Match by event category
   - Match by filter expression
3. Event Platform creates delivery tasks for each matching subscription
4. Event Platform dispatches delivery tasks

**Routing Logic:**
- Exact match on event type
- Category match for category subscriptions
- Filter evaluation for filtered subscriptions
- Priority-based dispatch order

**Outputs:**
- Delivery tasks

**Duration:** Typically < 1ms

#### Stage 6: Event Delivery

**Purpose:** Deliver event to subscribers.

**Process:**
For each subscriber:
1. Event Platform retrieves subscriber callback
2. Event Platform delivers event to subscriber
3. Subscriber processes event
4. Subscriber returns delivery confirmation
5. If delivery succeeds: Mark as delivered
6. If delivery fails: Apply retry policy

**Delivery Guarantees:**
- At-most-once: Deliver once, don't retry on failure
- At-least-once: Deliver, retry on failure, may deliver multiple times
- Exactly-once: Deliver once, deduplicate on subscriber side

**Retry Policy:**
- Maximum retries: 3 (configurable)
- Backoff: Exponential backoff (1s, 2s, 4s)
- Retry on: Network errors, subscriber unavailable
- Don't retry on: Validation errors, schema errors

**Outputs:**
- Delivery confirmation
- Delivery failure (if retries exhausted)

**Duration:** Typically < 100ms per subscriber

#### Stage 7: Event Archival

**Purpose:** Archive event after retention period.

**Process:**
1. Event Platform checks event age
2. If event exceeds retention period:
   - Move event to cold storage
   - Compress event
   - Update event index
3. If event is within retention period: Keep in hot storage

**Retention Policy:**
- Hot storage: 30 days (configurable)
- Cold storage: 1 year (configurable)
- Archive: Indefinite (configurable)

**Outputs:**
- Archived event

**Duration:** Background process

### 11.3 Lifecycle Events

The Event Platform publishes the following lifecycle events:

| Event | Trigger | Payload |
|---|---|---|
| `event.created` | Event created | eventId, eventType, source, timestamp |
| `event.validated` | Event validated | eventId, valid, errors (if invalid) |
| `event.enriched` | Event enriched | eventId, enrichmentMetadata |
| `event.persisted` | Event persisted | eventId, storageLocation |
| `event.routed` | Event routed | eventId, subscriberCount |
| `event.delivered` | Event delivered | eventId, subscriberId, deliveryMode |
| `event.delivery_failed` | Event delivery failed | eventId, subscriberId, error, retryCount |
| `event.dead_lettered` | Event sent to DLQ | eventId, subscriberId, error, failureReason |
| `event.archived` | Event archived | eventId, archiveLocation |
| `schema.registered` | Schema registered | schemaId, version, eventType |
| `schema.updated` | Schema updated | schemaId, oldVersion, newVersion |
| `subscription.created` | Subscription created | subscriptionId, eventTypes, subscriber |
| `subscription.deleted` | Subscription deleted | subscriptionId |
| `replay.started` | Replay started | replayId, source, eventCount |
| `replay.completed` | Replay completed | replayId, eventsReplayed, duration |
| `replay.failed` | Replay failed | replayId, error |

---

## 12. Event Routing

The Event Platform routes events from publishers to subscribers.

### 12.1 Routing Model

The Event Platform uses a multi-level routing model:

```
Event
    │
    ▼
Category Router
    │
    ├──► KERNEL
    │   └──► Kernel subscribers
    │
    ├──► RUNTIME
    │   └──► Runtime subscribers
    │
    ├──► WORKFLOW
    │   └──► Workflow subscribers
    │
    └──► ...
        └──► Category subscribers

Event
    │
    ▼
Type Router
    │
    ├──► project.created
    │   ├──► Subscriber 1 (exact match)
    │   └──► Subscriber 2 (exact match)
    │
    ├──► task.completed
    │   ├──► Subscriber 3 (exact match)
    │   └──► Subscriber 4 (exact match)
    │
    └──► ...
        └──► Type subscribers

Event
    │
    ▼
Filter Router
    │
    ├──► Filter: projectId = "123"
    │   └──► Subscriber 5 (filtered)
    │
    ├──► Filter: source = "kernel"
    │   └──► Subscriber 6 (filtered)
    │
    └──► ...
        └──► Filtered subscribers
```

### 12.2 Publishers

Publishers emit events to the Event Platform.

**Publisher Responsibilities:**
- Create events with correct structure
- Validate events before publication
- Provide required fields (eventType, source, payload)
- Provide optional fields (correlationId, aggregateId, priority, deliveryMode)
- Handle publication responses
- Handle publication failures

**Publisher Types:**
- **Internal Publishers** — Platform subsystems (Kernel, Runtime, etc.)
- **External Publishers** — External systems via API
- **System Publishers** — Event Platform itself (lifecycle events)

**Publisher Interface:**
```
Publish(
  eventType: EventType,
  source: String,
  payload: Map,
  correlationId: UUID | null = null,
  aggregateId: UUID | null = null,
  aggregateType: String | null = null,
  priority: Priority = Priority.NORMAL,
  deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
  metadata: Map | null = null
) -> EventId
```

### 12.3 Subscribers

Subscribers receive events from the Event Platform.

**Subscriber Responsibilities:**
- Register subscriptions with correct filters
- Process events within timeout
- Return delivery confirmations
- Handle event processing failures
- Handle duplicate events (for at-least-once delivery)
- Maintain idempotency

**Subscriber Types:**
- **Internal Subscribers** — Platform subsystems (Kernel, Runtime, etc.)
- **External Subscribers** — External systems via webhook
- **System Subscribers** — Event Platform internal components (DLQ, Replay, etc.)

**Subscriber Interface:**
```
Subscribe(
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  filter: String | null = null,
  deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
  callback: Function<Event, void>
) -> SubscriptionId
```

### 12.4 Topic Routing

Events are routed to subscribers based on event type (topic).

**Topic Subscription:**
- Subscriber subscribes to specific event type
- Event Platform routes all events of that type to subscriber
- Example: Subscribe to `task.completed` events

**Topic Matching:**
- Exact match on event type
- No wildcards in v1.0
- Future: Support wildcards (e.g., `task.*`)

### 12.5 Category Routing

Events are routed to subscribers based on event category.

**Category Subscription:**
- Subscriber subscribes to event category
- Event Platform routes all events in that category to subscriber
- Example: Subscribe to all `project` events

**Category Matching:**
- Exact match on event category
- Subscriber receives all event types in category
- More efficient than subscribing to individual types

### 12.6 Broadcast

Events can be broadcast to all interested subscribers.

**Broadcast Events:**
- System events (e.g., `kernel.started`)
- Health events (e.g., `service.healthy`)
- Alert events (e.g., `observability.alert`)

**Broadcast Routing:**
- Event Platform routes broadcast events to all subscribers
- Subscribers cannot opt out of broadcast events
- Broadcast events bypass filters

### 12.7 Directed Events

Events can be directed to specific subscribers.

**Directed Events:**
- Approval events (directed to specific approver)
- Task assignment events (directed to specific worker)
- Recovery events (directed to specific component)

**Directed Routing:**
- Event Platform routes directed events to specific subscriber
- Routing based on event metadata (e.g., `targetSubscriber`)
- Other subscribers do not receive directed events

### 12.8 Internal Events

Internal events are events emitted by the Event Platform itself.

**Internal Event Sources:**
- Event Bus (lifecycle events)
- Schema Registry (schema events)
- Replay Engine (replay events)
- Dead Letter Queue (DLQ events)

**Internal Event Routing:**
- Internal events are routed to system subscribers
- Internal events are not exposed to external publishers/subscribers
- Internal events are used for platform monitoring and management

### 12.9 External Events

External events are events from external systems.

**External Event Sources:**
- Webhooks from external systems
- API calls from external systems
- Connector events from external systems

**External Event Routing:**
- External events are validated and enriched
- External events are routed like internal events
- External events are tagged with `external` source

---

## 13. Event Publication

The Event Platform accepts and processes event publications.

### 13.1 Publication Flow

```
Publisher
    │
    │ 1. Create event
    ▼
Event Platform
    │
    │ 2. Validate event
    ▼
Schema Validator
    │
    │ 3. Validate against schema
    ▼
Event Validator
    │
    │ 4. Enrich event
    ▼
Event Enricher
    │
    │ 5. Persist event
    ▼
Event Persistence
    │
    │ 6. Route event
    ▼
Event Router
    │
    │ 7. Deliver to subscribers
    ▼
Subscribers
    │
    │ 8. Confirm delivery
    ▼
Event Platform
    │
    │ 9. Confirm publication
    ▼
Publisher
```

### 13.2 Publication Process

#### Step 1: Receive Event

**Input:** Event from publisher

**Process:**
1. Event Platform receives event
2. Event Platform validates event structure
3. Event Platform checks publisher authorization
4. Event Platform assigns to validation queue

**Output:** Event (unvalidated)

**Duration:** Typically < 1ms

#### Step 2: Validate Event

**Input:** Event (unvalidated)

**Process:**
1. Event Platform retrieves schema for event type
2. Schema Validator validates event against schema
3. Schema Validator checks:
   - Event type is registered
   - Required fields are present
   - Field types are correct
   - Field values are valid
4. If valid: Proceed to enrichment
5. If invalid: Reject event, return validation error

**Output:**
- Valid event (proceed to enrichment)
- Validation error (reject event)

**Duration:** Typically < 1ms

#### Step 3: Enrich Event

**Input:** Valid event

**Process:**
1. Event Platform generates event ID
2. Event Platform sets timestamp
3. Event Platform sets causation ID (if not set)
4. Event Platform sets correlation ID (if not set)
5. Event Platform adds standard metadata
6. Event Platform assigns to priority queue
7. Event Platform assigns sequence number (if ordering required)

**Enrichment:**
- `eventId` — Generated UUID
- `timestamp` — Current timestamp
- `causationId` — Set if not provided
- `correlationId` — Set if not provided
- `metadata.publisherId` — Added
- `metadata.publisherVersion` — Added
- `metadata.schemaVersion` — Added
- `metadata.traceId` — Added
- `metadata.spanId` — Added

**Output:** Enriched event

**Duration:** Typically < 1ms

#### Step 4: Persist Event

**Input:** Enriched event

**Process:**
1. Event Platform writes event to persistent storage
2. Event Platform confirms write
3. If write succeeds: Proceed to routing
4. If write fails: Queue event for retry

**Persistence:**
- Write to primary storage
- Confirm write completion
- Handle write failures

**Output:** Persisted event

**Duration:** Typically < 10ms

#### Step 5: Route Event

**Input:** Persisted event

**Process:**
1. Event Platform queries subscription registry
2. Event Platform matches event to subscriptions
3. Event Platform creates delivery tasks
4. Event Platform dispatches delivery tasks

**Routing:**
- Match by event type
- Match by event category
- Evaluate filter expressions
- Create delivery tasks

**Output:** Delivery tasks

**Duration:** Typically < 1ms

#### Step 6: Deliver Event

**Input:** Delivery tasks

**Process:**
For each delivery task:
1. Event Platform retrieves subscriber callback
2. Event Platform delivers event to subscriber
3. Subscriber processes event
4. Subscriber returns delivery confirmation
5. If delivery succeeds: Mark as delivered
6. If delivery fails: Apply retry policy

**Delivery:**
- Deliver to subscriber callback
- Handle delivery failures
- Apply retry policy
- Track delivery status

**Output:** Delivery confirmations

**Duration:** Typically < 100ms per subscriber

#### Step 7: Confirm Publication

**Input:** Delivery confirmations

**Process:**
1. Event Platform aggregates delivery confirmations
2. Event Platform determines publication status:
   - All delivered: Success
   - Some delivered: Partial success
   - None delivered: Failure (for at-least-once and exactly-once)
3. Event Platform returns publication confirmation to publisher

**Confirmation:**
- Return event ID
- Return publication status
- Return delivery status (if requested)

**Output:** Publication confirmation

**Duration:** Typically < 1ms

### 13.3 Publication Guarantees

The Event Platform provides the following publication guarantees:

**Event Acceptance:**
- Event is accepted if valid
- Event is rejected if invalid
- Event is queued if storage unavailable
- Event is never lost once accepted

**Event Persistence:**
- Event is persisted before routing
- Event is durably stored
- Event is recoverable from storage
- Event is never lost

**Event Routing:**
- Event is routed to all matching subscribers
- Event is routed according to delivery mode
- Event routing failures are retried
- Event is sent to DLQ if retries exhausted

**Publication Confirmation:**
- Publisher receives confirmation
- Confirmation includes event ID
- Confirmation includes delivery status (if requested)
- Confirmation is returned after persistence

---

## 14. Event Subscription

The Event Platform manages event subscriptions.

### 14.1 Subscription Flow

```
Subscriber
    │
    │ 1. Create subscription
    ▼
Event Platform
    │
    │ 2. Validate subscription
    ▼
Subscription Validator
    │
    │ 3. Register subscription
    ▼
Subscription Registry
    │
    │ 4. Begin delivering events
    ▼
Event Router
    │
    │ 5. Deliver matching events
    ▼
Subscriber
    │
    │ 6. Process events
    ▼
Subscriber
    │
    │ 7. Return confirmations
    ▼
Event Platform
```

### 14.2 Subscription Process

#### Step 1: Receive Subscription Request

**Input:** Subscription request from subscriber

**Process:**
1. Event Platform receives subscription request
2. Event Platform validates request structure
3. Event Platform checks subscriber authorization
4. Event Platform assigns to validation queue

**Output:** Subscription request (unvalidated)

**Duration:** Typically < 1ms

#### Step 2: Validate Subscription

**Input:** Subscription request

**Process:**
1. Event Platform validates event types (if provided)
2. Event Platform validates event categories (if provided)
3. Event Platform validates filter expression (if provided)
4. Event Platform validates delivery mode
5. Event Platform validates callback
6. If valid: Proceed to registration
7. If invalid: Reject subscription, return validation error

**Validation Checks:**
- At least one event type or category specified
- Event types are valid
- Event categories are valid
- Filter expression is valid (if provided)
- Delivery mode is supported
- Callback is reachable

**Output:**
- Valid subscription (proceed to registration)
- Validation error (reject subscription)

**Duration:** Typically < 1ms

#### Step 3: Register Subscription

**Input:** Valid subscription

**Process:**
1. Event Platform generates subscription ID
2. Event Platform creates subscription record
3. Event Platform stores subscription in registry
4. Event Platform registers subscription with router
5. Event Platform begins routing matching events
6. Event Platform publishes `subscription.created` event

**Registration:**
- Generate subscription ID
- Create subscription record
- Store in registry
- Register with router
- Begin event delivery

**Output:** Registered subscription

**Duration:** Typically < 1ms

#### Step 4: Deliver Events

**Input:** Matching events

**Process:**
1. Event Router matches events to subscription
2. Event Platform delivers events to subscriber callback
3. Subscriber processes events
4. Subscriber returns delivery confirmations
5. Event Platform tracks delivery status

**Delivery:**
- Match events to subscription
- Deliver events to callback
- Handle delivery failures
- Track delivery status

**Output:** Delivery confirmations

**Duration:** Continuous

### 14.3 Subscription Types

#### Type-Based Subscription

Subscriber subscribes to specific event types.

**Example:**
```
Subscribe(
  eventTypes: [TaskCompleted, TaskFailed],
  callback: HandleTaskEvents
)
```

**Behavior:**
- Receive all events of specified types
- No category filtering
- No additional filtering

#### Category-Based Subscription

Subscriber subscribes to event category.

**Example:**
```
Subscribe(
  eventCategories: [Task],
  callback: HandleAllTaskEvents
)
```

**Behavior:**
- Receive all events in specified categories
- No type filtering
- No additional filtering

#### Filtered Subscription

Subscriber subscribes with filter expression.

**Example:**
```
Subscribe(
  eventTypes: [TaskCompleted],
  filter: "projectId = '123' AND priority = 'high'",
  callback: HandleHighPriorityTaskEvents
)
```

**Behavior:**
- Receive events matching filter
- Filter evaluated at runtime
- Filter can reference event fields

### 14.4 Subscription Management

#### Create Subscription

**Input:** Subscription request

**Process:**
1. Validate subscription request
2. Register subscription
3. Begin delivering events
4. Return subscription ID

**Output:** Subscription ID

#### Get Subscription

**Input:** Subscription ID

**Process:**
1. Look up subscription
2. Return subscription details

**Output:** Subscription details

#### Update Subscription

**Input:** Subscription ID, update request

**Process:**
1. Validate update request
2. Update subscription
3. Return updated subscription

**Output:** Updated subscription

#### Delete Subscription

**Input:** Subscription ID

**Process:**
1. Look up subscription
2. Stop delivering events
3. Remove subscription from registry
4. Publish `subscription.deleted` event
5. Return success

**Output:** Success confirmation

#### List Subscriptions

**Input:** Filter criteria (optional)

**Process:**
1. Query subscriptions
2. Apply filters
3. Return subscription list

**Output:** List of subscriptions

---

## 15. Event Delivery Guarantees

The Event Platform provides explicit event delivery guarantees.

### 15.1 Delivery Modes

The Event Platform supports three delivery modes:

#### At-Most-Once Delivery

**Guarantee:** Event may be lost but never delivered more than once.

**Behavior:**
- Event is delivered once
- If delivery fails: Event is not retried
- Event is sent to DLQ if delivery fails
- No duplicate detection required

**Use Cases:**
- Metrics and telemetry
- Log events
- Non-critical notifications
- Idempotent operations

**Configuration:**
```
Publish(
  eventType: MetricEmitted,
  source: "observability",
  payload: {metric: "cpu_usage", value: 0.85},
  deliveryMode: AtMostOnce
)
```

#### At-Least-Once Delivery

**Guarantee:** Event will be delivered at least once, may be delivered multiple times.

**Behavior:**
- Event is delivered
- If delivery fails: Event is retried
- Event may be delivered multiple times
- Subscriber must handle duplicates
- Event is sent to DLQ if retries exhausted

**Use Cases:**
- Task lifecycle events
- Project lifecycle events
- State change events
- Critical notifications

**Configuration:**
```
Publish(
  eventType: TaskCompleted,
  source: "execution",
  payload: {taskId: "123", result: "success"},
  deliveryMode: AtLeastOnce
)
```

**Retry Policy:**
- Maximum retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Retry on: Network errors, subscriber unavailable
- Don't retry on: Validation errors, schema errors

#### Exactly-Once Delivery

**Guarantee:** Event will be delivered exactly once.

**Behavior:**
- Event is delivered once
- Event is deduplicated at subscriber
- Event is tracked for deduplication
- Event is sent to DLQ if delivery fails after deduplication

**Use Cases:**
- Payment events
- Approval events
- State transition events
- Financial transactions

**Configuration:**
```
Publish(
  eventType: ApprovalDecided,
  source: "approval",
  payload: {approvalId: "456", decision: "approved"},
  deliveryMode: ExactlyOnce
)
```

**Deduplication:**
- Event Platform assigns unique event ID
- Subscribers MAY track processed event IDs to ensure idempotency
- Deduplication window: Implementation-specific

**Implementation Note:**
Exactly-once delivery is a semantic guarantee. Implementations achieve this through various mechanisms including idempotent processing, deduplication, transactional guarantees, or equivalent approaches. The Event Platform defines the contract; implementations choose the mechanism.

### 15.2 Delivery Guarantee Matrix

| Event Category | Default Delivery Mode | Configurable | Rationale |
|---|---|---|---|
| KERNEL | at-least-once | Yes | Kernel events are critical |
| RUNTIME | at-least-once | Yes | State changes must be delivered |
| WORKFLOW | at-least-once | Yes | Workflow events are critical |
| EXECUTION | at-least-once | Yes | Execution events are critical |
| REVIEW | at-least-once | Yes | Review events are critical |
| KNOWLEDGE | at-most-once | Yes | Knowledge queries are idempotent |
| MEMORY | at-least-once | Yes | Memory events are critical |
| LEARNING | at-most-once | Yes | Learning events are idempotent |
| INFRASTRUCTURE | at-least-once | Yes | Infrastructure events are critical |
| CONNECTOR | at-least-once | Yes | Connector events are critical |
| SECURITY | exactly-once | Yes | Security events must not be duplicated |
| OBSERVABILITY | at-most-once | Yes | Metrics and logs are idempotent |
| APPROVAL | exactly-once | Yes | Approval events must not be duplicated |
| ARTIFACT | at-least-once | Yes | Artifact events are critical |
| WORKER | at-least-once | Yes | Worker events are critical |
| TASK | at-least-once | Yes | Task events are critical |
| PROJECT | at-least-once | Yes | Project events are critical |
| CHECKPOINT | at-least-once | Yes | Checkpoint events are critical |
| RECOVERY | at-least-once | Yes | Recovery events are critical |

### 15.3 Delivery Semantics

#### At-Most-Once Semantics

**Guarantees:**
- Event is delivered zero or one times
- Event is never duplicated
- Event may be lost

**Implementation:**
- Fire-and-forget delivery
- No retry on failure
- No deduplication

**Subscriber Responsibilities:**
- Handle missing events gracefully
- No duplicate detection required

#### At-Least-Once Semantics

**Guarantees:**
- Event is delivered one or more times
- Event is never lost
- Event may be duplicated

**Implementation:**
- Delivery with retry
- Retry on failure
- No deduplication

**Subscriber Responsibilities:**
- Handle duplicate events
- Implement idempotency
- Track processed event IDs (optional)

#### Exactly-Once Semantics

**Guarantees:**
- Event is delivered exactly once
- Event is never lost
- Event is never duplicated

**Implementation:**
- Delivery with retry
- Deduplication at subscriber
- Event tracking for deduplication

**Subscriber Responsibilities:**
- Implement deduplication
- Track processed event IDs
- Ignore duplicate events

### 15.4 Delivery Retry Policy

**Retry Configuration:**
- Maximum retries: 3 (configurable per subscription)
- Initial backoff: 1 second
- Backoff multiplier: 2x
- Maximum backoff: 60 seconds
- Jitter: ±10%

**Retry Triggers:**
- Network errors
- Subscriber unavailable
- Subscriber timeout
- Delivery confirmation timeout

**Retry Exclusions:**
- Validation errors
- Schema errors
- Authorization errors
- Subscription not found

**Retry Process:**
1. Delivery fails
2. Wait for backoff period
3. Retry delivery
4. If success: Mark as delivered
5. If failure: Increment retry count
6. If retries exhausted: Send to DLQ

### 15.5 Delivery Timeout

**Delivery Timeout Configuration:**
- Default timeout: 30 seconds (configurable per subscription)
- Priority multiplier:
  - Critical: 2x timeout
  - High: 1.5x timeout
  - Normal: 1x timeout
  - Low: 0.5x timeout

**Timeout Handling:**
- Subscriber doesn't respond within timeout
- Event Platform retries delivery
- Event Platform tracks timeout count
- Event Platform sends to DLQ if retries exhausted

---

## 16. Event Ordering

The Event Platform preserves event order where required.

### 16.1 Ordering Guarantees

The Event Platform provides the following ordering guarantees:

#### No Ordering Guarantee

**Guarantee:** Events may be delivered in any order.

**Use Cases:**
- Independent events
- Events without causal relationship
- Events where order doesn't matter

**Configuration:**
```
Subscribe(
  eventTypes: [TaskCompleted],
  orderingGuarantee: None,
  callback: HandleTaskCompleted
)
```

#### Per-Aggregate Ordering

**Guarantee:** Events for the same aggregate are delivered in order.

**Use Cases:**
- State changes for the same entity
- Events with same aggregate ID
- Event sourcing

**Configuration:**
```
Subscribe(
  eventTypes: [TaskStarted, TaskCompleted],
  orderingGuarantee: PerAggregate,
  callback: HandleTaskEvents
)
```

**Implementation:**
- Events with same aggregate ID are sequenced
- Sequence numbers assigned per aggregate
- Events delivered in sequence number order
- Out-of-order events buffered

#### Per-Stream Ordering

**Guarantee:** Events in the same stream are delivered in order.

**Use Cases:**
- Events with same correlation ID
- Events in the same workflow
- Events in the same project

**Configuration:**
```
Subscribe(
  eventTypes: [TaskStarted, TaskCompleted],
  orderingGuarantee: PerStream,
  callback: HandleTaskEvents
)
```

**Implementation:**
- Events with same correlation ID are sequenced
- Sequence numbers assigned per stream
- Events delivered in sequence number order
- Out-of-order events buffered

#### Global Ordering

**Guarantee:** All events are delivered in global order.

**Use Cases:**
- Audit trails
- Compliance logging
- Debugging

**Configuration:**
```
Subscribe(
  eventCategories: [All],
  orderingGuarantee: Global,
  callback: HandleAllEvents
)
```

**Implementation:**
- All events are sequenced globally
- Single sequence number space
- Events delivered in sequence number order
- Significant performance impact

### 16.2 Ordering Implementation

#### Sequence Numbers

**Per-Aggregate Sequence:**
- Sequence number scoped to aggregate ID
- Incremented for each event on aggregate
- Stored in event metadata
- Used for ordering

**Per-Stream Sequence:**
- Sequence number scoped to correlation ID
- Incremented for each event in stream
- Stored in event metadata
- Used for ordering

**Global Sequence:**
- Single sequence number space
- Incremented for each event
- Stored in event metadata
- Used for ordering

#### Ordering Buffer

**Purpose:** Buffer out-of-order events until missing events arrive.

**Buffer Configuration:**
- Buffer size: 100 events (configurable)
- Buffer timeout: 5 seconds (configurable)
- Buffer strategy: Per-aggregate or per-stream

**Buffer Process:**
1. Event arrives with sequence number N
2. Check if event N-1 has been delivered
3. If yes: Deliver event N
4. If no: Buffer event N
5. When event N-1 arrives: Deliver buffered events in order

**Buffer Overflow:**
- If buffer overflows: Deliver events in order received
- Log ordering violation
- Publish `ordering.violation` event

### 16.3 Ordering Violations

**Detection:**
- Event arrives with sequence number gap
- Buffer timeout expires
- Sequence number out of range

**Handling:**
- Log ordering violation
- Publish `ordering.violation` event
- Deliver events in order received
- Continue processing

**Recovery:**
- Detect missing events
- Request event replay
- Fill sequence gap
- Resume ordered delivery

---

## 17. Event Replay

The Event Platform supports event replay from history.

### 17.1 Replay Model

The Event Platform replays events from event history.

**Replay Sources:**
- From timestamp
- From event ID
- From checkpoint
- From beginning of time

**Replay Destinations:**
- Subscriber callback
- File export
- Event bus (isolated replay)

**Replay Modes:**
- Live replay (deliver to subscriber)
- Export replay (write to file)
- Isolated replay (deliver to isolated bus)

### 17.2 Replay Process

#### Step 1: Create Replay Session

**Input:** Replay request

**Process:**
1. Validate replay request
2. Create replay session
3. Query events from history
4. Calculate total event count
5. Return replay ID and status

**Output:** Replay session

**Duration:** Typically < 1s

#### Step 2: Query Events

**Input:** Replay session

**Process:**
1. Query event history based on source
2. Apply filters (event types, categories, project ID, etc.)
3. Order events by timestamp or sequence
4. Paginate events
5. Return event stream

**Query:**
- Filter by time range
- Filter by event types
- Filter by event categories
- Filter by project ID
- Filter by correlation ID
- Filter by source
- Order by timestamp or sequence

**Output:** Event stream

**Duration:** Depends on event count

#### Step 3: Deliver Events

**Input:** Event stream

**Process:**
1. Read events from stream
2. Apply replay speed
3. Deliver events to subscriber
4. Track replay progress
5. Handle delivery failures
6. Continue until all events delivered

**Delivery:**
- Deliver events at specified speed
- Handle delivery failures
- Track progress
- Support pause/resume/stop

**Output:** Delivery confirmations

**Duration:** Depends on event count and speed

#### Step 4: Complete Replay

**Input:** Delivery confirmations

**Process:**
1. Verify all events delivered
2. Calculate replay statistics
3. Publish `replay.completed` event
4. Clean up replay session
5. Return replay results

**Output:** Replay results

**Duration:** Typically < 1s

### 17.3 Replay Features

#### Replay from Checkpoint

**Purpose:** Replay events from a specific checkpoint.

**Process:**
1. Load checkpoint
2. Get checkpoint timestamp or event ID
3. Query events from checkpoint
4. Replay events

**Use Cases:**
- Recovery after failure
- Debugging from specific point
- Testing from known state

#### Replay with Filters

**Purpose:** Replay filtered events.

**Process:**
1. Apply filters to event query
2. Query filtered events
3. Replay filtered events

**Filters:**
- Event types
- Event categories
- Project ID
- Correlation ID
- Source
- Time range

#### Replay at Different Speeds

**Purpose:** Replay events at different speeds.

**Speeds:**
- 1x (real-time)
- 2x (twice as fast)
- 4x (four times as fast)
- 8x (eight times as fast)
- Maximum (as fast as possible)

**Use Cases:**
- Testing (fast replay)
- Debugging (slow replay)
- Analysis (maximum speed)

#### Pause and Resume Replay

**Purpose:** Control replay execution.

**Controls:**
- Pause: Pause replay
- Resume: Resume paused replay
- Stop: Stop replay
- Seek: Jump to specific event

**Use Cases:**
- Debugging (pause at specific event)
- Analysis (pause to examine state)
- Testing (stop on error)

### 17.4 Replay Isolation

**Purpose:** Isolate replay from live event flow.

**Isolation Methods:**
- Separate event bus (replay bus)
- Separate subscriber (replay subscriber)
- Event tagging (replay events tagged)

**Isolation Guarantees:**
- Replay events do not affect live subscribers
- Replay events do not trigger live workflows
- Replay events are clearly identified

---

## 18. Event Persistence

The Event Platform persists events to durable storage.

### 18.1 Persistence Model

The Event Platform uses a multi-tier persistence model:

```
Event
    │
    ▼
Hot Storage (SSD)
    │
    │ — Recent events (last 30 days)
    │ — Fast access
    │ — Full indexing
    │
    ▼
Warm Storage (HDD)
    │
    │ — Older events (30 days - 1 year)
    │ — Slower access
    │ — Compressed
    │
    ▼
Cold Storage (Archive)
    │
    │ — Old events (1+ years)
    │ — Slowest access
    │ — Highly compressed
    │ — Infrequent access
```

### 18.2 Persistence Process

#### Write Path

**Process:**
1. Event is accepted
2. Event is validated
3. Event is enriched
4. Event is written to hot storage
5. Write is confirmed
6. Event is routed to subscribers

**Write Guarantees:**
- Event is durably written before routing
- Write is atomic
- Write is recoverable
- Write is confirmed

**Write Performance:**
- Target: < 10ms write latency
- Throughput: 10,000 events/second
- Batching: Enabled for performance

#### Read Path

**Process:**
1. Query request received
2. Query is parsed and validated
3. Query is executed against storage
4. Results are filtered and sorted
5. Results are paginated
6. Results are returned

**Read Guarantees:**
- Read is consistent
- Read reflects all persisted events
- Read is recoverable

**Read Performance:**
- Target: < 100ms query latency
- Throughput: 1,000 queries/second
- Caching: Enabled for frequent queries

### 18.3 Storage Tiers

#### Hot Storage

**Purpose:** Store recent events for fast access.

**Characteristics:**
- Storage: SSD
- Retention: 30 days (configurable)
- Access: Fast (< 10ms)
- Indexing: Full
- Compression: None

**Use Cases:**
- Recent event queries
- Live event delivery
- Replay from recent history

#### Warm Storage

**Purpose:** Store older events for occasional access.

**Characteristics:**
- Storage: HDD
- Retention: 30 days - 1 year (configurable)
- Access: Moderate (< 100ms)
- Indexing: Partial
- Compression: Enabled

**Use Cases:**
- Historical event queries
- Replay from older history
- Analytics

#### Cold Storage

**Purpose:** Store old events for long-term retention.

**Characteristics:**
- Storage: Archive (S3, Glacier, etc.)
- Retention: 1+ years (configurable)
- Access: Slow (seconds to minutes)
- Indexing: Metadata only
- Compression: High

**Use Cases:**
- Compliance
- Audit
- Long-term analysis

### 18.4 Retention Policy

**Retention Rules:**
- Hot storage: 30 days
- Warm storage: 1 year
- Cold storage: Indefinite
- Deletion: Never (archived only)

**Retention Enforcement:**
- Background job runs daily
- Moves events from hot to warm
- Moves events from warm to cold
- Archives events (does not delete)

**Retention Configuration:**
- Configurable per event category
- Configurable per event type
- Configurable per project
- Override for compliance requirements

### 18.5 Storage Optimization

**Compression:**
- Warm storage: gzip compression
- Cold storage: gzip + parquet compression
- Compression ratio: 10:1

**Indexing:**
- Hot storage: Full index on all fields
- Warm storage: Partial index on frequently queried fields
- Cold storage: Metadata index only

**Partitioning:**
- Partition by date (monthly partitions)
- Partition by category (optional)
- Partition by project (optional)

**Caching:**
- In-memory cache for frequent queries
- Cache size: 10% of hot storage
- Cache invalidation: On write

---

## 19. Event History

The Event Platform maintains complete event history.

### 19.1 History Model

The Event Platform maintains a complete, immutable history of all events.

**History Characteristics:**
- Complete: All events are recorded
- Immutable: Events cannot be modified or deleted
- Ordered: Events are ordered by timestamp and sequence
- Indexed: Events are indexed for efficient querying
- Durable: Events are persisted durably

### 19.2 History Queries

The Event Platform provides rich query APIs for event history.

#### Query by Event Type

**Input:**
- Event types
- Time range (optional)
- Limit
- Offset

**Output:**
- Events matching event types
- Total count
- Pagination metadata

**Example:**
```
QueryEvents(
  eventTypes: [TaskCompleted, TaskFailed],
  timeRange: ("2024-01-01", "2024-01-31"),
  limit: 100,
  offset: 0
)
```

#### Query by Event Category

**Input:**
- Event categories
- Time range (optional)
- Limit
- Offset

**Output:**
- Events matching categories
- Total count
- Pagination metadata

**Example:**
```
QueryEvents(
  eventCategories: [Task],
  timeRange: ("2024-01-01", "2024-01-31"),
  limit: 100,
  offset: 0
)
```

#### Query by Project

**Input:**
- Project ID
- Time range (optional)
- Limit
- Offset

**Output:**
- Events for project
- Total count
- Pagination metadata

**Example:**
```
QueryEvents(
  projectId: "123",
  timeRange: ("2024-01-01", "2024-01-31"),
  limit: 100,
  offset: 0
)
```

#### Query by Correlation ID

**Input:**
- Correlation ID
- Time range (optional)
- Limit
- Offset

**Output:**
- Events with correlation ID
- Total count
- Pagination metadata

**Example:**
```
QueryEvents(
  correlationId: "456",
  timeRange: ("2024-01-01", "2024-01-31"),
  limit: 100,
  offset: 0
)
```

#### Query by Source

**Input:**
- Source
- Time range (optional)
- Limit
- Offset

**Output:**
- Events from source
- Total count
- Pagination metadata

**Example:**
```
QueryEvents(
  source: "kernel",
  timeRange: ("2024-01-01", "2024-01-31"),
  limit: 100,
  offset: 0
)
```

### 19.3 History Aggregation

The Event Platform supports aggregation of event history.

#### Count Events

**Input:**
- Event types or categories
- Time range
- Group by (optional)

**Output:**
- Event counts
- Grouped by specified dimension

**Example:**
```
CountEvents(
  eventCategories: [Task],
  timeRange: ("2024-01-01", "2024-01-31"),
  groupBy: "eventType"
)
```

#### Aggregate Metrics

**Input:**
- Metric definition
- Time range
- Group by

**Output:**
- Aggregated metrics
- Grouped by specified dimension

**Example:**
```
AggregateMetrics(
  metric: "task.duration",
  timeRange: ("2024-01-01", "2024-01-31"),
  groupBy: "day"
)
```

### 19.4 History Export

The Event Platform supports export of event history.

**Export Formats:**
- JSON
- CSV
- Parquet

**Export Destinations:**
- File system
- S3
- External system

**Export Process:**
1. Define export query
2. Query events
3. Transform to export format
4. Write to destination
5. Return export location

**Example:**
```
ExportEvents(
  eventCategories: [Task],
  timeRange: ("2024-01-01", "2024-01-31"),
  format: "parquet",
  destination: "s3://bucket/events.parquet"
)
```

---

## 20. Event Correlation

The Event Platform correlates related events.

### 20.1 Correlation Model

The Event Platform uses correlation IDs and causation IDs to correlate events.

**Correlation ID:**
- Groups related events
- Set by event publisher
- Spans multiple subsystems
- Represents a logical operation

**Causation ID:**
- Traces event causation
- Set by Event Platform
- Represents direct cause-and-effect
- Forms event chain

### 20.2 Correlation Patterns

#### Project Correlation

**Pattern:** All events for a project are correlated.

**Correlation ID:** Project ID

**Events:**
- `project.created`
- `project.started`
- `task.completed`
- `project.finished`

**Usage:**
- Track all events for a project
- Debug project execution
- Analyze project metrics

#### Workflow Correlation

**Pattern:** All events for a workflow are correlated.

**Correlation ID:** Workflow ID

**Events:**
- `workflow.started`
- `loop.started`
- `task.completed`
- `workflow.completed`

**Usage:**
- Track workflow execution
- Debug workflow issues
- Analyze workflow performance

#### Task Correlation

**Pattern:** All events for a task are correlated.

**Correlation ID:** Task ID

**Events:**
- `task.created`
- `task.started`
- `task.completed`
- `task.failed`

**Usage:**
- Track task execution
- Debug task issues
- Analyze task performance

#### Causation Chain

**Pattern:** Events are linked in causation chain.

**Causation ID:** Event ID of causing event

**Example:**
1. `task.completed` (eventId: 1)
2. `workflow.completed` (causationId: 1)
3. `project.finished` (causationId: 2)

**Usage:**
- Trace event causation
- Debug event chains
- Analyze event flow

### 20.3 Correlation Queries

The Event Platform provides correlation queries.

#### Query by Correlation ID

**Input:** Correlation ID

**Output:** All events with correlation ID

**Example:**
```
QueryEvents(correlationId: "123")
```

#### Query Causation Chain

**Input:** Event ID

**Output:** Event causation chain

**Example:**
```
QueryCausationChain(eventId: "1")
```

#### Query Related Events

**Input:** Event ID

**Output:** All related events (correlated and caused)

**Example:**
```
QueryRelatedEvents(eventId: "1")
```

---

## 21. Event Filtering

The Event Platform filters events for subscribers.

### 21.1 Filter Model

Subscribers can filter events based on:

- Event type
- Event category
- Source
- Project ID
- Correlation ID
- Aggregate ID
- Time range
- Payload content
- Metadata

### 21.2 Filter Expressions

The Event Platform supports filter expressions.

**Syntax:**
```
{field} {operator} {value}
```

**Operators:**
- `=` — Equals
- `!=` — Not equals
- `>` — Greater than
- `<` — Less than
- `>=` — Greater than or equal
- `<=` — Less than or equal
- `IN` — In list
- `NOT IN` — Not in list
- `CONTAINS` — Contains substring
- `STARTS WITH` — Starts with substring
- `ENDS WITH` — Ends with substring

**Logical Operators:**
- `AND` — Logical AND
- `OR` — Logical OR
- `NOT` — Logical NOT

**Examples:**
```
projectId = '123'
priority = 'high' OR priority = 'critical'
source = 'kernel' AND eventType IN ('project.created', 'project.started')
timestamp >= '2024-01-01' AND timestamp <= '2024-01-31'
```

### 21.3 Filter Evaluation

**Evaluation Process:**
1. Parse filter expression
2. Validate filter syntax
3. Evaluate filter against event
4. Return match result

**Evaluation Performance:**
- Target: < 1ms per event
- Optimization: Pre-compile filter expressions
- Caching: Cache filter results

### 21.4 Filter Optimization

**Optimization Techniques:**
- Pre-compile filter expressions
- Index frequently filtered fields
- Cache filter results
- Short-circuit evaluation
- Push down filters to storage

---

## 22. Event Validation

The Event Platform validates events against schemas.

### 22.1 Validation Process

#### Step 1: Schema Lookup

**Input:** Event type

**Process:**
1. Look up schema for event type
2. If schema found: Proceed to validation
3. If schema not found: Reject event

**Output:** Schema

**Duration:** Typically < 1ms

#### Step 2: Structure Validation

**Input:** Event, schema

**Process:**
1. Validate event structure
2. Check required fields
3. Check field types
4. Check field constraints
5. If valid: Proceed to payload validation
6. If invalid: Return validation error

**Validation Checks:**
- Event type matches schema
- Required fields present
- Field types correct
- Field values within constraints

**Output:**
- Valid structure (proceed to payload validation)
- Validation error (reject event)

**Duration:** Typically < 1ms

#### Step 3: Payload Validation

**Input:** Event payload, payload schema

**Process:**
1. Validate payload against schema
2. Check required fields
3. Check field types
4. Check field constraints
5. If valid: Accept event
6. If invalid: Return validation error

**Validation Checks:**
- Payload structure matches schema
- Required fields present
- Field types correct
- Field values within constraints
- Nested objects valid
- Arrays valid

**Output:**
- Valid payload (accept event)
- Validation error (reject event)

**Duration:** Typically < 1ms

### 22.2 Validation Errors

**Error Format:**
```json
{
  "error": "validation_error",
  "message": "Event validation failed",
  "details": [
    {
      "field": "payload.projectId",
      "error": "required_field_missing",
      "message": "Field 'projectId' is required"
    },
    {
      "field": "payload.configuration",
      "error": "invalid_type",
      "message": "Field 'configuration' must be an object"
    }
  ]
}
```

**Error Codes:**
- `required_field_missing` — Required field is missing
- `invalid_type` — Field type is incorrect
- `invalid_value` — Field value is invalid
- `constraint_violation` — Field violates constraint
- `schema_not_found` — Schema not found for event type
- `schema_version_not_found` — Schema version not found

### 22.3 Schema Validation

**Schema Validation:**
- Schemas are validated before registration
- Schemas must conform to JSON Schema standard
- Schemas must include compatibility rules
- Schemas must be versioned

**Schema Registration:**
1. Publisher submits schema
2. Schema Registry validates schema
3. Schema Registry checks compatibility
4. Schema Registry assigns version
5. Schema Registry stores schema
6. Schema Registry publishes `schema.registered` event

---

## 23. Dead Letter Queue

The Event Platform manages a dead letter queue (DLQ) for failed events.

### 23.1 DLQ Model

The DLQ stores events that cannot be delivered to subscribers.

**DLQ Characteristics:**
- Events that failed delivery after retries
- Events with permanent errors
- Events for manual intervention
- Events for analysis and debugging

### 23.2 DLQ Process

#### Event Failure

**Process:**
1. Event delivery fails
2. Event Platform retries delivery
3. Retries exhausted
4. Event is sent to DLQ
5. DLQ stores event with failure context
6. DLQ publishes `event.dead_lettered` event
7. DLQ alerts on DLQ growth

**Failure Context:**
- Event ID
- Subscriber ID
- Error message
- Retry count
- Failure timestamp
- Failure reason

#### DLQ Storage

**Storage:**
- Events stored in durable storage
- Events indexed for querying
- Events tagged with failure reason
- Events retained according to policy

**Retention:**
- DLQ events retained for 30 days (configurable)
- DLQ events archived after retention
- DLQ events never deleted

#### DLQ Query

**Query DLQ:**
```
QueryDeadLetters(
  subscriberId: null,
  eventType: null,
  failureReason: null,
  timeRange: null,
  limit: 100,
  offset: 0
)
```

**Output:**
- Dead letter events
- Failure context
- Total count
- Pagination metadata

### 23.3 DLQ Operations

#### List Dead Letters

**Input:** Filter criteria (optional)

**Output:** List of dead letter events

**Example:**
```
ListDeadLetters(
  subscriberId: "sub-123",
  timeRange: ("2024-01-01", "2024-01-31")
)
```

#### Retry Dead Letter

**Input:** Dead letter event ID

**Process:**
1. Retrieve dead letter event
2. Remove from DLQ
3. Retry delivery
4. If success: Mark as delivered
5. If failure: Return to DLQ

**Output:** Retry result

**Example:**
```
RetryDeadLetter(deadLetterId: "dlq-456")
```

#### Replay Dead Letters

**Input:** Filter criteria

**Process:**
1. Query dead letters
2. Remove from DLQ
3. Retry delivery for all
4. Track replay progress
5. Return replay results

**Output:** Replay results

**Example:**
```
ReplayDeadLetters(
  subscriberId: "sub-123",
  timeRange: ("2024-01-01", "2024-01-31")
)
```

#### Delete Dead Letter

**Input:** Dead letter event ID

**Process:**
1. Retrieve dead letter event
2. Remove from DLQ
3. Archive event
4. Return success

**Output:** Success confirmation

**Example:**
```
DeleteDeadLetter(deadLetterId: "dlq-456")
```

#### Analyze Dead Letters

**Input:** Time range

**Process:**
1. Query dead letters
2. Analyze failure patterns
3. Generate failure report
4. Return analysis

**Output:** Analysis report

**Example:**
```
AnalyzeDeadLetters(
  timeRange: ("2024-01-01", "2024-01-31")
)
```

**Analysis:**
- Failure reasons
- Failure patterns
- Subscriber failure rates
- Event type failure rates
- Time-based patterns
- Recommendations

### 23.4 DLQ Alerts

**Alert Conditions:**
- DLQ size exceeds threshold
- DLQ growth rate exceeds threshold
- Specific subscriber has high failure rate
- Specific event type has high failure rate

**Alert Channels:**
- Dashboard notification
- Email notification
- Slack notification
- PagerDuty notification

**Alert Actions:**
- Notify on-call team
- Create incident
- Trigger automatic retry
- Escalate to human

---

## 24. Failure Handling

The Event Platform handles failures gracefully.

### 24.1 Failure Types

#### Publication Failures

**Failures:**
- Schema validation failure
- Persistence failure
- Routing failure

**Handling:**
- Schema validation: Reject event, return error
- Persistence failure: Queue event, retry, return accepted with warning
- Routing failure: Queue event, retry, return accepted with warning

#### Delivery Failures

**Failures:**
- Subscriber unavailable
- Subscriber timeout
- Subscriber error

**Handling:**
- Retry delivery (at-least-once, exactly-once)
- Send to DLQ if retries exhausted
- Alert on DLQ growth
- Notify subscriber

#### Persistence Failures

**Failures:**
- Storage unavailable
- Write timeout
- Write error

**Handling:**
- Queue event for retry
- Failover to backup storage
- Alert on storage failure
- Recover from backup

#### Subscription Failures

**Failures:**
- Invalid subscription
- Subscriber callback unavailable
- Subscription limit exceeded

**Handling:**
- Invalid subscription: Reject, return error
- Callback unavailable: Queue subscription, retry
- Limit exceeded: Reject, return error

### 24.2 Retry Policy

**Retry Configuration:**
- Maximum retries: 3 (configurable)
- Initial backoff: 1 second
- Backoff multiplier: 2x
- Maximum backoff: 60 seconds
- Jitter: ±10%

**Retry Triggers:**
- Network errors
- Subscriber unavailable
- Subscriber timeout
- Storage unavailable

**Retry Exclusions:**
- Validation errors
- Schema errors
- Authorization errors
- Subscription not found

### 24.3 Circuit Breaker

**Purpose:** Prevent cascading failures.

**Circuit Breaker States:**
- **Closed** — Normal operation
- **Open** — Failing, reject requests
- **Half-Open** — Testing recovery

**Circuit Breaker Configuration:**
- Failure threshold: 5 failures
- Recovery timeout: 30 seconds
- Half-open max requests: 3

**Circuit Breaker Process:**
1. Track failure count
2. If failures exceed threshold: Open circuit
3. Reject requests while open
4. After recovery timeout: Half-open
5. Test with limited requests
6. If success: Close circuit
7. If failure: Open circuit again

### 24.4 Fallback

**Purpose:** Provide fallback behavior on failure.

**Fallback Strategies:**
- **Queue and retry** — Queue event, retry later
- **Send to DLQ** — Send to DLQ for manual intervention
- **Drop event** — Drop event (at-most-once only)
- **Degrade gracefully** — Continue with reduced functionality

**Fallback Configuration:**
- Configurable per event type
- Configurable per subscriber
- Configurable per delivery mode

---

## 25. Kernel Interactions

The Event Platform interacts with the Kernel throughout the request lifecycle.

### 25.1 Kernel as Publisher

The Kernel publishes events to signal occurrences.

**Published Events:**
- `project.created` — New project created
- `project.started` — Project execution started
- `project.planning` — Planning phase began
- `project.running` — Execution began
- `project.reviewing` — Awaiting human review
- `project.paused` — Execution paused
- `project.resumed` — Execution resumed
- `project.completing` — Validating completion
- `project.finished` — Project completed
- `project.failed` — Project failed
- `project.cancelled` — Project cancelled
- `loop.started` — Engineering loop began
- `loop.planning` — Loop in planning phase
- `loop.executing` — Loop executing tasks
- `loop.reviewing` — Loop reviewing outputs
- `loop.completed` — Loop completed
- `loop.remediating` — Loop requires remediation
- `loop.escalated` — Loop escalated to human
- `loop.failed` — Loop failed
- `task.dispatched` — Task dispatched to worker
- `task.started` — Task execution began
- `task.completed` — Task completed
- `task.failed` — Task failed
- `task.retrying` — Task retrying
- `task.waiting` — Task waiting for approval
- `task.blocked` — Task blocked
- `approval.required` — Human approval needed
- `approval.decided` — Human made decision
- `approval.timeout` — Approval timeout
- `approval.escalated` — Approval escalated
- `failure.detected` — Failure detected
- `recovery.started` — Recovery began
- `recovery.completed` — Recovery completed
- `recovery.failed` — Recovery failed

**Publication Process:**
1. Kernel creates event
2. Kernel publishes event to Event Platform
3. Event Platform validates event
4. Event Platform enriches event
5. Event Platform persists event
6. Event Platform routes event to subscribers
7. Event Platform confirms publication
8. Kernel receives confirmation

### 25.2 Kernel as Subscriber

The Kernel subscribes to events to detect changes.

**Subscribed Events:**
- `loop.completed` — Loop completed, proceed to next loop
- `loop.remediating` — Loop requires remediation
- `loop.escalated` — Loop requires human intervention
- `loop.failed` — Loop failed, invoke recovery
- `task.completed` — Task completed, trigger dependent tasks
- `task.failed` — Task failed, apply retry policy
- `task.retrying` — Task retrying, update state
- `task.waiting` — Task waiting for approval
- `task.blocked` — Task blocked, update state
- `review.completed` — Review completed, process decision
- `review.approved` — Artifact approved, release to downstream
- `review.rejected` — Artifact rejected, create remediation task
- `review.changes_requested` — Changes requested, create remediation task
- `recovery.completed` — Recovery completed, resume execution
- `recovery.failed` — Recovery failed, escalate to human
- `checkpoint.restored` — Checkpoint restored, resume from checkpoint
- `approval.decided` — Human made decision, execute decision
- `approval.timeout` — Approval timeout, apply default policy
- `approval.escalated` — Approval escalated, notify new approver
- `service.degraded` — Service degraded, adjust execution
- `service.recovered` — Service recovered, resume normal operation
- `service.failed` — Service failed, invoke failover

**Subscription Process:**
1. Kernel creates subscription
2. Event Platform validates subscription
3. Event Platform registers subscription
4. Event Platform delivers matching events
5. Kernel processes events
6. Kernel triggers orchestration actions

### 25.3 Event Handling

The Kernel handles events through:

**Event Reception:**
- Kernel subscribes to event topics
- Event Platform delivers events to Kernel
- Kernel receives events asynchronously

**Event Processing:**
- Kernel validates event
- Kernel correlates event with project
- Kernel updates state based on event
- Kernel triggers orchestration actions

**Event Correlation:**
- Kernel uses correlationId to correlate related events
- Kernel uses causationId to trace event chains
- Kernel uses projectId to scope events to projects

**Event Ordering:**
- Kernel processes events in order within a project
- Kernel handles out-of-order events gracefully
- Kernel uses event versioning for backward compatibility

---

## 26. Runtime Interactions

The Event Platform interacts with the Runtime State Manager.

### 26.1 Runtime as Publisher

The Runtime State Manager publishes events for state changes.

**Published Events:**
- `state.transitioned` — State transition occurred
- `state.created` — State entity created
- `state.updated` — State entity updated
- `state.deleted` — State entity deleted
- `state.restored` — State restored from checkpoint

**Publication Process:**
1. Runtime State Manager transitions state
2. Runtime State Manager creates event
3. Runtime State Manager publishes event to Event Platform
4. Event Platform validates event
5. Event Platform routes event to subscribers
6. Event Platform confirms publication
7. Runtime State Manager receives confirmation

### 26.2 Runtime as Subscriber

The Runtime State Manager subscribes to events to detect external state changes.

**Subscribed Events:**
- `project.created` — Create project state
- `project.started` — Transition to Running
- `project.planning` — Transition to Planning
- `project.running` — Transition to Running
- `project.reviewing` — Transition to Reviewing
- `project.paused` — Transition to Paused
- `project.resumed` — Transition to Running
- `project.completing` — Transition to Completing
- `project.finished` — Transition to Finished
- `project.failed` — Transition to Failed
- `project.cancelled` — Transition to Cancelled
- `loop.started` — Create loop state
- `loop.completed` — Transition loop to Complete
- `loop.failed` — Transition loop to Failed
- `task.dispatched` — Create task state
- `task.started` — Transition task to Running
- `task.completed` — Transition task to Completed
- `task.failed` — Transition task to Failed
- `task.retrying` — Transition task to Retrying
- `checkpoint.created` — Create checkpoint state
- `checkpoint.restored` — Restore state from checkpoint

**Subscription Process:**
1. Runtime State Manager creates subscription
2. Event Platform delivers matching events
3. Runtime State Manager processes events
4. Runtime State Manager updates state
5. Runtime State Manager publishes state change events

### 26.3 State Change Events

The Runtime State Manager publishes events for all state changes.

**Event Publication:**
- Every state transition publishes an event
- Event includes old state and new state
- Event includes transition metadata
- Event is published after state is persisted

**Event Consumption:**
- Kernel subscribes to state change events
- Observability subscribes to state change events
- Other subsystems subscribe to relevant state changes

---

## 27. Platform Engine Interactions

The Event Platform interacts with all Platform Engines.

### 27.1 Strategic Engine

**As Publisher:**
- `plan.created` — Strategic plan created
- `plan.updated` — Strategic plan updated
- `research.completed` — Research completed

**As Subscriber:**
- `knowledge.queried` — Knowledge queried
- `project.created` — New project created

### 27.2 Workflow Engine

**As Publisher:**
- `workflow.created` — Workflow created
- `workflow.started` — Workflow started
- `workflow.completed` — Workflow completed
- `workflow.failed` — Workflow failed
- `task.created` — Task created
- `task.ready` — Task ready to execute
- `task.blocked` — Task blocked

**As Subscriber:**
- `loop.completed` — Loop completed
- `task.completed` — Task completed
- `task.failed` — Task failed
- `approval.decided` — Approval decided

### 27.3 Execution Engine

**As Publisher:**
- `execution.started` — Execution started
- `execution.completed` — Execution completed
- `execution.failed` — Execution failed
- `worker.dispatched` — Worker dispatched
- `task.started` — Task started
- `task.completed` — Task completed
- `task.failed` — Task failed

**As Subscriber:**
- `workflow.created` — Workflow created
- `task.ready` — Task ready
- `approval.required` — Approval required
- `recovery.completed` — Recovery completed

### 27.4 Review Engine

**As Publisher:**
- `review.started` — Review started
- `review.completed` — Review completed
- `review.approved` — Artifact approved
- `review.rejected` — Artifact rejected
- `review.changes_requested` — Changes requested

**As Subscriber:**
- `artifact.created` — Artifact created
- `loop.reviewing` — Loop reviewing

### 27.5 Learning Engine

**As Publisher:**
- `learning.analyzed` — Learning analyzed
- `learning.validated` — Learning validated
- `learning.promoted` — Learning promoted

**As Subscriber:**
- `project.finished` — Project finished
- `loop.completed` — Loop completed

### 27.6 Knowledge Engine

**As Publisher:**
- `knowledge.queried` — Knowledge queried
- `knowledge.researched` — Research completed
- `knowledge.promoted` — Learning promoted

**As Subscriber:**
- `intent.analyzed` — Intent analyzed
- `loop.started` — Loop started

### 27.7 Memory Engine

**As Publisher:**
- `memory.stored` — Memory stored
- `memory.updated` — Memory updated
- `memory.retrieved` — Memory retrieved

**As Subscriber:**
- `project.created` — Project created
- `project.finished` — Project finished
- `task.completed` — Task completed

---

## 28. Shared Platform Service Interactions

The Event Platform interacts with all Shared Platform Services.

### 28.1 Runtime State Manager

**Interactions:**
- Runtime State Manager publishes state change events
- Event Platform routes state change events
- Kernel subscribes to state change events

**Events:**
- `state.transitioned` — State transition
- `state.created` — State created
- `state.updated` — State updated

### 28.2 Memory Engine

**Interactions:**
- Memory Engine publishes memory events
- Event Platform routes memory events
- Subscribers consume memory events

**Events:**
- `memory.stored` — Memory stored
- `memory.updated` — Memory updated
- `memory.retrieved` — Memory retrieved

### 28.3 Knowledge Engine

**Interactions:**
- Knowledge Engine publishes knowledge events
- Event Platform routes knowledge events
- Subscribers consume knowledge events

**Events:**
- `knowledge.queried` — Knowledge queried
- `knowledge.researched` — Research completed
- `knowledge.promoted` — Learning promoted

### 28.4 Model Router

**Interactions:**
- Model Router publishes model events
- Event Platform routes model events
- Subscribers consume model events

**Events:**
- `model.selected` — Model selected
- `model.failed` — Model failed
- `model.switched` — Model switched

### 28.5 Execution Continuity Manager

**Interactions:**
- Execution Continuity Manager publishes recovery events
- Event Platform routes recovery events
- Subscribers consume recovery events

**Events:**
- `recovery.started` — Recovery started
- `recovery.completed` — Recovery completed
- `recovery.failed` — Recovery failed

### 28.6 Connector Layer

**Interactions:**
- Connector Layer publishes connector events
- Event Platform routes connector events
- Subscribers consume connector events

**Events:**
- `connector.connected` — Connector connected
- `connector.executed` — Connector executed
- `connector.failed` — Connector failed

### 28.7 Observability

**Interactions:**
- Observability publishes observability events
- Event Platform routes observability events
- Observability subscribes to all events for telemetry

**Events:**
- `observability.metric` — Metric emitted
- `observability.log` — Log event
- `observability.trace` — Trace created

### 28.8 Security

**Interactions:**
- Security publishes security events
- Event Platform routes security events
- Security subscribes to all events for audit

**Events:**
- `security.authenticated` — Authentication successful
- `security.authorized` — Authorization successful
- `security.denied` — Access denied
- `security.policy_violated` — Policy violated

---

## 29. Sequence Diagrams

### 29.1 Event Publication Sequence

```
Publisher       Event Platform      Schema Registry      Persistence      Subscriber
   │                  │                    │                  │                │
   │─ Publish Event ──►│                    │                  │                │
   │                  │─ Validate Schema ──►│                  │                │
   │                  │◄─ Schema Valid ─────│                  │                │
   │                  │                    │                  │                │
   │                  │─ Enrich Event ─────┤                  │                │
   │                  │                    │                  │                │
   │                  │─ Persist Event ───────────────────────►│                │
   │                  │◄─ Persist Confirm ─────────────────────│                │
   │                  │                    │                  │                │
   │                  │─ Route Event ────────────────────────────────────────►│
   │                  │                    │                  │                │
   │                  │                    │                  │   ─ Process ──►│
   │                  │                    │                  │                │
   │                  │                    │                  │◄─ Confirm ─────│
   │                  │                    │                  │                │
   │◄─ Confirm Pub ────│                    │                  │                │
   │                  │                    │                  │                │
```

### 29.2 Event Subscription Sequence

```
Subscriber     Event Platform      Subscription Registry      Event Bus
   │                  │                    │                    │
   │─ Subscribe ──────►│                    │                    │
   │                  │─ Validate ──────────┤                    │
   │                  │◄─ Valid ─────────────│                    │
   │                  │                    │                    │
   │                  │─ Register ──────────►│                    │
   │                  │◄─ Sub ID ────────────│                    │
   │                  │                    │                    │
   │◄─ Sub ID ─────────│                    │                    │
   │                  │                    │                    │
   │                  │                    │   ─ Event Match ───►│
   │                  │                    │                    │
   │                  │◄── Deliver Event ───────────────────────│
   │                  │                    │                    │
   │─ Process Event ──►│                    │                    │
   │                  │                    │                    │
   │◄─ Confirm ────────│                    │                    │
   │                  │                    │                    │
```

### 29.3 Event Replay Sequence

```
Client         Event Platform      History Store      Subscriber
   │                  │                    │                │
   │─ Replay Request ─►│                    │                │
   │                  │─ Query History ──────────────────────►│
   │                  │◄─ Events ─────────────────────────────│
   │                  │                    │                │
   │                  │─ Deliver Event 1 ────────────────────►│
   │                  │                    │                │
   │                  │◄─ Confirm 1 ──────────────────────────│
   │                  │                    │                │
   │                  │─ Deliver Event 2 ────────────────────►│
   │                  │                    │                │
   │                  │◄─ Confirm 2 ──────────────────────────│
   │                  │                    │                │
   │◄─ Replay ID ──────│                    │                │
   │                  │                    │                │
```

### 29.4 Dead Letter Queue Sequence

```
Event Bus      Event Platform      DLQ Storage      Alert System
   │                  │                  │                  │
   │─ Delivery Fail ──►│                  │                  │
   │                  │─ Retry 1 ────────►│                  │
   │                  │◄─ Fail ───────────│                  │
   │                  │                  │                  │
   │                  │─ Retry 2 ────────►│                  │
   │                  │◄─ Fail ───────────│                  │
   │                  │                  │                  │
   │                  │─ Retry 3 ────────►│                  │
   │                  │◄─ Fail ───────────│                  │
   │                  │                  │                  │
   │                  │─ Write to DLQ ──────────────────────►│
   │                  │                  │                  │
   │                  │─ Alert ──────────────────────────────►│
   │                  │                  │                  │
```

---

## 30. State Diagrams

### 30.1 Event Lifecycle State Diagram

```
┌──────────┐
│ Created  │  Event created by publisher
└────┬─────┘
     │
     │ validate
     ▼
┌──────────┐
│Validating│  Event being validated
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │ Rejected │  Validation failed
     │     └──────────┘
     │
     │ valid
     ▼
┌──────────┐
│ Enriching│  Event being enriched
└────┬─────┘
     │
     │ enriched
     ▼
┌──────────┐
│Persisting│  Event being persisted
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │  Failed  │  Persistence failed
     │     └────┬─────┘
     │          │
     │          │ retry
     │          └──────────┐
     │                     │
     │                     ▼
     │               ┌──────────┐
     │               │Persisting│
     │               └──────────┘
     │
     │ persisted
     ▼
┌──────────┐
│ Routing  │  Event being routed
└────┬─────┘
     │
     │ routed
     ▼
┌──────────┐
│Delivering│  Event being delivered
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │  Failed  │  Delivery failed
     │     └────┬─────┘
     │          │
     │          │ retry
     │          └──────────┐
     │                     │
     │                     ▼
     │               ┌──────────┐
     │               │Delivering│
     │               └──────────┘
     │
     │ delivered
     ▼
┌──────────┐
│Delivered │  Event delivered to all subscribers
└────┬─────┘
     │
     │ archive
     ▼
┌──────────┐
│ Archived │  Event archived
└──────────┘
```

### 30.2 Subscription State Diagram

```
┌──────────┐
│ Pending  │  Subscription request received
└────┬─────┘
     │
     │ validate
     ▼
┌──────────┐
│Validating│  Subscription being validated
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │ Rejected │  Validation failed
     │     └──────────┘
     │
     │ valid
     ▼
┌──────────┐
│Registering│  Subscription being registered
└────┬─────┘
     │
     │ registered
     ▼
┌──────────┐
│  Active  │  Subscription active, delivering events
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │  Failed  │  Delivery failure
     │     └────┬─────┘
     │          │
     │          │ retry
     │          └──────────┐
     │                     │
     │                     ▼
     │               ┌──────────┐
     │               │  Active  │
     │               └──────────┘
     │
     │ delete
     ▼
┌──────────┐
│Deleting  │  Subscription being deleted
└────┬─────┘
     │
     │ deleted
     ▼
┌──────────┐
│ Deleted  │  Subscription deleted
└──────────┘
```

### 30.3 Replay State Diagram

```
┌──────────┐
│  Idle    │  No replay in progress
└────┬─────┘
     │
     │ start
     ▼
┌──────────┐
│Starting  │  Replay session starting
└────┬─────┘
     │
     │ started
     ▼
┌──────────┐
│ Running  │  Replay in progress
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │ Paused   │  Replay paused
     │     └────┬─────┘
     │          │
     │          │ resume
     │          └──────────┐
     │                     │
     │                     ▼
     │               ┌──────────┐
     │               │ Running  │
     │               └──────────┘
     │
     │ complete
     ▼
┌──────────┐
│Completed │  Replay completed
└────┬─────┘
     │
     │ cleanup
     ▼
┌──────────┐
│  Idle    │  Replay session cleaned up
└──────────┘
```

### 30.4 DLQ Event State Diagram

```
┌──────────┐
│ Delivering│  Event being delivered
└────┬─────┘
     │
     │ fail
     ▼
┌──────────┐
│Retrying  │  Event being retried
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │Delivered │  Retry succeeded
     │     └──────────┘
     │
     │ retries exhausted
     ▼
┌──────────┐
│Dead Letter│  Event in dead letter queue
└────┬─────┘
     │
     ├───► ┌──────────┐
     │     │Retried   │  Manual retry
     │     └────┬─────┘
     │          │
     │          │ success
     │          └──────────┐
     │                     │
     │                     ▼
     │               ┌──────────┐
     │               │Delivered │
     │               └──────────┘
     │
     │ deleted
     ▼
┌──────────┐
│ Archived │  Event archived
└──────────┘
```

---

## 31. Public API Reference

### 31.1 Event Publication API

#### publish_event

Publish an event to the event bus.

**Signature:**
```
Publish(
  eventType: EventType,
  source: String,
  payload: Map<String, Any>,
  correlationId: UUID | null = null,
  aggregateId: UUID | null = null,
  aggregateType: String | null = null,
  priority: Priority = Priority.NORMAL,
  deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
  metadata: Map<String, Any> | null = null
) -> EventId
```

**Parameters:**
- `event_type` — Event type (required)
- `source` — Event source (required)
- `payload` — Event payload (required)
- `correlation_id` — Correlation ID (optional)
- `aggregate_id` — Aggregate ID (optional)
- `aggregate_type` — Aggregate type (optional)
- `priority` — Event priority (default: NORMAL)
- `delivery_mode` — Delivery mode (default: AT_LEAST_ONCE)
- `metadata` — Additional metadata (optional)

**Returns:**
- `EventId` — Unique event identifier

**Raises:**
- `ValidationError` — Event validation failed
- `PersistenceError` — Event persistence failed
- `RoutingError` — Event routing failed

**Example:**
```
eventId = EventPlatform.Publish(
  eventType: TaskCompleted,
  source: "execution",
  payload: {taskId: "123", result: "success"},
  correlationId: UUID("456"),
  priority: High,
  deliveryMode: AtLeastOnce
)
```

### 31.2 Event Subscription API

#### subscribe

Subscribe to events from the event bus.

**Signature:**
```
Subscribe(
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  filter: String | null = null,
  deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
  orderingGuarantee: OrderingGuarantee = OrderingGuarantee.NONE,
  callback: Function<Event, void>
) -> SubscriptionId
```

**Parameters:**
- `event_types` — Event types to subscribe to (optional)
- `event_categories` — Event categories to subscribe to (optional)
- `filter` — Filter expression (optional)
- `delivery_mode` — Required delivery mode (default: AT_LEAST_ONCE)
- `ordering_guarantee` — Required ordering guarantee (default: NONE)
- `callback` — Subscriber callback (required)

**Returns:**
- `SubscriptionId` — Unique subscription identifier

**Raises:**
- `ValidationError` — Subscription validation failed
- `SubscriptionError` — Subscription creation failed

**Example:**
```
Function HandleTaskEvents(event: Event):
  Print("Received event: ${event.eventType}")

subscriptionId = EventPlatform.Subscribe(
  eventTypes: [TaskCompleted, TaskFailed],
  filter: "projectId = '123'",
  deliveryMode: AtLeastOnce,
  callback: HandleTaskEvents
)
```

### 31.3 Event Query API

#### query_events

Query historical events.

**Signature:**
```
QueryEvents(
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  projectId: UUID | null = null,
  correlationId: UUID | null = null,
  source: String | null = null,
  timeRange: Tuple<DateTime, DateTime> | null = null,
  limit: Integer = 100,
  offset: Integer = 0,
  orderBy: String = "timestamp"
) -> EventQueryResult
```

**Parameters:**
- `event_types` — Filter by event types (optional)
- `event_categories` — Filter by event categories (optional)
- `project_id` — Filter by project ID (optional)
- `correlation_id` — Filter by correlation ID (optional)
- `source` — Filter by source (optional)
- `time_range` — Filter by time range (optional)
- `limit` — Maximum results (default: 100)
- `offset` — Pagination offset (default: 0)
- `order_by` — Sort order (default: "timestamp")

**Returns:**
- `EventQueryResult` — Query results

**Raises:**
- `ValidationError` — Query validation failed
- `QueryError` — Query execution failed

**Example:**
```
result = EventPlatform.QueryEvents(
  eventCategories: [Task],
  projectId: UUID("123"),
  timeRange: (DateTime(2024, 1, 1), DateTime(2024, 1, 31)),
  limit: 100,
  offset: 0
)

For Each event In result.events:
  Print("Event: ${event.eventType}")

Print("Total: ${result.totalCount}")
```

### 31.4 Event Replay API

#### start_replay

Start an event replay session.

**Signature:**
```
StartReplay(
  source: ReplaySource,
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  projectId: UUID | null = null,
  speed: ReplaySpeed = ReplaySpeed.REALTIME,
  subscriber: Function<Event, void>,
  stopOnError: Boolean = false
) -> ReplayId
```

**Parameters:**
- `source` — Replay source (timestamp, event ID, or checkpoint)
- `event_types` — Filter by event types (optional)
- `event_categories` — Filter by event categories (optional)
- `project_id` — Filter by project ID (optional)
- `speed` — Replay speed (default: REALTIME)
- `subscriber` — Subscriber callback (required)
- `stop_on_error` — Stop on error (default: False)

**Returns:**
- `ReplayId` — Unique replay identifier

**Raises:**
- `ValidationError` — Replay request validation failed
- `ReplayError` — Replay start failed

**Example:**
```
Function HandleReplayedEvent(event: Event):
  Print("Replayed event: ${event.eventType}")

replayId = EventPlatform.StartReplay(
  source: ReplaySource.FromTimestamp(DateTime(2024, 1, 1)),
  eventCategories: [Task],
  speed: FourTimes,
  subscriber: HandleReplayedEvent
)
```

#### pause_replay

Pause a replay session.

**Signature:**
```
PauseReplay(replayId: ReplayId) -> void
```

**Parameters:**
- `replay_id` — Replay identifier (required)

**Raises:**
- `ReplayError` — Replay not found or not pausable

#### resume_replay

Resume a paused replay session.

**Signature:**
```
ResumeReplay(replayId: ReplayId) -> void
```

**Parameters:**
- `replay_id` — Replay identifier (required)

**Raises:**
- `ReplayError` — Replay not found or not resumable

#### stop_replay

Stop a replay session.

**Signature:**
```
StopReplay(replayId: ReplayId) -> void
```

**Parameters:**
- `replay_id` — Replay identifier (required)

**Raises:**
- `ReplayError` — Replay not found

#### get_replay_status

Get replay session status.

**Signature:**
```
GetReplayStatus(replayId: ReplayId) -> ReplayStatus
```

**Parameters:**
- `replay_id` — Replay identifier (required)

**Returns:**
- `ReplayStatus` — Replay status

**Raises:**
- `ReplayError` — Replay not found

### 31.5 Dead Letter Queue API

#### list_dead_letters

List dead letter events.

**Signature:**
```
ListDeadLetters(
  subscriberId: UUID | null = null,
  eventType: EventType | null = null,
  failureReason: String | null = null,
  timeRange: Tuple<DateTime, DateTime> | null = null,
  limit: Integer = 100,
  offset: Integer = 0
) -> DeadLetterQueryResult
```

**Parameters:**
- `subscriber_id` — Filter by subscriber ID (optional)
- `event_type` — Filter by event type (optional)
- `failure_reason` — Filter by failure reason (optional)
- `time_range` — Filter by time range (optional)
- `limit` — Maximum results (default: 100)
- `offset` — Pagination offset (default: 0)

**Returns:**
- `DeadLetterQueryResult` — Query results

**Example:**
```
result = EventPlatform.ListDeadLetters(
  timeRange: (DateTime(2024, 1, 1), DateTime(2024, 1, 31)),
  limit: 100
)

For Each dlqEvent In result.deadLetters:
  Print("DLQ Event: ${dlqEvent.eventId}, Reason: ${dlqEvent.failureReason}")
```

#### retry_dead_letter

Retry a dead letter event.

**Signature:**
```
RetryDeadLetter(deadLetterId: UUID) -> RetryResult
```

**Parameters:**
- `dead_letter_id` — Dead letter identifier (required)

**Returns:**
- `RetryResult` — Retry result

**Raises:**
- `DeadLetterError` — Dead letter not found

#### replay_dead_letters

Replay all dead letter events.

**Signature:**
```
ReplayDeadLetters(
  subscriberId: UUID | null = null,
  timeRange: Tuple<DateTime, DateTime> | null = null
) -> ReplayResult
```

**Parameters:**
- `subscriber_id` — Filter by subscriber ID (optional)
- `time_range` — Filter by time range (optional)

**Returns:**
- `ReplayResult` — Replay results

#### analyze_dead_letters

Analyze dead letter events.

**Signature:**
```
AnalyzeDeadLetters(
  timeRange: Tuple<DateTime, DateTime>
) -> DeadLetterAnalysis
```

**Parameters:**
- `time_range` — Time range (required)

**Returns:**
- `DeadLetterAnalysis` — Analysis results

### 31.6 Subscription Management API

#### create_subscription

Create an event subscription.

**Signature:**
```
CreateSubscription(
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  filter: String | null = null,
  deliveryMode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
  orderingGuarantee: OrderingGuarantee = OrderingGuarantee.NONE,
  callback: Function<Event, void>
) -> SubscriptionId
```

**Parameters:**
- `event_types` — Event types to subscribe to (optional)
- `event_categories` — Event categories to subscribe to (optional)
- `filter` — Filter expression (optional)
- `delivery_mode` — Required delivery mode (default: AT_LEAST_ONCE)
- `ordering_guarantee` — Required ordering guarantee (default: NONE)
- `callback` — Subscriber callback (required)

**Returns:**
- `SubscriptionId` — Unique subscription identifier

#### get_subscription

Get subscription details.

**Signature:**
```
GetSubscription(subscriptionId: SubscriptionId) -> Subscription
```

**Parameters:**
- `subscription_id` — Subscription identifier (required)

**Returns:**
- `Subscription` — Subscription details

#### update_subscription

Update a subscription.

**Signature:**
```
UpdateSubscription(
  subscriptionId: SubscriptionId,
  eventTypes: List<EventType> | null = null,
  eventCategories: List<EventCategory> | null = null,
  filter: String | null = null
) -> Subscription
```

**Parameters:**
- `subscription_id` — Subscription identifier (required)
- `event_types` — New event types (optional)
- `event_categories` — New event categories (optional)
- `filter` — New filter expression (optional)

**Returns:**
- `Subscription` — Updated subscription

#### delete_subscription

Delete a subscription.

**Signature:**
```
DeleteSubscription(subscriptionId: SubscriptionId) -> void
```

**Parameters:**
- `subscription_id` — Subscription identifier (required)

**Raises:**
- `SubscriptionError` — Subscription not found

#### list_subscriptions

List subscriptions.

**Signature:**
```
ListSubscriptions(
  eventType: EventType | null = null,
  eventCategory: EventCategory | null = null,
  subscriberId: UUID | null = null
) -> List<Subscription>
```

**Parameters:**
- `event_type` — Filter by event type (optional)
- `event_category` — Filter by event category (optional)
- `subscriber_id` — Filter by subscriber ID (optional)

**Returns:**
- `list[Subscription]` — List of subscriptions

---

## 32. Internal Component Reference

### 32.1 Event Bus

#### EventRouter

**Responsibility:** Route events to subscribers.

**Methods:**
- `route_event(event: Event) -> list[Subscription]`
- `register_subscription(subscription: Subscription) -> None`
- `unregister_subscription(subscription_id: SubscriptionId) -> None`
- `match_event_to_subscriptions(event: Event) -> list[Subscription]`

#### EventDispatcher

**Responsibility:** Dispatch events to subscribers.

**Methods:**
- `dispatch_event(event: Event, subscription: Subscription) -> DeliveryResult`
- `retry_delivery(event: Event, subscription: Subscription, retry_count: int) -> DeliveryResult`
- `handle_delivery_failure(event: Event, subscription: Subscription, error: Exception) -> None`

#### EventValidator

**Responsibility:** Validate events.

**Methods:**
- `validate_event(event: Event) -> ValidationResult`
- `validate_schema(event: Event, schema: Schema) -> ValidationResult`
- `validate_payload(payload: dict, schema: Schema) -> ValidationResult`

#### PriorityQueue

**Responsibility:** Manage event priority queues.

**Methods:**
- `enqueue(event: Event, priority: Priority) -> None`
- `dequeue() -> Event`
- `peek() -> Event | None`
- `get_queue_size(priority: Priority) -> int`

#### OrderingManager

**Responsibility:** Manage event ordering.

**Methods:**
- `assign_sequence_number(event: Event) -> int`
- `buffer_event(event: Event) -> None`
- `get_next_event(aggregate_id: uuid.UUID) -> Event | None`
- `detect_ordering_violation(event: Event) -> bool`

#### FilterEngine

**Responsibility:** Filter events.

**Methods:**
- `evaluate_filter(event: Event, filter: str) -> bool`
- `compile_filter(filter: str) -> FilterExpression`
- `optimize_filter(filter: FilterExpression) -> FilterExpression`

### 32.2 Event Schema Registry

#### SchemaRegistry

**Responsibility:** Manage event schemas.

**Methods:**
- `register_schema(schema: Schema) -> SchemaId`
- `get_schema(schema_id: SchemaId) -> Schema`
- `get_schema_for_event_type(event_type: EventType) -> Schema`
- `update_schema(schema_id: SchemaId, schema: Schema) -> Schema`
- `list_schemas() -> list[Schema]`

#### SchemaValidator

**Responsibility:** Validate schemas.

**Methods:**
- `validate_schema(schema: dict) -> ValidationResult`
- `validate_event_against_schema(event: Event, schema: Schema) -> ValidationResult`
- `check_compatibility(old_schema: Schema, new_schema: Schema) -> CompatibilityResult`

#### SchemaTransformer

**Responsibility:** Transform events between schema versions.

**Methods:**
- `transform_event(event: Event, from_version: str, to_version: str) -> Event`
- `migrate_event(event: Event, target_schema: Schema) -> Event`
- `apply_compatibility_rules(event: Event, schema: Schema) -> Event`

### 32.3 Event Persistence

#### EventWriter

**Responsibility:** Write events to storage.

**Methods:**
- `write_event(event: Event) -> WriteResult`
- `write_events(events: list[Event]) -> WriteResult`
- `batch_write(events: list[Event]) -> WriteResult`

#### EventReader

**Responsibility:** Read events from storage.

**Methods:**
- `read_event(event_id: EventId) -> Event | None`
- `read_events(query: EventQuery) -> EventIterator`
- `count_events(query: EventQuery) -> int`

#### EventArchiver

**Responsibility:** Archive old events.

**Methods:**
- `archive_events(older_than: datetime) -> ArchiveResult`
- `compress_events(events: list[Event]) -> bytes`
- `move_to_cold_storage(events: list[Event]) -> None`

### 32.4 Event Replay Engine

#### ReplayController

**Responsibility:** Control replay sessions.

**Methods:**
- `start_replay(request: ReplayRequest) -> ReplaySession`
- `pause_replay(replay_id: ReplayId) -> None`
- `resume_replay(replay_id: ReplayId) -> None`
- `stop_replay(replay_id: ReplayId) -> None`
- `get_replay_status(replay_id: ReplayId) -> ReplayStatus`

#### HistoryQuery

**Responsibility:** Query event history.

**Methods:**
- `query_events(query: EventQuery) -> EventIterator`
- `count_events(query: EventQuery) -> int`
- `get_event_timestamp_range() -> tuple[datetime, datetime]`

#### CorrelationEngine

**Responsibility:** Correlate events.

**Methods:**
- `correlate_events(correlation_id: uuid.UUID) -> list[Event]`
- `trace_causation_chain(event_id: EventId) -> list[Event]`
- `find_related_events(event_id: EventId) -> list[Event]`

### 32.5 Dead Letter Queue

#### DLQWriter

**Responsibility:** Write events to DLQ.

**Methods:**
- `write_to_dlq(event: Event, error: Exception, failure_reason: str) -> None`
- `write_batch_to_dlq(events: list[tuple[Event, Exception, str]]) -> None`

#### DLQReader

**Responsibility:** Read events from DLQ.

**Methods:**
- `read_dlq(query: DLQQuery) -> DLQIterator`
- `count_dlq(query: DLQQuery) -> int`
- `get_dlq_metrics() -> DLQMetrics`

#### DLQAnalyzer

**Responsibility:** Analyze DLQ events.

**Methods:**
- `analyze_failures(time_range: tuple[datetime, datetime]) -> FailureAnalysis`
- `identify_patterns() -> list[FailurePattern]`
- `generate_report() -> DLQReport`

---

## 33. Extension Points

The Event Platform provides the following extension points:

### 33.1 Custom Event Types

**Extension:** Add custom event types.

**Mechanism:**
1. Define event schema
2. Register schema with Event Schema Registry
3. Publish events with new event type
4. Subscribe to new event type

**Use Cases:**
- Domain-specific events
- Custom subsystem events
- Third-party integration events

### 33.2 Custom Event Categories

**Extension:** Add custom event categories.

**Mechanism:**
1. Define event category
2. Register event types in category
3. Subscribe to category
4. Route events to category

**Use Cases:**
- Domain-specific categories
- Custom subsystem categories
- Third-party integration categories

### 33.3 Custom Filters

**Extension:** Add custom filter functions.

**Mechanism:**
1. Implement filter function
2. Register filter function
3. Use filter in subscription

**Use Cases:**
- Complex filtering logic
- Domain-specific filters
- Performance optimization

### 33.4 Custom Delivery Handlers

**Extension:** Add custom delivery handlers.

**Mechanism:**
1. Implement delivery handler
2. Register delivery handler
3. Configure subscription to use handler

**Use Cases:**
- Custom delivery logic
- Protocol-specific delivery
- Third-party delivery systems

### 33.5 Custom Persistence Providers

**Extension:** Add custom persistence providers.

**Mechanism:**
1. Implement persistence provider interface
2. Register persistence provider
3. Configure Event Platform to use provider

**Use Cases:**
- Custom storage backends
- Third-party storage systems
- Performance optimization

### 33.6 Custom Schema Transformers

**Extension:** Add custom schema transformers.

**Mechanism:**
1. Implement transformer
2. Register transformer
3. Configure schema evolution to use transformer

**Use Cases:**
- Custom transformation logic
- Data enrichment
- Format conversion

### 33.7 Custom DLQ Handlers

**Extension:** Add custom DLQ handlers.

**Mechanism:**
1. Implement DLQ handler
2. Register DLQ handler
3. Configure DLQ to use handler

**Use Cases:**
- Custom DLQ processing
- Alerting and notification
- Automated remediation

---

## 34. ADR Requirements

The Event Platform requires the following Architecture Decision Records (ADRs):

### 34.1 Required ADRs

#### ADR-001: Event Bus Technology Selection

**Decision:** Select event bus technology (e.g., Apache Kafka, RabbitMQ, AWS EventBridge, in-memory).

**Rationale:**
- Event bus is core infrastructure
- Technology choice affects scalability, reliability, and performance
- Decision must consider deployment topology (local vs. cloud)

**Stakeholders:**
- Architecture team
- Infrastructure team
- Platform team

**Status:** Required before implementation

#### ADR-002: Event Schema Registry Technology Selection

**Decision:** Select schema registry technology (e.g., Confluent Schema Registry, custom implementation).

**Rationale:**
- Schema registry is critical for schema evolution
- Technology choice affects compatibility checking and transformation
- Decision must consider integration with event bus

**Stakeholders:**
- Architecture team
- Platform team

**Status:** Required before implementation

#### ADR-003: Event Persistence Technology Selection

**Decision:** Select event persistence technology (e.g., PostgreSQL, Cassandra, S3).

**Rationale:**
- Event persistence is critical for durability and replay
- Technology choice affects performance, cost, and scalability
- Decision must consider retention requirements

**Stakeholders:**
- Architecture team
- Infrastructure team
- Platform team

**Status:** Required before implementation

#### ADR-004: Event Ordering Strategy

**Decision:** Select event ordering strategy (per-aggregate, per-stream, global, none).

**Rationale:**
- Ordering affects performance and complexity
- Different use cases require different ordering guarantees
- Decision must balance consistency and performance

**Stakeholders:**
- Architecture team
- Platform team

**Status:** Required before implementation

#### ADR-005: Event Delivery Guarantee Implementation

**Decision:** Select implementation approach for at-least-once and exactly-once delivery.

**Rationale:**
- Delivery guarantees affect performance and complexity
- Exactly-once requires deduplication infrastructure
- Decision must balance guarantees and performance

**Stakeholders:**
- Architecture team
- Platform team

**Status:** Required before implementation

#### ADR-006: Multi-Tenancy Strategy

**Decision:** Select multi-tenancy strategy for event isolation.

**Rationale:**
- Multi-tenancy may be required for SaaS deployment
- Strategy affects event routing, storage, and security
- Decision must consider isolation requirements

**Stakeholders:**
- Architecture team
- Security team
- Platform team

**Status:** Required before cloud deployment

#### ADR-007: Event Retention Policy

**Decision:** Define event retention policy (hot, warm, cold storage tiers).

**Rationale:**
- Retention policy affects storage cost and performance
- Policy must balance compliance, audit, and cost requirements
- Decision must consider legal and business requirements

**Stakeholders:**
- Architecture team
- Infrastructure team
- Legal team
- Platform team

**Status:** Required before implementation

### 34.2 ADR Template

All Event Platform ADRs must follow this template:

```markdown
# ADR-XXX: {Title}

**Status:** Proposed | Accepted | Rejected | Superseded
**Date:** YYYY-MM-DD
**Decision Makers:** {List of decision makers}

## Context

{Describe the context and problem}

## Decision

{Describe the decision}

## Rationale

{Describe the rationale}

## Alternatives Considered

{Describe alternatives}

## Consequences

{Describe consequences}

## Implementation Notes

{Describe implementation notes}
```

---

## 35. Glossary

### 35.1 Event Platform Terms

**Event**
An immutable record of something that happened in the platform. Events are the primary communication mechanism between subsystems.

**Event Bus**
The central communication backbone that transports events between publishers and subscribers.

**Event Category**
A high-level grouping of related event types (e.g., `project`, `task`, `execution`).

**Event Type**
A specific event occurrence (e.g., `project.created`, `task.completed`).

**Event Schema**
A formal definition of an event's structure, including payload and metadata schemas.

**Event Publisher**
A component that creates and publishes events to the Event Platform.

**Event Subscriber**
A component that receives events from the Event Platform.

**Event Subscription**
A registered interest in receiving specific events from the Event Platform.

**Event Delivery**
The process of delivering an event from the Event Platform to a subscriber.

**Event Persistence**
The process of storing events durably for history, replay, and audit.

**Event Replay**
The process of re-delivering historical events to subscribers.

**Event History**
The complete, immutable record of all events that have occurred.

**Event Correlation**
The process of grouping related events using correlation IDs and causation IDs.

**Event Filtering**
The process of selecting events based on criteria (type, category, source, etc.).

**Event Validation**
The process of validating events against schemas.

**Dead Letter Queue (DLQ)**
A queue for events that cannot be delivered to subscribers after retries.

**Delivery Mode**
The guarantee provided for event delivery (at-most-once, at-least-once, exactly-once).

**Ordering Guarantee**
The guarantee provided for event ordering (none, per-aggregate, per-stream, global).

**Correlation ID**
A UUID that groups related events together.

**Causation ID**
A UUID that links an event to the event that caused it.

**Aggregate ID**
A UUID that identifies the aggregate root for an event.

**Aggregate Type**
The type of the aggregate root (e.g., `Project`, `Task`).

**Replay**
The process of re-delivering historical events.

**Checkpoint**
A point in time from which events can be replayed.

**Schema Registry**
A repository of event schemas that enables schema evolution and validation.

**Schema Versioning**
The practice of versioning event schemas to enable evolution.

**Backward Compatibility**
The property that new schema versions can read old events.

**Forward Compatibility**
The property that old schema versions can read new events.

### 35.2 Delivery Guarantee Terms

**At-Most-Once Delivery**
Event may be lost but never delivered more than once.

**At-Least-Once Delivery**
Event will be delivered at least once, may be delivered multiple times.

**Exactly-Once Delivery**
Event will be delivered exactly once.

**Idempotency**
The property that an operation can be applied multiple times without changing the result.

**Deduplication**
The process of identifying and ignoring duplicate events.

### 35.3 Event Lifecycle Terms

**Publication**
The act of creating and submitting an event to the Event Platform.

**Enrichment**
The process of adding metadata to an event (event ID, timestamp, etc.).

**Routing**
The process of determining which subscribers should receive an event.

**Delivery**
The act of sending an event to a subscriber.

**Confirmation**
The acknowledgment that an event was delivered successfully.

**Retry**
The act of re-attempting event delivery after failure.

**Archival**
The process of moving old events to cold storage.

**Retention**
The policy that determines how long events are kept.

### 35.4 Technical Terms

**JSON Schema**
A standard for describing the structure of JSON data.

**Semantic Versioning**
A versioning scheme (major.minor.patch) that conveys meaning about the underlying changes.

**UUID**
Universally Unique Identifier, a 128-bit identifier guaranteed to be unique.

**ISO 8601**
An international standard for date and time representation.

**Exponential Backoff**
A retry strategy where the wait time between retries increases exponentially.

**Jitter**
Random variation added to retry delays to prevent thundering herd.

**Circuit Breaker**
A pattern that prevents cascading failures by stopping requests to a failing service.

**Event Sourcing**
A pattern where state changes are captured as a sequence of events.

**CQRS**
Command Query Responsibility Segregation, a pattern that separates read and write operations.

**Pub/Sub**
Publish/Subscribe, a messaging pattern where publishers send messages to subscribers.

---

## Appendix A: Event Type Registry

The complete registry of all event types in the platform.

### A.1 Project Events

| Event Type | Category | Description |
|---|---|---|
| `project.created` | PROJECT | A new project was created |
| `project.updated` | PROJECT | An existing project was updated |
| `project.archived` | PROJECT | A project was archived |
| `project.deleted` | PROJECT | A project was permanently deleted |
| `project.started` | PROJECT | Project execution begins |
| `project.planning` | PROJECT | Planning phase begins |
| `project.running` | PROJECT | Execution begins |
| `project.reviewing` | PROJECT | Awaiting human review |
| `project.paused` | PROJECT | Execution paused |
| `project.resumed` | PROJECT | Execution resumes |
| `project.completing` | PROJECT | Validating completion |
| `project.finished` | PROJECT | Project completed |
| `project.failed` | PROJECT | Project failed |
| `project.cancelled` | PROJECT | Project cancelled |

### A.2 Task Events

| Event Type | Category | Description |
|---|---|---|
| `task.created` | TASK | A new task was created |
| `task.updated` | TASK | An existing task was updated |
| `task.queued` | TASK | A task was queued |
| `task.ready` | TASK | Task is ready to execute |
| `task.started` | TASK | Task execution began |
| `task.paused` | TASK | Task was paused |
| `task.resumed` | TASK | Paused task was resumed |
| `task.completed` | TASK | Task completed successfully |
| `task.failed` | TASK | Task failed |
| `task.cancelled` | TASK | Task was cancelled |
| `task.blocked` | TASK | Task is blocked |
| `task.deleted` | TASK | Task was deleted |
| `task.dispatched` | TASK | Task dispatched to worker |
| `task.retrying` | TASK | Task retrying |
| `task.waiting` | TASK | Task waiting for approval |

### A.3 Execution Events

| Event Type | Category | Description |
|---|---|---|
| `execution.started` | EXECUTION | Execution session started |
| `execution.completed` | EXECUTION | Execution session completed |
| `execution.failed` | EXECUTION | Execution session failed |
| `execution.paused` | EXECUTION | Execution session paused |
| `execution.resumed` | EXECUTION | Execution session resumed |
| `execution.cancelled` | EXECUTION | Execution session cancelled |
| `execution.timed_out` | EXECUTION | Execution session timed out |

### A.4 Loop Events

| Event Type | Category | Description |
|---|---|---|
| `loop.started` | LOOP | Engineering loop began |
| `loop.planning` | LOOP | Loop in planning phase |
| `loop.executing` | LOOP | Loop executing tasks |
| `loop.reviewing` | LOOP | Loop reviewing outputs |
| `loop.completed` | LOOP | Loop completed successfully |
| `loop.remediating` | LOOP | Loop requires remediation |
| `loop.escalated` | LOOP | Loop escalated to human |
| `loop.failed` | LOOP | Loop failed |

### A.5 Worker Events

| Event Type | Category | Description |
|---|---|---|
| `worker.registered` | WORKER | Worker registered |
| `worker.dispatched` | WORKER | Worker dispatched to task |
| `worker.started` | WORKER | Worker started task |
| `worker.completed` | WORKER | Worker completed task |
| `worker.failed` | WORKER | Worker failed |
| `worker.retired` | WORKER | Worker retired |

### A.6 Approval Events

| Event Type | Category | Description |
|---|---|---|
| `approval.required` | APPROVAL | Human approval needed |
| `approval.decided` | APPROVAL | Human made decision |
| `approval.timeout` | APPROVAL | Approval timeout |
| `approval.escalated` | APPROVAL | Approval escalated |
| `approval.cancelled` | APPROVAL | Approval cancelled |

### A.7 Review Events

| Event Type | Category | Description |
|---|---|---|
| `review.started` | REVIEW | Review started |
| `review.completed` | REVIEW | Review completed |
| `review.approved` | REVIEW | Artifact approved |
| `review.rejected` | REVIEW | Artifact rejected |
| `review.changes_requested` | REVIEW | Changes requested |
| `review.escalated` | REVIEW | Review escalated |

### A.8 Failure and Recovery Events

| Event Type | Category | Description |
|---|---|---|
| `failure.detected` | FAILURE | Failure detected |
| `recovery.started` | RECOVERY | Recovery started |
| `recovery.completed` | RECOVERY | Recovery completed |
| `recovery.failed` | RECOVERY | Recovery failed |
| `recovery.aborted` | RECOVERY | Recovery aborted |
| `checkpoint.restored` | CHECKPOINT | Checkpoint restored |

### A.9 Artifact Events

| Event Type | Category | Description |
|---|---|---|
| `artifact.created` | ARTIFACT | Artifact created |
| `artifact.updated` | ARTIFACT | Artifact updated |
| `artifact.deleted` | ARTIFACT | Artifact deleted |
| `artifact.published` | ARTIFACT | Artifact published |
| `artifact.archived` | ARTIFACT | Artifact archived |

### A.10 Memory Events

| Event Type | Category | Description |
|---|---|---|
| `memory.stored` | MEMORY | Memory entry stored |
| `memory.updated` | MEMORY | Memory entry updated |
| `memory.deleted` | MEMORY | Memory entry deleted |
| `memory.retrieved` | MEMORY | Memory entry retrieved |
| `memory.context_loaded` | MEMORY | Project context loaded |

### A.11 Knowledge Events

| Event Type | Category | Description |
|---|---|---|
| `knowledge.queried` | KNOWLEDGE | Knowledge queried |
| `knowledge.researched` | KNOWLEDGE | Research completed |
| `knowledge.promoted` | KNOWLEDGE | Learning promoted to knowledge |
| `knowledge.updated` | KNOWLEDGE | Knowledge updated |
| `knowledge.deleted` | KNOWLEDGE | Knowledge deleted |

### A.12 Learning Events

| Event Type | Category | Description |
|---|---|---|
| `learning.analyzed` | LEARNING | Learning analysis completed |
| `learning.validated` | LEARNING | Learning validated |
| `learning.promoted` | LEARNING | Learning promoted |
| `learning.discarded` | LEARNING | Learning discarded |

### A.13 Infrastructure Events

| Event Type | Category | Description |
|---|---|---|
| `service.started` | INFRASTRUCTURE | Service started |
| `service.stopped` | INFRASTRUCTURE | Service stopped |
| `service.healthy` | INFRASTRUCTURE | Service is healthy |
| `service.degraded` | INFRASTRUCTURE | Service is degraded |
| `service.recovered` | INFRASTRUCTURE | Service recovered |
| `service.failed` | INFRASTRUCTURE | Service failed |

### A.14 Connector Events

| Event Type | Category | Description |
|---|---|---|
| `connector.connected` | CONNECTOR | Connector connected |
| `connector.disconnected` | CONNECTOR | Connector disconnected |
| `connector.executed` | CONNECTOR | Connector operation executed |
| `connector.failed` | CONNECTOR | Connector operation failed |
| `connector.retrying` | CONNECTOR | Connector operation retrying |

### A.15 Security Events

| Event Type | Category | Description |
|---|---|---|
| `security.authenticated` | SECURITY | Authentication successful |
| `security.authorized` | SECURITY | Authorization successful |
| `security.denied` | SECURITY | Access denied |
| `security.policy_violated` | SECURITY | Security policy violated |
| `security.audit` | SECURITY | Security audit event |

### A.16 Observability Events

| Event Type | Category | Description |
|---|---|---|
| `observability.metric` | OBSERVABILITY | Metric emitted |
| `observability.log` | OBSERVABILITY | Log event |
| `observability.trace` | OBSERVABILITY | Trace created |
| `observability.span` | OBSERVABILITY | Span recorded |
| `observability.alert` | OBSERVABILITY | Alert triggered |

### A.17 Kernel Events

| Event Type | Category | Description |
|---|---|---|
| `kernel.created` | KERNEL | Kernel instance created |
| `kernel.starting` | KERNEL | Kernel is starting up |
| `kernel.started` | KERNEL | Kernel has started |
| `kernel.pausing` | KERNEL | Kernel is pausing |
| `kernel.paused` | KERNEL | Kernel is paused |
| `kernel.resuming` | KERNEL | Kernel is resuming |
| `kernel.ready` | KERNEL | Kernel is ready |
| `kernel.stopping` | KERNEL | Kernel is stopping |
| `kernel.stopped` | KERNEL | Kernel has stopped |

### A.18 Runtime Events

| Event Type | Category | Description |
|---|---|---|
| `state.transitioned` | RUNTIME | State transition occurred |
| `state.created` | RUNTIME | State entity created |
| `state.updated` | RUNTIME | State entity updated |
| `state.deleted` | RUNTIME | State entity deleted |
| `state.restored` | RUNTIME | State restored from checkpoint |

### A.19 Workflow Events

| Event Type | Category | Description |
|---|---|---|
| `workflow.created` | WORKFLOW | Workflow created |
| `workflow.started` | WORKFLOW | Workflow execution started |
| `workflow.completed` | WORKFLOW | Workflow execution completed |
| `workflow.failed` | WORKFLOW | Workflow execution failed |
| `workflow.paused` | WORKFLOW | Workflow execution paused |
| `workflow.resumed` | WORKFLOW | Workflow execution resumed |
| `workflow.cancelled` | WORKFLOW | Workflow execution cancelled |

### A.20 Checkpoint Events

| Event Type | Category | Description |
|---|---|---|
| `checkpoint.created` | CHECKPOINT | Checkpoint created |
| `checkpoint.restored` | CHECKPOINT | Checkpoint restored |
| `checkpoint.deleted` | CHECKPOINT | Checkpoint deleted |
| `checkpoint.archived` | CHECKPOINT | Checkpoint archived |

### A.21 Intent and Planning Events

| Event Type | Category | Description |
|---|---|---|
| `intent.analyzed` | KERNEL | Intent analysis completed |
| `plan.created` | KERNEL | Execution plan created |

### A.22 System Events

| Event Type | Category | Description |
|---|---|---|
| `created` | SYSTEM_EVENT | Generic created event |
| `updated` | SYSTEM_EVENT | Generic updated event |
| `started` | SYSTEM_EVENT | Generic started event |
| `completed` | SYSTEM_EVENT | Generic completed event |
| `failed` | SYSTEM_EVENT | Generic failed event |
| `paused` | SYSTEM_EVENT | Generic paused event |
| `resumed` | SYSTEM_EVENT | Generic resumed event |
| `cancelled` | SYSTEM_EVENT | Generic cancelled event |
| `approved` | SYSTEM_EVENT | Generic approved event |
| `rejected` | SYSTEM_EVENT | Generic rejected event |
| `changes_requested` | SYSTEM_EVENT | Generic changes requested event |
| `restored` | SYSTEM_EVENT | Generic restored event |
| `degraded` | SYSTEM_EVENT | Generic degraded event |
| `recovered` | SYSTEM_EVENT | Generic recovered event |
| `system_event` | SYSTEM_EVENT | Fallback for unknown event types |

---

## Appendix B: Event Category Registry

The complete registry of all event categories in the platform.

| Category | Description | Default Delivery Mode |
|---|---|---|
| KERNEL | Kernel lifecycle and orchestration events | at-least-once |
| RUNTIME | Runtime state management events | at-least-once |
| WORKFLOW | Workflow execution events | at-least-once |
| EXECUTION | Execution session events | at-least-once |
| REVIEW | Review engine events | at-least-once |
| KNOWLEDGE | Knowledge engine events | at-most-once |
| MEMORY | Memory engine events | at-least-once |
| LEARNING | Learning engine events | at-most-once |
| INFRASTRUCTURE | Infrastructure service events | at-least-once |
| CONNECTOR | Connector layer events | at-least-once |
| SECURITY | Security events | exactly-once |
| OBSERVABILITY | Observability events | at-most-once |
| APPROVAL | Human approval events | exactly-once |
| ARTIFACT | Artifact management events | at-least-once |
| WORKER | Worker lifecycle events | at-least-once |
| TASK | Task lifecycle events | at-least-once |
| PROJECT | Project lifecycle events | at-least-once |
| CHECKPOINT | Checkpoint events | at-least-once |
| RECOVERY | Recovery events | at-least-once |
| SYSTEM_EVENT | System-level events | at-most-once |

---

## Appendix C: Event Schema Registry

The complete registry of all event schemas in the platform.

### C.1 Schema Registration

All event schemas must be registered in the Event Schema Registry before use.

**Registration Process:**
1. Define event schema
2. Validate schema
3. Submit schema for registration
4. Schema Registry validates schema
5. Schema Registry checks compatibility
6. Schema Registry assigns version
7. Schema Registry stores schema
8. Schema Registry publishes `schema.registered` event

### C.2 Schema Versioning

All event schemas must be versioned using semantic versioning.

**Version Format:** `major.minor.patch`

**Versioning Rules:**
- Major version: Breaking changes
- Minor version: Backward-compatible changes
- Patch version: Non-breaking fixes

### C.3 Schema Compatibility

All schema changes must maintain backward and forward compatibility.

**Backward Compatibility:**
- New fields must be optional
- Removed fields must have been optional
- Field types must not change
- Field constraints must not be tightened

**Forward Compatibility:**
- Removed fields must have been optional
- New fields must have default values
- Field types must not change
- Field constraints must not be tightened

---

## Appendix D: Event Platform Configuration

### D.1 Configuration Options

```yaml
event_platform:
  # Event Bus Configuration
  event_bus:
    provider: "kafka"  # kafka, rabbitmq, memory, aws_eventbridge
    brokers:
      - "localhost:9092"
    topic_prefix: "autoforge"
    partition_count: 10
    replication_factor: 3

  # Schema Registry Configuration
  schema_registry:
    provider: "confluent"  # confluent, custom
    url: "http://localhost:8081"
    compatibility: "BACKWARD"  # BACKWARD, FORWARD, FULL, NONE

  # Persistence Configuration
  persistence:
    provider: "postgresql"  # postgresql, cassandra, s3
    connection_string: "postgresql://localhost/autoforge_events"
    hot_storage_retention_days: 30
    warm_storage_retention_days: 365
    cold_storage_enabled: true

  # Delivery Configuration
  delivery:
    default_delivery_mode: "at_least_once"
    max_retries: 3
    initial_backoff_seconds: 1
    backoff_multiplier: 2
    max_backoff_seconds: 60
    delivery_timeout_seconds: 30

  # Ordering Configuration
  ordering:
    default_ordering: "none"  # none, per_aggregate, per_stream, global
    buffer_size: 100
    buffer_timeout_seconds: 5

  # DLQ Configuration
  dlq:
    enabled: true
    retention_days: 30
    alert_threshold: 100
    auto_retry: false
    auto_retry_interval_seconds: 3600

  # Replay Configuration
  replay:
    enabled: true
    max_replay_speed: 100
    max_concurrent_replays: 10

  # Monitoring Configuration
  monitoring:
    enabled: true
    metrics_interval_seconds: 60
    log_level: "INFO"
```

### D.2 Environment-Specific Configuration

**Development:**
```yaml
event_platform:
  event_bus:
    provider: "memory"
  persistence:
    provider: "sqlite"
  delivery:
    max_retries: 1
```

**Production:**
```yaml
event_platform:
  event_bus:
    provider: "kafka"
    brokers:
      - "kafka-1:9092"
      - "kafka-2:9092"
      - "kafka-3:9092"
  persistence:
    provider: "postgresql"
    connection_string: "${DATABASE_URL}"
  delivery:
    max_retries: 3
  monitoring:
    enabled: true
```

---

## Appendix E: Event Platform Checklist

Use this checklist to verify Event Platform implementation completeness.

### E.1 Core Functionality

- [ ] Event Bus implemented
- [ ] Event Schema Registry implemented
- [ ] Event Persistence implemented
- [ ] Event Replay Engine implemented
- [ ] Dead Letter Queue implemented
- [ ] Event Routing implemented
- [ ] Event Publication implemented
- [ ] Event Subscription implemented
- [ ] Event Validation implemented
- [ ] Event Filtering implemented
- [ ] Event Ordering implemented
- [ ] Event Correlation implemented

### E.2 Delivery Guarantees

- [ ] At-most-once delivery implemented
- [ ] At-least-once delivery implemented
- [ ] Exactly-once delivery implemented
- [ ] Retry logic implemented
- [ ] Circuit breaker implemented
- [ ] Fallback strategies implemented

### E.3 Event Management

- [ ] Event history maintained
- [ ] Event queries supported
- [ ] Event aggregation supported
- [ ] Event export supported
- [ ] Event archival implemented
- [ ] Event retention enforced

### E.4 Monitoring and Observability

- [ ] Event metrics collected
- [ ] Event logs emitted
- [ ] Event traces created
- [ ] DLQ alerts configured
- [ ] Performance monitoring enabled
- [ ] Health checks implemented

### E.5 Integration

- [ ] Kernel integration complete
- [ ] Runtime integration complete
- [ ] Platform Engine integration complete
- [ ] Shared Platform Service integration complete
- [ ] External system integration complete

### E.6 Documentation

- [ ] Event catalog documented
- [ ] Event schemas documented
- [ ] API documentation complete
- [ ] Integration guides complete
- [ ] Operational runbooks complete

### E.7 Testing

- [ ] Unit tests complete
- [ ] Integration tests complete
- [ ] Performance tests complete
- [ ] Failure scenario tests complete
- [ ] Replay tests complete
- [ ] DLQ tests complete

### E.8 Operations

- [ ] Deployment guides complete
- [ ] Monitoring dashboards created
- [ ] Alert rules configured
- [ ] Runbooks documented
- [ ] Backup/restore procedures documented
- [ ] Disaster recovery plan documented

---

**END OF DOCUMENT**

**Document Control:**
- **Version:** 1.0
- **Status:** Frozen
- **Phase:** 4.1
- **Author:** AutoForge AI Architecture Team
- **Reviewers:** Platform Team, Infrastructure Team, Security Team
- **Approval:** Architecture Review Board

**Change History:**
- 2026-02-08: Initial version — Phase 4.1 deliverable

**Next Review:** Phase 4.3 validation