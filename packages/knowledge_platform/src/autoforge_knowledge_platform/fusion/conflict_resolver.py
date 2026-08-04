"""
Conflict Resolver

Resolves conflicts between sources as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from autoforge_knowledge_platform.models import KnowledgeItem


class ConflictResolver:
    """
    Resolves conflicts between sources.
    
    As defined in Knowledge Platform Specification v1.0, Section 14.3.
    """
    
    async def resolve(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve conflicts between sources.
        
        Resolution rules (in order of precedence):
        1. Trust Priority - Higher trust source wins
        2. Recency Priority - More recent source wins (for time-sensitive topics)
        3. Consensus Priority - Majority view wins when trust is equal
        4. Expert Priority - Expert-endorsed source wins when trust is equal
        5. Flag Uncertainty - Flag as unresolved conflict
        
        Args:
            conflicts: List of detected conflicts
            
        Returns:
            Resolved conflicts
        """
        resolved = []
        
        for conflict in conflicts:
            resolution = await self._resolve_conflict(conflict)
            resolved.append(resolution)
        
        return resolved
    
    async def _resolve_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a single conflict."""
        sources = conflict.get("sources", [])
        
        # Rule 1: Trust Priority
        if len(sources) >= 2:
            sorted_by_trust = sorted(sources, key=lambda s: s.get("trust_score", 0), reverse=True)
            if sorted_by_trust[0].get("trust_score", 0) > sorted_by_trust[1].get("trust_score", 0):
                return {
                    "conflict": conflict,
                    "resolution": "trust_priority",
                    "winning_source": sorted_by_trust[0],
                    "confidence": 0.9,
                }
        
        # Rule 2: Recency Priority
        if len(sources) >= 2:
            sorted_by_date = sorted(
                sources,
                key=lambda s: s.get("created_at", datetime.min.replace(tzinfo=timezone.utc)),
                reverse=True,
            )
            if sorted_by_date[0].get("created_at") != sorted_by_date[1].get("created_at"):
                return {
                    "conflict": conflict,
                    "resolution": "recency_priority",
                    "winning_source": sorted_by_date[0],
                    "confidence": 0.7,
                }
        
        # Rule 3: Consensus Priority
        if len(sources) >= 2:
            # Count sources supporting each view
            view_counts: Dict[str, int] = {}
            for source in sources:
                view = source.get("view", "unknown")
                view_counts[view] = view_counts.get(view, 0) + 1
            
            majority_view = max(view_counts, key=view_counts.get)
            majority_count = view_counts[majority_view]
            
            if majority_count > len(sources) / 2:
                majority_sources = [s for s in sources if s.get("view", "unknown") == majority_view]
                return {
                    "conflict": conflict,
                    "resolution": "consensus_priority",
                    "winning_source": majority_sources[0],
                    "confidence": 0.6,
                }
        
        # Rule 4: Expert Priority
        if len(sources) >= 2:
            expert_sources = [s for s in sources if s.get("is_expert", False)]
            if expert_sources:
                return {
                    "conflict": conflict,
                    "resolution": "expert_priority",
                    "winning_source": expert_sources[0],
                    "confidence": 0.8,
                }
        
        # Rule 5: Flag Uncertainty
        return {
            "conflict": conflict,
            "resolution": "unresolved",
            "winning_source": None,
            "confidence": 0.0,
            "requires_human_review": True,
        }