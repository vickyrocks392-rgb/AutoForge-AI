"""
Source Registry

Manages knowledge source registration and lookup as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from autoforge_knowledge_platform.interfaces.query_interfaces import ISourceRegistry
from autoforge_knowledge_platform.models import Source


class SourceRegistry(ISourceRegistry):
    """
    Manages knowledge source registration and lookup.
    
    As defined in Knowledge Platform Specification v1.0, Section 9.7.
    """
    
    def __init__(self):
        """Initialize Source Registry."""
        self._sources: Dict[str, Source] = {}
    
    async def register_source(self, source: Source) -> str:
        """Register a new knowledge source."""
        source_id = str(source.id)
        self._sources[source_id] = source
        return source_id
    
    async def unregister_source(self, source_id: str) -> None:
        """Unregister a knowledge source."""
        if source_id in self._sources:
            del self._sources[source_id]
    
    async def get_source(self, source_id: str) -> Optional[Source]:
        """Get source by ID."""
        return self._sources.get(source_id)
    
    async def get_sources_by_domain(self, domain: str) -> List[Source]:
        """Get all sources for a domain."""
        return [s for s in self._sources.values() if s.domain == domain]
    
    async def get_sources_by_type(self, source_type: str) -> List[Source]:
        """Get all sources of a type."""
        return [s for s in self._sources.values() if s.type == source_type]
    
    async def get_active_sources(self) -> List[Source]:
        """Get all active sources."""
        return [s for s in self._sources.values() if s.status == "active"]
    
    async def update_source(self, source_id: str, updates: Dict[str, Any]) -> Source:
        """Update source configuration."""
        source = self._sources.get(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
        
        # Update source fields
        for key, value in updates.items():
            if hasattr(source, key):
                setattr(source, key, value)
        
        return source
    
    async def list_sources(self, filters: Optional[Dict[str, Any]] = None) -> List[Source]:
        """List sources with optional filters."""
        sources = list(self._sources.values())
        
        if filters:
            if "type" in filters:
                sources = [s for s in sources if s.type == filters["type"]]
            if "status" in filters:
                sources = [s for s in sources if s.status == filters["status"]]
            if "domain" in filters:
                sources = [s for s in sources if s.domain == filters["domain"]]
        
        return sources