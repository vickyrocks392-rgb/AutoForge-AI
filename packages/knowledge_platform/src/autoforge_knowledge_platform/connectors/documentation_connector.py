"""
Documentation Connector

Interfaces with documentation sources as defined in the Knowledge Platform Specification v1.0, Section 10.2.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class DocumentationConnector(BaseConnector):
    """
    Interfaces with documentation sources (API docs, guides, tutorials).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.2.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Documentation Connector."""
        super().__init__(source, config)
        self.base_url = config.get("base_url", source.url)
        self.crawl_depth = config.get("crawl_depth", 3)
        self.content_types = config.get("content_types", ["markdown", "html", "pdf"])
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from documentation sources.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from documentation
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for documentation search
        keywords = self._extract_keywords(query_text)
        
        # In a real implementation, this would crawl documentation sites,
        # parse Markdown/HTML/PDF, and extract structured content.
        # This implementation provides the retrieval coordination logic.
        items: List[KnowledgeItem] = []
        
        # Search documentation content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Documentation reference for '{keyword}' from {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.REFERENCE,
                summary=f"Documentation entry for {keyword}",
                tags=[keyword, "documentation"],
                metadata={
                    "source_url": self.base_url,
                    "crawl_depth": self.crawl_depth,
                    "content_type": "markdown",
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize documentation source content."""
        result = await super().sync()
        result["content_types"] = self.content_types
        result["base_url"] = self.base_url
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        # Simple keyword extraction - split on whitespace and filter stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]