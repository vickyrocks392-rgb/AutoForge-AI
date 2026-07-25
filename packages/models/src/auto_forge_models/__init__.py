"""
AutoForge AI — Canonical Domain Models.

This package defines the shared, infrastructure-independent domain models
for the entire AutoForge AI platform. Every subsystem depends on these models
as the universal language of the platform.
"""

from auto_forge_models.base import (
    AutoForgeBaseModel,
    TimestampedModel,
    IdentifiedModel,
    AuditableModel,
)
from auto_forge_models.enums import (
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
from auto_forge_models.project import Project
from auto_forge_models.task import Task, ResourceRequirements
from auto_forge_models.artifact import Artifact
from auto_forge_models.checkpoint import Checkpoint
from auto_forge_models.execution_session import ExecutionSession
from auto_forge_models.employee import Employee, ModelConfig
from auto_forge_models.review import Review
from auto_forge_models.event import Event
from auto_forge_models.model_profile import ModelProfile
from auto_forge_models.memory_entry import MemoryEntry
from auto_forge_models.knowledge import KnowledgeNode, KnowledgeEdge
from auto_forge_models.quality_gate import QualityGate

__all__ = [
    # Base
    "AutoForgeBaseModel",
    "TimestampedModel",
    "IdentifiedModel",
    "AuditableModel",
    # Enums
    "ArtifactType",
    "CheckpointType",
    "EmployeeRole",
    "EventType",
    "ExecutionStatus",
    "KnowledgeEdgeType",
    "MemoryType",
    "ModelProvider",
    "QualityGateStatus",
    "ReviewStatus",
    "TaskPriority",
    "TaskStatus",
    # Models
    "Project",
    "Task",
    "ResourceRequirements",
    "Artifact",
    "Checkpoint",
    "ExecutionSession",
    "Employee",
    "ModelConfig",
    "Review",
    "Event",
    "ModelProfile",
    "MemoryEntry",
    "KnowledgeNode",
    "KnowledgeEdge",
    "QualityGate",
]