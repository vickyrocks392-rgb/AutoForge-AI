"""
Knowledge Platform Cache Interfaces

Cache interfaces as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID


class IKnowledgeCache(ABC):
    """Interface for Knowledge Cache."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value by key."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """Set cached value with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached value."""
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached values."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass
    
    @abstractmethod
    async def warm_cache(self, queries: List[Dict[str, Any]]) -> None:
        """Warm cache with pre-computed results."""
        pass