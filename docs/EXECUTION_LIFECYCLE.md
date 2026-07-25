# Execution Lifecycle

## Purpose

This document describes the complete end-to-end execution lifecycle of an AutoForge AI project — from the moment a user submits a request to the moment the completed project is delivered. It ties together all components of the execution architecture into a coherent flow.

## Scope

This document covers the high-level lifecycle stages, the transitions between them, and the components involved at each stage. It does not repeat the detailed design of individual components — those are documented in their respective architecture documents.

---

## Lifecycle Overview

The execution lifecycle consists of nine major stages, each with distinct inputs, outputs, and responsible components.

```
User Request
     │
     ▼
┌─────────────┐
│  1. Intake  │  Validate request, create project
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  2. Plan   │  Decompose request into task graph
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  3. Graph  │  Refine tasks, resolve dependencies
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  4. Schedule│  Prioritize, queue, allocate workers
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  5. Execute │  Dispatch tasks, route models, collect results
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  6. Validate│  Verify outputs, run tests, check quality
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  7. Deploy  │  Build, package, deploy to target
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  8. Document│  Generate documentation, changelog
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  9. Complete│  Finalize, notify, archive
└─────────────┘
```

## Stage 1: Intake

**Purpose:** Validate the user's request and create the project record.

**Inputs:**
- User request (natural language or structured)
- Project configuration (language, framework, deployment target)
- Context (existing codebase, dependencies, reference materials)

**Process:**
1. Validate request completeness and clarity
2. Parse project configuration
3. Create project record in state manager
4. Publish `project.created` event
5. Transition to Planning stage

**Outputs:**
- Project record with unique ID
- Validated request payload
- Project configuration

**Responsible Components:**
- API Gateway (apps/api)
- State Manager
- Event Bus

## Stage 2: Plan

**Purpose:** Decompose the user request into a high-level plan of work items.

**Inputs:**
- Validated user request
- Project configuration
- Context materials

**Process:**
1. Planner service analyzes the request
2. Identifies SDLC phases required (research, architecture, backend, etc.)
3. Decomposes request into high-level work items
4. Estimates effort, cost, and duration for each work item
5. Produces a structured plan

**Outputs:**
- High-level plan with work items
- Estimated costs and durations
- Recommended execution order

**Responsible Components:**
- Planner Service (services/planner)
- Model Router (for LLM access)
- Event Bus (publishes planning events)

## Stage 3: Graph

**Purpose:** Refine the plan into a complete task graph with dependencies.

**Inputs:**
- High-level plan from Planner
- Service contracts for each AI agent

**Process:**
1. Decompose each work item into one or more tasks
2. Define task inputs, outputs, and success criteria
3. Identify and encode dependencies between tasks
4. Validate graph acyclicity
5. Assign tasks to appropriate agent services
6. Set task priorities and retry policies
7. Publish task graph

**Outputs:**
- Complete task graph (DAG)
- Task definitions with all fields populated
- Dependency matrix

**Responsible Components:**
- Planner Service (services/planner)
- Task Graph (conceptual component)
- State Manager (stores graph)
- Event Bus (publishes `task.created` events)

## Stage 4: Schedule

**Purpose:** Determine execution order and allocate resources.

**Inputs:**
- Task graph
- Worker pool configuration
- Scheduling strategy configuration

**Process:**
1. Perform topological sort on task graph
2. Identify parallel execution sets
3. Calculate critical path
4. Populate ready queue with root tasks
5. Apply scheduling strategy (priority, FIFO, etc.)
6. Allocate worker slots to ready tasks
7. Dispatch tasks to execution engine

**Outputs:**
- Scheduled task queue
- Worker assignments
- Execution timeline

**Responsible Components:**
- Scheduler
- State Manager (queue states)
- Event Bus (publishes `task.queued`, `task.assigned` events)

## Stage 5: Execute

**Purpose:** Execute tasks through AI agent services and collect results.

**Inputs:**
- Scheduled tasks with inputs and context
- Available worker slots
- Model registry

**Process:**
1. Receive dispatched task from scheduler
2. Route task through Model Router to select optimal LLM
3. Send task to appropriate AI agent service
4. Monitor agent execution (heartbeats, progress)
5. Handle agent responses (success, failure, partial)
6. Apply retry policies on failure
7. Save checkpoints at configured intervals
8. Publish task completion events
9. Release worker slot back to scheduler

**Outputs:**
- Task results (output, artifacts, metadata)
- Execution metrics (duration, cost, token usage)
- Checkpoint snapshots

