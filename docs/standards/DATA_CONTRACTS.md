# Data Contracts

## Purpose

This document defines the canonical data contracts for all platform entities in the AutoForge AI system. These contracts establish the shared vocabulary and structure that all components use to communicate. They are not language-specific implementations — they are conceptual contracts that define what data is required, what is optional, and how entities relate to each other.

## Scope

This document covers the purpose, required fields, optional fields, relationships, lifecycle, ownership, and versioning strategy for each platform entity. It does not cover database schemas, API definitions, or language-specific types.

---

## Versioning Strategy

All data contracts follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** — Breaking change (field removed, required field added, type changed)
- **MINOR** — Non-breaking addition (optional field added, new relationship)
- **PATCH** — Clarification or documentation change

Contracts are versioned independently. The version is included in every event and stored with every entity record.

---

## Naming Conventions

- Entity names: PascalCase (e.g., `ExecutionSession`, `ToolInvocation`)
- Field names: camelCase (e.g., `projectId`, `createdAt`)
- Enum values: UPPER_SNAKE_CASE (e.g., `PENDING`, `RUNNING`, `COMPLETED`)
- Relationship names: snake_case (e.g., `produces`, `depends_on`)
- All identifiers: UUID v4

---

## Contracts

### Project

**Purpose:** Represents a software engineering project from inception to completion. The top-level entity that contains all other entities.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `projectId` | UUID | Globally unique identifier |
| `title` | String | Human-readable project name |
| `status` | Enum | `CREATED`, `PLANNING`, `EXECUTING`, `PAUSED`, `COMPLETED`, `FAILED`, `CANCELLED` |
| `createdAt` | Timestamp | When the project was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `description` | Text | Detailed project description |
| `config` | JSON | Project configuration (language, framework, deployment target) |
| `taskGraphId` | UUID | Reference to the current task graph |
| `currentCheckpointId` | UUID | Most recent checkpoint |
| `taskCount` | Integer | Total number of tasks |
| `completedCount` | Integer | Completed task count |
| `failedCount` | Integer | Failed task count |
| `progress` | Float | Overall progress (0.0–1.0) |
| `estimatedDuration` | Duration | Estimated total execution time |
| `actualDuration` | Duration | Actual elapsed execution time |
| `estimatedCost` | Float | Estimated total cost in USD |
| `actualCost` | Float | Actual total cost in USD |
| `startedAt` | Timestamp | When execution started |
| `completedAt` | Timestamp | When execution completed |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Contains many `Task` entities
- Contains many `Artifact` entities
- Contains many `ExecutionSession` entities
- Contains one `TaskGraph` (current version)
- Contains many `Checkpoint` entities
- Contains many `Event` entities
- Contains many `Review` entities
- Contains many `KnowledgeNode` and `KnowledgeEdge` entities

**Lifecycle:** Created → Planning → Executing → Completed/Failed/Cancelled. Can transition to Paused from Executing. Can transition back to Planning for replanning.

**Ownership:** Created by the API Gateway. Owned by the Project Director during execution. Archived by the Persistence Plane after completion.

---

### Task

