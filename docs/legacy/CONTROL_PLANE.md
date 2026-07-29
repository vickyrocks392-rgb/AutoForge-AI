# Control Plane

## Purpose

The Control Plane is the orchestration and management layer of the AutoForge AI platform. It is responsible for all decision-making, coordination, and state management activities — determining what work to do, when to do it, and how to respond to changing conditions. The Control Plane is the "brain" of the platform.

## Responsibilities

- **Orchestration** — Coordinate the execution of workflows, tasks, and agent services
- **State Management** — Maintain authoritative state of all execution entities
- **Scheduling** — Determine execution order and resource allocation
- **Policy Enforcement** — Enforce quality gates, review policies, and governance rules
- **Health Monitoring** — Monitor system health and trigger corrective actions
- **Event Processing** — Process and route events between components
- **Human Interface** — Manage human-in-the-loop interactions

## Design Goals

1. **Stateless Decision-Making** — The Control Plane makes decisions based on current state but does not own state. State is owned by the Persistence Plane.
2. **Event-Driven** — All communication within the Control Plane is event-driven through the Event Bus.
3. **Horizontal Scalability** — Control Plane components are stateless and can be scaled horizontally.
4. **Fault Isolation** — Failure in one Control Plane component does not affect others.

## Core Concepts

### Control Plane Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Control Plane                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Orchestration Layer                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │Scheduler │  │Execution │  │  Task    │  │Project│ │   │
│  │  │          │  │ Engine   │  │  Graph   │  │Director│ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Policy Layer                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │ Quality  │  │  Review  │  │  Model   │  │Failure│ │   │
│  │  │ Gates    │  │  System  │  │  Router  │  │Recovery│ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Intelligence Layer                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │Knowledge │  │ Artifact │  │  Project         │   │   │
│  │  │ Graph    │  │ Manager  │  │  Director        │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Communication Layer                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │Event Bus │  │  Agent   │  │  Human           │   │   │
│  │  │          │  │ Protocol │  │  Interface       │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Layers

#### Orchestration Layer
The execution core — determines what work to do and manages its execution:
- **Scheduler** — Decides which tasks to run and when
- **Execution Engine** — Dispatches tasks to agents and manages execution
- **Task Graph** — Defines the DAG of work items
- **Project Director** — Monitors health and triggers interventions

#### Policy Layer
The governance core — enforces rules and standards:
- **Quality Gates** — Validate artifact quality
- **Review System** — Manage human review workflows
- **Model Router** — Select and route to LLM models
- **Failure Recovery** — Handle errors and retries

#### Intelligence Layer
The knowledge core — stores and provides context:
- **Knowledge Graph** — Model entity relationships
- **Artifact Manager** — Store and version artifacts
- **Project Director** — Monitor project health

#### Communication Layer
The connectivity core — enables component interaction:
- **Event Bus** — Asynchronous event distribution
- **Agent Protocol** — Standardized agent communication
- **Human Interface** — User-facing interaction points

## Ownership Boundaries

| Component | Owns | Does Not Own |
|---|---|---|
| **Scheduler** | Queue states, worker assignments | Task data, artifact content |
| **Execution Engine** | Task dispatch, agent sessions | Persistent state, artifact storage |
| **Quality Gates** | Gate criteria, evaluation results | Artifact content, review decisions |
| **Review System** | Review workflows, reviewer assignments | Artifact content, quality metrics |
| **Model Router** | Model selection, provider routing | Task data, execution state |
| **Knowledge Graph** | Entity relationships, graph structure | Artifact content, task data |
| **Artifact Manager** | Artifact metadata, version history | Execution state, graph relationships |
| **Project Director** | Health assessments, drift detection | Execution state, artifact content |

## Communication Between Planes

```
┌──────────────┐         Events         ┌──────────────┐
│  Control     │───────────────────────▶│  Data Plane  │
│  Plane       │◀───────────────────────│              │
│              │     State Queries       │              │
└──────────────┘                        └──────────────┘
        │                                      │
        │         State Writes                 │
        ├──────────────────────────────────────▶│
        │                                      │
        │                              ┌───────▼────────┐
        └──────────────────────────────│  Persistence   │
                                       │  Plane         │
                                       └────────────────┘
```

- **Control Plane → Data Plane**: Commands (execute task, route model, run gate)
- **Data Plane → Control Plane**: Results (task output, model response, gate report)
- **Control Plane → Persistence Plane**: State writes (task created, artifact stored)
- **Persistence Plane → Control Plane**: State reads (task state, artifact content)

## Fault Isolation

- Each Control Plane component operates independently
- Component failure does not cascade — the Event Bus buffers undelivered events
- Critical components (Scheduler, Execution Engine) have hot standbys
- Non-critical components (Project Director, Review System) can be restarted without affecting execution
- The Control Plane can operate in degraded mode with reduced functionality

## Security Considerations

- Control Plane components authenticate via service-to-service tokens
- All Control Plane communication is encrypted in transit
- Control Plane decisions are logged for audit
- Human-in-the-loop overrides are authenticated and recorded

## Scalability Considerations

- Control Plane components are stateless and scale horizontally
- The Event Bus partitions events by project for parallel processing
- State reads are cached to reduce Persistence Plane load
- Control Plane components can be deployed independently

## Future Implementation Notes

- The Control Plane should support multi-region deployment for disaster recovery
- Control Plane components should support canary deployments for safe updates
- The Control Plane should expose health and readiness endpoints for orchestration

## Open Questions

- Should the Control Plane support a "pause all" mechanism for emergency maintenance?
- How should the Control Plane handle version incompatibilities between components during rolling updates?
- Should the Control Plane support priority inversion — where a lower-priority task temporarily blocks a higher-priority task due to resource contention?