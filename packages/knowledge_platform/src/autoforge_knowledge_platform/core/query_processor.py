"""
Query Processor

Processes and normalizes knowledge queries as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.interfaces.query_interfaces import IQueryProcessor


class QueryProcessor(IQueryProcessor):
    """
    Processes and normalizes knowledge queries.
    
    As defined in Knowledge Platform Specification v1.0, Section 11.2.
    """
    
    async def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse and normalize query."""
        return {
            "original": query,
            "normalized": await self.normalize_query(query),
            "keywords": await self.extract_keywords(query),
            "entities": await self.extract_entities(query),
            "type": await self.identify_query_type(query),
            "domain": await self.determine_domain(query),
        }
    
    async def extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple keyword extraction (in real implementation, use NLP)
        stop_words = {"what", "how", "why", "when", "where", "who", "is", "are", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or"}
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords
    
    async def extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """Extract entities from query."""
        # Simple entity extraction (in real implementation, use NER)
        return []
    
    async def identify_query_type(self, query: str) -> str:
        """Identify query type (factual, procedural, conceptual, etc.)."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what is", "how does", "explain"]):
            return "conceptual"
        elif any(word in query_lower for word in ["how to", "steps", "procedure"]):
            return "procedural"
        elif any(word in query_lower for word in ["vs", "versus", "compare", "difference"]):
            return "comparative"
        elif any(word in query_lower for word in ["best", "optimal", "recommend"]):
            return "best_practice"
        elif any(word in query_lower for word in ["why", "error", "fix", "troubleshoot"]):
            return "troubleshooting"
        else:
            return "factual"
    
    async def determine_domain(self, query: str) -> str:
        """Determine domain and scope of query."""
        # Simple domain detection (in real implementation, use classification)
        domain_keywords = {
            "backend": ["api", "database", "server", "microservice"],
            "frontend": ["ui", "react", "vue", "angular", "css"],
            "devops": ["docker", "kubernetes", "ci/cd", "deployment"],
            "security": ["authentication", "authorization", "encryption", "vulnerability"],
            "testing": ["unit test", "integration test", "test coverage"],
        }
        
        query_lower = query.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return domain
        
        return "general"
    
    async def normalize_query(self, query: str) -> str:
        """Normalize query to canonical format."""
        # Convert to lowercase
        normalized = query.lower()
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        return normalized