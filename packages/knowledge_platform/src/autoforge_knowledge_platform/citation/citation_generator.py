"""
Citation Generator

Generates citations for knowledge as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict
from autoforge_knowledge_platform.models import Citation, CitationFormat, CitationType, KnowledgeItem, Source


class CitationGenerator:
    """
    Generates citations for knowledge.
    
    As defined in Knowledge Platform Specification v1.0, Section 18.1.
    """
    
    async def generate(
        self,
        knowledge_item: KnowledgeItem,
        source: Source,
        context: str,
    ) -> Citation:
        """
        Generate a citation for knowledge.
        
        Args:
            knowledge_item: Knowledge item to cite
            source: Source of the knowledge
            context: Context in which knowledge is used
            
        Returns:
            Citation: Generated citation
        """
        # Determine citation format based on source type
        format_type = self._determine_format(source)
        
        # Create citation
        citation = Citation(
            knowledge_item_id=knowledge_item.id,
            source_id=source.id,
            type=CitationType.DIRECT,
            location=source.url,
            excerpt=knowledge_item.content[:200],
            context=context,
            format=format_type,
            formatted_citation=self._format_citation(knowledge_item, source, format_type),
            metadata={},
        )
        
        return citation
    
    def _determine_format(self, source: Source) -> CitationFormat:
        """Determine citation format based on source type."""
        source_type = str(source.type)
        if source_type == "academic":
            return CitationFormat.ACADEMIC
        elif source_type == "code":
            return CitationFormat.CODE
        elif source_type == "proprietary":
            return CitationFormat.INTERNAL
        else:
            return CitationFormat.TECHNICAL
    
    def _format_citation(
        self,
        knowledge_item: KnowledgeItem,
        source: Source,
        format_type: CitationFormat,
    ) -> str:
        """Format citation string based on format type."""
        if format_type == CitationFormat.ACADEMIC:
            return f"{source.name}. {knowledge_item.summary}. {source.url}"
        elif format_type == CitationFormat.CODE:
            return f"{source.name}. {knowledge_item.summary}. {source.url}"
        elif format_type == CitationFormat.INTERNAL:
            return f"Document ID: {source.id}. {source.name}. Internal Knowledge Base."
        else:
            return f"{knowledge_item.summary}. {source.name}. {source.url}. Accessed: {knowledge_item.created_at.isoformat()}"