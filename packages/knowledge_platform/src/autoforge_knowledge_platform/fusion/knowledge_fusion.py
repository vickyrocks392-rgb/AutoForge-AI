"""
Knowledge Fusion

Combines knowledge from multiple sources as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List

from autoforge_knowledge_platform.interfaces.knowledge_interfaces import IKnowledgeFusion
from autoforge_knowledge_platform.models import KnowledgeItem


class KnowledgeFusion(IKnowledgeFusion):
    """
    Combines knowledge from multiple sources.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.5.
    """
    
    def __init__(
        self,
        conflict_resolver: Any,
        consensus_builder: Any,
        merge_engine: Any,
        contradiction_detector: Any,
        trust_scorer: Any,
    ):
        """Initialize Knowledge Fusion with dependencies."""
        self.conflict_resolver = conflict_resolver
        self.consensus_builder = consensus_builder
        self.merge_engine = merge_engine
        self.contradiction_detector = contradiction_detector
        self.trust_scorer = trust_scorer
    
    async def fuse(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """
        Combine knowledge from multiple sources.
        
        Args:
            knowledge_items: List of knowledge items from multiple sources
            
        Returns:
            Fused knowledge items
        """
        if not knowledge_items:
            return []
        
        # Step 1: Detect conflicts
        conflicts = await self.detect_conflicts(knowledge_items)
        
        # Step 2: Resolve conflicts
        resolved_conflicts = await self.resolve_conflicts(conflicts)
        
        # Step 3: Build consensus
        consensus = await self.build_consensus(knowledge_items)
        
        # Step 4: Merge information
        merged_items = await self.merge_information(knowledge_items)
        
        # Step 5: Weight sources
        weighted_sources = await self.weight_sources(knowledge_items)
        
        return merged_items
    
    async def detect_conflicts(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """Detect conflicts between sources."""
        return await self.contradiction_detector.detect(knowledge_items)
    
    async def resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicts between sources."""
        return await self.conflict_resolver.resolve(conflicts)
    
    async def build_consensus(self, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Build consensus across sources."""
        return await self.consensus_builder.build(knowledge_items)
    
    async def merge_information(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """Merge complementary information."""
        return await self.merge_engine.merge(knowledge_items)
    
    async def weight_sources(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """Weight sources based on trust and relevance."""
        weighted = []
        for item in knowledge_items:
            weight = await self._calculate_source_weight(item)
            weighted.append({
                "knowledge_item": item,
                "weight": weight,
            })
        return weighted
    
    async def _calculate_source_weight(self, item: KnowledgeItem) -> float:
        """Calculate source weight."""
        # Source weight factors from specification:
        # - Trust score (40%)
        # - Relevance (30%)
        # - Recency (15%)
        # - Authority (10%)
        # - Community validation (5%)
        
        trust_score = item.trust_score * 0.40
        relevance = self._calculate_relevance(item) * 0.30
        recency = self._calculate_recency(item) * 0.15
        authority = self._calculate_authority(item) * 0.10
        community = self._calculate_community_validation(item) * 0.05
        
        return trust_score + relevance + recency + authority + community
    
    def _calculate_relevance(self, item: KnowledgeItem) -> float:
        """Calculate relevance score based on item metadata."""
        # Relevance is derived from item metadata and tags
        metadata = item.metadata or {}
        relevance = metadata.get("relevance_score", 0.5)
        return min(max(relevance, 0.0), 1.0)
    
    def _calculate_recency(self, item: KnowledgeItem) -> float:
        """Calculate recency score based on item age."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        age_days = (now - item.created_at).days if hasattr(item, 'created_at') else 0
        
        if age_days < 30:
            return 1.0
        elif age_days < 180:
            return 0.7
        elif age_days < 365:
            return 0.4
        else:
            return 0.1
    
    def _calculate_authority(self, item: KnowledgeItem) -> float:
        """Calculate authority score based on item metadata."""
        metadata = item.metadata or {}
        authority = metadata.get("authority_score", 0.5)
        return min(max(authority, 0.0), 1.0)
    
    def _calculate_community_validation(self, item: KnowledgeItem) -> float:
        """Calculate community validation score."""
        metadata = item.metadata or {}
        community = metadata.get("community_validation", 0.5)
        return min(max(community, 0.0), 1.0)