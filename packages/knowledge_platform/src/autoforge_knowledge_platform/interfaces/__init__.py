"""
Knowledge Platform Interfaces

Public interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from .knowledge_interfaces import (
    IKnowledgeEngine,
    IKnowledgeRouter,
    IRetrievalPipeline,
    IKnowledgeFusion,
    ITrustScorer,
    ICitationManager,
    IKnowledgeValidator,
    IContextAssembler,
    IResearchBriefGenerator,
)
from .connector_interfaces import (
    ISourceConnector,
    ISourceConnectorManager,
)
from .cache_interfaces import (
    IKnowledgeCache,
)
from .query_interfaces import (
    IQueryProcessor,
    ISourceRegistry,
)
from .event_interfaces import (
    IKnowledgeEventPublisher,
)

__all__ = [
    "IKnowledgeEngine",
    "IKnowledgeRouter",
    "IRetrievalPipeline",
    "IKnowledgeFusion",
    "ITrustScorer",
    "ICitationManager",
    "IKnowledgeValidator",
    "IContextAssembler",
    "IResearchBriefGenerator",
    "ISourceConnector",
    "ISourceConnectorManager",
    "IKnowledgeCache",
    "IQueryProcessor",
    "ISourceRegistry",
    "IKnowledgeEventPublisher",
]