**Purpose:** Represents a single unit of work assigned to an AI agent service. The fundamental execution unit.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `taskId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `title` | String | Human-readable short description |
| `owner` | String | AI agent service responsible (e.g., `planner`, `backend`) |
| `status` | Enum | `CREATED`, `QUEUED`, `ASSIGNED`, `RUNNING`, `WAITING`, `BLOCKED`, `REVIEW`, `COMPLETED`, `FAILED`, `RETRYING`, `CANCELLED`, `ARCHIVED` |
| `createdAt` | Timestamp | When the task was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `description` | Text | Detailed description |
| `department` | String | Logical group (e.g., `planning`, `generation`, `testing`) |
| `priority` | Enum | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `dependencies` | List[UUID] | Task IDs that must complete first |
| `estimatedCost` | Float | Estimated token cost in USD |
| `actualCost` | Float | Actual token cost |
| `estimatedDuration` | Duration | Estimated execution time |
| `actualDuration` | Duration | Actual execution time |
| `maxRetries` | Integer | Maximum retry attempts |
| `retryCount` | Integer | Current retry attempt |
| `confidence` | Float | Agent confidence score (0.0–1.0) |
| `checkpointId` | UUID | Last checkpoint reference |
| `input` | JSON | Structured input data |
| `output` | JSON | Structured output data |
| `assignedWorker` | String | Worker slot executing this task |
| `assignedModel` | String | LLM model being used |
| `lastHeartbeat` | Timestamp | Last progress signal |
| `startedAt` | Timestamp | When execution began |
| `completedAt` | Timestamp | When execution completed |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Belongs to one `Project`
- Depends on zero or more `Task` entities (dependencies)
- Is depended on by zero or more `Task` entities (dependents)
- Produces zero or more `Artifact` entities
- Consumes zero or more `Artifact` entities
- Contains zero or more `Event` entries
- Contains zero or more `ToolInvocation` entries
- Contains zero or more `Review` entries
- Contains one `ExecutionSession` (if running)

**Lifecycle:** See TASK_MODEL.md for the complete state machine.

**Ownership:** Created by the Planner service. Owned by the Scheduler during queuing. Owned by the Execution Engine during execution. Archived by the Persistence Plane after terminal state.

---

### Artifact

**Purpose:** Represents any output produced during project execution — code, documentation, diagrams, schemas, reports, logs.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `artifactId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `taskId` | UUID | Task that produced this artifact |
| `artifactType` | Enum | `REQUIREMENTS`, `ARCHITECTURE`, `DIAGRAM`, `DATABASE_SCHEMA`, `API_SPEC`, `UI_DESIGN`, `SOURCE_CODE`, `TEST`, `DOCUMENTATION`, `DEPLOYMENT_REPORT`, `LOG` |
| `version` | Integer | Version number (monotonically increasing) |
| `contentHash` | String | SHA-256 hash of content |
| `status` | Enum | `CREATED`, `DRAFT`, `REVIEWED`, `APPROVED`, `DEPRECATED`, `ARCHIVED` |
| `createdAt` | Timestamp | When the artifact was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `title` | String | Human-readable name |
| `description` | Text | Description of the artifact |
| `owner` | String | Agent service or human that created it |
| `parentArtifactIds` | List[UUID] | Artifacts consumed as input |
| `childArtifactIds` | List[UUID] | Artifacts derived from this one |
| `metadata` | JSON | Type-specific metadata |
| `size` | Integer | Size in bytes |
| `mimeType` | String | MIME type |
| `storagePath` | String | Path in object storage |
| `reviewId` | UUID | Associated review (if reviewed) |
| `gateResults` | List[GateResult] | Quality gate evaluation results |
| `deprecatedAt` | Timestamp | When deprecated |
| `archivedAt` | Timestamp | When archived |

**Relationships:**
- Belongs to one `Project`
- Produced by one `Task`
- Consumed by zero or more `Task` entities
- Has zero or more parent `Artifact` entities
- Has zero or more child `Artifact` entities
- Has zero or one `Review`
- Has zero or more `QualityGate` results

**Lifecycle:** Created → Draft → Reviewed → Approved → Deprecated → Archived. Can transition from Draft back to Draft for revision.

**Ownership:** Created by the Execution Engine (via agent output). Owned by the Artifact Manager. Reviewed by the Review System. Archived by the Persistence Plane.

---

### Checkpoint

