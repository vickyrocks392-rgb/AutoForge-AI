"""
Recency Weighter

Weights recent content higher for time-sensitive topics as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from autoforge_knowledge_platform.models import KnowledgeItem


class RecencyWeighter:
    """
    Weights recent content higher for time-sensitive topics.
    
    As defined in Knowledge Platform Specification v1.0, Section 15.5.
    """
    
    async def weight(self, knowledge_item: KnowledgeItem) -> float:
        """
        Weight recent content higher for time-sensitive topics.
        
        Recency factors:
        - Content age
        - Domain sensitivity
        - Update frequency
        
        Args:
            knowledge_item: Knowledge item to weight
            
        Returns:
            Recency weight (0.0 to 1.0)
        """
        now = datetime.now(timezone.utc)
        updated_at = knowledge_item.updated_at
        
        # Ensure updated_at is timezone-aware
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        
        age_days = (now - updated_at).days
        
        # Determine recency based on domain
        if knowledge_item.domain in ["security", "api", "breaking_changes"]:
            # High sensitivity - recent content is critical
            if age_days < 7:
                return 1.0
            elif age_days < 30:
                return 0.8
            elif age_days < 90:
                return 0.5
            else:
                return 0.2
        elif knowledge_item.domain in ["best_practice", "patterns"]:
            # Medium sensitivity
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
        else:
            # Low sensitivity - general knowledge
            if age_days < 90:
                return 1.0
            elif age_days < 180:
                return 0.8
            elif age_days < 365:
                return 0.6
            elif age_days < 730:  # 2 years
                return 0.4
            else:
                return 0.2