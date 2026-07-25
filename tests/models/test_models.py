"""
Unit tests for domain model creation, validation, and serialization.
"""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from autoforge_models.artifact import Artifact
from autoforge_models.checkpoint import Checkpoint
from autoforge_models.employee import Employee, ModelConfig
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
from autoforge_models.event import Event
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.knowledge import KnowledgeEdge, KnowledgeNode
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.model_profile import ModelProfile
from autoforge_models.project import Project
from autoforge_models.quality_gate import QualityGate
from autoforge_models.review import Review
from autoforge_models.task import ResourceRequirements, Task


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class TestProject:
    def test_create_minimal(self):
        """A Project can be created with only required fields."""
        p = Project(name="Test Project")
        assert p.name == "Test Project"
        assert isinstance(p.id, uuid.UUID)
        assert isinstance(p.created_at, datetime)
        assert p.is_archived is False

    def test_create_full(self):
        """A Project can be created with all fields."""
        p = Project(
            name="Full Project",
            description="A full project description",
            version="1.0.0",
            tags=["backend", "api"],
            metadata={"team": "alpha"},
            is_archived=False,
        )
        assert p.name == "Full Project"
        assert p.version == "1.0.0"
        assert "backend" in p.tags
        assert p.metadata["team"] == "alpha"

    def test_name_validation(self):
        """Project name must be at least 1 character."""
        with pytest.raises(ValidationError):
            Project(name="")

    def test_serialization_roundtrip(self):
        """Project can be serialized to dict and back."""
        p1 = Project(name="Roundtrip", tags=["test"])
        d = p1.to_dict()
        p2 = Project.from_dict(d)
        assert p1.id == p2.id
        assert p1.name == p2.name
        assert p1.tags == p2.tags


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TestTask:
    def test_create_minimal(self):
        """A Task can be created with only required fields."""
        t = Task(project_id=uuid.uuid4(), title="Implement login")
        assert t.title == "Implement login"
        assert t.status == TaskStatus.PENDING
        assert t.priority == TaskPriority.MEDIUM
        assert isinstance(t.resources, ResourceRequirements)

    def test_create_with_dependencies(self):
        """A Task can reference dependent tasks."""
        dep_id = uuid.uuid4()
        t = Task(
            project_id=uuid.uuid4(),
            title="Task with deps",
            depends_on=[dep_id],
        )
        assert dep_id in t.depends_on

    def test_status_transition_values(self):
        """Task status accepts valid enum values."""
        t = Task(project_id=uuid.uuid4(), title="Status test", status=TaskStatus.READY)
        assert t.status == TaskStatus.READY

    def test_priority_values(self):
        """Task priority accepts valid enum values."""
        t = Task(project_id=uuid.uuid4(), title="Priority test", priority=TaskPriority.CRITICAL)
        assert t.priority == TaskPriority.CRITICAL

    def test_serialization_roundtrip(self):
        """Task can be serialized to dict and back."""
        t1 = Task(project_id=uuid.uuid4(), title="Roundtrip")
        d = t1.to_dict()
        t2 = Task.from_dict(d)
        assert t1.id == t2.id
        assert t1.title == t2.title


# ---------------------------------------------------------------------------
# ResourceRequirements
# ---------------------------------------------------------------------------


class TestResourceRequirements:
    def test_defaults(self):
        """ResourceRequirements has sensible defaults."""
        r = ResourceRequirements()
        assert r.max_retries == 3
        assert r.estimated_cpu_cores is None
        assert r.timeout_seconds is None

    def test_validation(self):
        """ResourceRequirements validates numeric constraints."""
        with pytest.raises(ValidationError):
            ResourceRequirements(estimated_cpu_cores=-1)

        with pytest.raises(ValidationError):
            ResourceRequirements(max_retries=-1)


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------


