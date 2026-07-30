# AutoForge AI Kernel

**Executive Orchestrator for the AutoForge AI Platform**

## Overview

The Kernel is the single entry point for all platform requests and the central coordination layer that transforms user intent into completed software engineering projects. It is the executive orchestrator that determines how each request is executed.

## Architecture

The Kernel implements a clean, modular architecture with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Kernel                                │
│  (Executive Orchestrator - Single Entry Point)               │
└───────────────────────────┬─────────────────────────────────┘
                             │ coordinates
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Platform Engines                          │
│  (Own engineering capabilities)                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Strategic  │  │   Workflow   │  │  Execution   │      │
│  │    Engine    │  │    Engine    │  │    Engine    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Review    │  │   Learning   │  │     ...      │      │
│  │    Engine    │  │    Engine    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                             │ execute
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Engineering Loops                         │
│  (Bounded workflow implementations)                          │
└─────────────────────────────────────────────────────────────┘
```

## Core Responsibilities

The Kernel owns the following responsibilities:

### 1. Request Management
- **Receive requests** — Accept user requests through all supported interfaces
- **Validate requests** — Verify request completeness, clarity, and feasibility
- **Normalize requests** — Transform diverse request formats into canonical representation
- **Assign execution identifiers** — Generate unique project IDs, workflow IDs, and correlation IDs
- **Initialize runtime state** — Create initial project state in the Runtime State Manager
- **Publish execution events** — Emit `project.created` and `project.started` events

### 2. Intent Understanding
- **Analyze user intent** — Determine what the user wants to achieve
- **Classify request type** — Identify whether the request requires research, implementation, review, deployment, or a combination
- **Determine execution path** — Select the appropriate engineering loops and services to invoke
- **Extract constraints** — Identify budget, timeline, quality, and compliance constraints
- **Identify approval requirements** — Determine where human approval gates are needed

### 3. Planning Coordination
- **Coordinate strategic planning** — Invoke Strategic Engine to produce strategic plan
- **Coordinate execution planning** — Invoke Workflow Engine to produce executable workflow
- **Validate planning outputs** — Ensure strategic plan and executable workflow are complete and consistent
- **Persist planning outputs** — Store strategic plan and executable workflow in state
- **Monitor project progress** — Track overall progress against the executable workflow
- **Request replanning** — Invoke Workflow Engine for replanning when execution conditions change

### 4. Orchestration Decisions
- **Review platform engine outputs** — Evaluate strategic plans and executable workflows
- **Coordinate loop execution** — Invoke and monitor Engineering Loops through Execution Engine
- **Coordinate worker dispatch** — Review worker assignments from Workflow Engine
- **Coordinate model selection** — Request model routing from Model Router
- **Set orchestration policies** — Configure retry, recovery, and approval policies
- **Monitor execution** — Track progress and detect condition changes
- **Request replanning** — Invoke Workflow Engine when execution conditions change

### 5. Infrastructure Coordination
- **Coordinate Shared Platform Services** — Invoke infrastructure services at appropriate points in the lifecycle
- **Manage service lifecycles** — Ensure services are initialized, used, and cleaned up correctly
- **Orchestrate service interactions** — Coordinate data flow between services
- **Maintain service contracts** — Ensure all service interactions conform to documented contracts

### 6. Lifecycle Management
- **Coordinate execution order** — Manage the sequence of Platform Engine and Engineering Loop execution
- **Coordinate engine handoffs** — Ensure clean transitions between Platform Engines
- **Coordinate shared platform services** — Integrate infrastructure services into the execution flow
- **Monitor project progress** — Track status, timing, and quality metrics
- **Coordinate retries** — Manage retry logic across all loops and workers
- **Coordinate recovery** — Orchestrate failure recovery and checkpoint restoration
- **Coordinate cancellation** — Manage graceful shutdown and resource cleanup
- **Coordinate completion** — Finalize projects and trigger post-completion activities

## What the Kernel Does NOT Do

The Kernel explicitly does NOT perform engineering work:

- **Implementation** — The Kernel never writes code, creates configurations, or produces artifacts
- **Research** — The Kernel never performs technical research or documentation research
- **Architecture design** — The Kernel never designs system architecture or makes technical design decisions
- **Coding** — The Kernel never writes source code
- **Testing** — The Kernel never executes tests or validates code quality
- **Review** — The Kernel never evaluates artifacts against quality criteria
- **Deployment** — The Kernel never deploys applications or manages infrastructure

## Package Structure

```
packages/kernel/src/autoforge_kernel/
├── __init__.py              # Package exports
├── interfaces.py            # All interfaces and contracts
├── kernel.py                # Main Kernel class
├── kernel_factory.py        # Factory for creating Kernel instances
├── request_intake.py        # Request validation, normalization, project initialization
├── intent_analysis.py       # Intent understanding and request classification
├── planning_coordination.py # Strategic and execution planning coordination
├── orchestration.py         # Engineering loop orchestration and worker dispatch
├── infrastructure.py        # Shared Platform Services coordination
├── recovery.py              # Failure detection and recovery coordination
├── approval.py              # Human approval gate management
├── completion.py            # Completion validation and finalization
└── lifecycle.py             # Runtime and project lifecycle coordination
```

## Public Interfaces

The Kernel exposes the following public interfaces:

### Request Intake Interface
```python
async def submit_request(request: Request) -> dict[str, Any]:
    """
    Submit a request to the Kernel.
    
    Returns:
        - project_id: Unique identifier for the initiated project
        - status: Initial project status
        - estimated_duration: Estimated time to completion
        - estimated_cost: Estimated cost in tokens/currency
    """
