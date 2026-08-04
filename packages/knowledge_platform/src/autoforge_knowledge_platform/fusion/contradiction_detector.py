"""
Contradiction Detector

Detects and flags contradictions as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.models import KnowledgeItem


class ContradictionDetector:
    """
    Detects and flags contradictions.
    
    As defined in Knowledge Platform Specification v1.0, Section 14.5.
    """
    
    async def detect(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """
        Detect contradictions between sources.
        
        Contradiction types:
        - Direct contradiction: Sources explicitly disagree
        - Implicit contradiction: Sources imply different things
        - Temporal contradiction: Sources describe different time periods
        - Contextual contradiction: Sources apply to different contexts
        
        Args:
            knowledge_items: List of knowledge items
            
        Returns:
            List of detected contradictions
        """
        contradictions = []
        
        # Compare all pairs of items
        for i, item1 in enumerate(knowledge_items):
            for item2 in knowledge_items[i+1:]:
                contradiction = await self._check_contradiction(item1, item2)
                if contradiction:
                    contradictions.append(contradiction)
        
        return contradictions
    
    async def _check_contradiction(
        self,
        item1: KnowledgeItem,
        item2: KnowledgeItem,
    ) -> Dict[str, Any] | None:
        """Check if two items contradict each other."""
        # Simplified contradiction detection
        # In production, use NLP and semantic analysis
        
        content1 = item1.content.lower()
        content2 = item2.content.lower()
        
        # Check for direct contradictions (simplified)
        contradiction_indicators = [
            ("is not", "is"),
            ("never", "always"),
            ("always", "never"),
            ("should not", "should"),
            ("must not", "must"),
            ("cannot", "can"),
            ("won't", "will"),
        ]
        
        for neg, pos in contradiction_indicators:
            if (neg in content1 and pos in content2) or (pos in content1 and neg in content2):
                return {
                    "type": "direct",
                    "item1": item1,
                    "item2": item2,
                    "severity": "high",
                    "description": f"Direct contradiction detected between sources",
                    "requires_human_review": True,
                }
        
        return None