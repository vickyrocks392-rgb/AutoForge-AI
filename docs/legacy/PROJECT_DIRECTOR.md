# Project Director

## Purpose

The Project Director is the platform-level orchestration component responsible for monitoring overall project health, detecting drift, managing scope, and coordinating long-running execution. It is NOT an LLM — it is a deterministic orchestration component that observes, analyzes, and acts based on structured data from the execution system.

## Responsibilities

- **Health Monitoring** — Continuously assess project health across all dimensions (progress, quality, budget, timeline)
- **Scope Drift Detection** — Detect when generated output deviates from original requirements or when new requirements are implicitly introduced
- **Architecture Drift Detection** — Detect when generated code or design deviates from the approved architecture
- **Progress Monitoring** — Track completion percentage, critical path status, and milestone achievement
- **Replanning Trigger** — Initiate replanning when drift, failure, or scope change exceeds thresholds
- **Budget Monitoring** — Track token spend, API costs, and compute usage against allocated budget
- **Execution Time Monitoring** — Track wall-clock time against estimated duration and escalate on overruns
- **Coordination** — Act as the central coordinator for long-running execution sessions

## Design Goals

1. **Zero-LLM Dependency** — The Project Director must operate without LLM calls. All decisions are based on structured metrics and deterministic rules.
2. **Stateless Observation** — The Director reads state but does not own state. It observes and recommends, but the execution system acts.
3. **Configurable Policies** — All thresholds, escalation paths, and intervention strategies are configurable per project.
4. **Minimal Intervention** — The Director only intervenes when thresholds are exceeded. Normal execution proceeds without its involvement.

## Core Concepts

### Health Dimensions

| Dimension | Metrics | Threshold Example |
|---|---|---|
| **Progress Health** | Tasks completed vs. planned, critical path status | < 80% of expected progress at checkpoint |
| **Quality Health** | Test pass rate, lint errors, validation failures | > 5% test failure rate |
| **Budget Health** | Token spend vs. allocated, cost per task | > 90% of budget consumed at 50% progress |
| **Timeline Health** | Elapsed time vs. estimated, per-stage duration | > 120% of estimated duration |
| **Scope Health** | Task count growth, requirement changes | > 10% increase in task count since baseline |
| **Architecture Health** | Component count, dependency structure changes | New component without architectural approval |

### Drift Types

| Drift Type | Detection Method | Action |
|---|---|---|
| **Scope Drift** | Compare task graph against original requirements | Flag for human review, trigger replanning |
| **Architecture Drift** | Compare generated component structure against architecture spec | Flag for architect review, block dependent tasks |
| **Quality Drift** | Monitor test pass rates and validation results | Adjust quality gate thresholds, trigger remediation |
| **Budget Drift** | Track spend rate against allocation | Switch to cheaper model tier, pause non-critical tasks |
| **Timeline Drift** | Compare actual vs. estimated duration | Reprioritize tasks, allocate more workers, notify human |

## Major Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Project Director                         │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │  Health Monitor  │    │  Drift Detector              │   │
│  │  ┌────────────┐  │    │  ┌──────────┐ ┌───────────┐ │   │
│  │  │ Progress   │  │    │  │ Scope    │ │Architecture│ │   │
│  │  ├────────────┤  │    │  ├──────────┤ ├───────────┤ │   │
│  │  │ Quality    │  │    │  │ Budget   │ │ Timeline  │ │   │
│  │  ├────────────┤  │    │  └──────────┘ └───────────┘ │   │
│  │  │ Budget     │  │    └──────────────────────────────┘   │
│  │  ├────────────┤  │                                        │
│  │  │ Timeline   │  │    ┌──────────────────────────────┐   │
│  │  └────────────┘  │    │  Policy Engine               │   │
│  └──────────────────┘    │  ┌──────────┐ ┌───────────┐ │   │
│                          │  │ Threshold│ │Escalation │ │   │
│  ┌──────────────────┐    │  ├──────────┤ ├───────────┤ │   │
│  │  Action Router   │    │  │Replanning│ │ Notification│ │   │
│  │  (recommend)     │    │  └──────────┘ └───────────┘ │   │
│  └──────────────────┘    └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Health Monitor
Periodically evaluates all health dimensions by querying the State Manager and aggregating metrics. Produces a health score (0.0–1.0) for each dimension and an overall project health score.

### Drift Detector
Compares current state against baselines (original requirements, approved architecture, budget allocation, timeline estimates). Computes drift vectors and classifies severity.

### Policy Engine
Evaluates health and drift data against configurable policies. Determines whether intervention is required and what action to take.

### Action Router
Translates policy decisions into structured recommendations sent to the execution system. Actions include: notify human, trigger replanning, adjust priorities, pause execution, switch model tier.

## Inputs

- Project state from State Manager (progress, task statuses, queue states)
- Quality metrics from Quality Gates
- Budget data from Model Router (token spend, costs)
- Timeline data from Scheduler and Execution Engine
- Baseline data (original requirements, approved architecture, allocated budget)

## Outputs

- Health reports (periodic snapshots of all health dimensions)
- Drift alerts (notifications when drift exceeds thresholds)
- Replanning requests (structured requests to the Planner service)
- Escalation notifications (to human operators)
- Configuration adjustments (priority changes, model tier changes)

## Interactions

| Component | Interaction |
|---|---|
| **State Manager** | Reads project and task state for health evaluation |
| **Scheduler** | Recommends priority adjustments, receives timeline data |
| **Execution Engine** | Receives pause/resume commands, monitors execution duration |
| **Planner Service** | Sends replanning requests with drift context |
| **Quality Gates** | Receives quality metrics for health evaluation |
| **Model Router** | Receives budget data, recommends model tier changes |
| **Event Bus** | Publishes health reports and drift alerts |
| **Human Interface** | Sends escalation notifications and health summaries |

## Failure Modes

| Failure Mode | Impact | Mitigation |
|---|---|---|
| **Stale Data** | Director acts on outdated state | Implement staleness thresholds; skip evaluation if data is too old |
| **Policy Misconfiguration** | Incorrect interventions | Validate policy changes against previous outcomes; require human approval for policy changes |
| **Replanning Loop** | Continuous replanning without progress | Implement cooldown period between replanning triggers; escalate to human after N replans |
| **Health Monitor Overload** | Director consumes excessive resources | Limit evaluation frequency; use incremental health computation |

## Observability

- Health score time series for all dimensions
- Drift detection events with drift vectors
- Policy evaluation decisions with rationale
- Action router decisions with expected outcomes
- All Director outputs are published as events on the Event Bus

## Security Considerations

- The Director reads state but does not write state directly — it only sends recommendations
- Policy configuration is validated before activation
- Human escalation notifications include full context for informed decision-making
- All Director actions are logged in the audit trail

## Scalability Considerations

- The Director operates per-project; multiple projects scale horizontally
- Health evaluation is O(n) where n is the number of tasks — acceptable for thousands of tasks
- Drift detection uses baseline comparison, not historical analysis — constant time per evaluation
- The Director is stateless and can be restarted without data loss

## Future Implementation Notes

- The Director should support custom health dimensions via a plugin interface
- Machine learning could be applied to predict health degradation before it occurs
- The Director could support automated remediation for known drift patterns
- Health reports should be visualizable in the web UI

## Open Questions

- Should the Director have authority to pause execution autonomously, or should it always require human confirmation?
- How should the Director handle conflicting health signals (e.g., good progress but poor quality)?
- Should the Director maintain a history of its own decisions for retrospective analysis?
- How should the Director handle projects with no clear baseline (e.g., open-ended exploration)?
- Should the Director support multi-project portfolio management?