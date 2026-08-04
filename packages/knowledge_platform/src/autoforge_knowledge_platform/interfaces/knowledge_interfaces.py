"""
Knowledge Platform Core Interfaces

Core component interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from autoforge_knowledge_platform.models import (
    Citation,
    ConfidenceScore,
    Evidence,
    KnowledgeItem,
    QueryResult,
    ResearchBrief,
    RetrievalResult,
    Source,
    TrustScore,
    ValidationResult,
)


class IKnowledgeEngine(ABC):
    """Interface for the Knowledge Engine."""
    
    @abstractmethod
    async def research(
        self,
        topic: str,
        context: str,
        depth: str,
        sources: List[str],
        max_results: int,
    ) -> ResearchBrief:
        """Perform research on a topic and return a structured research brief."""
        pass
    
    @abstractmethod
    async def query(
        self,
        query: str,
        type: str,
        filters: Dict[str, Any],
        max_results: int,
        min_trust: float,
    ) -> QueryResult:
        """Query the knowledge base for specific information."""
        pass
    
    @abstractmethod
    async def validate(
        self,
        claim: str,
        sources: List[str],
        strictness: str,
    ) -> ValidationResult:
        """Validate knowledge against trusted sources."""
        pass
    
    @abstractmethod
    async def get_trust_score(
        self,
        target_id: UUID,
        target_type: str,
    ) -> TrustScore:
        """Query trust scores for sources or knowledge items."""
        pass
    
    @abstractmethod
    async def get_citations(
        self,
        knowledge_item_id: UUID,
        depth: str,
    ) -> Dict[str, Any]:
        """Look up citations for a knowledge item."""
        pass
    
    @abstractmethod
    async def ingest(
        self,
        source_id: UUID,
        content: str,
        metadata: Dict[str, Any],
    ) -> KnowledgeItem:
        """Ingest knowledge from external sources."""
        pass
    
    @abstractmethod
    async def promote(self, learning: Dict[str, Any]) -> KnowledgeItem:
        """Promote validated learning to knowledge base."""
        pass


class IKnowledgeRouter(ABC):
    """Interface for the Knowledge Router."""
    
    @abstractmethod
    async def route(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Route query to appropriate sources and strategies."""
        pass
    
    @abstractmethod
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine intent and scope."""
        pass
    
    @abstractmethod
    async def select_sources(self, query_analysis: Dict[str, Any]) -> List[Source]:
        """Select appropriate sources for query."""
        pass
    
    @abstractmethod
    async def select_strategy(self, query_analysis: Dict[str, Any]) -> str:
        """Select retrieval strategy for query."""
        pass


class IRetrievalPipeline(ABC):
    """Interface for the Retrieval Pipeline."""
    
    @abstractmethod
    async def retrieve(
        self,
        query: Dict[str, Any],
        sources: List[Source],
        strategy: str,
    ) -> RetrievalResult:
        """Retrieve knowledge from sources."""
        pass
    
    @abstractmethod
    async def rank(
        self,
        results: List[KnowledgeItem],
        query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Rank results by relevance and trust."""
        pass
    
    @abstractmethod
    async def filter(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter results by criteria."""
        pass
    
    @abstractmethod
    async def deduplicate(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Remove duplicate results."""
        pass


class IKnowledgeFusion(ABC):
    """Interface for Knowledge Fusion."""
    
    @abstractmethod
    async def fuse(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[KnowledgeItem]:
        """Combine knowledge from multiple sources."""
        pass
    
    @abstractmethod
    async def detect_conflicts(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between sources."""
        pass
    
    @abstractmethod
    async def resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts between sources."""
        pass
    
    @abstractmethod
    async def build_consensus(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> Dict[str, Any]:
        """Build consensus across sources."""
        pass
    
    @abstractmethod
    async def merge_information(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[KnowledgeItem]:
        """Merge complementary information."""
        pass
    
    @abstractmethod
    async def weight_sources(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[Dict[str, Any]]:
        """Weight sources based on trust and relevance."""
        pass


class ITrustScorer(ABC):
    """Interface for Trust Scorer."""
    
    @abstractmethod
    async def calculate_source_trust(self, source: Source) -> TrustScore:
        """Evaluate trustworthiness of a knowledge source."""
        pass
    
    @abstractmethod
    async def calculate_content_trust(
        self,
        knowledge_item: KnowledgeItem,
    ) -> TrustScore:
        """Score individual knowledge items."""
        pass
    
    @abstractmethod
    async def track_historical_accuracy(self, source: Source) -> Dict[str, Any]:
        """Track source accuracy over time."""
        pass
    
    @abstractmethod
    async def weight_expert_endorsement(
        self,
        knowledge_item: KnowledgeItem,
    ) -> float:
        """Weight expert-endorsed content higher."""
        pass
    
    @abstractmethod
    async def weight_recency(self, knowledge_item: KnowledgeItem) -> float:
        """Weight recent content higher for time-sensitive topics."""
        pass
    
    @abstractmethod
    async def incorporate_community_validation(
        self,
        knowledge_item: KnowledgeItem,
    ) -> float:
        """Incorporate community validation signals."""
        pass


class ICitationManager(ABC):
    """Interface for Citation Manager."""
    
    @abstractmethod
    async def track_citations(
        self,
        knowledge_item: KnowledgeItem,
    ) -> List[Citation]:
        """Track citations for knowledge items."""
        pass
    
    @abstractmethod
    async def record_provenance(
        self,
        knowledge_item: KnowledgeItem,
    ) -> List[Dict[str, Any]]:
        """Record complete provenance chain."""
        pass
    
    @abstractmethod
    async def format_citation(
        self,
        citation: Citation,
        format: str,
    ) -> str:
        """Format citations according to standards."""
        pass
    
    @abstractmethod
    async def attribute_source(
        self,
        knowledge_item: KnowledgeItem,
    ) -> Dict[str, Any]:
        """Attribute knowledge to original sources."""
        pass
    
    @abstractmethod
    async def validate_citation(self, citation: Citation) -> Dict[str, Any]:
        """Validate citation accuracy."""
        pass
    
    @abstractmethod
    async def index_citations(self, citations: List[Citation]) -> None:
        """Index citations for retrieval."""
        pass


class IKnowledgeValidator(ABC):
    """Interface for Knowledge Validator."""
    
    @abstractmethod
    async def fact_check(
        self,
        claim: str,
        sources: List[Source],
    ) -> Dict[str, Any]:
        """Verify factual claims against trusted sources."""
        pass
    
    @abstractmethod
    async def cross_reference(
        self,
        knowledge_item: KnowledgeItem,
    ) -> Dict[str, Any]:
        """Cross-reference claims across multiple sources."""
        pass
    
    @abstractmethod
    async def check_consistency(
        self,
        knowledge_item: KnowledgeItem,
    ) -> Dict[str, Any]:
        """Check internal consistency of knowledge."""
        pass
    
    @abstractmethod
    async def detect_outdated_content(
        self,
        knowledge_item: KnowledgeItem,
    ) -> Dict[str, Any]:
        """Detect outdated or superseded information."""
        pass
    
    @abstractmethod
    async def flag_contradictions(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[Dict[str, Any]]:
        """Flag contradictory information."""
        pass
    
    @abstractmethod
    async def score_validation(
        self,
        validation_result: Dict[str, Any],
    ) -> float:
        """Score validation confidence."""
        pass


class IContextAssembler(ABC):
    """Interface for Context Assembler."""
    
    @abstractmethod
    async def gather_context(self, task: Dict[str, Any]) -> List[KnowledgeItem]:
        """Gather relevant knowledge for a task."""
        pass
    
    @abstractmethod
    async def filter_context(
        self,
        knowledge_items: List[KnowledgeItem],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """Filter knowledge by relevance and trust."""
        pass
    
    @abstractmethod
    async def rank_context(
        self,
        knowledge_items: List[KnowledgeItem],
        task: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Rank knowledge by importance."""
        pass
    
    @abstractmethod
    async def summarize_context(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> str:
        """Summarize large knowledge sets."""
        pass
    
    @abstractmethod
    async def package_context(
        self,
        knowledge_items: List[KnowledgeItem],
        format: str,
    ) -> Dict[str, Any]:
        """Package knowledge for consumption."""
        pass
    
    @abstractmethod
    async def enrich_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with related knowledge."""
        pass


class IResearchBriefGenerator(ABC):
    """Interface for Research Brief Generator."""
    
    @abstractmethod
    async def orchestrate_research(
        self,
        topic: str,
        context: str,
        depth: str,
    ) -> ResearchBrief:
        """Orchestrate multi-source research."""
        pass
    
    @abstractmethod
    async def synthesize_information(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> Dict[str, Any]:
        """Synthesize information from multiple sources."""
        pass
    
    @abstractmethod
    async def structure_brief(
        self,
        synthesized_information: Dict[str, Any],
    ) -> ResearchBrief:
        """Structure research into coherent briefs."""
        pass
    
    @abstractmethod
    async def extract_findings(
        self,
        synthesized_information: Dict[str, Any],
    ) -> List[str]:
        """Extract key findings from research."""
        pass
    
    @abstractmethod
    async def generate_recommendations(
        self,
        findings: List[str],
    ) -> List[str]:
        """Generate recommendations based on research."""
        pass
    
    @abstractmethod
    async def format_brief(
        self,
        research_brief: ResearchBrief,
        format: str,
    ) -> str:
        """Format briefs for consumption."""
        pass