**Responsible Components:**
- Execution Engine (packages/execution)
- Model Router
- AI Agent Services (services/*)
- Checkpoint Manager
- State Manager
- Event Bus (publishes all task lifecycle events)

## Stage 6: Validate

**Purpose:** Verify that generated outputs meet quality and correctness standards.

**Inputs:**
- Task outputs (code, configuration, documentation)
- Validation criteria (test suites, lint rules, schema validation)

**Process:**
1. Run automated validation on task outputs
2. Execute generated test suites
3. Check code quality (linting, formatting, type checking)
4. Validate against requirements specification
5. If validation fails: create remediation tasks
6. If validation passes: mark tasks as verified
7. Publish validation results

**Outputs:**
- Validation results (pass/fail, coverage, quality metrics)
- Remediation tasks (if validation failed)
- Verified artifacts

**Responsible Components:**
- Testing Service (services/testing)
- Scheduler (for remediation tasks)
- Event Bus (publishes validation events)

## Stage 7: Deploy

**Purpose:** Build, package, and deploy the generated project to the target environment.

**Inputs:**
- Verified artifacts (code, configuration, assets)
- Deployment configuration (target, credentials, environment)

**Process:**
1. Generate build configuration (Dockerfile, build scripts)
2. Build and package artifacts
3. Generate deployment manifests (Kubernetes, Docker Compose)
4. Deploy to target environment
5. Verify deployment (health checks, smoke tests)
6. Publish deployment results

**Outputs:**
- Deployed application
- Deployment URL or endpoint
- Deployment logs and metrics

**Responsible Components:**
- Deployment Service (services/deployment)
- Event Bus (publishes deployment events)

## Stage 8: Document

**Purpose:** Generate project documentation, changelog, and handoff materials.

**Inputs:**
- All task outputs and artifacts
- Execution trace and audit log
- Deployment information

**Process:**
1. Generate project README and overview
2. Generate API documentation
3. Generate architecture documentation
4. Generate changelog from execution events
5. Generate deployment and operations guide
6. Publish documentation

**Outputs:**
- Complete project documentation
- API reference
- Operations guide
- Changelog

**Responsible Components:**
- Documentation Service (services/documentation)
- Event Bus (publishes documentation events)

## Stage 9: Complete

**Purpose:** Finalize the project, notify the user, and archive execution data.

**Inputs:**
- All task results and artifacts
- Documentation
- Deployment information
- Execution metrics

**Process:**
1. Aggregate all project outputs
2. Generate project summary (duration, cost, tasks completed, quality metrics)
3. Save final checkpoint
4. Notify user of completion
5. Archive project data according to retention policy
6. Publish `project.finished` event

**Outputs:**
- Project summary report
- Final checkpoint
- User notification
- Archived project record

**Responsible Components:**
- Execution Engine
- State Manager
- Checkpoint Manager
- Event Bus

## Cross-Cutting Concerns

### Checkpointing
Checkpoints are saved throughout the lifecycle, with frequency determined by the checkpoint strategy. Critical checkpoints occur at:
- After task graph generation (Stage 3 complete)
- After each task completion (Stage 5)
- Before human approval checkpoints
- Before deployment (Stage 7)
- At project completion (Stage 9)

### Human Approval
Human approval checkpoints can be inserted at any stage. When triggered:
1. Execution pauses at the next task boundary
2. Current state is captured as a checkpoint
3. Human is notified with context and options
4. On approval: execution resumes
5. On rejection: remediation tasks are created
6. On modification: task graph is updated

### Error Recovery
At any stage, if a failure occurs:
1. Failure is classified (recoverable, non-recoverable, unknown)
2. If recoverable: retry policy is applied
3. If non-recoverable: human is notified
4. If fatal: system restores from last checkpoint

## Future Implementation Notes

- The lifecycle should support parallel execution of independent stages (e.g., documentation generation can begin before deployment completes)
- Each stage should have configurable timeouts and escalation policies
- The lifecycle should support manual stage skipping for experienced users
- Stage transitions should be observable through the event bus for real-time monitoring

## Open Questions

- Should the lifecycle support partial completion — where some stages complete successfully and others fail, and the user can choose to accept partial results?
- How should the lifecycle handle stages that are not applicable (e.g., no deployment target)?
- Should the lifecycle support user-defined custom stages?
- How should the lifecycle handle rollback — reverting to a previous stage's outputs?
- Should the lifecycle support iterative refinement — where the user can request changes after seeing results, triggering a new execution cycle?