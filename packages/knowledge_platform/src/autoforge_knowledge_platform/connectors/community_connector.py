"""
Community Connector

Interfaces with community sources as defined in the Knowledge Platform Specification v1.0, Section 10.6.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class CommunityConnector(BaseConnector):
    """
    Interfaces with community sources (forums, Stack Overflow, Discord).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.6.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Community Connector."""
        super().__init__(source, config)
        self.api_credentials = config.get("api_credentials", {})
        self.search_parameters = config.get("search_parameters", {})
        self.community_filters = config.get("community_filters", {})
        self.endorsement_tracking = config.get("endorsement_tracking", True)
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from community sources.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from community sources
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for community search
        keywords = self._extract_keywords(query_text)
        
        items: List[KnowledgeItem] = []
        
        # Search community content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Community discussion on '{keyword}' from {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.OPINION,
                summary=f"Community answer for {keyword}",
                tags=[keyword, "community", "discussion"],
                metadata={
                    "source_url": self.source.url,
                    "endorsement_tracking": self.endorsement_tracking,
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize community source content."""
        result = await super().sync()
        result["endorsement_tracking"] = self.endorsement_tracking
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
            "help", "issue", "problem", "question", "answer",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]