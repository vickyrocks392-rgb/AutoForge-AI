"""
AutoForge Knowledge Platform

Implements the Knowledge Platform Specification v1.0.
"""

__version__ = "1.0.0"

from .models import (
    KnowledgeItem,
    Source,
    Citation,
    Evidence,
    TrustScore,
    ConfidenceScore,
    RetrievalResult,
    ResearchBrief,
    QueryResult,
    ValidationResult,
)
from .interfaces import (
    IKnowledgeEngine,
    IKnowledgeRouter,
    ISourceConnector,
    ISourceConnectorManager,
    IRetrievalPipeline,
    IKnowledgeFusion,
    ITrustScorer,
    ICitationManager,
    IKnowledgeValidator,
    IContextAssembler,
    IResearchBriefGenerator,
    IKnowledgeCache,
    IQueryProcessor,
    ISourceRegistry,
    IKnowledgeEventPublisher,
)
from .core import (
    KnowledgeEngine,
    KnowledgeRouter,
    SourceConnectorManager,
    QueryProcessor,
    SourceRegistry,
    KnowledgeEventPublisher,
    ResearchOrchestrator,
)
from .connectors import (
    DocumentationConnector,
    CodeConnector,
    AcademicConnector,
    ExpertConnector,
    CommunityConnector,
    ProprietaryConnector,
)
from .retrieval import (
    RetrievalPipeline,
    SemanticRetrieval,
    KeywordRetrieval,
    HybridRetrieval,
    MultiSourceRetrieval,
    RankEngine,
    FilterEngine,
    DeduplicationEngine,
)
from .fusion import (
    KnowledgeFusion,
    ConflictResolver,
    ConsensusBuilder,
    MergeEngine,
    ContradictionDetector,
)
from .trust import (
    TrustScorer,
    SourceTrustEvaluator,
    ContentTrustScorer,
    HistoricalAccuracyTracker,
    ExpertEndorsementWeighter,
    RecencyWeighter,
    CommunityValidationIntegrator,
)
from .citation import (
    CitationManager,
    CitationGenerator,
    CitationValidator,
    CitationFormatter,
    CitationIndexer,
    ProvenanceTracker,
)
from .validation import (
    KnowledgeValidator,
    FactChecker,
    CrossReferencer,
    ConsistencyChecker,
    OutdatedDetector,
    ContradictionFlagger,
)
from .context import ContextAssembler
from .research import ResearchBriefGenerator
from .cache import KnowledgeCache

__all__ = [
    # Models
    "KnowledgeItem",
    "Source",
    "Citation",
    "Evidence",
    "TrustScore",
    "ConfidenceScore",
    "RetrievalResult",
    "ResearchBrief",
    "QueryResult",
    "ValidationResult",
    # Interfaces
    "IKnowledgeEngine",
    "IKnowledgeRouter",
    "ISourceConnector",
    "ISourceConnectorManager",
    "IRetrievalPipeline",
    "IKnowledgeFusion",
    "ITrustScorer",
    "ICitationManager",
    "IKnowledgeValidator",
    "IContextAssembler",
    "IResearchBriefGenerator",
    "IKnowledgeCache",
    "IQueryProcessor",
    "ISourceRegistry",
    "IKnowledgeEventPublisher",
    # Core
    "KnowledgeEngine",
    "KnowledgeRouter",
    "SourceConnectorManager",
    "QueryProcessor",
    "SourceRegistry",
    "KnowledgeEventPublisher",
    "ResearchOrchestrator",
    # Connectors
    "DocumentationConnector",
    "CodeConnector",
    "AcademicConnector",
    "ExpertConnector",
    "CommunityConnector",
    "ProprietaryConnector",
    # Retrieval
    "RetrievalPipeline",
    "SemanticRetrieval",
    "KeywordRetrieval",
    "HybridRetrieval",
    "MultiSourceRetrieval",
    "RankEngine",
    "FilterEngine",
    "DeduplicationEngine",
    # Fusion
    "KnowledgeFusion",
    "ConflictResolver",
    "ConsensusBuilder",
    "MergeEngine",
    "ContradictionDetector",
    # Trust
    "TrustScorer",
    "SourceTrustEvaluator",
    "ContentTrustScorer",
    "HistoricalAccuracyTracker",
    "ExpertEndorsementWeighter",
    "RecencyWeighter",
    "CommunityValidationIntegrator",
    # Citation
    "CitationManager",
    "CitationGenerator",
    "CitationValidator",
    "CitationFormatter",
    "CitationIndexer",
    "ProvenanceTracker",
    # Validation
    "KnowledgeValidator",
    "FactChecker",
    "CrossReferencer",
    "ConsistencyChecker",
    "OutdatedDetector",
    "ContradictionFlagger",
    # Context
    "ContextAssembler",
    # Research
    "ResearchBriefGenerator",
    # Cache
    "KnowledgeCache",
]