**Purpose:** Represents a point-in-time snapshot of execution state for recovery and audit.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `checkpointId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `timestamp` | Timestamp | When the checkpoint was created |
| `stateHash` | String | Hash of captured state for integrity |
| `taskCount` | Integer | Number of tasks in checkpoint |
| `runningTaskCount` | Integer | Number of running tasks |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `version` | Integer | Checkpoint schema version |
| `parentCheckpointId` | UUID | Previous checkpoint in chain |
| `trigger` | Enum | `TIME_BASED`, `TASK_BASED`, `MANUAL`, `SHUTDOWN` |
| `data` | JSON | Serialized state data |
| `size` | Integer | Size in bytes |
| `duration` | Duration | Time to create checkpoint |
| `valid` | Boolean | Whether validation passed |
| `storagePath` | String | Path in object storage |

**Relationships:**
- Belongs to one `Project`
- References many `Task` states
- References one `TaskGraph` version
- References one `ExecutionSession` state
- Has zero or one parent `Checkpoint`

**Lifecycle:** Created → Validated → Stored → (optionally) Restored. Checkpoints are immutable after creation.

**Ownership:** Created by the Checkpoint Manager. Stored by the Persistence Plane. Restored by the Failure Recovery system.

---

### ExecutionSession

**Purpose:** Represents a single execution session for an AI agent — the period during which an agent is actively processing a task.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `sessionId` | UUID | Globally unique identifier |
| `taskId` | UUID | Task being executed |
| `projectId` | UUID | Parent project |
| `employee` | String | AI agent service name |
| `status` | Enum | `CREATED`, `ACTIVE`, `PAUSED`, `COMPLETED`, `FAILED`, `INTERRUPTED` |
| `startedAt` | Timestamp | When the session started |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `model` | String | LLM model used |
| `provider` | String | LLM provider |
| `inputTokens` | Integer | Tokens consumed in input |
| `outputTokens` | Integer | Tokens produced in output |
| `cost` | Float | Session cost in USD |
| `duration` | Duration | Session duration |
| `contextWindow` | Integer | Context window size used |
| `toolCalls` | Integer | Number of tool invocations |
| `conversationHistory` | JSON | Agent conversation history |
| `intermediateResults` | JSON | Partial results if interrupted |
| `checkpointIds` | List[UUID] | Checkpoints saved during session |
| `error` | JSON | Error information if failed |
| `completedAt` | Timestamp | When the session ended |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Belongs to one `Task`
- Belongs to one `Project`
- Contains zero or more `ToolInvocation` entries
- Contains zero or more `Event` entries
- References zero or more `Checkpoint` entries
- References one `ModelProfile`

**Lifecycle:** Created → Active → Completed/Failed/Interrupted. Can transition to Paused from Active. Can transition back to Active from Paused.

**Ownership:** Created by the Execution Engine. Owned by the Agent Runner during execution. Archived after completion.

---

### Employee

**Purpose:** Represents an AI agent service — an "AI employee" with a specific role and capabilities.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `employeeId` | String | Unique name (e.g., `planner`, `backend`) |
| `displayName` | String | Human-readable name |
| `role` | String | Role description |
| `status` | Enum | `ACTIVE`, `DEGRADED`, `OFFLINE`, `MAINTENANCE` |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `capabilities` | List[String] | List of capabilities |
| `department` | String | Logical department |
| `defaultModel` | String | Default LLM model |
| `supportedModels` | List[String] | Models this employee can use |
| `maxConcurrency` | Integer | Maximum concurrent tasks |
| `currentLoad` | Integer | Currently assigned tasks |
| `totalTasksCompleted` | Integer | Lifetime task count |
| `totalCost` | Float | Lifetime cost |
| `averageConfidence` | Float | Average confidence score |
| `averageDuration` | Duration | Average task duration |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Assigned to zero or more `Task` entities
- Uses zero or more `ModelProfile` entries
- Produces zero or more `Artifact` entities
- Has zero or more `ExecutionSession` entries

**Lifecycle:** Created at platform startup. Status changes based on health checks. No deletion — employees are deactivated.

**Ownership:** Defined in platform configuration. Status managed by the Execution Engine.

---

### Event

**Purpose:** Represents a significant occurrence in the system. The fundamental unit of communication on the Event Bus.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `eventId` | UUID | Globally unique identifier |
| `eventType` | String | Type from the event catalog |
| `source` | String | Component that produced the event |
| `timestamp` | Timestamp | When the event occurred |
| `projectId` | UUID | Related project |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `version` | Integer | Event schema version |
| `correlationId` | UUID | For correlating related events |
| `causationId` | UUID | Event that caused this event |
| `workflowId` | UUID | Related workflow |
| `taskId` | UUID | Related task |
| `payload` | JSON | Event-specific data |
| `metadata` | JSON | Additional metadata |

**Relationships:**
- Belongs to one `Project`
- May reference one `Task`
- May reference one `Workflow`
- May reference one `ExecutionSession`

**Lifecycle:** Created → Published → (optionally) Consumed → Archived. Events are immutable after creation.

**Ownership:** Created by any platform component. Published by the Event Bus. Stored by the Persistence Plane.

---

### Review

**Purpose:** Represents a human or automated review of an artifact.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `reviewId` | UUID | Globally unique identifier |
| `artifactId` | UUID | Artifact being reviewed |
| `projectId` | UUID | Parent project |
| `reviewerType` | Enum | `ARCHITECT`, `QA`, `SECURITY`, `PERFORMANCE`, `DOCUMENTATION`, `HUMAN` |
| `status` | Enum | `CREATED`, `ASSIGNED`, `IN_PROGRESS`, `COMPLETED`, `ESCALATED` |
| `createdAt` | Timestamp | When the review was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `reviewerId` | String | Who performed the review |
| `outcome` | Enum | `APPROVED`, `APPROVED_WITH_COMMENTS`, `CHANGES_REQUESTED`, `REJECTED`, `ESCALATED`, `SKIPPED` |
| `comments` | Text | Reviewer comments |
| `decision` | JSON | Structured decision data |
| `escalationReason` | String | Why escalated |
| `escalatedTo` | String | Who it was escalated to |
| `completedAt` | Timestamp | When review completed |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Belongs to one `Artifact`
- Belongs to one `Project`
- May be escalated to another `Review`

**Lifecycle:** Created → Assigned → In Progress → Completed/Escalated.

**Ownership:** Created by the Review System. Assigned by the Assignment Manager. Completed by the reviewer.

---

### ToolInvocation

**Purpose:** Represents a single tool call made by an AI agent during task execution.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `invocationId` | UUID | Globally unique identifier |
| `sessionId` | UUID | Parent execution session |
| `taskId` | UUID | Parent task |
| `toolName` | String | Name of the tool invoked |
| `status` | Enum | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED` |
| `startedAt` | Timestamp | When invocation started |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `input` | JSON | Tool input parameters |
| `output` | JSON | Tool output |
| `error` | JSON | Error if failed |
| `duration` | Duration | Execution duration |
| `retryCount` | Integer | Number of retries |
| `completedAt` | Timestamp | When invocation completed |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Belongs to one `ExecutionSession`
- Belongs to one `Task`

