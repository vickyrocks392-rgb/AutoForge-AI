"""
Knowledge Fusion Components

Knowledge fusion engine and sub-components as defined in the Knowledge Platform Specification v1.0.
"""

from .knowledge_fusion import KnowledgeFusion
from .conflict_resolver import ConflictResolver
from .consensus_builder import ConsensusBuilder
from .merge_engine import MergeEngine
from .contradiction_detector import ContradictionDetector

__all__ = [
    "KnowledgeFusion",
    "ConflictResolver",
    "ConsensusBuilder",
    "MergeEngine",
    "ContradictionDetector",
]