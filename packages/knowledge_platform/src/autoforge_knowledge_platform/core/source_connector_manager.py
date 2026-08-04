"""
Source Connector Manager

Manages source connectors as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from autoforge_knowledge_platform.interfaces.connector_interfaces import ISourceConnectorManager
from autoforge_knowledge_platform.models import Source, SourceType
from autoforge_knowledge_platform.connectors import (
    DocumentationConnector,
    CodeConnector,
    AcademicConnector,
    ExpertConnector,
    CommunityConnector,
    ProprietaryConnector,
)


class SourceConnectorManager(ISourceConnectorManager):
    """
    Manages source connectors.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.3.
    """
    
    def __init__(self):
        """Initialize Source Connector Manager."""
        self._connectors: Dict[str, Any] = {}
    
    async def register_connector(
        self,
        source: Source,
        connector_type: str,
        config: Dict[str, Any],
    ) -> str:
        """Register a new source connector."""
        connector_id = f"{source.id}_{connector_type}"
        
        # Instantiate the appropriate connector based on source type
        connector = self._create_connector(source, connector_type, config)
        self._connectors[connector_id] = connector
        return connector_id
    
    def _create_connector(
        self,
        source: Source,
        connector_type: str,
        config: Dict[str, Any],
    ) -> Any:
        """Create the appropriate connector instance based on source type."""
        source_type = source.type
        if isinstance(source_type, str):
            source_type = SourceType(source_type)
        
        if source_type == SourceType.DOCUMENTATION:
            return DocumentationConnector(source, config)
        elif source_type == SourceType.CODE:
            return CodeConnector(source, config)
        elif source_type == SourceType.ACADEMIC:
            return AcademicConnector(source, config)
        elif source_type == SourceType.EXPERT:
            return ExpertConnector(source, config)
        elif source_type == SourceType.COMMUNITY:
            return CommunityConnector(source, config)
        elif source_type == SourceType.PROPRIETARY:
            return ProprietaryConnector(source, config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def unregister_connector(self, connector_id: str) -> None:
        """Unregister a source connector."""
        if connector_id in self._connectors:
            connector = self._connectors[connector_id]
            if connector:
                await connector.disconnect()
            del self._connectors[connector_id]
    
    async def get_connector(self, connector_id: str) -> Any:
        """Get a source connector by ID."""
        return self._connectors.get(connector_id)
    
    async def get_connectors_for_source(self, source_id: UUID) -> List[Any]:
        """Get all connectors for a source."""
        return [c for cid, c in self._connectors.items() if cid.startswith(str(source_id))]
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all connectors."""
        results = {}
        for connector_id, connector in self._connectors.items():
            if connector:
                results[connector_id] = await connector.health_check()
        return results
    
    async def sync_all(self) -> Dict[str, Dict[str, Any]]:
        """Synchronize all sources."""
        results = {}
        for connector_id, connector in self._connectors.items():
            if connector:
                results[connector_id] = await connector.sync()
        return results