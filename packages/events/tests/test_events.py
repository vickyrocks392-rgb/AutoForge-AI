"""
Comprehensive tests for the autoforge-events package.

Tests cover:
- Inheritance (all events inherit from BaseEvent)
- Immutability (events cannot be modified after creation)
- Serialization (to_dict, to_json, from_dict round-trips)
- Typing (event_type, event_category are correct)
- Event IDs (unique, UUID type)
- Timestamps (UTC, timezone-aware)
- Domain-specific payloads
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from autoforge_events import (
    BaseEvent,
    EventCategory,
    EventType,
    # Project events
    ProjectCreated,
    ProjectUpdated,
    ProjectArchived,
    ProjectDeleted,
    # Task events
    TaskCreated,
    TaskUpdated,
    TaskQueued,
    TaskReady,
    TaskStarted,
    TaskPaused,
    TaskResumed,
    TaskCompleted,
    TaskFailed,
    TaskCancelled,
    TaskBlocked,
    TaskDeleted,
    # Execution events
    ExecutionStarted,
    ExecutionCompleted,
    ExecutionFailed,
    ExecutionPaused,
    ExecutionResumed,
    ExecutionCancelled,
    ExecutionTimedOut,
    # Artifact events
    ArtifactCreated,
    ArtifactUpdated,
    ArtifactDeleted,
    # Memory events
    MemoryStored,
    MemoryUpdated,
    MemoryDeleted,
    MemoryRetrieved,
)

# =========================================================================
# Helpers
# =========================================================================

ALL_EVENT_CLASSES = [
    ProjectCreated,
    ProjectUpdated,
    ProjectArchived,
    ProjectDeleted,
    TaskCreated,
    TaskUpdated,
    TaskQueued,
    TaskReady,
    TaskStarted,
    TaskPaused,
    TaskResumed,
    TaskCompleted,
    TaskFailed,
    TaskCancelled,
    TaskBlocked,
    TaskDeleted,
    ExecutionStarted,
    ExecutionCompleted,
    ExecutionFailed,
    ExecutionPaused,
    ExecutionResumed,
    ExecutionCancelled,
    ExecutionTimedOut,
    ArtifactCreated,
    ArtifactUpdated,
    ArtifactDeleted,
    MemoryStored,
    MemoryUpdated,
    MemoryDeleted,
    MemoryRetrieved,
]

PROJECT_EVENTS = [ProjectCreated, ProjectUpdated, ProjectArchived, ProjectDeleted]
TASK_EVENTS = [
    TaskCreated, TaskUpdated, TaskQueued, TaskReady, TaskStarted,
    TaskPaused, TaskResumed, TaskCompleted, TaskFailed, TaskCancelled,
    TaskBlocked, TaskDeleted,
]
EXECUTION_EVENTS = [
    ExecutionStarted, ExecutionCompleted, ExecutionFailed,
    ExecutionPaused, ExecutionResumed, ExecutionCancelled, ExecutionTimedOut,
]
ARTIFACT_EVENTS = [ArtifactCreated, ArtifactUpdated, ArtifactDeleted]
MEMORY_EVENTS = [MemoryStored, MemoryUpdated, MemoryDeleted, MemoryRetrieved]


def make_minimal_kwargs(event_class: type[BaseEvent]) -> dict:
    """Build minimal keyword arguments for a given event class."""
    agg_id = uuid.uuid4()
    kwargs: dict = {"aggregate_id": agg_id}

    # Add required fields specific to each event type
    if event_class in PROJECT_EVENTS:
        if event_class is ProjectCreated:
            kwargs["project_name"] = "Test Project"
        elif event_class is ProjectUpdated:
            kwargs["updated_fields"] = ["name"]
        elif event_class is ProjectArchived:
            pass  # No extra required fields
        elif event_class is ProjectDeleted:
            pass  # No extra required fields

    elif event_class in TASK_EVENTS:
        kwargs["project_id"] = uuid.uuid4()
        if event_class is TaskCreated:
            kwargs["task_title"] = "Test Task"
        elif event_class is TaskUpdated:
            kwargs["updated_fields"] = ["title"]
        elif event_class is TaskQueued:
            pass
        elif event_class is TaskReady:
            pass
        elif event_class is TaskStarted:
            pass
        elif event_class is TaskPaused:
            kwargs["reason"] = "Waiting for input"
        elif event_class is TaskResumed:
            pass
        elif event_class is TaskCompleted:
            pass
        elif event_class is TaskFailed:
            kwargs["error_code"] = "ERR_001"
            kwargs["error_message"] = "Something went wrong"
        elif event_class is TaskCancelled:
            kwargs["reason"] = "No longer needed"
        elif event_class is TaskBlocked:
            kwargs["blocked_by"] = [uuid.uuid4()]
        elif event_class is TaskDeleted:
            pass

    elif event_class in EXECUTION_EVENTS:
        kwargs["task_id"] = uuid.uuid4()
        kwargs["project_id"] = uuid.uuid4()
        if event_class is ExecutionCompleted:
            kwargs["duration_seconds"] = 42.0
        elif event_class is ExecutionFailed:
            kwargs["error_code"] = "ERR_002"
            kwargs["error_message"] = "Execution failed"
        elif event_class is ExecutionPaused:
            kwargs["reason"] = "Manual pause"
        elif event_class is ExecutionCancelled:
            kwargs["reason"] = "Cancelled by user"
        elif event_class is ExecutionTimedOut:
            kwargs["max_duration_seconds"] = 60.0
            kwargs["actual_duration_seconds"] = 61.5

    elif event_class in ARTIFACT_EVENTS:
        kwargs["project_id"] = uuid.uuid4()
        if event_class is ArtifactCreated:
            kwargs["artifact_name"] = "test.py"
            kwargs["artifact_type"] = "code"
        elif event_class is ArtifactUpdated:
            kwargs["updated_fields"] = ["name"]
        elif event_class is ArtifactDeleted:
            kwargs["artifact_name"] = "test.py"

    elif event_class in MEMORY_EVENTS:
        kwargs["key"] = "test_key"
        if event_class is MemoryStored:
            kwargs["memory_type"] = "semantic"
            kwargs["value"] = {"data": "test"}
        elif event_class is MemoryUpdated:
            kwargs["updated_fields"] = ["value"]
            kwargs["new_value"] = {"data": "updated"}
        elif event_class is MemoryDeleted:
            pass
        elif event_class is MemoryRetrieved:
            pass

    return kwargs


# =========================================================================
# 1. Inheritance
# =========================================================================

class TestInheritance:
    """All events must inherit from BaseEvent."""

    def test_all_events_inherit_base_event(self):
        for cls in ALL_EVENT_CLASSES:
            assert issubclass(cls, BaseEvent), f"{cls.__name__} does not inherit from BaseEvent"

    def test_base_event_is_abstract(self):
        """BaseEvent should not be instantiable directly (missing required fields)."""
        with pytest.raises(ValidationError):
            BaseEvent()  # type: ignore[call-arg]

    def test_all_events_have_correct_mro(self):
        for cls in ALL_EVENT_CLASSES:
            assert BaseEvent in cls.__mro__, f"{cls.__name__} MRO missing BaseEvent"


# =========================================================================
# 2. Immutability
# =========================================================================

class TestImmutability:
    """Events must be immutable after construction."""

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_event_is_frozen(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        event = event_class(**kwargs)
        with pytest.raises(ValidationError):
            event.event_type = EventType.TASK_COMPLETED  # type: ignore[misc]

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_cannot_set_arbitrary_field(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        event = event_class(**kwargs)
        with pytest.raises(ValidationError):
            event.nonexistent_field = "value"  # type: ignore[attr-defined]

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_extra_fields_forbidden(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        kwargs["extra_field"] = "should_not_work"
        with pytest.raises(ValidationError):
            event_class(**kwargs)


# =========================================================================
# 3. Serialization
# =========================================================================

class TestSerialization:
    """Events must support to_dict, to_json, and from_dict round-trips."""

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_to_dict_round_trip(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        event = event_class(**kwargs)
        data = event.to_dict()
        restored = event_class.from_dict(data)
        assert restored == event, f"to_dict/from_dict round-trip failed for {event_class.__name__}"

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_to_json_round_trip(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        event = event_class(**kwargs)
        json_str = event.to_json()
        data = json.loads(json_str)
        restored = event_class.model_validate(data)
        assert restored == event, f"to_json/from_json round-trip failed for {event_class.__name__}"

    @pytest.mark.parametrize("event_class", ALL_EVENT_CLASSES)
    def test_serialization_preserves_types(self, event_class):
        kwargs = make_minimal_kwargs(event_class)
        event = event_class(**kwargs)
        # to_dict with mode="python" keeps UUID as UUID objects
        data = event.model_dump(mode="python")
        assert isinstance(data["event_id"], uuid.UUID), "event_id should be a UUID in python mode"
        assert isinstance(data["occurred_at"], datetime), "occurred_at should be a datetime in python mode"
        assert isinstance(data["event_type"], str), "event_type should be a string"
        assert isinstance(data["event_category"], str), "event_category should be a string"
        # to_dict with mode="json" serializes to JSON-compatible types
        json_data = event.model_dump(mode="json")
        assert isinstance(json_data["event_id"], str), "event_id should be a string in json mode"
        assert isinstance(json_data["occurred_at"], str), "occurred_at should be a string in json mode"

    def test_json_serialization_is_valid(self):
        event = ProjectCreated(
            aggregate_id=uuid.uuid4(),
            project_name="Test",
        )
        json_str = event.to_json()
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "project.created"
        assert parsed["event_category"] == "project"
        assert parsed["aggregate_type"] == "Project"
        assert parsed["project_name"] == "Test"


# =========================================================================
# 4. Typing
# =========================================================================

class TestTyping:
    """Events must have correct event_type and event_category."""

    def test_project_events_have_correct_types(self):
        for cls in PROJECT_EVENTS:
            kwargs = make_minimal_kwargs(cls)
            event = cls(**kwargs)
            assert event.event_category == EventCategory.PROJECT
            assert event.aggregate_type == "Project"

    def test_task_events_have_correct_types(self):
        for cls in TASK_EVENTS:
            kwargs = make_minimal_kwargs(cls)
            event = cls(**kwargs)
            assert event.event_category == EventCategory.TASK
            assert event.aggregate_type == "Task"

    def test_execution_events_have_correct_types(self):
        for cls in EXECUTION_EVENTS:
            kwargs = make_minimal_kwargs(cls)
            event = cls(**kwargs)
            assert event.event_category == EventCategory.EXECUTION
            assert event.aggregate_type == "ExecutionSession"

    def test_artifact_events_have_correct_types(self):
        for cls in ARTIFACT_EVENTS:
            kwargs = make_minimal_kwargs(cls)
            event = cls(**kwargs)
            assert event.event_category == EventCategory.ARTIFACT
            assert event.aggregate_type == "Artifact"

    def test_memory_events_have_correct_types(self):
        for cls in MEMORY_EVENTS:
            kwargs = make_minimal_kwargs(cls)
            event = cls(**kwargs)
            assert event.event_category == EventCategory.MEMORY
            assert event.aggregate_type == "MemoryEntry"

    def test_specific_event_types(self):
        """Verify specific event_type values."""
        assert ProjectCreated(event_type=EventType.PROJECT_CREATED, aggregate_id=uuid.uuid4(), project_name="X").event_type == EventType.PROJECT_CREATED
        assert TaskStarted(event_type=EventType.TASK_STARTED, aggregate_id=uuid.uuid4(), project_id=uuid.uuid4()).event_type == EventType.TASK_STARTED
        assert ExecutionCompleted(event_type=EventType.EXECUTION_COMPLETED, aggregate_id=uuid.uuid4(), task_id=uuid.uuid4(), project_id=uuid.uuid4(), duration_seconds=10.0).event_type == EventType.EXECUTION_COMPLETED
        assert ArtifactCreated(event_type=EventType.ARTIFACT_CREATED, aggregate_id=uuid.uuid4(), project_id=uuid.uuid4(), artifact_name="a", artifact_type="code").event_type == EventType.ARTIFACT_CREATED
        assert MemoryStored(event_type=EventType.MEMORY_STORED, aggregate_id=uuid.uuid4(), key="k", memory_type="semantic", value={"x": 1}).event_type == EventType.MEMORY_STORED


# =========================================================================
# 5. Event IDs
# =========================================================================

class TestEventIDs:
    """Events must have unique UUID event IDs."""

    def test_event_id_is_uuid(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert isinstance(event.event_id, uuid.UUID)

    def test_event_ids_are_unique(self):
        ids = set()
        for _ in range(100):
            event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
            ids.add(event.event_id)
        assert len(ids) == 100

    def test_aggregate_id_is_uuid(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert isinstance(event.aggregate_id, uuid.UUID)

    def test_correlation_id_is_optional_uuid(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert event.correlation_id is None
        cid = uuid.uuid4()
        event2 = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test", correlation_id=cid)
        assert event2.correlation_id == cid

    def test_causation_id_is_optional_uuid(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert event.causation_id is None
        cid = uuid.uuid4()
        event2 = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test", causation_id=cid)
        assert event2.causation_id == cid


# =========================================================================
# 6. Timestamps
# =========================================================================

class TestTimestamps:
    """Events must have UTC timezone-aware timestamps."""

    def test_occurred_at_is_datetime(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert isinstance(event.occurred_at, datetime)

    def test_occurred_at_is_utc(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert event.occurred_at.tzinfo is not None
        assert event.occurred_at.tzinfo == timezone.utc

    def test_occurred_at_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        after = datetime.now(timezone.utc)
        assert before <= event.occurred_at <= after

    def test_naive_datetime_is_converted_to_utc(self):
        naive = datetime(2025, 1, 1, 12, 0, 0)
        event = ProjectCreated(
            aggregate_id=uuid.uuid4(),
            project_name="Test",
            occurred_at=naive,
        )
        assert event.occurred_at.tzinfo == timezone.utc
        assert event.occurred_at.hour == 12  # Same hour, just made aware


# =========================================================================
# 7. Domain-specific payloads
# =========================================================================

class TestProjectEvents:
    """Project event payloads must be correct."""

    def test_project_created(self):
        pid = uuid.uuid4()
        event = ProjectCreated(
            aggregate_id=pid,
            project_name="My Project",
            project_description="A test project",
            owner_id=uuid.uuid4(),
            initial_config={"language": "python"},
        )
        assert event.project_name == "My Project"
        assert event.project_description == "A test project"
        assert event.aggregate_id == pid

    def test_project_updated(self):
        event = ProjectUpdated(
            aggregate_id=uuid.uuid4(),
            updated_fields=["name", "description"],
            previous_values={"name": "Old", "description": "Old desc"},
            new_values={"name": "New", "description": "New desc"},
        )
        assert "name" in event.updated_fields
        assert event.previous_values["name"] == "Old"

    def test_project_archived(self):
        event = ProjectArchived(
            aggregate_id=uuid.uuid4(),
            reason="No longer active",
            archived_by=uuid.uuid4(),
        )
        assert event.reason == "No longer active"

    def test_project_deleted(self):
        event = ProjectDeleted(
            aggregate_id=uuid.uuid4(),
            reason="Cleanup",
            task_count=5,
        )
        assert event.task_count == 5


class TestTaskEvents:
    """Task event payloads must be correct."""

    def test_task_created(self):
        pid = uuid.uuid4()
        dep_id = uuid.uuid4()
        event = TaskCreated(
            aggregate_id=uuid.uuid4(),
            task_title="Implement feature X",
            task_description="Do the thing",
            project_id=pid,
            priority="high",
            depends_on=[dep_id],
            estimated_cost=10.5,
        )
        assert event.task_title == "Implement feature X"
        assert event.project_id == pid
        assert event.priority == "high"
        assert dep_id in event.depends_on
        assert event.estimated_cost == 10.5

    def test_task_completed(self):
        art_id = uuid.uuid4()
        event = TaskCompleted(
            aggregate_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            output_data={"result": "success"},
            actual_cost=8.0,
            duration_seconds=120.5,
            artifact_ids=[art_id],
        )
        assert event.output_data["result"] == "success"
        assert event.actual_cost == 8.0
        assert event.duration_seconds == 120.5
        assert art_id in event.artifact_ids

    def test_task_failed(self):
        event = TaskFailed(
            aggregate_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            error_code="EXEC_ERR",
            error_message="Execution failed with exit code 1",
            recoverable=True,
            retry_count=2,
        )
        assert event.error_code == "EXEC_ERR"
        assert event.recoverable is True
        assert event.retry_count == 2

    def test_task_blocked(self):
        blocker = uuid.uuid4()
        event = TaskBlocked(
            aggregate_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            blocked_by=[blocker],
            reason="Waiting for dependency",
        )
        assert blocker in event.blocked_by


class TestExecutionEvents:
    """Execution event payloads must be correct."""

    def test_execution_started(self):
        event = ExecutionStarted(
            aggregate_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            model_profile_id=uuid.uuid4(),
            max_duration_seconds=300.0,
        )
        assert event.max_duration_seconds == 300.0

    def test_execution_completed(self):
        event = ExecutionCompleted(
            aggregate_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            output_data={"result": "done"},
            duration_seconds=45.0,
            total_cost=2.5,
            token_count=1500,
        )
        assert event.duration_seconds == 45.0
        assert event.total_cost == 2.5
        assert event.token_count == 1500

    def test_execution_timed_out(self):
        event = ExecutionTimedOut(
            aggregate_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            max_duration_seconds=60.0,
            actual_duration_seconds=61.5,
            partial_output={"progress": "50%"},
        )
        assert event.max_duration_seconds == 60.0
        assert event.actual_duration_seconds == 61.5


class TestArtifactEvents:
    """Artifact event payloads must be correct."""

    def test_artifact_created(self):
        event = ArtifactCreated(
            aggregate_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            artifact_name="main.py",
            artifact_type="code",
            file_path="src/main.py",
            mime_type="text/x-python",
            size_bytes=1024,
            content_hash="abc123",
            tags=["python", "core"],
        )
        assert event.artifact_name == "main.py"
        assert event.file_path == "src/main.py"
        assert event.size_bytes == 1024
        assert "python" in event.tags

    def test_artifact_deleted(self):
        event = ArtifactDeleted(
            aggregate_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            artifact_name="old_file.py",
            reason="No longer needed",
        )
        assert event.artifact_name == "old_file.py"


class TestMemoryEvents:
    """Memory event payloads must be correct."""

    def test_memory_stored(self):
        event = MemoryStored(
            aggregate_id=uuid.uuid4(),
            key="user_preference",
            memory_type="semantic",
            value={"theme": "dark"},
            importance=0.8,
            tags=["user", "preference"],
            ttl_seconds=86400,
        )
        assert event.key == "user_preference"
        assert event.importance == 0.8
        assert event.ttl_seconds == 86400

    def test_memory_updated(self):
        event = MemoryUpdated(
            aggregate_id=uuid.uuid4(),
            key="user_preference",
            updated_fields=["value"],
            previous_value={"theme": "light"},
            new_value={"theme": "dark"},
            previous_importance=0.5,
            new_importance=0.9,
        )
        assert event.new_value["theme"] == "dark"
        assert event.new_importance == 0.9

    def test_memory_retrieved(self):
        event = MemoryRetrieved(
            aggregate_id=uuid.uuid4(),
            key="user_preference",
            retrieved_by=uuid.uuid4(),
            retrieval_context="Loading user settings",
        )
        assert event.retrieval_context == "Loading user settings"


# =========================================================================
# 8. Version and metadata
# =========================================================================

class TestVersionAndMetadata:
    """Events must have version and metadata fields."""

    def test_default_version_is_1(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert event.version == 1

    def test_custom_version(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test", version=2)
        assert event.version == 2

    def test_version_must_be_positive(self):
        with pytest.raises(ValidationError):
            ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test", version=0)

    def test_default_metadata_is_empty(self):
        event = ProjectCreated(aggregate_id=uuid.uuid4(), project_name="Test")
        assert event.metadata == {}

    def test_custom_metadata(self):
        event = ProjectCreated(
            aggregate_id=uuid.uuid4(),
            project_name="Test",
            metadata={"source": "cli", "env": "production"},
        )
        assert event.metadata["source"] == "cli"


# =========================================================================
# 9. Edge cases
# =========================================================================

class TestEdgeCases:
    """Edge cases and validation."""

    def test_empty_string_rejected_for_required_fields(self):
        with pytest.raises(ValidationError):
            ProjectCreated(aggregate_id=uuid.uuid4(), project_name="")

    def test_negative_cost_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreated(
                aggregate_id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                task_title="Test",
                estimated_cost=-1.0,
            )

    def test_importance_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            MemoryStored(
                aggregate_id=uuid.uuid4(),
                key="test",
                memory_type="semantic",
                value={"x": 1},
                importance=1.5,
            )

    def test_empty_updated_fields_rejected(self):
        with pytest.raises(ValidationError):
            ProjectUpdated(
                aggregate_id=uuid.uuid4(),
                updated_fields=[],
            )

    def test_empty_blocked_by_rejected(self):
        with pytest.raises(ValidationError):
            TaskBlocked(
                aggregate_id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                blocked_by=[],
            )

    def test_long_strings_rejected(self):
        with pytest.raises(ValidationError):
            ProjectCreated(
                aggregate_id=uuid.uuid4(),
                project_name="x" * 257,
            )

    def test_invalid_priority_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreated(
                aggregate_id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                task_title="Test",
                priority="invalid",
            )

    def test_negative_duration_rejected(self):
        with pytest.raises(ValidationError):
            ExecutionCompleted(
                aggregate_id=uuid.uuid4(),
                task_id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                duration_seconds=-1.0,
            )