```

### Status Query Interface
```python
async def get_status(project_id: uuid.UUID) -> dict[str, Any]:
    """
    Get the current status of a project.
    
    Returns:
        - status: Current project status
        - progress: Completion percentage
        - current_phase: Current execution phase
        - active_tasks: Currently executing tasks
        - estimated_completion: Estimated completion time
        - metrics: Execution metrics (cost, duration, token usage)
    """
```

### Control Interface
```python
async def pause(project_id: uuid.UUID, reason: str) -> None
async def resume(project_id: uuid.UUID) -> None
async def cancel(project_id: uuid.UUID, reason: str) -> None
```

### Approval Interface
```python
async def submit_approval_decision(
    approval_id: uuid.UUID,
    decision: str,
    feedback: str | None = None,
    modifications: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Submit a human approval decision.
    
    Args:
        approval_id: The approval request identifier
        decision: approved, rejected, or modified
        feedback: Optional human feedback
        modifications: Optional modifications to the plan
    
    Returns:
        - status: Updated project status
        - next_actions: Actions to be taken based on decision
    """
```

## Usage

### Creating a Kernel Instance

```python
from autoforge_kernel import create_kernel

# Create a Kernel with default implementations
kernel = create_kernel()

# Or create a Kernel with custom implementations
kernel = create_kernel(
    runtime_state_manager=my_state_manager,
    event_bus=my_event_bus,
    strategic_engine=my_strategic_engine,
    workflow_engine=my_workflow_engine,
    execution_engine=my_execution_engine,
    config={"max_concurrent_projects": 10}
)
```

### Submitting a Request

```python
from autoforge_kernel import Request
import uuid

# Create a request
request = Request(
    user_id=uuid.uuid4(),
    request_text="Build a REST API for user management",
    context={"framework": "fastapi", "database": "postgresql"},
    configuration={"language": "python", "deployment_target": "aws"}
)

# Submit the request
result = await kernel.submit_request(request)
project_id = result["project_id"]
```

### Querying Status

```python
# Get project status
status = await kernel.get_status(project_id)
print(f"Project status: {status['status']}")
print(f"Progress: {status['progress']}%")
```

### Controlling Execution

```python
# Pause a project
await kernel.pause(project_id, reason="User requested pause")

# Resume a project
await kernel.resume(project_id)

# Cancel a project
await kernel.cancel(project_id, reason="User cancelled")
```

### Managing Approvals

```python
# Submit approval decision
result = await kernel.submit_approval_decision(
    approval_id=approval_id,
    decision="approved",
    feedback="Looks good, proceed with implementation"
)
```

## Design Principles

The Kernel adheres to the following architectural principles:

### 1. Separation of Concerns
The Kernel owns orchestration. Every other component owns execution. This separation is absolute and non-negotiable.

### 2. Single Responsibility
The Kernel has one responsibility: orchestrate the transformation of user intent into completed software.

### 3. Interface First
The Kernel defines explicit interfaces for all interactions with other components. These interfaces are contracts that both the Kernel and the component adhere to.

### 4. No Circular Dependencies
The Kernel may depend on infrastructure services, but infrastructure services never depend on the Kernel.

### 5. Event-Driven Communication
The Kernel communicates with components through events, not direct invocations.

### 6. State-Driven Coordination
The Kernel coordinates through state transitions, not imperative commands.

### 7. Loose Coupling
The Kernel depends on contracts, not implementations.

### 8. High Cohesion
All orchestration logic resides in the Kernel.

### 9. Idempotency
All Kernel operations are idempotent.

### 10. Observability
Every Kernel operation is observable.

## Dependencies

The Kernel depends on the following packages:

- **autoforge-models** — Domain models and base classes
- **autoforge-events** — Event models and types
- **autoforge-runtime** — Runtime state management

## Implementation Notes

### Interface-Based Design

All dependencies are defined as interfaces (abstract base classes). This enables:
- Loose coupling
- Independent evolution
- Testability
- Clean abstractions

### Dependency Injection

All dependencies are injected into the Kernel and its components. This enables:
- Easy testing with mock implementations
- Flexible configuration
- Runtime component swapping

### Event-Driven Architecture

The Kernel communicates with other components primarily through events. This enables:
- Decoupling
- Asynchronous communication
- Replayability
- Observability

### State-Driven Coordination

The Kernel coordinates through state transitions. This enables:
- Loose coupling
- Recoverability
- Observability
- Replayability

## Extension Points

The Kernel is designed to accommodate future extensions:

- **New Engineering Loops** — Add new loop types by implementing the loop interface
- **New Workers** — Add new worker types by implementing the worker protocol
- **New Infrastructure Services** — Add new services by implementing the service interface
- **New Connector Types** — Add new connectors by implementing the connector interface
- **New Model Providers** — Add new providers by registering with the Model Router
- **New Approval Policies** — Add new policies by implementing the policy interface
- **New Scheduling Strategies** — Add new strategies by implementing the strategy interface

## Testing

The Kernel is designed for testability:

- All dependencies are interfaces that can be mocked
- All components are independent and testable in isolation
- The Kernel factory enables easy test setup
- Event publishing can be intercepted for verification
- State transitions can be verified

## License

MIT License

## Version

0.1.0

## Status

Phase 2.2 — Kernel Implementation (In Progress)