**Lifecycle:** Created → Running → Completed/Failed.

**Ownership:** Created by the Tool Executor. Archived after task completion.

---

### ModelProfile

**Purpose:** Represents an LLM model available for use by the platform.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `modelId` | String | Unique identifier (e.g., `claude-3.5-sonnet`) |
| `provider` | String | Provider name |
| `modelName` | String | Provider-specific model name |
| `tier` | Integer | Model tier (1–4) |
| `status` | Enum | `ACTIVE`, `DEGRADED`, `DEPRECATED`, `RETIRED` |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `capabilities` | List[String] | Model capabilities |
| `contextWindow` | Integer | Maximum context window |
| `costPerInputToken` | Float | Cost per 1K input tokens |
| `costPerOutputToken` | Float | Cost per 1K output tokens |
| `averageLatency` | Duration | Average response latency |
| `maxBatchSize` | Integer | Maximum batch size |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Used by zero or more `ExecutionSession` entries
- Used by zero or more `Employee` entries

**Lifecycle:** Added to registry when available. Status changes based on provider health. Retired when deprecated by provider.

**Ownership:** Maintained by the Model Router. Updated from provider API responses.

---

### MemoryEntry

**Purpose:** Represents a stored piece of context or knowledge in the Memory Engine.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `entryId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `memoryType` | Enum | `SHORT_TERM`, `LONG_TERM`, `VECTOR` |
| `key` | String | Lookup key |
| `createdAt` | Timestamp | When the entry was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `value` | JSON | Stored data |
| `embedding` | Float[] | Vector embedding (for VECTOR type) |
| `ttl` | Duration | Time-to-live (for SHORT_TERM) |
| `source` | String | What created this entry |
| `metadata` | JSON | Flexible metadata |
| `expiresAt` | Timestamp | When the entry expires |

**Relationships:**
- Belongs to one `Project`
- May reference one `Task`
- May reference one `Artifact`

**Lifecycle:** Created → Active → Expired/Deleted. SHORT_TERM entries expire via TTL. LONG_TERM entries persist until archived.

**Ownership:** Created by the Memory Engine. Managed by the Persistence Plane.

---

### KnowledgeNode

**Purpose:** Represents a node in the Knowledge Graph.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `nodeId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `nodeType` | Enum | `PROJECT`, `REQUIREMENT`, `TASK`, `ARTIFACT`, `FILE`, `COMPONENT`, `TEST`, `DEPLOYMENT`, `MODEL`, `EMPLOYEE`, `DECISION`, `QUALITY_GATE` |
| `externalId` | String | ID of the referenced entity |
| `label` | String | Human-readable label |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `description` | Text | Node description |
| `properties` | JSON | Node-specific properties |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Connected to zero or more `KnowledgeNode` entities via `KnowledgeEdge` entities
- References one external entity (Project, Task, Artifact, etc.)

