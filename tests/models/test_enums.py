"""
Unit tests for shared enumerations.
"""

from autoforge_models.enums import (
    ArtifactType,
    CheckpointType,
    EmployeeRole,
    EventType,
    ExecutionStatus,
    KnowledgeEdgeType,
    MemoryType,
    ModelProvider,
    QualityGateStatus,
    ReviewStatus,
    TaskPriority,
    TaskStatus,
)


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.READY.value == "ready"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.PAUSED.value == "paused"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.BLOCKED.value == "blocked"

    def test_membership(self):
        assert "pending" in {s.value for s in TaskStatus}
        assert len(TaskStatus) == 8


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_values(self):
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"

    def test_membership(self):
        assert len(TaskPriority) == 4


class TestReviewStatus:
    """Tests for ReviewStatus enum."""

    def test_values(self):
        assert ReviewStatus.PENDING.value == "pending"
        assert ReviewStatus.IN_PROGRESS.value == "in_progress"
        assert ReviewStatus.APPROVED.value == "approved"
        assert ReviewStatus.CHANGES_REQUESTED.value == "changes_requested"
        assert ReviewStatus.REJECTED.value == "rejected"

    def test_membership(self):
        assert len(ReviewStatus) == 5


class TestArtifactType:
    """Tests for ArtifactType enum."""

    def test_values(self):
        assert ArtifactType.SPECIFICATION.value == "specification"
        assert ArtifactType.DESIGN.value == "design"
        assert ArtifactType.CODE.value == "code"
        assert ArtifactType.TEST.value == "test"
        assert ArtifactType.DOCUMENTATION.value == "documentation"
        assert ArtifactType.CONFIG.value == "config"
        assert ArtifactType.DATA.value == "data"
        assert ArtifactType.OTHER.value == "other"

    def test_membership(self):
        assert len(ArtifactType) == 8


class TestEmployeeRole:
    """Tests for EmployeeRole enum."""

    def test_values(self):
        assert EmployeeRole.ARCHITECT.value == "architect"
        assert EmployeeRole.DEVELOPER.value == "developer"
        assert EmployeeRole.REVIEWER.value == "reviewer"
        assert EmployeeRole.TESTER.value == "tester"
        assert EmployeeRole.PLANNER.value == "planner"
        assert EmployeeRole.RESEARCHER.value == "researcher"
        assert EmployeeRole.OPERATOR.value == "operator"

    def test_membership(self):
        assert len(EmployeeRole) == 7


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""

    def test_values(self):
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.PAUSED.value == "paused"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.CANCELLED.value == "cancelled"
        assert ExecutionStatus.TIMED_OUT.value == "timed_out"

    def test_membership(self):
        assert len(ExecutionStatus) == 7


class TestCheckpointType:
    """Tests for CheckpointType enum."""

    def test_values(self):
        assert CheckpointType.AUTOMATIC.value == "automatic"
        assert CheckpointType.MANUAL.value == "manual"
        assert CheckpointType.MILESTONE.value == "milestone"
        assert CheckpointType.RECOVERY.value == "recovery"

    def test_membership(self):
        assert len(CheckpointType) == 4


class TestEventType:
    """Tests for EventType enum."""

    def test_values(self):
        assert EventType.CREATED.value == "created"
        assert EventType.UPDATED.value == "updated"
        assert EventType.DELETED.value == "deleted"
        assert EventType.STARTED.value == "started"
        assert EventType.COMPLETED.value == "completed"
        assert EventType.FAILED.value == "failed"
        assert EventType.CANCELLED.value == "cancelled"
        assert EventType.PAUSED.value == "paused"
        assert EventType.RESUMED.value == "resumed"
        assert EventType.APPROVED.value == "approved"
        assert EventType.REJECTED.value == "rejected"
        assert EventType.CHANGES_REQUESTED.value == "changes_requested"
        assert EventType.GATE_PASSED.value == "gate_passed"
        assert EventType.GATE_FAILED.value == "gate_failed"
        assert EventType.GATE_WARNING.value == "gate_warning"
        assert EventType.CHECKPOINT_CREATED.value == "checkpoint_created"
        assert EventType.CHECKPOINT_RESTORED.value == "checkpoint_restored"
        assert EventType.ARTIFACT_PRODUCED.value == "artifact_produced"
        assert EventType.ARTIFACT_UPDATED.value == "artifact_updated"
        assert EventType.SYSTEM_EVENT.value == "system_event"
        assert EventType.ERROR.value == "error"
        assert EventType.WARNING.value == "warning"

    def test_membership(self):
        assert len(EventType) == 22


class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_values(self):
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.GOOGLE.value == "google"
        assert ModelProvider.LOCAL.value == "local"
        assert ModelProvider.CUSTOM.value == "custom"

    def test_membership(self):
        assert len(ModelProvider) == 5


class TestMemoryType:
    """Tests for MemoryType enum."""

    def test_values(self):
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.PROCEDURAL.value == "procedural"

    def test_membership(self):
        assert len(MemoryType) == 3


class TestKnowledgeEdgeType:
    """Tests for KnowledgeEdgeType enum."""

    def test_values(self):
        assert KnowledgeEdgeType.DEPENDS_ON.value == "depends_on"
        assert KnowledgeEdgeType.PRODUCES.value == "produces"
        assert KnowledgeEdgeType.REQUIRES.value == "requires"
        assert KnowledgeEdgeType.RELATES_TO.value == "relates_to"
        assert KnowledgeEdgeType.IMPLEMENTS.value == "implements"
        assert KnowledgeEdgeType.EXTENDS.value == "extends"

    def test_membership(self):
        assert len(KnowledgeEdgeType) == 6


class TestQualityGateStatus:
    """Tests for QualityGateStatus enum."""

    def test_values(self):
        assert QualityGateStatus.PENDING.value == "pending"
        assert QualityGateStatus.PASSING.value == "passing"
        assert QualityGateStatus.WARNING.value == "warning"
        assert QualityGateStatus.FAILING.value == "failing"
        assert QualityGateStatus.ERROR.value == "error"

    def test_membership(self):
        assert len(QualityGateStatus) == 5