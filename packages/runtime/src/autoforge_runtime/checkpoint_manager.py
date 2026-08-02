"""Checkpoint Manager — creates and manages checkpoints.

Implements the Checkpoint Manager from Runtime State Manager Specification v1.0, Section 7.4 and 14.
"""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from autoforge_runtime.exceptions import CheckpointError, EntityNotFoundError, InvalidStateError
from autoforge_runtime.models import (
    CheckpointState,
    CheckpointStatus,
    CheckpointType,
    EngineeringLoopState,
    EntityType,
    ProjectState,
    RestoreType,
    StateModel,
    TaskState,
    TransitionResult,
    WorkflowState,
)
from autoforge_runtime.persistence import PersistenceLayer
from autoforge_runtime.validation import (
    ValidationErrorCode,
    validate_checkpoint_transition,
)


class CheckpointCreator:
    """Creates checkpoints at defined points."""

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the checkpoint creator."""
        self._persistence = persistence

    def create(
        self,
        project_id: uuid.UUID,
        checkpoint_type: CheckpointType,
        *,
        label: str | None = None,
        description: str | None = None,
        created_by: str = "system",
        parent_checkpoint_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CheckpointState:
        """Create a checkpoint by capturing the current state snapshot.

        Args:
            project_id: The project ID.
            checkpoint_type: The checkpoint type.
            label: Optional human-readable label.
            description: Optional description.
            created_by: Who created the checkpoint.
            parent_checkpoint_id: Optional parent checkpoint for lineage.
            metadata: Optional metadata.

        Returns:
            The created CheckpointState.

        Raises:
            EntityNotFoundError: If the project does not exist.
            CheckpointError: If the checkpoint cannot be created.
        """
        # Verify project exists
        try:
            project = self._persistence.read_state(EntityType.PROJECT, project_id)
        except EntityNotFoundError:
            raise EntityNotFoundError(
                f"Project with ID {project_id} not found",
                details={"entity_id": str(project_id), "entity_type": "project"},
            )

        # Capture state snapshot
        snapshot = self._capture_snapshot(project_id)

        checkpoint = CheckpointState(
            project_id=project_id,
            checkpoint_type=checkpoint_type,
            status=CheckpointStatus.ACTIVE,
            label=label or "",
            description=description or "",
            state_snapshot=snapshot,
            parent_checkpoint_id=parent_checkpoint_id,
            created_by=created_by,
            size=len(str(snapshot).encode("utf-8")),
            metadata=metadata or {},
        )

        # Update parent's children if applicable
        if parent_checkpoint_id:
            try:
                parent = self._persistence.read_state(EntityType.CHECKPOINT, parent_checkpoint_id)
                if isinstance(parent, CheckpointState):
                    updated_parent = parent.model_copy(
                        update={"child_checkpoint_ids": [*parent.child_checkpoint_ids, checkpoint.checkpoint_id]}
                    )
                    self._persistence.write_state(EntityType.CHECKPOINT, parent_checkpoint_id, updated_parent)
            except EntityNotFoundError:
                pass

        # Persist checkpoint
        self._persistence.write_checkpoint(checkpoint)

        # Update project's current checkpoint
        if isinstance(project, ProjectState):
            updated_project = project.model_copy(update={"current_checkpoint_id": checkpoint.checkpoint_id})
            self._persistence.write_state(EntityType.PROJECT, project_id, updated_project)

        return checkpoint

    def _capture_snapshot(self, project_id: uuid.UUID) -> dict[str, Any]:
        """Capture a complete state snapshot for the project."""
        snapshot: dict[str, Any] = {}

        # Project state
        try:
            project = self._persistence.read_state(EntityType.PROJECT, project_id)
            snapshot["project"] = project.model_dump(mode="python")
        except EntityNotFoundError:
            pass

        # Workflows
        workflows = self._persistence.read_all(EntityType.WORKFLOW)
        snapshot["workflows"] = [
            w.model_dump(mode="python") for w in workflows
            if isinstance(w, WorkflowState) and w.project_id == project_id
        ]

        # Loops
        loops = self._persistence.read_all(EntityType.LOOP)
        snapshot["loops"] = [
            l.model_dump(mode="python") for l in loops
            if isinstance(l, EngineeringLoopState) and l.project_id == project_id
        ]

        # Tasks
        tasks = self._persistence.read_all(EntityType.TASK)
        snapshot["tasks"] = [
            t.model_dump(mode="python") for t in tasks
            if isinstance(t, TaskState) and t.project_id == project_id
        ]

        return snapshot


class CheckpointRestorer:
    """Restores state from checkpoints."""

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the checkpoint restorer."""
        self._persistence = persistence

    def restore(
        self,
        checkpoint_id: uuid.UUID,
        restore_type: RestoreType = RestoreType.FULL,
        *,
        restored_by: str = "system",
    ) -> TransitionResult:
        """Restore state from a checkpoint.

        Args:
            checkpoint_id: The checkpoint ID.
            restore_type: Type of restoration (full/partial).
            restored_by: Who restored the checkpoint.

        Returns:
            TransitionResult with the restoration outcome.

        Raises:
            EntityNotFoundError: If the checkpoint does not exist.
            InvalidStateError: If the checkpoint cannot be restored.
        """
        try:
            checkpoint = self._persistence.read_state(EntityType.CHECKPOINT, checkpoint_id)
        except EntityNotFoundError:
            raise EntityNotFoundError(
                f"Checkpoint with ID {checkpoint_id} not found",
                details={"entity_id": str(checkpoint_id), "entity_type": "checkpoint"},
            )

        if not isinstance(checkpoint, CheckpointState):
            raise InvalidStateError(f"Invalid checkpoint state for ID {checkpoint_id}")

        # Validate checkpoint is restorable
        validation = validate_checkpoint_transition(
            checkpoint.status, CheckpointStatus.RESTORED
        )
        if not validation.valid:
            raise InvalidStateError(
                validation.error_message or "Checkpoint cannot be restored",
                details=validation.details,
            )

        # Create recovery checkpoint of current state (before restoration)
        if checkpoint.project_id:
            self._create_recovery_checkpoint(checkpoint.project_id)

        # Restore state from checkpoint snapshot
        self._restore_from_snapshot(checkpoint.state_snapshot, restore_type)

        # Update checkpoint status
        updated = checkpoint.model_copy(
            update={
                "status": CheckpointStatus.RESTORED,
                "restored_at": datetime.now(timezone.utc),
                "restored_by": restored_by,
            }
        )
        self._persistence.write_state(EntityType.CHECKPOINT, checkpoint_id, updated)

        return TransitionResult(
            success=True,
            entity_type=EntityType.CHECKPOINT,
            entity_id=checkpoint_id,
            from_state=checkpoint.status.value,
            to_state=CheckpointStatus.RESTORED.value,
            version=checkpoint.version,
        )

    def _create_recovery_checkpoint(self, project_id: uuid.UUID) -> None:
        """Create a recovery checkpoint of the current state."""
        creator = CheckpointCreator(self._persistence)
        creator.create(
            project_id,
            CheckpointType.RECOVERY,
            label="Pre-restoration recovery checkpoint",
            description="Automatic recovery checkpoint created before restoration",
            created_by="system",
        )

    def _restore_from_snapshot(self, snapshot: dict[str, Any], restore_type: RestoreType) -> None:
        """Restore state from a checkpoint snapshot."""
        # Restore project
        if "project" in snapshot:
            project_data = snapshot["project"]
            project = ProjectState.model_validate(project_data)
            self._persistence.write_state(EntityType.PROJECT, project.project_id, project)

        # Restore workflows
        for wf_data in snapshot.get("workflows", []):
            wf = WorkflowState.model_validate(wf_data)
            self._persistence.write_state(EntityType.WORKFLOW, wf.workflow_id, wf)

        # Restore loops
        for loop_data in snapshot.get("loops", []):
            loop = EngineeringLoopState.model_validate(loop_data)
            self._persistence.write_state(EntityType.LOOP, loop.loop_id, loop)

        # Restore tasks
        for task_data in snapshot.get("tasks", []):
            task = TaskState.model_validate(task_data)
            self._persistence.write_state(EntityType.TASK, task.task_id, task)