**Lifecycle:** Created when the referenced entity is created. Updated when the entity is updated. Archived when the project is archived.

**Ownership:** Created by the Knowledge Graph. Synchronized with entity lifecycle events.

---

### KnowledgeEdge

**Purpose:** Represents a relationship between two nodes in the Knowledge Graph.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `edgeId` | UUID | Globally unique identifier |
| `projectId` | UUID | Parent project |
| `sourceNodeId` | UUID | Source node |
| `targetNodeId` | UUID | Target node |
| `edgeType` | Enum | `DERIVES_FROM`, `PRODUCES`, `CONSUMES`, `IMPLEMENTS`, `TESTS`, `DEPLOYS`, `ASSIGNED_TO`, `USED_MODEL`, `DEPENDS_ON`, `VALIDATED_BY`, `SUPERSEDES`, `RELATED_TO` |
| `createdAt` | Timestamp | When the edge was created |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `weight` | Float | Edge weight for relevance scoring |
| `properties` | JSON | Edge-specific properties |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Connects two `KnowledgeNode` entities
- Belongs to one `Project`

**Lifecycle:** Created when the relationship is established. Archived when either node is archived.

**Ownership:** Created by the Knowledge Graph. Synchronized with relationship events.

---

### QualityGate

**Purpose:** Represents a quality gate evaluation result for an artifact.

**Required Fields:**
| Field | Type | Description |
|---|---|---|
| `gateId` | UUID | Globally unique identifier |
| `artifactId` | UUID | Artifact evaluated |
| `projectId` | UUID | Parent project |
| `gateType` | Enum | `REQUIREMENTS`, `ARCHITECTURE`, `BACKEND`, `FRONTEND`, `DATABASE`, `TESTING`, `DOCUMENTATION`, `DEPLOYMENT` |
| `result` | Enum | `PASS`, `FAIL`, `WARNING`, `SKIPPED` |
| `evaluatedAt` | Timestamp | When the evaluation occurred |

**Optional Fields:**
| Field | Type | Description |
|---|---|---|
| `criteria` | JSON | Criteria evaluated and their results |
| `score` | Float | Overall score (0.0–1.0) |
| `failures` | List[String] | List of failed criteria |
| `warnings` | List[String] | List of warnings |
| `duration` | Duration | Evaluation duration |
| `metadata` | JSON | Flexible metadata |

**Relationships:**
- Belongs to one `Artifact`
- Belongs to one `Project`

**Lifecycle:** Created when evaluation completes. Immutable after creation.

**Ownership:** Created by the Quality Gates system. Stored by the Persistence Plane.

---

## Traceability Model

Traceability is the ability to trace any entity back to its origin and forward to its impact. The platform supports traceability through:

1. **Parent-Child Relationships** — Every entity records its parent (e.g., artifact records its source task)
2. **Event Causation** — Every event records its causation (what caused this event)
3. **Knowledge Graph** — All entities and relationships are stored in a traversable graph
4. **Audit Trail** — Every state transition is recorded with timestamp, actor, and reason

### Traceability Paths

- **Requirement → Code**: Requirement → Task → Artifact → File → Component
- **Task → Deployment**: Task → Artifact → Component → Deployment
- **Change → Impact**: Entity → Knowledge Graph traversal → Affected entities
- **Failure → Root Cause**: Failed task → Events → Tool invocations → Error details

## Audit Strategy

All audit data is:
- **Append-only** — No data is ever modified or deleted
- **Immutable** — Once written, audit entries cannot be changed
- **Timestamped** — Every entry has a precise UTC timestamp
- **Attributed** — Every entry records the actor (component or human)
- **Retained** — Audit data is retained for 7 years minimum

### Audit Events

Every state transition, decision, and human interaction produces an audit event:
- Task state transitions
- Artifact state changes
- Review decisions
- Configuration changes
- Human approvals and overrides
- System failures and recoveries

## Engineering Governance

Governance is enforced through:
1. **Quality Gates** — Automated validation at every stage
2. **Review System** — Human oversight for critical artifacts
3. **Project Director** — Health monitoring and drift detection
4. **Audit Trail** — Complete record of all actions
5. **Policy Engine** — Configurable rules and thresholds

### Governance Principles

- **Least Privilege** — Components have minimum required access
- **Separation of Duties** — No single component controls both execution and validation
- **Auditability** — Every action is recorded and attributable
- **Transparency** — All decisions are explainable and inspectable