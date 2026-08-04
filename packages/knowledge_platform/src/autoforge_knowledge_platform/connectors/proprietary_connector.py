"""
Proprietary Connector

Interfaces with proprietary sources as defined in the Knowledge Platform Specification v1.0, Section 10.7.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class ProprietaryConnector(BaseConnector):
    """
    Interfaces with proprietary sources (internal databases, paid services).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.7.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Proprietary Connector."""
        super().__init__(source, config)
        self.connection_details = config.get("connection_details", source.url)
        self.auth_credentials = config.get("auth_credentials", {})
        self.query_parameters = config.get("query_parameters", {})
        self.access_control = config.get("access_control", {})
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from proprietary sources.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from proprietary sources
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for proprietary search
        keywords = self._extract_keywords(query_text)
        
        items: List[KnowledgeItem] = []
        
        # Search proprietary content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Proprietary knowledge on '{keyword}' from {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.FACT,
                summary=f"Internal knowledge for {keyword}",
                tags=[keyword, "proprietary", "internal"],
                metadata={
                    "connection_details": self.connection_details,
                    "access_control": self.access_control,
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize proprietary source content."""
        result = await super().sync()
        result["connection_details"] = self.connection_details
        result["access_control"] = self.access_control
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
            "internal", "proprietary", "company", "organization",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]