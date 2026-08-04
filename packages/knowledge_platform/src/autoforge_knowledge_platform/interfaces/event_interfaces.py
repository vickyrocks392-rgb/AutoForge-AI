"""
Knowledge Platform Event Interfaces

Event publisher interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IKnowledgeEventPublisher(ABC):
    """Interface for Knowledge Event Publisher."""
    
    @abstractmethod
    async def publish_knowledge_ingested(
        self,
        knowledge_item_id: str,
        source_id: str,
        domain: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.ingested event."""
        pass
    
    @abstractmethod
    async def publish_knowledge_updated(
        self,
        knowledge_item_id: str,
        version: str,
        changes: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish knowledge.updated event."""
        pass
    
    @abstractmethod
    async def publish_knowledge_superseded(
        self,
        old_knowledge_item_id: str,
        new_knowledge_item_id: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.superseded event."""
        pass
    
    @abstractmethod
    async def publish_knowledge_archived(
        self,
        knowledge_item_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish knowledge.archived event."""
        pass
    
    @abstractmethod
    async def publish_source_registered(
        self,
        source_id: str,
        source_type: str,
        name: str,
        timestamp: str,
    ) -> None:
        """Publish source.registered event."""
        pass
    
    @abstractmethod
    async def publish_source_updated(
        self,
        source_id: str,
        changes: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish source.updated event."""
        pass
    
    @abstractmethod
    async def publish_source_synced(
        self,
        source_id: str,
        items_added: int,
        items_updated: int,
        items_removed: int,
        timestamp: str,
    ) -> None:
        """Publish source.synced event."""
        pass
    
    @abstractmethod
    async def publish_source_removed(
        self,
        source_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish source.removed event."""
        pass
    
    @abstractmethod
    async def publish_source_error(
        self,
        source_id: str,
        error: str,
        timestamp: str,
    ) -> None:
        """Publish source.error event."""
        pass
    
    @abstractmethod
    async def publish_retrieval_performed(
        self,
        query_id: str,
        sources: List[str],
        result_count: int,
        retrieval_time: float,
        timestamp: str,
    ) -> None:
        """Publish retrieval.performed event."""
        pass
    
    @abstractmethod
    async def publish_retrieval_cached(
        self,
        query_id: str,
        cache_level: str,
        timestamp: str,
    ) -> None:
        """Publish retrieval.cached event."""
        pass
    
    @abstractmethod
    async def publish_retrieval_failed(
        self,
        query_id: str,
        error: str,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish retrieval.failed event."""
        pass
    
    @abstractmethod
    async def publish_trust_score_calculated(
        self,
        target_id: str,
        target_type: str,
        trust_score: float,
        factors: Dict[str, float],
        timestamp: str,
    ) -> None:
        """Publish trust.score.calculated event."""
        pass
    
    @abstractmethod
    async def publish_trust_score_updated(
        self,
        target_id: str,
        old_score: float,
        new_score: float,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish trust.score.updated event."""
        pass
    
    @abstractmethod
    async def publish_trust_score_expired(
        self,
        target_id: str,
        timestamp: str,
    ) -> None:
        """Publish trust.score.expired event."""
        pass
    
    @abstractmethod
    async def publish_validation_performed(
        self,
        knowledge_item_id: str,
        valid: bool,
        confidence: float,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish validation.performed event."""
        pass
    
    @abstractmethod
    async def publish_validation_failed(
        self,
        knowledge_item_id: str,
        error: str,
        timestamp: str,
    ) -> None:
        """Publish validation.failed event."""
        pass
    
    @abstractmethod
    async def publish_fusion_performed(
        self,
        query_id: str,
        sources: List[str],
        conflicts: int,
        consensus: float,
        timestamp: str,
    ) -> None:
        """Publish fusion.performed event."""
        pass
    
    @abstractmethod
    async def publish_fusion_conflict(
        self,
        query_id: str,
        conflict_type: str,
        sources: List[str],
        timestamp: str,
    ) -> None:
        """Publish fusion.conflict event."""
        pass
    
    @abstractmethod
    async def publish_fusion_resolved(
        self,
        query_id: str,
        resolution: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Publish fusion.resolved event."""
        pass
    
    @abstractmethod
    async def publish_citation_created(
        self,
        citation_id: str,
        knowledge_item_id: str,
        source_id: str,
        timestamp: str,
    ) -> None:
        """Publish citation.created event."""
        pass
    
    @abstractmethod
    async def publish_citation_validated(
        self,
        citation_id: str,
        valid: bool,
        timestamp: str,
    ) -> None:
        """Publish citation.validated event."""
        pass
    
    @abstractmethod
    async def publish_citation_invalidated(
        self,
        citation_id: str,
        reason: str,
        timestamp: str,
    ) -> None:
        """Publish citation.invalidated event."""
        pass