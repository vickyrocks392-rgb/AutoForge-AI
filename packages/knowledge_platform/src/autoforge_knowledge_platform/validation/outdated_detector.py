"""
Outdated Detector

Detects outdated or superseded information as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from autoforge_knowledge_platform.models import KnowledgeItem


class OutdatedDetector:
    """
    Detects outdated or superseded information.
    
    As defined in Knowledge Platform Specification v1.0, Section 17.4.
    """
    
    async def detect(self, knowledge_item: KnowledgeItem) -> Dict[str, Any]:
        """
        Detect outdated or superseded information.
        
        Outdated thresholds:
        - Critical (security, APIs): 1 month
        - Important (best practices): 6 months
        - General (concepts): 12 months
        - Historical: Never outdated
        
        Args:
            knowledge_item: Knowledge item to check
            
        Returns:
            Outdated detection results
        """
        now = datetime.now(timezone.utc)
        updated_at = knowledge_item.updated_at
        
        # Ensure updated_at is timezone-aware
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        
        age_days = (now - updated_at).days
        
        # Determine threshold based on domain
        threshold_days = 365  # Default: 12 months
        if knowledge_item.domain in ["security", "api"]:
            threshold_days = 30  # 1 month
        elif knowledge_item.domain in ["best_practice", "patterns"]:
            threshold_days = 180  # 6 months
        elif knowledge_item.domain in ["history", "theory"]:
            threshold_days = float('inf')  # Never outdated
        
        is_outdated = age_days > threshold_days
        
        return {
            "knowledge_item_id": knowledge_item.id,
            "is_outdated": is_outdated,
            "age_days": age_days,
            "threshold_days": threshold_days if threshold_days != float('inf') else None,
            "last_updated": knowledge_item.updated_at.isoformat(),
            "recommendation": "update" if is_outdated else "current",
        }