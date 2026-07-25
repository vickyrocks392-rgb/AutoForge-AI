# Knowledge Graph

## Purpose

The Knowledge Graph is the platform component that models and stores the relationships between all entities in the AutoForge AI system. It connects requirements, tasks, artifacts, files, components, tests, deployments, models, and AI employees into a traversable graph that enables impact analysis, traceability, and context retrieval.

## Responsibilities

- **Relationship Modeling** — Define and store relationships between all platform entities
- **Impact Analysis** — Enable queries that determine what is affected by a change
- **Traceability** — Provide end-to-end traceability from requirements to deployed code
- **Context Retrieval** — Supply relevant context to AI agents based on graph traversal
- **Graph Visualization** — Support graph queries for the web UI

## Design Goals

1. **Universal Connector** — Every platform entity is a node; every meaningful relationship is an edge.
2. **Bidirectional Traversal** — The graph supports forward and backward traversal for impact analysis.
3. **Temporal Awareness** — Edges have timestamps and versions to support historical queries.
4. **Weighted Relationships** — Edges can have weights for relevance scoring in context retrieval.

## Core Concepts

### Node Types

| Node Type | Description | Example |
|---|---|---|
| **Project** | A software engineering project | `project:auto-forge-api` |
| **Requirement** | A functional or non-functional requirement | `req:user-authentication` |
| **Task** | A unit of work in the execution graph | `task:design-auth-flow` |
| **Artifact** | An output produced by a task | `artifact:auth-flow-diagram` |
| **File** | A file in the generated codebase | `file:src/auth/login.ts` |
| **Component** | A logical component in the architecture | `component:auth-service` |
| **Test** | A test case or test suite | `test:auth-login-spec` |
| **Deployment** | A deployment to an environment | `deploy:staging-v1.2` |
| **Model** | An LLM model used during execution | `model:claude-3.5-sonnet` |
| **Employee** | An AI agent service | `employee:backend-service` |
| **Decision** | An architecture or design decision | `adr:use-postgresql` |
| **QualityGate** | A quality gate evaluation result | `gate:backend-v1-pass` |

### Edge Types

| Edge Type | Description | Example |
|---|---|---|
| **derives_from** | Artifact derived from requirement | `artifact:auth-flow → derives_from → req:user-auth` |
| **produces** | Task produces artifact | `task:design-auth → produces → artifact:auth-flow` |
| **consumes** | Task consumes artifact | `task:impl-auth → consumes → artifact:auth-flow` |
| **implements** | File implements component | `file:auth-service.ts → implements → component:auth-service` |
| **tests** | Test tests component or file | `test:auth-spec → tests → component:auth-service` |
| **deploys** | Deployment deploys component | `deploy:staging → deploys → component:auth-service` |
| **assigned_to** | Task assigned to employee | `task:impl-auth → assigned_to → employee:backend` |
| **used_model** | Task used model | `task:impl-auth → used_model → model:claude-3.5` |
| **depends_on** | Entity depends on another | `component:auth → depends_on → component:user-db` |
| **validated_by** | Artifact validated by gate | `artifact:auth-code → validated_by → gate:backend-v1` |
| **supersedes** | New version supersedes old | `artifact:auth-v2 → supersedes → artifact:auth-v1` |
| **related_to** | General relationship | `req:performance → related_to → req:scalability` |

### Graph Structure Example

```
                    ┌──────────────┐
                    │  Requirement │
                    │  "User Auth" │
                    └──────┬───────┘
                           │ derives_from
                    ┌──────▼───────┐
                    │   Artifact   │
                    │  Auth Design │
                    └──────┬───────┘
                           │ produces
                    ┌──────▼───────┐
                    │    Task      │
                    │  Implement   │──── assigned_to ────▶ Employee (Backend)
                    │  Auth        │
                    └──────┬───────┘
                           │ produces
                    ┌──────▼───────┐
                    │   Artifact   │
                    │  Auth Code   │
                    └──────┬───────┘
                           │ implements
                    ┌──────▼───────┐
                    │  Component   │
                    │ Auth Service │
                    └──────┬───────┘
                      ┌────┼────┐
                      │    │    │
              ┌───────▼┐ ┌─▼───┐ ┌▼────────┐
              │  File  │ │Test │ │Deploy   │
              │auth.ts │ │spec │ │staging  │
              └────────┘ └─────┘ └─────────┘
```

