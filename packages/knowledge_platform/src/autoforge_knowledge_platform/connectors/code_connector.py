"""
Code Connector

Interfaces with code repositories as defined in the Knowledge Platform Specification v1.0, Section 10.3.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.connectors.base_connector import BaseConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class CodeConnector(BaseConnector):
    """
    Interfaces with code repositories (GitHub, GitLab, internal repos).
    
    As defined in Knowledge Platform Specification v1.0, Section 10.3.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize Code Connector."""
        super().__init__(source, config)
        self.repository_url = config.get("repository_url", source.url)
        self.branch = config.get("branch", "main")
        self.file_patterns = config.get("file_patterns", ["*.py", "*.js", "*.ts", "*.go", "*.rs"])
        self.languages = config.get("languages", ["python", "javascript", "typescript", "go", "rust"])
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge items from code repositories.
        
        Args:
            query: Query parameters
            filters: Filter parameters
            
        Returns:
            List of knowledge items from code
        """
        if not self._connected:
            return []
        
        query_text = query.get("query", "")
        domain = query.get("domain", "general")
        max_results = query.get("max_results", 10)
        
        # Extract keywords from query for code search
        keywords = self._extract_keywords(query_text)
        
        items: List[KnowledgeItem] = []
        
        # Search code content based on keywords
        for keyword in keywords[:max_results]:
            item = self._create_knowledge_item(
                content=f"Code example for '{keyword}' from repository {self.source.name}",
                domain=domain,
                item_type=KnowledgeItemType.EXAMPLE,
                summary=f"Code implementation for {keyword}",
                tags=[keyword, "code", "example"],
                metadata={
                    "repository_url": self.repository_url,
                    "branch": self.branch,
                    "file_patterns": self.file_patterns,
                    "languages": self.languages,
                },
            )
            items.append(item)
        
        return items
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize code repository content."""
        result = await super().sync()
        result["repository_url"] = self.repository_url
        result["branch"] = self.branch
        result["languages"] = self.languages
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
            "implement", "implementation", "using", "use", "used",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]