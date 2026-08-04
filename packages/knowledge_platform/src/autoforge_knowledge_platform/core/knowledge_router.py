"""
Knowledge Router

Routes knowledge queries to appropriate sources and retrieval strategies.
As defined in Knowledge Platform Specification v1.0, Section 7.2.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.interfaces.knowledge_interfaces import IKnowledgeRouter
from autoforge_knowledge_platform.interfaces.query_interfaces import ISourceRegistry, IQueryProcessor
from autoforge_knowledge_platform.models import Source


class KnowledgeRouter(IKnowledgeRouter):
    """
    Routes knowledge queries to appropriate sources and retrieval strategies.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.2.
    """
    
    def __init__(
        self,
        query_processor: IQueryProcessor,
        source_registry: ISourceRegistry,
    ):
        """Initialize Knowledge Router with dependencies."""
        self.query_processor = query_processor
        self.source_registry = source_registry
    
    async def route(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route query to appropriate sources and strategies.
        
        Args:
            query: Query parameters
            
        Returns:
            Routing decision with sources and strategy
        """
        # Analyze query
        query_analysis = await self.analyze_query(query.get("query", ""))
        
        # Select sources
        sources = await self.select_sources(query_analysis)
        
        # Select strategy
        strategy = await self.select_strategy(query_analysis)
        
        return {
            "query": query,
            "query_analysis": query_analysis,
            "sources": sources,
            "strategy": strategy,
        }
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine intent and scope.
        
        Args:
            query: Query string
            
        Returns:
            Query analysis with type, domain, keywords, etc.
        """
        # Use query processor to analyze
        query_type = await self.query_processor.identify_query_type(query)
        domain = await self.query_processor.determine_domain(query)
        keywords = await self.query_processor.extract_keywords(query)
        entities = await self.query_processor.extract_entities(query)
        normalized_query = await self.query_processor.normalize_query(query)
        
        return {
            "original_query": query,
            "normalized_query": normalized_query,
            "type": query_type,
            "domain": domain,
            "keywords": keywords,
            "entities": entities,
        }
    
    async def select_sources(self, query_analysis: Dict[str, Any]) -> List[Source]:
        """
        Select appropriate sources for query.
        
        Args:
            query_analysis: Query analysis results
            
        Returns:
            List of selected sources
        """
        # Get active sources
        active_sources = await self.source_registry.get_active_sources()
        
        # Filter by domain match
        domain = query_analysis.get("domain", "")
        domain_sources = [s for s in active_sources if s.domain == domain] if domain else active_sources
        
        # Filter by query type compatibility
        query_type = query_analysis.get("type", "")
        compatible_sources = self._filter_by_query_type(domain_sources, query_type)
        
        # Filter by availability and trust
        available_sources = [s for s in compatible_sources if s.status == "active"]
        trusted_sources = [s for s in available_sources if s.trust_score >= 0.5]
        
        # Rank by historical performance and select top N
        ranked_sources = self._rank_sources(trusted_sources)
        top_sources = ranked_sources[:5]  # Select top 5 sources
        
        return top_sources
    
    async def select_strategy(self, query_analysis: Dict[str, Any]) -> str:
        """
        Select retrieval strategy for query.
        
        Args:
            query_analysis: Query analysis results
            
        Returns:
            Retrieval strategy (semantic, keyword, hybrid)
        """
        query_type = query_analysis.get("type", "")
        
        # Strategy selection rules from specification
        if query_type in ["conceptual", "exploratory"]:
            return "semantic"
        elif query_type in ["factual", "exact_match"]:
            return "keyword"
        else:
            return "hybrid"  # Default strategy
    
    def _filter_by_query_type(self, sources: List[Source], query_type: str) -> List[Source]:
        """Filter sources by query type compatibility."""
        # Source type prioritization from specification
        type_priority = {
            "factual": ["documentation", "code", "academic"],
            "procedural": ["documentation", "code", "community"],
            "conceptual": ["academic", "documentation", "expert"],
            "comparative": ["documentation", "community", "expert"],
            "best_practice": ["documentation", "expert", "community"],
            "troubleshooting": ["community", "documentation", "code"],
        }
        
        preferred_types = type_priority.get(query_type, list(set(s.type for s in sources)))
        
        # Prioritize preferred types but include all if needed
        prioritized = [s for s in sources if s.type in preferred_types]
        others = [s for s in sources if s.type not in preferred_types]
        
        return prioritized + others
    
    def _rank_sources(self, sources: List[Source]) -> List[Source]:
        """Rank sources by historical performance and trust."""
        return sorted(
            sources,
            key=lambda s: (s.trust_score, s.authority_score, s.historical_accuracy),
            reverse=True,
        )