class TestArtifact:
    def test_create_minimal(self):
        """An Artifact can be created with required fields."""
        a = Artifact(
            project_id=uuid.uuid4(),
            name="main.py",
            artifact_type=ArtifactType.CODE,
            file_path="src/main.py",
        )
        assert a.name == "main.py"
        assert a.artifact_type == ArtifactType.CODE
        assert a.mime_type == "application/octet-stream"

    def test_create_with_size(self):
        """An Artifact can include size and checksum."""
        a = Artifact(
            project_id=uuid.uuid4(),
            name="output.json",
            artifact_type=ArtifactType.DATA,
            file_path="output.json",
            size_bytes=1024,
            checksum="abc123",
        )
        assert a.size_bytes == 1024
        assert a.checksum == "abc123"

    def test_serialization_roundtrip(self):
        """Artifact can be serialized to dict and back."""
        a1 = Artifact(
            project_id=uuid.uuid4(),
            name="test.py",
            artifact_type=ArtifactType.CODE,
            file_path="test.py",
        )
        d = a1.to_dict()
        a2 = Artifact.from_dict(d)
        assert a1.id == a2.id
        assert a1.name == a2.name


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------


class TestCheckpoint:
    def test_create_minimal(self):
        """A Checkpoint can be created with required fields."""
        c = Checkpoint(
            execution_session_id=uuid.uuid4(),
            checkpoint_type=CheckpointType.AUTOMATIC,
        )
        assert c.checkpoint_type == CheckpointType.AUTOMATIC
        assert c.is_recovery_point is False

    def test_create_with_state(self):
        """A Checkpoint can include state snapshots."""
        c = Checkpoint(
            execution_session_id=uuid.uuid4(),
            checkpoint_type=CheckpointType.MILESTONE,
            label="v1.0",
            state_snapshot={"step": 5, "status": "ok"},
            is_recovery_point=True,
        )
        assert c.label == "v1.0"
        assert c.state_snapshot["step"] == 5
        assert c.is_recovery_point is True


# ---------------------------------------------------------------------------
# ExecutionSession
# ---------------------------------------------------------------------------


class TestExecutionSession:
    def test_create_minimal(self):
        """An ExecutionSession can be created with required fields."""
        s = ExecutionSession(project_id=uuid.uuid4())
        assert s.status == ExecutionStatus.PENDING
        assert s.retry_count == 0
        assert s.max_retries == 3

    def test_create_with_task(self):
        """An ExecutionSession can be linked to a task."""
        task_id = uuid.uuid4()
        s = ExecutionSession(project_id=uuid.uuid4(), task_id=task_id)
        assert s.task_id == task_id

    def test_status_values(self):
        """ExecutionSession status accepts valid enum values."""
        s = ExecutionSession(
            project_id=uuid.uuid4(),
            status=ExecutionStatus.RUNNING,
        )
        assert s.status == ExecutionStatus.RUNNING


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------


class TestEmployee:
    def test_create_minimal(self):
        """An Employee can be created with required fields."""
        e = Employee(name="Alice", role=EmployeeRole.DEVELOPER)
        assert e.name == "Alice"
        assert e.role == EmployeeRole.DEVELOPER
        assert e.is_ai is True
        assert e.is_active is True

    def test_create_with_model_config(self):
        """An AI Employee can have a model configuration."""
        mc = ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
        )
        e = Employee(
            name="GPT-4 Agent",
            role=EmployeeRole.DEVELOPER,
            model=mc,
        )
        assert e.model is not None
        assert e.model.provider == ModelProvider.OPENAI
        assert e.model.model_name == "gpt-4"

    def test_human_employee(self):
        """A human Employee has no model config."""
        e = Employee(
            name="Bob",
            role=EmployeeRole.REVIEWER,
            is_ai=False,
        )
        assert e.is_ai is False
        assert e.model is None


# ---------------------------------------------------------------------------
# ModelConfig
# ---------------------------------------------------------------------------


