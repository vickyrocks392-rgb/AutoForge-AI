"""
Knowledge graph models — nodes and edges for the platform's knowledge graph.

The knowledge graph represents structured relationships between domain
concepts, artifacts, tasks, and other entities. It enables semantic
reasoning, dependency analysis, and impact assessment.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import Field

from auto_forge_models.base import TimestampedModel
from auto_forge_models.enums import KnowledgeEdgeType


class KnowledgeNode(TimestampedModel):
    """
    A node in the platform's knowledge graph.

    Nodes represent entities, concepts, or artifacts in the knowledge
    graph. Each node has a type, label, and properties that describe it.
    """

    project_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the related Project, if applicable.",
    )
    node_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The type/category of this node (e.g. 'Task', 'Artifact', 'Concept').",
    )
    label: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Human-readable label for this node.",
    )
    description: str = Field(
        default="",
        max_length=4096,
        description="Detailed description of what this node represents.",
    )
    external_ref_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the external entity this node represents (e.g. a Task or Artifact).",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary properties associated with this node.",
    )
    embedding: list[float] | None = Field(
        default=None,
        description="Vector embedding of the node's content for similarity search.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering nodes.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )


class KnowledgeEdge(TimestampedModel):
    """
    A directed relationship between two knowledge nodes.

    Edges define how nodes in the knowledge graph relate to each other.
    They are typed (e.g. depends_on, produces, implements) and can carry
    properties describing the nature of the relationship.
    """

    source_node_id: uuid.UUID = Field(
        ...,
        description="UUID of the source KnowledgeNode.",
    )
    target_node_id: uuid.UUID = Field(
        ...,
        description="UUID of the target KnowledgeNode.",
    )
    edge_type: KnowledgeEdgeType = Field(
        ...,
        description="The type of relationship between source and target.",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Strength or weight of the relationship (0.0 to 1.0).",
    )
    label: str = Field(
        default="",
        max_length=256,
        description="Optional human-readable label for this edge.",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary properties associated with this edge.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata key-value store.",
    )