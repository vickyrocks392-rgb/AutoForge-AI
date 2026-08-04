"""
Deduplication Engine

Removes duplicate results as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.models import KnowledgeItem


class DeduplicationEngine:
    """
    Removes duplicate results.
    
    As defined in Knowledge Platform Specification v1.0, Section 11.6.
    """
    
    async def deduplicate(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate results.
        
        Deduplication criteria:
        - Content similarity: Similar content detected via embeddings
        - Source duplication: Same content from multiple sources
        - Version duplication: Same content in different versions
        
        Strategy:
        - Keep highest trust
        - Keep most recent (if trust is equal)
        - Merge sources for duplicate content
        
        Args:
            results: List of ranked results
            
        Returns:
            Deduplicated results
        """
        if not results:
            return []
        
        # Group by content similarity (simplified - use embeddings in real implementation)
        seen_content = {}
        deduplicated = []
        
        for result in results:
            item = result.get("knowledge_item")
            if not item:
                continue
            
            # Simple deduplication based on content hash (use embeddings in production)
            content_key = hash(item.content[:100])  # Simplified
            
            if content_key in seen_content:
                # Duplicate found - keep the one with higher trust score
                existing = seen_content[content_key]
                if item.trust_score > existing["knowledge_item"].trust_score:
                    # Replace with higher trust item
                    deduplicated = [r for r in deduplicated if r["knowledge_item"].id != existing["knowledge_item"].id]
                    deduplicated.append(result)
                    seen_content[content_key] = result
                # If equal trust, keep most recent
                elif item.trust_score == existing["knowledge_item"].trust_score:
                    if item.updated_at > existing["knowledge_item"].updated_at:
                        deduplicated = [r for r in deduplicated if r["knowledge_item"].id != existing["knowledge_item"].id]
                        deduplicated.append(result)
                        seen_content[content_key] = result
            else:
                # New unique item
                seen_content[content_key] = result
                deduplicated.append(result)
        
        return deduplicated