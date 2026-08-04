"""
Knowledge Event Publisher

Publishes knowledge events as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timezone
from autoforge_knowledge_platform.interfaces.event_interfaces import IKnowledgeEventPublisher


class KnowledgeEventPublisher(IKnowledgeEventPublisher):
    """
    Publishes knowledge events.
    
    As defined in Knowledge Platform Specification v1.0, Section 24.
    """
    
    def __init__(self, event_bus: Any):
        """Initialize Knowledge Event Publisher with event bus."""
        self.event_bus = event_bus
    
    async def publish_knowledge_ingested(
        self,
        knowledge_item_id: str,
        source_id: str,
        domain: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.ingested event."""
        await self._publish("knowledge.ingested", {
            "knowledgeItemId": knowledge_item_id,
            "sourceId": source_id,
            "domain": domain,
            "timestamp": timestamp,
        })
    
    async def publish_knowledge_updated(
        self,
        knowledge_item_id: str,
        version: str,
        changes: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish knowledge.updated event."""
        await self._publish("knowledge.updated", {
            "knowledgeItemId": knowledge_item_id,
            "version": version,
            "changes": changes,
            "timestamp": timestamp,
        })
    
    async def publish_knowledge_superseded(
        self,
        old_knowledge_item_id: str,
        new_knowledge_item_id: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.superseded event."""
        await self._publish("knowledge.superseded", {
            "oldKnowledgeItemId": old_knowledge_item_id,
            "newKnowledgeItemId": new_knowledge_item_id,
            "timestamp": timestamp,
        })
    
    async def publish_knowledge_archived(
        self,
        knowledge_item_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.archived event."""
        await self._publish("knowledge.archived", {
            "knowledgeItemId": knowledge_item_id,
            "reason": reason,
            "timestamp": timestamp,
        })
    
    async def publish_source_registered(
        self,
        source_id: str,
        source_type: str,
        name: str,
        timestamp: str,
    ) -> None:
        """Publish source.registered event."""
        await self._publish("source.registered", {
            "sourceId": source_id,
            "sourceType": source_type,
            "name": name,
            "timestamp": timestamp,
        })
    
    async def publish_source_updated(
        self,
        source_id: str,
        changes: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish source.updated event."""
        await self._publish("source.updated", {
            "sourceId": source_id,
            "changes": changes,
            "timestamp": timestamp,
        })
    
    async def publish_source_synced(
        self,
        source_id: str,
        items_added: int,
        items_updated: int,
        items_removed: int,
        timestamp: str,
    ) -> None:
        """Publish source.synced event."""
        await self._publish("source.synced", {
            "sourceId": source_id,
            "itemsAdded": items_added,
            "itemsUpdated": items_updated,
            "itemsRemoved": items_removed,
            "timestamp": timestamp,
        })
    
    async def publish_source_removed(
        self,
        source_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish source.removed event."""
        await self._publish("source.removed", {
            "sourceId": source_id,
            "reason": reason,
            "timestamp": timestamp,
        })
    
    async def publish_source_error(
        self,
        source_id: str,
        error: str,
        timestamp: str,
    ) -> None:
        """Publish source.error event."""
        await self._publish("source.error", {
            "sourceId": source_id,
            "error": error,
            "timestamp": timestamp,
        })
    
    async def publish_retrieval_performed(
        self,
        query_id: str,
        sources: List[str],
        result_count: int,
        retrieval_time: float,
        timestamp: str,
    ) -> None:
        """Publish retrieval.performed event."""
        await self._publish("retrieval.performed", {
            "queryId": query_id,
            "sources": sources,
            "resultCount": result_count,
            "retrievalTime": retrieval_time,
            "timestamp": timestamp,
        })
    
    async def publish_retrieval_cached(
        self,
        query_id: str,
        cache_level: str,
        timestamp: str,
    ) -> None:
        """Publish retrieval.cached event."""
        await self._publish("retrieval.cached", {
            "queryId": query_id,
            "cacheLevel": cache_level,
            "timestamp": timestamp,
        })
    
    async def publish_retrieval_failed(
        self,
        query_id: str,
        error: str,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish retrieval.failed event."""
        await self._publish("retrieval.failed", {
            "queryId": query_id,
            "error": error,
            "sources": sources,
            "timestamp": timestamp,
        })
    
    async def publish_trust_score_calculated(
        self,
        target_id: str,
        target_type: str,
        trust_score: float,
        factors: Dict[str, float],
        timestamp: str,
    ) -> None:
        """Publish trust.score.calculated event."""
        await self._publish("trust.score.calculated", {
            "targetId": target_id,
            "targetType": target_type,
            "trustScore": trust_score,
            "factors": factors,
            "timestamp": timestamp,
        })
    
    async def publish_trust_score_updated(
        self,
        target_id: str,
        old_score: float,
        new_score: float,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish trust.score.updated event."""
        await self._publish("trust.score.updated", {
            "targetId": target_id,
            "oldScore": old_score,
            "newScore": new_score,
            "reason": reason,
            "timestamp": timestamp,
        })
    
    async def publish_trust_score_expired(
        self,
        target_id: str,
        timestamp: str,
    ) -> None:
        """Publish trust.score.expired event."""
        await self._publish("trust.score.expired", {
            "targetId": target_id,
            "timestamp": timestamp,
        })
    
    async def publish_validation_performed(
        self,
        knowledge_item_id: str,
        valid: bool,
        confidence: float,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish validation.performed event."""
        await self._publish("validation.performed", {
            "knowledgeItemId": knowledge_item_id,
            "valid": valid,
            "confidence": confidence,
            "sources": sources,
            "timestamp": timestamp,
        })
    
    async def publish_validation_failed(
        self,
        knowledge_item_id: str,
        error: str,
        timestamp: str,
    ) -> None:
        """Publish validation.failed event."""
        await self._publish("validation.failed", {
            "knowledgeItemId": knowledge_item_id,
            "error": error,
            "timestamp": timestamp,
        })
    
    async def publish_fusion_performed(
        self,
        query_id: str,
        sources: List[str],
        conflicts: int,
        consensus: float,
        timestamp: str,
    ) -> None:
        """Publish fusion.performed event."""
        await self._publish("fusion.performed", {
            "queryId": query_id,
            "sources": sources,
            "conflicts": conflicts,
            "consensus": consensus,
            "timestamp": timestamp,
        })
    
    async def publish_fusion_conflict(
        self,
        query_id: str,
        conflict_type: str,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish fusion.conflict event."""
        await self._publish("fusion.conflict", {
            "queryId": query_id,
            "conflictType": conflict_type,
            "sources": sources,
            "timestamp": timestamp,
        })
    
    async def publish_fusion_resolved(
        self,
        query_id: str,
        resolution: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish fusion.resolved event."""
        await self._publish("fusion.resolved", {
            "queryId": query_id,
            "resolution": resolution,
            "timestamp": timestamp,
        })
    
    async def publish_citation_created(
        self,
        citation_id: str,
        knowledge_item_id: str,
        source_id: str,
        timestamp: str,
    ) -> None:
        """Publish citation.created event."""
        await self._publish("citation.created", {
            "citationId": citation_id,
            "knowledgeItemId": knowledge_item_id,
            "sourceId": source_id,
            "timestamp": timestamp,
        })
    
    async def publish_citation_validated(
        self,
        citation_id: str,
        valid: bool,
        timestamp: str,
    ) -> None:
        """Publish citation.validated event."""
        await self._publish("citation.validated", {
            "citationId": citation_id,
            "valid": valid,
            "timestamp": timestamp,
        })
    
    async def publish_citation_invalidated(
        self,
        citation_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish citation.invalidated event."""
        await self._publish("citation.invalidated", {
            "citationId": citation_id,
            "reason": reason,
            "timestamp": timestamp,
        })
    
    async def _publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish event to event bus."""
        if self.event_bus:
            await self.event_bus.publish(event_type, payload)