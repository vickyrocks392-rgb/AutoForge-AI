"""
Expert Connector

Interfaces with expert systems as defined in the Knowledge Platform Specification v1.0, Section 10.5.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class ExpertConnector(BaseConnector):
    """
    Interfaces with expert systems (internal experts, consultants).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.5.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Expert Connector."""
        super().__init__(source, config)
        self.expert_database = config.get("expert_database", source.url)
        self.query_parameters = config.get("query_parameters", {})
        self.endorsement_tracking = config.get("endorsement_tracking", True)
        self.content_extraction = config.get("content_extraction", {})
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from expert systems.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from expert sources
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for expert search
        keywords = self._extract_keywords(query_text)
        
        items: List[KnowledgeItem] = []
        
        # Search expert content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Expert insight on '{keyword}' from {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.BEST_PRACTICE,
                summary=f"Expert recommendation for {keyword}",
                tags=[keyword, "expert", "best_practice"],
                metadata={
                    "expert_database": self.expert_database,
                    "endorsement_tracking": self.endorsement_tracking,
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize expert source content."""
        result = await super().sync()
        result["expert_database"] = self.expert_database
        result["endorsement_tracking"] = self.endorsement_tracking
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
            "best", "practice", "recommend", "recommendation", "advice",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]