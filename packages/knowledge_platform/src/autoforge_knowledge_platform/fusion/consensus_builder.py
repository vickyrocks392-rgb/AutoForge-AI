"""
Consensus Builder

Builds consensus across sources as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.models import KnowledgeItem


class ConsensusBuilder:
    """
    Builds consensus across sources.
    
    As defined in Knowledge Platform Specification v1.0, Section 14.4.
    """
    
    async def build(self, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """
        Build consensus across sources.
        
        Consensus levels:
        - Strong Consensus (0.8-1.0): All or most sources agree
        - Moderate Consensus (0.5-0.79): Majority of sources agree
        - Weak Consensus (0.2-0.49): Limited agreement
        - No Consensus (0.0-0.19): Sources disagree or insufficient sources
        
        Args:
            knowledge_items: List of knowledge items
            
        Returns:
            Consensus information
        """
        if not knowledge_items:
            return {
                "level": "none",
                "score": 0.0,
                "supporting_sources": [],
                "contradicting_sources": [],
            }
        
        # Group similar claims
        claim_groups = await self._group_similar_claims(knowledge_items)
        
        # Calculate consensus for each group
        consensus_results = []
        for claim, items in claim_groups.items():
            consensus_score = len(items) / len(knowledge_items)
            consensus_level = self._determine_consensus_level(consensus_score)
            
            consensus_results.append({
                "claim": claim,
                "consensus_score": consensus_score,
                "consensus_level": consensus_level,
                "supporting_sources": [item.source_id for item in items],
                "source_count": len(items),
            })
        
        # Overall consensus
        overall_score = sum(r["consensus_score"] for r in consensus_results) / max(len(consensus_results), 1)
        overall_level = self._determine_consensus_level(overall_score)
        
        return {
            "level": overall_level,
            "score": overall_score,
            "details": consensus_results,
            "total_sources": len(knowledge_items),
        }
    
    def _determine_consensus_level(self, score: float) -> str:
        """Determine consensus level from score."""
        if score >= 0.8:
            return "strong"
        elif score >= 0.5:
            return "moderate"
        elif score >= 0.2:
            return "weak"
        else:
            return "none"
    
    async def _group_similar_claims(self, knowledge_items: List[KnowledgeItem]) -> Dict[str, List[KnowledgeItem]]:
        """Group similar claims together."""
        # Simplified grouping - use embeddings in production
        groups = {}
        for item in knowledge_items:
            # Use first 100 chars as claim key (use semantic similarity in production)
            claim_key = item.content[:100]
            if claim_key not in groups:
                groups[claim_key] = []
            groups[claim_key].append(item)
        return groups