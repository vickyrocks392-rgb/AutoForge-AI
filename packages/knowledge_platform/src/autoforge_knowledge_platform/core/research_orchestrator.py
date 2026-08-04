"""
Research Orchestrator

Coordinates multi-source research as defined in the Knowledge Platform Specification v1.0, Section 7.1 and 18.1.
Owned exclusively by the Knowledge Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from autoforge_knowledge_platform.models import (
    KnowledgeItem,
    ResearchBrief,
    RetrievalResult,
    Source,
)


class ResearchOrchestrator:
    """
    Coordinates multi-source research operations.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.1 and 18.1.
    Owned ONLY by the Knowledge Engine.
    
    Responsibilities:
    - Coordinate retrieval requests
    - Coordinate retrieval strategies
    - Coordinate Knowledge Fusion
    - Coordinate Knowledge Validation
    - Coordinate Research Brief generation
    
    Does NOT:
    - Execute engineering work
    - Own runtime state
    - Own orchestration outside the Knowledge Platform
    """
    
    def __init__(
        self,
        knowledge_router: Any,
        retrieval_pipeline: Any,
        knowledge_fusion: Any,
        knowledge_validator: Any,
        research_brief_generator: Any,
        citation_manager: Any,
        trust_scorer: Any,
    ):
        """Initialize Research Orchestrator with dependencies."""
        self.knowledge_router = knowledge_router
        self.retrieval_pipeline = retrieval_pipeline
        self.knowledge_fusion = knowledge_fusion
        self.knowledge_validator = knowledge_validator
        self.research_brief_generator = research_brief_generator
        self.citation_manager = citation_manager
        self.trust_scorer = trust_scorer
    
    async def orchestrate_research(
        self,
        topic: str,
        context: str,
        depth: str,
        sources: List[str],
        max_results: int,
    ) -> ResearchBrief:
        """
        Orchestrate multi-source research.
        
        Coordinates the full research pipeline:
        1. Analyze query to determine scope
        2. Identify relevant sources
        3. Dispatch retrieval requests to all sources
        4. Collect results from all sources
        5. Fuse knowledge from multiple sources
        6. Validate fused knowledge
        7. Generate research brief
        
        Args:
            topic: The research topic
            context: Optional context (project type, domain, constraints)
            depth: Research depth (quick, standard, deep)
            sources: Optional source preferences or exclusions
            max_results: Maximum number of results to include
            
        Returns:
            ResearchBrief: Structured research brief with findings, sources, and citations
        """
        # Step 1: Analyze query to determine scope
        query_analysis = await self.knowledge_router.analyze_query(topic)
        
        # Step 2: Route to appropriate sources via Knowledge Router
        routing_decision = await self.knowledge_router.route({
            "query": topic,
            "context": context,
            "depth": depth,
            "sources": sources,
            "max_results": max_results,
        })
        
        # Step 3: Retrieve knowledge from multiple sources
        retrieval_result = await self.retrieval_pipeline.retrieve(
            query=routing_decision["query"],
            sources=routing_decision["sources"],
            strategy=routing_decision["strategy"],
        )
        
        # Step 4: Fuse knowledge from multiple sources
        fused_knowledge = await self.knowledge_fusion.fuse(
            knowledge_items=retrieval_result.knowledge_items
        )
        
        # Step 5: Validate fused knowledge
        validated_knowledge = await self._validate_knowledge(fused_knowledge)
        
        # Step 6: Generate research brief
        research_brief = await self.research_brief_generator.orchestrate_research(
            topic=topic,
            context=context,
            depth=depth,
        )
        
        # Step 7: Generate citations for the brief
        citations = await self.citation_manager.track_citations_for_brief(research_brief)
        research_brief.citations = [c.to_dict() for c in citations]
        
        return research_brief
    
    async def _validate_knowledge(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[KnowledgeItem]:
        """Validate fused knowledge items."""
        validated_items = []
        for item in knowledge_items:
            validation_result = await self.knowledge_validator.fact_check(
                claim=item.content,
                sources=[],  # Sources are resolved by the validator
            )
            item.validation_status = "validated" if validation_result.get("valid") else "unvalidated"
            item.validation_confidence = validation_result.get("confidence", 0.0)
            validated_items.append(item)
        return validated_items
    
    async def coordinate_retrieval(
        self,
        query: Dict[str, Any],
        sources: List[Source],
        strategy: str,
    ) -> RetrievalResult:
        """Coordinate retrieval requests to sources."""
        return await self.retrieval_pipeline.retrieve(
            query=query,
            sources=sources,
            strategy=strategy,
        )
    
    async def coordinate_fusion(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[KnowledgeItem]:
        """Coordinate knowledge fusion."""
        return await self.knowledge_fusion.fuse(knowledge_items)
    
    async def coordinate_validation(
        self,
        knowledge_items: List[KnowledgeItem],
    ) -> List[KnowledgeItem]:
        """Coordinate knowledge validation."""
        return await self._validate_knowledge(knowledge_items)
    
    async def coordinate_brief_generation(
        self,
        topic: str,
        context: str,
        depth: str,
    ) -> ResearchBrief:
        """Coordinate research brief generation."""
        return await self.research_brief_generator.orchestrate_research(
            topic=topic,
            context=context,
            depth=depth,
        )