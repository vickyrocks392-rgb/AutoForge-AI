"""
Knowledge Platform Connector Interfaces

Source connector interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID

from autoforge_knowledge_platform.models import KnowledgeItem, Source


class ISourceConnector(ABC):
    """Interface for Source Connectors."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to source."""
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        query: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> List[KnowledgeItem]:
        """Retrieve knowledge items matching query."""
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Get source metadata."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check source health."""
        pass
    
    @abstractmethod
    async def sync(self) -> Dict[str, Any]:
        """Synchronize source content."""
        pass


class ISourceConnectorManager(ABC):
    """Interface for Source Connector Manager."""
    
    @abstractmethod
    async def register_connector(
        self,
        source: Source,
        connector_type: str,
        config: Dict[str, Any],
    ) -> str:
        """Register a new source connector."""
        pass
    
    @abstractmethod
    async def unregister_connector(self, connector_id: str) -> None:
        """Unregister a source connector."""
        pass
    
    @abstractmethod
    async def get_connector(self, connector_id: str) -> ISourceConnector:
        """Get a source connector by ID."""
        pass
    
    @abstractmethod
    async def get_connectors_for_source(self, source_id: UUID) -> List[ISourceConnector]:
        """Get all connectors for a source."""
        pass
    
    @abstractmethod
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all connectors."""
        pass
    
    @abstractmethod
    async def sync_all(self) -> Dict[str, Dict[str, Any]]:
        """Synchronize all sources."""
        pass