"""
Citation Manager

Manages citations and provenance as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.interfaces.knowledge_interfaces import ICitationManager
from autoforge_knowledge_platform.models import Citation, KnowledgeItem, ResearchBrief, Source


class CitationManager(ICitationManager):
    """
    Manages citations and provenance.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.7.
    """
    
    def __init__(
        self,
        citation_generator: Any,
        citation_validator: Any,
        citation_formatter: Any,
        citation_indexer: Any,
        provenance_tracker: Any,
    ):
        """Initialize Citation Manager with dependencies."""
        self.citation_generator = citation_generator
        self.citation_validator = citation_validator
        self.citation_formatter = citation_formatter
        self.citation_indexer = citation_indexer
        self.provenance_tracker = provenance_tracker
    
    async def create_citation(
        self,
        knowledge_item: KnowledgeItem,
        source: Source,
        context: str,
    ) -> Citation:
        """Create a citation for knowledge."""
        return await self.citation_generator.generate(knowledge_item, source, context)
    
    async def track_citations(
        self,
        knowledge_item: KnowledgeItem,
    ) -> List[Citation]:
        """Track citations for knowledge items."""
        citations = []
        for source_id in knowledge_item.sources:
            source = Source(id=source_id)
            citation = await self.citation_generator.generate(
                knowledge_item,
                source,
                knowledge_item.content[:200],
            )
            citations.append(citation)
        return citations
    
    async def track_citations_for_brief(
        self,
        research_brief: ResearchBrief,
    ) -> List[Citation]:
        """Track citations for a research brief."""
        citations = []
        for source_id in research_brief.sources:
            source = Source(id=source_id)
            # Create a minimal knowledge item for citation generation
            knowledge_item = KnowledgeItem(
                type="fact",
                content=research_brief.executive_summary,
                summary=research_brief.executive_summary[:200],
                domain="general",
                source_id=source_id,
                sources=[source_id],
            )
            citation = await self.citation_generator.generate(
                knowledge_item,
                source,
                research_brief.executive_summary[:200],
            )
            citations.append(citation)
        return citations
    
    async def validate_citation(self, citation: Citation) -> Dict[str, Any]:
        """Validate citation accuracy."""
        return await self.citation_validator.validate(citation)
    
    async def format_citation(
        self,
        citation: Citation,
        format_type: str,
    ) -> str:
        """Format citation in specified format."""
        return await self.citation_formatter.format(citation, format_type)
    
    async def index_citation(self, citation: Citation) -> str:
        """Index citation for retrieval."""
        return await self.citation_indexer.index(citation)
    
    async def track_provenance(
        self,
        knowledge_item: KnowledgeItem,
        source: Source,
    ) -> Dict[str, Any]:
        """Track knowledge provenance."""
        return await self.provenance_tracker.track(knowledge_item, source)
    
    async def record_provenance(
        self,
        knowledge_item: KnowledgeItem,
    ) -> List[Dict[str, Any]]:
        """Record complete provenance chain."""
        provenance = []
        for source_id in knowledge_item.sources:
            source = Source(id=source_id)
            result = await self.provenance_tracker.track(knowledge_item, source)
            provenance.append(result)
        return provenance