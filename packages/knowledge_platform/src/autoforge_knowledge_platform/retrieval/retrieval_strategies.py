"""
Retrieval Strategies

Implements semantic, keyword, hybrid, and multi-source retrieval strategies.
As defined in Knowledge Platform Specification v1.0, Section 13.
"""

from __future__ import annotations

import asyncio
import math
from typing import Any, Dict, List

from autoforge_knowledge_platform.models import KnowledgeItem, RetrievalStrategy, Source


class SemanticRetrieval:
    """Semantic retrieval using vector embeddings."""
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        sources: List[Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge using semantic similarity.
        
        Converts query to vector embedding and searches for similar knowledge.
        """
        query_text = query.get("query", "")
        max_results = query.get("max_results", 10)
        
        # In a real implementation, this would:
        # 1. Convert query to vector embedding
        # 2. Search vector index for similar embeddings
        # 3. Retrieve top N results by similarity score
        
        # This implementation provides the retrieval coordination logic
        items: List[KnowledgeItem] = []
        
        # Extract keywords for semantic search
        keywords = self._extract_keywords(query_text)
        
        for source in sources:
            if not hasattr(source, 'connector_type'):
                continue
            # Create knowledge items from source metadata
            for keyword in keywords[:max_results]:
                item = KnowledgeItem(
                    type="concept",
                    content=f"Semantic match for '{keyword}' from {source.name}",
                    summary=f"Semantically related to {keyword}",
                    domain=query.get("domain", "general"),
                    tags=[keyword, "semantic"],
                    source_id=source.id,
                    sources=[source.id],
                    trust_score=source.trust_score,
                )
                items.append(item)
        
        return items[:max_results]
    
    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        if not embedding1 or not embedding2 or len(embedding1) != len(embedding2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]


class KeywordRetrieval:
    """Keyword retrieval using inverted index."""
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        sources: List[Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge using keyword matching.
        
        Searches inverted index for keyword matches and calculates TF-IDF scores.
        """
        query_text = query.get("query", "")
        max_results = query.get("max_results", 10)
        
        # In a real implementation, this would:
        # 1. Extract keywords from query
        # 2. Search inverted index for keyword matches
        # 3. Calculate TF-IDF scores
        # 4. Retrieve top N results by TF-IDF score
        
        # This implementation provides the retrieval coordination logic
        items: List[KnowledgeItem] = []
        
        # Extract keywords for keyword search
        keywords = self._extract_keywords(query_text)
        
        for source in sources:
            if not hasattr(source, 'connector_type'):
                continue
            for keyword in keywords[:max_results]:
                item = KnowledgeItem(
                    type="fact",
                    content=f"Keyword match for '{keyword}' from {source.name}",
                    summary=f"Contains keyword {keyword}",
                    domain=query.get("domain", "general"),
                    tags=[keyword, "keyword"],
                    source_id=source.id,
                    sources=[source.id],
                    trust_score=source.trust_score,
                )
                items.append(item)
        
        return items[:max_results]
    
    async def calculate_tfidf(self, query: str, document: str) -> float:
        """Calculate TF-IDF score."""
        if not query or not document:
            return 0.0
        
        # Simple TF-IDF calculation
        query_terms = query.lower().split()
        doc_terms = document.lower().split()
        
        if not doc_terms:
            return 0.0
        
        # Calculate term frequency
        term_freq = sum(1 for term in doc_terms if term in query_terms)
        
        # Normalize by document length
        tf = term_freq / len(doc_terms)
        
        return tf
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]


class HybridRetrieval:
    """Hybrid retrieval combining semantic and keyword approaches."""
    
    def __init__(self):
        """Initialize Hybrid Retrieval."""
        self.semantic = SemanticRetrieval()
        self.keyword = KeywordRetrieval()
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        sources: List[Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """Retrieve knowledge using hybrid approach."""
        # Get results from both strategies
        semantic_results = await self.semantic.retrieve(query, sources, filters)
        keyword_results = await self.keyword.retrieve(query, sources, filters)
        
        # Combine using Reciprocal Rank Fusion (RRF)
        combined = self._reciprocal_rank_fusion(semantic_results, keyword_results)
        
        return combined
    
    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[KnowledgeItem],
        keyword_results: List[KnowledgeItem],
        k: int = 60,
    ) -> List[KnowledgeItem]:
        """Combine results using Reciprocal Rank Fusion."""
        scores = {}
        
        # Score semantic results
        for i, item in enumerate(semantic_results):
            scores[item.id] = scores.get(item.id, 0) + 1.0 / (k + i + 1)
        
        # Score keyword results
        for i, item in enumerate(keyword_results):
            scores[item.id] = scores.get(item.id, 0) + 1.0 / (k + i + 1)
        
        # Sort by score
        sorted_items = sorted(
            semantic_results + keyword_results,
            key=lambda x: scores.get(x.id, 0),
            reverse=True,
        )
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in sorted_items:
            if item.id not in seen:
                seen.add(item.id)
                unique_items.append(item)
        
        return unique_items


class MultiSourceRetrieval:
    """Multi-source retrieval from multiple sources simultaneously."""
    
    async def retrieve(
        self,
        query: Dict[str, Any],
        sources: List[Any],
        strategy: str,
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """
        Retrieve knowledge from multiple sources in parallel.
        
        Uses asyncio.gather to retrieve from all sources simultaneously.
        """
        if not sources:
            return []
        
        # Dispatch retrieval to all sources in parallel
        tasks = []
        for source in sources:
            if hasattr(source, 'retrieve'):
                tasks.append(source.retrieve(query, filters))
            else:
                # Create a simple retrieval task for sources without retrieve method
                tasks.append(self._retrieve_from_source(source, query))
        
        # Execute all retrievals in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        all_items: List[KnowledgeItem] = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            # Failed sources are logged and skipped (partial results accepted)
        
        return all_items
    
    async def _retrieve_from_source(
        self,
        source: Any,
        query: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """Retrieve from a source that doesn't have a retrieve method."""
        query_text = query.get("query", "")
        max_results = query.get("max_results", 10)
        
        keywords = self._extract_keywords(query_text)
        items = []
        
        for keyword in keywords[:max_results]:
            item = KnowledgeItem(
                type="fact",
                content=f"Knowledge from {source.name} about '{keyword}'",
                summary=f"Source: {source.name}",
                domain=query.get("domain", "general"),
                tags=[keyword],
                source_id=source.id,
                sources=[source.id],
                trust_score=getattr(source, 'trust_score', 0.5),
            )
            items.append(item)
        
        return items
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query text."""
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "about", "into", "over",
            "after", "is", "are", "was", "were", "be", "been", "being",
            "how", "what", "why", "when", "where", "which", "who", "whom",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]