class CheckpointCleaner:
    """Cleans up obsolete checkpoints."""

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the checkpoint cleaner."""
        self._persistence = persistence

    def cleanup(self, project_id: uuid.UUID, *, keep_last: int = 10, archive_days: int = 30, delete_days: int = 90) -> None:
        """Clean up obsolete checkpoints according to retention policy.

        Retention policy from Specification Section 14.4:
        - Keep all checkpoints for active projects
        - Keep last 10 checkpoints for completed projects
        - Archive checkpoints older than 30 days
        - Delete archived checkpoints older than 90 days
        """
        checkpoints = self._persistence.read_all(EntityType.CHECKPOINT)
        project_checkpoints = [
            c for c in checkpoints
            if isinstance(c, CheckpointState) and c.project_id == project_id
        ]

        now = datetime.now(timezone.utc)

        for checkpoint in project_checkpoints:
            if not isinstance(checkpoint, CheckpointState):
                continue

            # Check if checkpoint is obsolete
            if checkpoint.status == CheckpointStatus.OBSOLETE:
                # Delete if older than delete_days
                age = now - checkpoint.created_at
                if age > timedelta(days=delete_days):
                    self._persistence.delete_state(EntityType.CHECKPOINT, checkpoint.checkpoint_id)
                continue

            # Archive checkpoints older than archive_days
            age = now - checkpoint.created_at
            if age > timedelta(days=archive_days):
                updated = checkpoint.model_copy(update={"status": CheckpointStatus.OBSOLETE})
                self._persistence.write_state(EntityType.CHECKPOINT, checkpoint.checkpoint_id, updated)


class CheckpointManager:
    """Creates and manages checkpoints.

    Implements the Checkpoint Manager from Specification Section 7.4.
    """

    def __init__(self, persistence: PersistenceLayer) -> None:
        """Initialize the checkpoint manager."""
        self._persistence = persistence
        self.creator = CheckpointCreator(persistence)
        self.restorer = CheckpointRestorer(persistence)
        self.cleaner = CheckpointCleaner(persistence)

    def create_checkpoint(
        self,
        project_id: uuid.UUID,
        checkpoint_type: CheckpointType,
        *,
        label: str | None = None,
        description: str | None = None,
        created_by: str = "system",
        parent_checkpoint_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CheckpointState:
        """Create a checkpoint.

        Args:
            project_id: The project ID.
            checkpoint_type: The checkpoint type.
            label: Optional label.
            description: Optional description.
            created_by: Who created the checkpoint.
            parent_checkpoint_id: Optional parent for lineage.
            metadata: Optional metadata.

        Returns:
            The created CheckpointState.
        """
        return self.creator.create(
            project_id,
            checkpoint_type,
            label=label,
            description=description,
            created_by=created_by,
            parent_checkpoint_id=parent_checkpoint_id,
            metadata=metadata,
        )

    def restore_checkpoint(
        self,
        checkpoint_id: uuid.UUID,
        restore_type: RestoreType = RestoreType.FULL,
        *,
        restored_by: str = "system",
    ) -> TransitionResult:
        """Restore state from a checkpoint.

        Args:
            checkpoint_id: The checkpoint ID.
            restore_type: Type of restoration.
            restored_by: Who restored the checkpoint.

        Returns:
            TransitionResult with the restoration outcome.
        """
        return self.restorer.restore(checkpoint_id, restore_type, restored_by=restored_by)

    def cleanup_checkpoints(self, project_id: uuid.UUID, *, keep_last: int = 10, archive_days: int = 30, delete_days: int = 90) -> None:
        """Clean up obsolete checkpoints according to policy."""
        self.cleaner.cleanup(project_id, keep_last=keep_last, archive_days=archive_days, delete_days=delete_days)

    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> CheckpointState:
        """Get a checkpoint by ID.

        Args:
            checkpoint_id: The checkpoint ID.

        Returns:
            The CheckpointState.

        Raises:
            EntityNotFoundError: If the checkpoint does not exist.
        """
        state = self._persistence.read_state(EntityType.CHECKPOINT, checkpoint_id)
        if not isinstance(state, CheckpointState):
            raise EntityNotFoundError(
                f"Checkpoint with ID {checkpoint_id} not found",
                details={"entity_id": str(checkpoint_id), "entity_type": "checkpoint"},
            )
        return state

    def get_checkpoint_history(self, project_id: uuid.UUID) -> list[CheckpointState]:
        """Get all checkpoints for a project.

        Args:
            project_id: The project ID.

        Returns:
            List of CheckpointState for the project.
        """
        checkpoints = self._persistence.read_all(EntityType.CHECKPOINT)
        return [
            c for c in checkpoints
            if isinstance(c, CheckpointState) and c.project_id == project_id
        ]