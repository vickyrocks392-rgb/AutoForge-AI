"""
Unit tests for base model classes.
"""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from autoforge_models.base import (
    AutoForgeBaseModel,
    AuditableModel,
    IdentifiedModel,
    TimestampedModel,
)


class TestAutoForgeBaseModel:
    """Tests for the root base model."""

    def test_create_simple_model(self):
        """A simple model can be created with required fields."""

        class SimpleModel(AutoForgeBaseModel):
            name: str
            value: int

        obj = SimpleModel(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42

    def test_extra_fields_forbidden(self):
        """Extra fields are rejected by default."""

        class SimpleModel(AutoForgeBaseModel):
            name: str

        with pytest.raises(ValidationError, match="extra"):
            SimpleModel(name="test", extra_field="should_fail")

    def test_immutable_by_default(self):
        """Models are frozen (immutable) by default."""

        class SimpleModel(AutoForgeBaseModel):
            name: str

        obj = SimpleModel(name="test")
        with pytest.raises(ValidationError):
            obj.name = "changed"

    def test_to_dict(self):
        """to_dict returns a plain dictionary."""

        class SimpleModel(AutoForgeBaseModel):
            name: str
            value: int

        obj = SimpleModel(name="test", value=42)
        d = obj.to_dict()
        assert d == {"name": "test", "value": 42}

    def test_to_json(self):
        """to_json returns a JSON string."""

        class SimpleModel(AutoForgeBaseModel):
            name: str
            value: int

        obj = SimpleModel(name="test", value=42)
        json_str = obj.to_json()
        assert '"name"' in json_str
        assert '"test"' in json_str
        assert "42" in json_str

    def test_from_dict(self):
        """from_dict creates a model from a dictionary."""

        class SimpleModel(AutoForgeBaseModel):
            name: str
            value: int

        obj = SimpleModel.from_dict({"name": "test", "value": 42})
        assert obj.name == "test"
        assert obj.value == 42


class TestIdentifiedModel:
    """Tests for the identified model base class."""

    def test_auto_generates_uuid(self):
        """A UUID is auto-generated if not provided."""

        class TestModel(IdentifiedModel):
            name: str

        obj = TestModel(name="test")
        assert isinstance(obj.id, uuid.UUID)

    def test_unique_ids(self):
        """Each instance gets a unique UUID."""

        class TestModel(IdentifiedModel):
            name: str

        obj1 = TestModel(name="test1")
        obj2 = TestModel(name="test2")
        assert obj1.id != obj2.id

    def test_provided_uuid(self):
        """A UUID can be explicitly provided."""

        class TestModel(IdentifiedModel):
            name: str

        custom_id = uuid.uuid4()
        obj = TestModel(id=custom_id, name="test")
        assert obj.id == custom_id


class TestTimestampedModel:
    """Tests for the timestamped model base class."""

    def test_auto_generates_timestamps(self):
        """Timestamps are auto-generated on creation."""

        class TestModel(TimestampedModel):
            name: str

        obj = TestModel(name="test")
        assert isinstance(obj.created_at, datetime)
        assert isinstance(obj.updated_at, datetime)
        assert obj.created_at.tzinfo is not None
        assert obj.updated_at.tzinfo is not None

    def test_created_at_before_or_equal_updated_at(self):
        """created_at should be <= updated_at."""

        class TestModel(TimestampedModel):
            name: str

        obj = TestModel(name="test")
        assert obj.created_at <= obj.updated_at


class TestAuditableModel:
    """Tests for the auditable model base class."""

    def test_audit_fields_optional(self):
        """Audit fields are optional and default to None."""

        class TestModel(AuditableModel):
            name: str

        obj = TestModel(name="test")
        assert obj.created_by is None
        assert obj.updated_by is None

    def test_audit_fields_settable(self):
        """Audit fields can be explicitly set."""

        class TestModel(AuditableModel):
            name: str

        employee_id = uuid.uuid4()
        obj = TestModel(name="test", created_by=employee_id, updated_by=employee_id)
        assert obj.created_by == employee_id
        assert obj.updated_by == employee_id