"""
Rank Engine

Ranks retrieval results by relevance and trust as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from autoforge_knowledge_platform.models import KnowledgeItem


class RankEngine:
    """
    Ranks retrieval results by relevance and trust.
    
    As defined in Knowledge Platform Specification v1.0, Section 11.4.
    """
    
    async def rank(
        self,
        results: List[KnowledgeItem],
        query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Rank results by relevance and trust.
        
        Ranking factors:
        - Relevance (50%): semantic similarity, keyword match, domain relevance
        - Trust (30%): source trust, knowledge item trust, validation status
        - Freshness (10%): content age, last updated timestamp
        - Access Frequency (5%): access count, recent access frequency
        - Cross-Reference Count (5%): number of sources confirming
        
        Args:
            results: List of knowledge items
            query: Query parameters
            
        Returns:
            Ranked results with scores
        """
        ranked_results = []
        
        for item in results:
            # Calculate component scores
            relevance_score = await self._calculate_relevance(item, query)
            trust_score = item.trust_score
            freshness_score = await self._calculate_freshness(item)
            access_frequency_score = await self._calculate_access_frequency(item)
            cross_reference_score = await self._calculate_cross_reference(item)
            
            # Calculate final score
            final_score = (
                relevance_score * 0.50 +
                trust_score * 0.30 +
                freshness_score * 0.10 +
                access_frequency_score * 0.05 +
                cross_reference_score * 0.05
            )
            
            ranked_results.append({
                "knowledge_item": item,
                "relevance_score": relevance_score,
                "trust_score": trust_score,
                "freshness_score": freshness_score,
                "access_frequency_score": access_frequency_score,
                "cross_reference_score": cross_reference_score,
                "final_score": final_score,
            })
        
        # Sort by final score
        ranked_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return ranked_results
    
    async def _calculate_relevance(self, item: KnowledgeItem, query: Dict[str, Any]) -> float:
        """Calculate relevance score based on keyword overlap and domain match."""
        query_text = query.get("query", "").lower()
        domain = query.get("domain", "")
        
        # Keyword overlap score
        item_text = f"{item.content} {item.summary} {' '.join(item.tags)}".lower()
        query_terms = set(query_text.split())
        item_terms = set(item_text.split())
        
        if not query_terms:
            return 0.5
        
        overlap = len(query_terms & item_terms) / len(query_terms)
        
        # Domain match bonus
        domain_bonus = 0.2 if domain and item.domain == domain else 0.0
        
        return min(overlap + domain_bonus, 1.0)
    
    async def _calculate_freshness(self, item: KnowledgeItem) -> float:
        """Calculate freshness score based on content age."""
        now = datetime.now(timezone.utc)
        age_days = (now - item.created_at).days if hasattr(item, 'created_at') else 0
        
        if age_days < 30:
            return 1.0
        elif age_days < 90:
            return 0.8
        elif age_days < 180:
            return 0.6
        elif age_days < 365:
            return 0.4
        else:
            return 0.2
    
    async def _calculate_access_frequency(self, item: KnowledgeItem) -> float:
        """Calculate access frequency score."""
        return min(item.access_count / 100.0, 1.0)
    
    async def _calculate_cross_reference(self, item: KnowledgeItem) -> float:
        """Calculate cross-reference score based on number of sources."""
        return min(len(item.sources) / 10.0, 1.0)