## Major Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Knowledge Graph                          │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │  Graph Database  │    │  Index Manager               │   │
│  │  ┌────────────┐  │    │  ┌──────────┐ ┌───────────┐ │   │
│  │  │ Node Store │  │    │  │ Node     │ │ Edge      │ │   │
│  │  ├────────────┤  │    │  │ Index    │ │ Index     │ │   │
│  │  │ Edge Store │  │    │  └──────────┘ └───────────┘ │   │
│  │  └────────────┘  │    └──────────────────────────────┘   │
│  └──────────────────┘                                        │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │  Traversal Engine│    │  Impact Analyzer             │   │
│  │  ┌────────────┐  │    │  ┌──────────┐ ┌───────────┐ │   │
│  │  │ Forward    │  │    │  │ Change   │ │ Risk      │ │   │
│  │  ├────────────┤  │    │  │ Scope    │ │ Assessment│ │   │
│  │  │ Backward   │  │    │  └──────────┘ └───────────┘ │   │
│  │  └────────────┘  │    └──────────────────────────────┘   │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### Graph Database
Stores nodes and edges in a graph-native database (or a relational store with graph query capabilities). Supports property-based filtering on both nodes and edges.

### Index Manager
Maintains indexes on node types, edge types, and properties for efficient querying. Supports full-text search on node labels and descriptions.

### Traversal Engine
Supports forward traversal (from source to dependents) and backward traversal (from target to dependencies). Supports configurable depth limits and edge type filters.

### Impact Analyzer
Uses graph traversal to determine the impact scope of a change. Given a node, identifies all downstream nodes that would be affected. Produces a risk assessment based on the number and criticality of affected nodes.

## Impact Analysis

### Change Impact
When a requirement changes, the Knowledge Graph can answer:
- Which tasks are affected?
- Which artifacts need to be regenerated?
- Which components are impacted?
- Which tests need to be re-run?
- Which deployments need to be updated?

### Failure Impact
When a task fails, the Knowledge Graph can answer:
- Which downstream tasks are blocked?
- Which artifacts are incomplete?
- Which components are missing?
- What is the critical path impact?

### Regression Impact
When a test fails, the Knowledge Graph can answer:
- Which component is being tested?
- Which requirement does the component implement?
- Which tasks produced the component?
- Which other tests might be affected?

## Inputs

- Entity creation events from all platform components
- Relationship events linking entities
- Query requests for impact analysis and context retrieval
- Graph traversal requests

## Outputs

- Impact analysis reports (affected entities, risk levels)
- Context subgraphs for AI agent prompts
- Traceability paths from requirements to deployment
- Graph visualizations for the web UI

## Interactions

| Component | Interaction |
|---|---|
| **Artifact Manager** | Receives artifact metadata for node creation |
| **State Manager** | Receives task and project state for node updates |
| **Execution Engine** | Receives task-artifact relationships for edge creation |
| **Quality Gates** | Receives gate results for validation edges |
| **Review System** | Receives review decisions for decision nodes |
| **Event Bus** | Subscribes to all entity lifecycle events |
| **Model Router** | Receives model usage data for model nodes |

## Failure Modes

| Failure Mode | Impact | Mitigation |
|---|---|---|
| **Stale Graph** | Graph does not reflect current state | Implement TTL-based refresh; publish invalidation events |
| **Missing Edges** | Impact analysis is incomplete | Implement edge validation on write; periodic graph consistency checks |
| **Graph Too Large** | Traversal is slow | Implement pagination; limit traversal depth; use summary nodes |
| **Orphan Nodes** | Nodes with no edges | Periodic cleanup; alert on orphan creation |

## Observability

- Graph size (node count, edge count) by type
- Traversal latency by query type
- Impact analysis results with scope size
- Orphan node count
- All graph mutations published to Event Bus

## Security Considerations

- The graph contains sensitive relationships (which components depend on which)
- Access control is enforced at the project level
- Graph queries are audited for compliance
- The graph does not store artifact content — only references

## Scalability Considerations

- The graph is partitioned by project for horizontal scaling
- Frequently accessed subgraphs are cached
- Traversal depth is limited to prevent runaway queries
- Indexes are maintained on all query dimensions
- Graph mutations are batched for efficiency

## Future Implementation Notes

- The Knowledge Graph should support graph embeddings for semantic context retrieval
- Impact analysis should support what-if scenarios (simulate change without applying it)
- The graph should support time-travel queries (what was the graph state at time T)
- Graph visualization should be interactive in the web UI

## Open Questions

- Should the Knowledge Graph support multiple graph databases (Neo4j, Dgraph, Amazon Neptune) via abstraction?
- How should the graph handle cyclic relationships (e.g., circular dependencies)?
- Should the graph support edge weights for relevance scoring in context retrieval?
- How should the graph handle cross-project relationships?
- Should the graph support automated relationship discovery (inferring edges from content analysis)?