class TestModelConfig:
    def test_create_minimal(self):
        """ModelConfig can be created with required fields."""
        mc = ModelConfig(provider=ModelProvider.ANTHROPIC, model_name="claude-3-opus")
        assert mc.provider == ModelProvider.ANTHROPIC
        assert mc.model_name == "claude-3-opus"

    def test_create_with_parameters(self):
        """ModelConfig can include optional parameters."""
        mc = ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=2048,
        )
        assert mc.temperature == 0.5
        assert mc.max_tokens == 2048


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------


class TestReview:
    def test_create_minimal(self):
        """A Review can be created with required fields."""
        r = Review(
            project_id=uuid.uuid4(),
            reviewer_id=uuid.uuid4(),
        )
        assert r.status == ReviewStatus.PENDING
        assert r.score is None

    def test_create_with_results(self):
        """A Review can include scores and checklist results."""
        r = Review(
            project_id=uuid.uuid4(),
            reviewer_id=uuid.uuid4(),
            status=ReviewStatus.APPROVED,
            score=95.0,
            comments="Looks good!",
            checklist_results={"tests_pass": True, "style_ok": True},
        )
        assert r.status == ReviewStatus.APPROVED
        assert r.score == 95.0
        assert r.checklist_results["tests_pass"] is True

    def test_score_validation(self):
        """Review score must be between 0 and 100."""
        with pytest.raises(ValidationError):
            Review(
                project_id=uuid.uuid4(),
                reviewer_id=uuid.uuid4(),
                score=150.0,
            )


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------


class TestEvent:
    def test_create_minimal(self):
        """An Event can be created with required fields."""
        e = Event(
            event_type=EventType.CREATED,
            source="test",
        )
        assert e.event_type == EventType.CREATED
        assert e.source == "test"
        assert isinstance(e.timestamp, datetime)

    def test_create_with_correlation(self):
        """An Event can include correlation and causation IDs."""
        corr_id = uuid.uuid4()
        cause_id = uuid.uuid4()
        e = Event(
            event_type=EventType.STARTED,
            source="executor",
            subject_id=uuid.uuid4(),
            subject_type="Task",
            correlation_id=corr_id,
            causation_id=cause_id,
        )
        assert e.correlation_id == corr_id
        assert e.causation_id == cause_id

    def test_serialization_roundtrip(self):
        """Event can be serialized to dict and back."""
        e1 = Event(event_type=EventType.COMPLETED, source="worker")
        d = e1.to_dict()
        e2 = Event.from_dict(d)
        assert e1.event_type == e2.event_type
        assert e1.source == e2.source


# ---------------------------------------------------------------------------
# ModelProfile
# ---------------------------------------------------------------------------


class TestModelProfile:
    def test_create_minimal(self):
        """A ModelProfile can be created with required fields."""
        mp = ModelProfile(
            name="GPT-4 Production",
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
        )
        assert mp.name == "GPT-4 Production"
        assert mp.default_temperature == 0.7
        assert mp.supports_streaming is True

    def test_create_with_costs(self):
        """A ModelProfile can include cost information."""
        mp = ModelProfile(
            name="Claude-3",
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-opus",
            cost_per_input_token=0.000015,
            cost_per_output_token=0.000075,
        )
        assert mp.cost_per_input_token == 0.000015
        assert mp.cost_per_output_token == 0.000075


# ---------------------------------------------------------------------------
# MemoryEntry
# ---------------------------------------------------------------------------


