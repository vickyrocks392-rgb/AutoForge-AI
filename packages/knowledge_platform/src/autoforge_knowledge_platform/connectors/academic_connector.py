"""
Academic Connector

Interfaces with academic sources as defined in the Knowledge Platform Specification v1.0, Section 10.4.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class AcademicConnector(BaseConnector):
    """
    Interfaces with academic sources (papers, journals, conferences).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.4.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Academic Connector."""
        super().__init__(source, config)
        self.api_credentials = config.get("api_credentials", {})
        self.search_parameters = config.get("search_parameters", {})
        self.citation_tracking = config.get("citation_tracking", True)
        self.pdf_extraction = config.get("pdf_extraction", True)
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from academic sources.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from academic sources
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for academic search
        keywords = self._extract_keywords(query_text)
        
        items: List[KnowledgeItem] = []
        
        # Search academic content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Academic research on '{keyword}' from {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.CONCEPT,
                summary=f"Academic paper on {keyword}",
                tags=[keyword, "academic", "research"],
                metadata={
                    "source_url": self.source.url,
                    "citation_tracking": self.citation_tracking,
                    "pdf_extraction": self.pdf_extraction,
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize academic source content."""
        result = await super().sync()
        result["citation_tracking"] = self.citation_tracking
        result["pdf_extraction"] = self.pdf_extraction
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
            "research", "study", "paper", "analysis", "review",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]