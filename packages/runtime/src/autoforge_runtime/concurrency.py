"""Concurrency Controller — manages concurrent state access with optimistic concurrency control.

Implements the concurrency model from Runtime State Manager Specification v1.0, Section 28.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any

from autoforge_runtime.exceptions import VersionConflictError
from autoforge_runtime.validation import ValidationErrorCode


@dataclass(frozen=True)
class ResolutionResult:
    """Result of a version conflict resolution."""

    resolved: bool
    latest_version: int | None = None
    error_code: str | None = None
    error_message: str | None = None


class ConcurrencyController:
    """Manages concurrent state access using optimistic concurrency control.

    Implements the optimistic concurrency control mechanism from
    Specification Section 28. State includes a version number. Transitions
    check the version before writing. Version conflicts trigger retry.
    """

    def __init__(self) -> None:
        """Initialize the concurrency controller."""
        self._locks: dict[uuid.UUID, asyncio.Lock] = {}
        self._lock_guard = asyncio.Lock()

    async def acquire_lock(self, entity_id: uuid.UUID) -> asyncio.Lock:
        """Acquire a per-entity lock for exclusive access.

        Args:
            entity_id: The entity ID to lock.

        Returns:
            An asyncio.Lock for the entity.
        """
        async with self._lock_guard:
            if entity_id not in self._locks:
                self._locks[entity_id] = asyncio.Lock()
            return self._locks[entity_id]

    async def release_lock(self, entity_id: uuid.UUID) -> None:
        """Release the lock for an entity.

        Args:
            entity_id: The entity ID to unlock.
        """
        async with self._lock_guard:
            self._locks.pop(entity_id, None)

    def check_version(self, current_version: int, expected_version: int) -> ResolutionResult:
        """Check if the current version matches the expected version.

        Args:
            current_version: The current state version.
            expected_version: The version the caller expects.

        Returns:
            ResolutionResult indicating whether the version matches.
        """
        if current_version != expected_version:
            return ResolutionResult(
                resolved=False,
                latest_version=current_version,
                error_code=ValidationErrorCode.VERSION_CONFLICT,
                error_message=(
                    f"Version conflict: expected version {expected_version}, "
                    f"current version is {current_version}"
                ),
            )
        return ResolutionResult(resolved=True, latest_version=current_version)

    def handle_version_conflict(self, entity_id: uuid.UUID, attempted_version: int, latest_version: int) -> ResolutionResult:
        """Handle a version conflict.

        Args:
            entity_id: The entity ID that had the conflict.
            attempted_version: The version that was attempted.
            latest_version: The current latest version.

        Returns:
            ResolutionResult with the resolution outcome.
        """
        return ResolutionResult(
            resolved=False,
            latest_version=latest_version,
            error_code=ValidationErrorCode.VERSION_CONFLICT,
            error_message=(
                f"Version conflict for entity {entity_id}: "
                f"attempted version {attempted_version}, latest is {latest_version}"
            ),
        )

    def next_version(self, current_version: int) -> int:
        """Return the next version number after a successful write.

        Args:
            current_version: The current version.

        Returns:
            The next version number.
        """
        return current_version + 1