class TestMemoryEntry:
    def test_create_minimal(self):
        """A MemoryEntry can be created with required fields."""
        m = MemoryEntry(
            memory_type=MemoryType.SEMANTIC,
            key="python/patterns",
            title="Python Design Patterns",
            content="Factory pattern: ...",
        )
        assert m.memory_type == MemoryType.SEMANTIC
        assert m.key == "python/patterns"
        assert m.importance_score == 0.5

    def test_create_episodic(self):
        """An episodic memory entry can be created."""
        m = MemoryEntry(
            memory_type=MemoryType.EPISODIC,
            key="session/123",
            title="Execution of task X",
            content="Task X completed successfully after 2 retries.",
            importance_score=0.8,
        )
        assert m.memory_type == MemoryType.EPISODIC
        assert m.importance_score == 0.8

    def test_importance_validation(self):
        """Importance score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            MemoryEntry(
                memory_type=MemoryType.PROCEDURAL,
                key="test",
                title="Test",
                content="Test content",
                importance_score=1.5,
            )


# ---------------------------------------------------------------------------
# KnowledgeNode
# ---------------------------------------------------------------------------


class TestKnowledgeNode:
    def test_create_minimal(self):
        """A KnowledgeNode can be created with required fields."""
        n = KnowledgeNode(
            node_type="Concept",
            label="Dependency Injection",
        )
        assert n.node_type == "Concept"
        assert n.label == "Dependency Injection"

    def test_create_with_ref(self):
        """A KnowledgeNode can reference an external entity."""
        ref_id = uuid.uuid4()
        n = KnowledgeNode(
            node_type="Task",
            label="Implement DI Container",
            external_ref_id=ref_id,
        )
        assert n.external_ref_id == ref_id

    def test_serialization_roundtrip(self):
        """KnowledgeNode can be serialized to dict and back."""
        n1 = KnowledgeNode(node_type="Concept", label="Test")
        d = n1.to_dict()
        n2 = KnowledgeNode.from_dict(d)
        assert n1.id == n2.id
        assert n1.label == n2.label


# ---------------------------------------------------------------------------
# KnowledgeEdge
# ---------------------------------------------------------------------------


class TestKnowledgeEdge:
    def test_create_minimal(self):
        """A KnowledgeEdge can be created with required fields."""
        e = KnowledgeEdge(
            source_node_id=uuid.uuid4(),
            target_node_id=uuid.uuid4(),
            edge_type=KnowledgeEdgeType.DEPENDS_ON,
        )
        assert e.edge_type == KnowledgeEdgeType.DEPENDS_ON
        assert e.weight == 1.0

    def test_create_with_properties(self):
        """A KnowledgeEdge can include properties."""
        e = KnowledgeEdge(
            source_node_id=uuid.uuid4(),
            target_node_id=uuid.uuid4(),
            edge_type=KnowledgeEdgeType.IMPLEMENTS,
            weight=0.8,
            label="implements interface",
        )
        assert e.weight == 0.8
        assert e.label == "implements interface"


# ---------------------------------------------------------------------------
# QualityGate
# ---------------------------------------------------------------------------


class TestQualityGate:
    def test_create_minimal(self):
        """A QualityGate can be created with required fields."""
        q = QualityGate(
            project_id=uuid.uuid4(),
            name="Test Coverage",
            gate_type="test_coverage",
        )
        assert q.name == "Test Coverage"
        assert q.status == QualityGateStatus.PENDING
        assert q.is_required is True
        assert q.is_blocking is True

    def test_create_with_threshold(self):
        """A QualityGate can include threshold values."""
        q = QualityGate(
            project_id=uuid.uuid4(),
            name="Lint Check",
            gate_type="lint",
            threshold_value=100.0,
            actual_value=95.0,
            status=QualityGateStatus.WARNING,
            failure_reason="3 lint warnings found",
        )
        assert q.threshold_value == 100.0
        assert q.actual_value == 95.0
        assert q.status == QualityGateStatus.WARNING
        assert "lint warnings" in q.failure_reason

    def test_optional_gate(self):
        """A QualityGate can be optional and non-blocking."""
        q = QualityGate(
            project_id=uuid.uuid4(),
            name="Optional Check",
            gate_type="style",
            is_required=False,
            is_blocking=False,
        )
        assert q.is_required is False
        assert q.is_blocking is False