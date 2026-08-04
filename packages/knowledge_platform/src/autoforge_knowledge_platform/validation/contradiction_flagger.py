"""
Contradiction Flagger

Flags contradictory information as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.models import KnowledgeItem


class ContradictionFlagger:
    """
    Flags contradictory information.
    
    As defined in Knowledge Platform Specification v1.0, Section 17.5.
    """
    
    async def flag(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """
        Flag contradictory information.
        
        Contradiction severity:
        - Critical: Contradicts safety or security information
        - High: Contradicts core concepts
        - Medium: Contradicts best practices
        - Low: Minor contradictions
        
        Args:
            knowledge_items: List of knowledge items
            
        Returns:
            List of flagged contradictions
        """
        # Simplified contradiction flagging
        # In production, use comprehensive contradiction detection
        
        contradictions = []
        
        # Compare all pairs
        for i, item1 in enumerate(knowledge_items):
            for item2 in knowledge_items[i+1:]:
                # Check for contradictions
                if self._are_contradictory(item1, item2):
                    severity = self._determine_severity(item1, item2)
                    contradictions.append({
                        "type": "contradiction",
                        "item1_id": item1.id,
                        "item2_id": item2.id,
                        "severity": severity,
                        "description": "Contradictory information detected",
                        "requires_human_review": severity in ["critical", "high"],
                    })
        
        return contradictions
    
    def _are_contradictory(self, item1: KnowledgeItem, item2: KnowledgeItem) -> bool:
        """Check if two items are contradictory."""
        # Simplified check - use semantic analysis in production
        content1 = item1.content.lower()
        content2 = item2.content.lower()
        
        # Check for opposite statements
        opposites = [
            ("true", "false"),
            ("yes", "no"),
            ("enable", "disable"),
            ("required", "optional"),
            ("always", "never"),
        ]
        
        for word1, word2 in opposites:
            if (word1 in content1 and word2 in content2) or (word2 in content1 and word1 in content2):
                return True
        
        return False
    
    def _determine_severity(self, item1: KnowledgeItem, item2: KnowledgeItem) -> str:
        """Determine contradiction severity."""
        # Simplified severity determination
        if item1.domain in ["security", "safety"]:
            return "critical"
        elif item1.domain in ["core", "architecture"]:
            return "high"
        elif item1.domain in ["best_practice", "patterns"]:
            return "medium"
        else:
            return "low"