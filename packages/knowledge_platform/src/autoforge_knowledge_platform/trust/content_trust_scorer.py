"""
Content Trust Scorer

Scores individual knowledge items as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict
from autoforge_knowledge_platform.models import KnowledgeItem, TrustScore


class ContentTrustScorer:
    """
    Scores individual knowledge items.
    
    As defined in Knowledge Platform Specification v1.0, Section 15.2.
    """
    
    async def score(self, knowledge_item: KnowledgeItem) -> TrustScore:
        """
        Score individual knowledge items.
        
        Scoring factors:
        - Source trust (50%)
        - Validation status (25%)
        - Cross-reference count (15%)
        - Recency (10%)
        
        Args:
            knowledge_item: Knowledge item to score
            
        Returns:
            TrustScore: Calculated trust score
        """
        # Calculate factor scores
        source_trust = knowledge_item.trust_score * 0.50
        validation_status = self._calculate_validation_score(knowledge_item) * 0.25
        cross_reference = self._calculate_cross_reference_score(knowledge_item) * 0.15
        recency = self._calculate_recency_score(knowledge_item) * 0.10
        
        # Calculate overall score
        overall_score = source_trust + validation_status + cross_reference + recency
        
        # Create trust score
        trust_score = TrustScore(
            target_id=knowledge_item.id,
            target_type="knowledgeItem",
            overall_score=overall_score,
            factors={
                "sourceTrust": source_trust,
                "validationStatus": validation_status,
                "crossReferenceCount": cross_reference,
                "recency": recency,
            },
        )
        
        return trust_score
    
    def _calculate_validation_score(self, item: KnowledgeItem) -> float:
        """Calculate validation score."""
        if item.validation_status == "validated":
            return item.validation_confidence
        elif item.validation_status == "contradicted":
            return 0.2
        else:
            return 0.5  # unvalidated
    
    def _calculate_cross_reference_score(self, item: KnowledgeItem) -> float:
        """Calculate cross-reference score."""
        # Simplified - count sources
        return min(len(item.sources) / 10.0, 1.0)
    
    def _calculate_recency_score(self, item: KnowledgeItem) -> float:
        """Calculate recency score."""
        # Simplified - use updated_at
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        updated = item.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        
        age_days = (now - updated).days
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