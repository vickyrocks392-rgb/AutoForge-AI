"""Recovery Manager — supports system recovery and state restoration.

Implements the Recovery Model from Runtime State Manager Specification v1.0, Section 19.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_runtime.exceptions import RecoveryError
from autoforge_runtime.models import (
    CheckpointState,
    EntityType,
    FailureRecoverability,
    FailureSeverity,
    FailureSource,
    RecoveryState,
    RecoveryStatus,
    StateTransition,
)
from autoforge_runtime.persistence import PersistenceLayer


class RecoveryManager:
    """Supports system recovery and state restoration.

    Implements the Recovery Model from Specification Section 19.
    """

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the recovery manager."""
        self._persistence = persistence

    def detect_failure(
        self,
        *,
        source: FailureSource,
        severity: FailureSeverity,
        recoverability: FailureRecoverability,
        error_code: str | None = None,
        error_message: str = "",
        project_id: uuid.UUID | None = None,
    ) -> RecoveryState:
        """Detect and classify a failure.

        Args:
            source: The failure source.
            severity: The failure severity.
            recoverability: The failure recoverability.
            error_code: Optional error code.
            error_message: The error message.
            project_id: Optional project ID.

        Returns:
            The created RecoveryState.
        """
        recovery = RecoveryState(
            project_id=project_id,
            status=RecoveryStatus.FAILURE_DETECTED,
            source=source,
            severity=severity,
            recoverability=recoverability,
            error_code=error_code,
            error_message=error_message,
            started_at=datetime.now(timezone.utc),
        )
        self._persistence.write_state(EntityType.RECOVERY, recovery.recovery_id, recovery)
        return recovery

    def classify_failure(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Classify a detected failure.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(update={"status": RecoveryStatus.FAILURE_CLASSIFIED})
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def restore_from_checkpoint(self, recovery_id: uuid.UUID, checkpoint_id: uuid.UUID) -> RecoveryState:
        """Restore state from a checkpoint during recovery.

        Args:
            recovery_id: The recovery ID.
            checkpoint_id: The checkpoint ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(
            update={
                "status": RecoveryStatus.CHECKPOINT_RESTORED,
                "checkpoint_id": checkpoint_id,
                "progress": 50.0,
            }
        )
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def resume_execution(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Resume execution after recovery.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(
            update={
                "status": RecoveryStatus.EXECUTION_RESUMED,
                "progress": 100.0,
                "completed_at": datetime.now(timezone.utc),
            }
        )
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def escalate_to_human(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Escalate a recovery to human intervention.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(update={"status": RecoveryStatus.HUMAN_INTERVENTION})
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def notify_human(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Notify a human about a recovery.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(update={"status": RecoveryStatus.HUMAN_NOTIFIED})
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def retry(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Retry a recovery operation.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The updated RecoveryState.
        """
        recovery = self._get_recovery(recovery_id)
        updated = recovery.model_copy(update={"status": RecoveryStatus.RETRY})
        self._persistence.write_state(EntityType.RECOVERY, recovery_id, updated)
        return updated

    def get_recovery_state(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Get the state of a recovery operation.

        Args:
            recovery_id: The recovery ID.

        Returns:
            The RecoveryState.

        Raises:
            RecoveryError: If the recovery does not exist.
        """
        return self._get_recovery(recovery_id)

    def _get_recovery(self, recovery_id: uuid.UUID) -> RecoveryState:
        """Get a recovery state by ID."""
        try:
            state = self._persistence.read_state(EntityType.RECOVERY, recovery_id)
        except Exception as exc:
            raise RecoveryError(
                f"Recovery with ID {recovery_id} not found",
                details={"recovery_id": str(recovery_id)},
            ) from exc
        if not isinstance(state, RecoveryState):
            raise RecoveryError(
                f"Invalid recovery state for ID {recovery_id}",
                details={"recovery_id": str(recovery_id)},
            )
        return state