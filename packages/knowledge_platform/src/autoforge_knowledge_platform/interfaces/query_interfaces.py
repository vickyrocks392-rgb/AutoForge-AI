"""
Knowledge Platform Query Interfaces

Query processor and source registry interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from autoforge_knowledge_platform.models import Source


class IQueryProcessor(ABC):
    """Interface for Query Processor."""
    
    @abstractmethod
    async def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse and normalize query."""
        pass
    
    @abstractmethod
    async def extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        pass
    
    @abstractmethod
    async def extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """Extract entities from query."""
        pass
    
    @abstractmethod
    async def identify_query_type(self, query: str) -> str:
        """Identify query type (factual, procedural, conceptual, etc.)."""
        pass
    
    @abstractmethod
    async def determine_domain(self, query: str) -> str:
        """Determine domain and scope of query."""
        pass
    
    @abstractmethod
    async def normalize_query(self, query: str) -> str:
        """Normalize query to canonical format."""
        pass


class ISourceRegistry(ABC):
    """Interface for Source Registry."""
    
    @abstractmethod
    async def register_source(self, source: Source) -> str:
        """Register a new knowledge source."""
        pass
    
    @abstractmethod
    async def unregister_source(self, source_id: UUID) -> None:
        """Unregister a knowledge source."""
        pass
    
    @abstractmethod
    async def get_source(self, source_id: UUID) -> Optional[Source]:
        """Get source by ID."""
        pass
    
    @abstractmethod
    async def get_sources_by_domain(self, domain: str) -> List[Source]:
        """Get all sources for a domain."""
        pass
    
    @abstractmethod
    async def get_sources_by_type(self, source_type: str) -> List[Source]:
        """Get all sources of a type."""
        pass
    
    @abstractmethod
    async def get_active_sources(self) -> List[Source]:
        """Get all active sources."""
        pass
    
    @abstractmethod
    async def update_source(self, source_id: UUID, updates: Dict[str, Any]) -> Source:
        """Update source configuration."""
        pass
    
    @abstractmethod
    async def list_sources(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Source]:
        """List sources with optional filters."""
        pass