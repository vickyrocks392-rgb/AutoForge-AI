"""
Shared enumerations for the AutoForge AI platform.

These enums define the canonical set of allowed values used across
all domain models. They replace stringly-typed fields with strict,
validated constants.
"""

from enum import Enum


class TaskStatus(str, Enum):
    """The lifecycle status of a task within a project."""

    PENDING = "pending"
    """Task has been created but is not yet ready to execute."""

    READY = "ready"
    """All dependencies are satisfied; task is ready to execute."""

    RUNNING = "running"
    """Task is currently being executed."""

    PAUSED = "paused"
    """Task execution has been paused (e.g. waiting for input)."""

    COMPLETED = "completed"
    """Task has finished successfully."""

    FAILED = "failed"
    """Task has finished with an error."""

    CANCELLED = "cancelled"
    """Task was cancelled before completion."""

    BLOCKED = "blocked"
    """Task is blocked by an unresolved dependency or condition."""


class TaskPriority(str, Enum):
    """Priority level for scheduling and resource allocation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewStatus(str, Enum):
    """The status of a quality review."""

    PENDING = "pending"
    """Review has been requested but not yet started."""

    IN_PROGRESS = "in_progress"
    """Review is currently being performed."""

    APPROVED = "approved"
    """Review has passed; the artifact/task is accepted."""

    CHANGES_REQUESTED = "changes_requested"
    """Review identified issues that need to be addressed."""

    REJECTED = "rejected"
    """Review has failed; the artifact/task is rejected."""


class ArtifactType(str, Enum):
    """The type or category of an artifact produced during execution."""

    SPECIFICATION = "specification"
    """A requirements or specification document."""

    DESIGN = "design"
    """An architecture or design document."""

    CODE = "code"
    """Source code files."""

    TEST = "test"
    """Test files or test data."""

    DOCUMENTATION = "documentation"
    """Documentation files."""

    CONFIG = "config"
    """Configuration files."""

    DATA = "data"
    """Data files (datasets, outputs, etc.)."""

    OTHER = "other"
    """Any other type of artifact."""


class EmployeeRole(str, Enum):
    """The role of an employee (AI agent or human) in the platform."""

    ARCHITECT = "architect"
    """Responsible for system architecture decisions."""

    DEVELOPER = "developer"
    """Responsible for writing code."""

    REVIEWER = "reviewer"
    """Responsible for reviewing work products."""

    TESTER = "tester"
    """Responsible for testing and quality assurance."""

    PLANNER = "planner"
    """Responsible for planning and task decomposition."""

    RESEARCHER = "researcher"
    """Responsible for research and information gathering."""

    OPERATOR = "operator"
    """Responsible for operations and monitoring."""


class ExecutionStatus(str, Enum):
    """The status of an execution session."""

    PENDING = "pending"
    """Session has been created but not yet started."""

    RUNNING = "running"
    """Session is actively executing."""

    PAUSED = "paused"
    """Session has been paused."""

    COMPLETED = "completed"
    """Session has completed successfully."""

    FAILED = "failed"
    """Session has failed with an error."""

    CANCELLED = "cancelled"
    """Session was cancelled."""

    TIMED_OUT = "timed_out"
    """Session exceeded its time limit."""


class CheckpointType(str, Enum):
    """The type or trigger for a checkpoint."""

    AUTOMATIC = "automatic"
    """Checkpoint created automatically at regular intervals."""

    MANUAL = "manual"
    """Checkpoint created manually by an operator."""

    MILESTONE = "milestone"
    """Checkpoint created at a significant milestone."""

    RECOVERY = "recovery"
    """Checkpoint created specifically for recovery purposes."""


class EventType(str, Enum):
    """The type of a domain event."""

    # Lifecycle events
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    # Execution events
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RESUMED = "resumed"

    # Review events
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"

    # Quality gate events
    GATE_PASSED = "gate_passed"
    GATE_FAILED = "gate_failed"
    GATE_WARNING = "gate_warning"

    # Checkpoint events
    CHECKPOINT_CREATED = "checkpoint_created"
    CHECKPOINT_RESTORED = "checkpoint_restored"

    # Artifact events
    ARTIFACT_PRODUCED = "artifact_produced"
    ARTIFACT_UPDATED = "artifact_updated"

    # System events
    SYSTEM_EVENT = "system_event"
    ERROR = "error"
    WARNING = "warning"


class ModelProvider(str, Enum):
    """The AI model provider."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    CUSTOM = "custom"


class MemoryType(str, Enum):
    """The type of memory entry."""

    EPISODIC = "episodic"
    """Memory of specific events or experiences."""

    SEMANTIC = "semantic"
    """Memory of facts, concepts, and knowledge."""

    PROCEDURAL = "procedural"
    """Memory of how to perform tasks and processes."""


class KnowledgeEdgeType(str, Enum):
    """The type of relationship between two knowledge nodes."""

    DEPENDS_ON = "depends_on"
    """Node A depends on Node B."""

    PRODUCES = "produces"
    """Node A produces Node B."""

    REQUIRES = "requires"
    """Node A requires Node B."""

    RELATES_TO = "relates_to"
    """Node A is related to Node B (generic)."""

    IMPLEMENTS = "implements"
    """Node A implements Node B."""

    EXTENDS = "extends"
    """Node A extends Node B."""


class QualityGateStatus(str, Enum):
    """The status of a quality gate check."""

    PENDING = "pending"
    """Quality gate check has not yet been performed."""

    PASSING = "passing"
    """Quality gate check passed successfully."""

    WARNING = "warning"
    """Quality gate check passed with warnings."""

    FAILING = "failing"
    """Quality gate check failed."""

    ERROR = "error"
    """Quality gate check encountered an error."""