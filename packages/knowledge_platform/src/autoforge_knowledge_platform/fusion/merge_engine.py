"""
Merge Engine

Merges complementary information as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.models import KnowledgeItem


class MergeEngine:
    """
    Merges complementary information from multiple sources.
    
    As defined in Knowledge Platform Specification v1.0, Section 14.6.
    """
    
    async def merge(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """
        Merge complementary information.
        
        Args:
            knowledge_items: List of knowledge items
            
        Returns:
            Merged knowledge items
        """
        if not knowledge_items:
            return []
        
        # Group items by similarity
        groups = await self._group_by_similarity(knowledge_items)
        
        # Merge each group
        merged_items = []
        for group in groups:
            if len(group) == 1:
                merged_items.append(group[0])
            else:
                merged = await self._merge_group(group)
                merged_items.append(merged)
        
        return merged_items
    
    async def _group_by_similarity(self, items: List[KnowledgeItem]) -> List[List[KnowledgeItem]]:
        """Group items by similarity."""
        # Simplified grouping - use embeddings in production
        groups = []
        seen = set()
        
        for item in items:
            if item.id in seen:
                continue
            
            group = [item]
            seen.add(item.id)
            
            # Find similar items
            for other in items:
                if other.id not in seen and self._is_similar(item, other):
                    group.append(other)
                    seen.add(other.id)
            
            groups.append(group)
        
        return groups
    
    def _is_similar(self, item1: KnowledgeItem, item2: KnowledgeItem) -> bool:
        """Check if two items are similar."""
        # Simplified similarity check - use embeddings in production
        if item1.domain != item2.domain:
            return False
        
        # Check content similarity
        words1 = set(item1.content.lower().split())
        words2 = set(item2.content.lower().split())
        overlap = len(words1 & words2) / max(len(words1 | words2), 1)
        
        return overlap > 0.5
    
    async def _merge_group(self, items: List[KnowledgeItem]) -> KnowledgeItem:
        """Merge a group of similar items."""
        # Use the highest trust item as base
        base_item = max(items, key=lambda x: x.trust_score)
        
        # Merge sources
        all_sources = list(set([base_item.source_id] + [s for item in items for s in item.sources]))
        
        # Create merged item
        merged = KnowledgeItem(
            type=base_item.type,
            content=base_item.content,
            summary=base_item.summary,
            domain=base_item.domain,
            tags=list(set(t for item in items for t in item.tags)),
            source_id=base_item.source_id,
            sources=all_sources,
            trust_score=base_item.trust_score,
            confidence_score=max(item.confidence_score for item in items),
            validation_status=base_item.validation_status,
            validation_confidence=base_item.validation_confidence,
            version=base_item.version,
            metadata=base_item.metadata,
            embeddings=base_item.embeddings,
            keywords=list(set(k for item in items for k in item.keywords)),
        )
        
        return merged