"""
Base Source Connector

Provides common functionality for all source connectors as defined in the Knowledge Platform Specification v1.0, Section 10.1.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from autoforge_knowledge_platform.interfaces.connector_interfaces import ISourceConnector
from autoforge_knowledge_platform.models import KnowledgeItem, KnowledgeItemType, Source


class BaseConnector(ISourceConnector):
    """
    Base class for all source connectors.
    
    Provides common connection state management and metadata handling.
    As defined in Knowledge Platform Specification v1.0, Section 10.1.
    """
    
    def __init__(
        self,
        source: Source,
        config: Dict[str, Any],
    ):
        """Initialize connector with source and configuration."""
        self.source = source
        self.config = config
        self._connected = False
        self._connected_at: Optional[datetime] = None
    
    async def connect(self) -> None:
        """Establish connection to source."""
        self._connected = True
        self._connected_at = datetime.now(timezone.utc)
    
    async def disconnect(self) -> None:
        """Close connection to source."""
        self._connected = False
        self._connected_at = None
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get source metadata."""
        return {
            "source_id": str(self.source.id),
            "source_name": self.source.name,
            "source_type": self.source.type,
            "connector_type": self.source.connector_type,
            "url": self.source.url,
            "connected": self._connected,
            "connected_at": self._connected_at.isoformat() if self._connected_at else None,
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check source health."""
        return {
            "healthy": self._connected,
            "source_id": str(self.source.id),
            "source_name": self.source.name,
            "connected": self._connected,
            "last_connected_at": self._connected_at.isoformat() if self._connected_at else None,
        }
    
    async def sync(self) -> Dict[str, Any]:
        """Synchronize source content."""
        return {
            "source_id": str(self.source.id),
            "status": "synced" if self._connected else "not_connected",
            "items_added": 0,
            "items_updated": 0,
            "items_removed": 0,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def _create_knowledge_item(
        self,
        content: str,
        domain: str,
        item_type: KnowledgeItemType = KnowledgeItemType.FACT,
        summary: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeItem:
        """Create a knowledge item from retrieved content."""
        return KnowledgeItem(
            type=item_type,
            content=content,
            summary=summary or content[:200],
            domain=domain,
            tags=tags or [],
            source_id=self.source.id,
            sources=[self.source.id],
            metadata=metadata or {},
        )