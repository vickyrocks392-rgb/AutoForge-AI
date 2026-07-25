"""
AutoForge AI — Canonical Domain Models.

This package defines the shared, infrastructure-independent domain models
for the entire AutoForge AI platform. Every subsystem depends on these models
as the universal language of the platform.
"""

from autoforge_models.base import (
    AutoForgeBaseModel,
    TimestampedModel,
    IdentifiedModel,
    AuditableModel,
)
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
from autoforge_models.project import Project
from autoforge_models.task import Task, ResourceRequirements
from autoforge_models.artifact import Artifact
from autoforge_models.checkpoint import Checkpoint
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.employee import Employee, ModelConfig
from autoforge_models.review import Review
from autoforge_models.event import Event
from autoforge_models.model_profile import ModelProfile
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.knowledge import KnowledgeNode, KnowledgeEdge
from autoforge_models.quality_gate import QualityGate

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