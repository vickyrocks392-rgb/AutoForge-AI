"""
Lifecycle Coordination Module

Responsible for coordinating Kernel runtime lifecycle and project lifecycle.
This module implements the Lifecycle Coordination component of the Kernel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from autoforge_kernel.interfaces import (
    LifecycleCoordinator,
    RuntimeLifecycleManager,
    ProjectLifecycleManager,
    EventBus,
    RuntimeStateManager,
    ExecutionContinuityManager,
)
from autoforge_events.event_types import EventCategory, EventType
from autoforge_kernel.event_utils import publish_event, make_timestamp


class KernelRuntimeStatus(str, Enum):
    """Runtime status for the Kernel."""

    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    PROCESSING = "processing"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ProjectStatus(str, Enum):
    """Project status matching the Kernel Specification v1.0 Section 10.1."""

    CREATED = "created"
    PLANNING = "planning"
    RUNNING = "running"
    REVIEWING = "reviewing"
    PAUSED = "paused"
    COMPLETING = "completing"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DefaultRuntimeLifecycleManager(RuntimeLifecycleManager):
    """
    Default implementation of runtime lifecycle management.

    Manages the Kernel runtime lifecycle.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
        kernel_id: uuid.UUID | None = None,
    ):
        """
        Initialize the runtime lifecycle manager.

        Args:
            event_bus: Event bus for publishing events.
            runtime_state_manager: Runtime state manager.
            kernel_id: Optional kernel ID (generates new one if not provided).
        """
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager
        self.kernel_id = kernel_id or uuid.uuid4()
        self.status = KernelRuntimeStatus.CREATED
        self.started_at: datetime | None = None
        self.active_project_count = 0

    async def initialize(self) -> None:
        """Initialize the runtime."""
        self.status = KernelRuntimeStatus.STARTING
        self.started_at = datetime.now(timezone.utc)

        # Publish kernel.starting event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_STARTING,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"version": "0.1.0"},
        )

    async def start(self) -> None:
        """Start the runtime."""
        self.status = KernelRuntimeStatus.READY

        # Publish kernel.started event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_STARTED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={
                "version": "0.1.0",
                "active_project_count": self.active_project_count,
            },
        )

    async def pause(self, reason: str) -> None:
        """
        Pause the runtime.

        Args:
            reason: Reason for pausing.
        """
        self.status = KernelRuntimeStatus.PAUSING

        # Publish kernel.pausing event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_PAUSING,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

        self.status = KernelRuntimeStatus.PAUSED

        # Publish kernel.paused event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_PAUSED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

    async def resume(self) -> None:
        """Resume the runtime."""
        self.status = KernelRuntimeStatus.RESUMING

        # Publish kernel.resuming event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_RESUMING,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
        )

        self.status = KernelRuntimeStatus.READY

        # Publish kernel.ready event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_READY,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
        )

    async def shutdown(self, reason: str) -> None:
        """
        Shutdown the runtime.

        Args:
            reason: Reason for shutdown.
        """
        self.status = KernelRuntimeStatus.STOPPING

        # Publish kernel.stopping event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_STOPPING,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

        self.status = KernelRuntimeStatus.STOPPED

        # Publish kernel.stopped event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.KERNEL_STOPPED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

    def get_status(self) -> str:
        """Get the current runtime status."""
        return self.status.value


class DefaultProjectLifecycleManager(ProjectLifecycleManager):
    """
    Default implementation of project lifecycle management.

    Manages project lifecycle state transitions.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
    ):
        """
        Initialize the project lifecycle manager.

        Args:
            event_bus: Event bus for publishing events.
            runtime_state_manager: Runtime state manager.
            execution_continuity_manager: Execution continuity manager.
        """
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager
        self.execution_continuity_manager = execution_continuity_manager
        self.project_statuses: dict[uuid.UUID, ProjectStatus] = {}

    async def start_project(self, project_id: uuid.UUID) -> None:
        """
        Start a project.

        Args:
            project_id: The project to start.
        """
        await self.transition_project_status(project_id, ProjectStatus.RUNNING)

        # Publish project.running event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_RUNNING,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
        )

    async def pause_project(self, project_id: uuid.UUID, reason: str) -> None:
        """
        Pause a project.

        Args:
            project_id: The project to pause.
            reason: Reason for pausing.
        """
        # Save checkpoint before pausing
        if self.execution_continuity_manager:
            try:
                await self.execution_continuity_manager.recover(
                    failure_context={"project_id": str(project_id), "action": "pause"}
                )
            except Exception:
                # Checkpoint failed, but continue with pause
                pass

        await self.transition_project_status(project_id, ProjectStatus.PAUSED)

        # Publish project.paused event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_PAUSED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={"reason": reason},
        )

    async def resume_project(self, project_id: uuid.UUID) -> None:
        """
        Resume a project.

        Args:
            project_id: The project to resume.
        """
        await self.transition_project_status(project_id, ProjectStatus.RUNNING)

        # Publish project.resumed event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_RESUMED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
        )

    async def cancel_project(self, project_id: uuid.UUID, reason: str) -> None:
        """
        Cancel a project.

        Args:
            project_id: The project to cancel.
            reason: Reason for cancellation.
        """
        await self.transition_project_status(project_id, ProjectStatus.CANCELLED)

        # Publish project.cancelled event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_CANCELLED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={"reason": reason},
        )

    async def complete_project(self, project_id: uuid.UUID) -> None:
        """
        Complete a project.

        Args:
            project_id: The project to complete.
        """
        await self.transition_project_status(project_id, ProjectStatus.COMPLETING)

        # Publish project.completing event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_COMPLETING,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
        )

    async def fail_project(self, project_id: uuid.UUID, error: str) -> None:
        """
        Fail a project.

        Args:
            project_id: The project to fail.
            error: The error message.
        """
        await self.transition_project_status(project_id, ProjectStatus.FAILED)

        # Publish project.failed event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_FAILED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={"error": error},
        )

    def get_project_status(self, project_id: uuid.UUID) -> str:
        """
        Get the current project status.

        Args:
            project_id: The project.

        Returns:
            The project status.
        """
        status = self.project_statuses.get(project_id, ProjectStatus.CREATED)
        return status.value

    async def transition_project_status(
        self,
        project_id: uuid.UUID,
        new_status: ProjectStatus,
    ) -> None:
        """
        Transition a project to a new status.

        Args:
            project_id: The project.
            new_status: The new status.
        """
        # Validate transition
        current_status = self.project_statuses.get(project_id)
        if not self._is_valid_transition(current_status, new_status):
            raise ValueError(
                f"Invalid transition from {current_status} to {new_status}"
            )

        # Update status
        self.project_statuses[project_id] = new_status

        # Update state manager
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status=new_status.value,
            )

    def _is_valid_transition(
        self,
        current_status: ProjectStatus | None,
        new_status: ProjectStatus,
    ) -> bool:
        """
        Check if a status transition is valid per Kernel Specification v1.0 Section 10.3.

        Args:
            current_status: The current status.
            new_status: The new status.

        Returns:
            True if the transition is valid, False otherwise.
        """
        # Terminal states cannot transition
        if current_status in [ProjectStatus.FINISHED, ProjectStatus.FAILED, ProjectStatus.CANCELLED]:
            return False

        # Valid transitions per specification Section 10.2 and 10.3:
        # Created -> Planning, Cancelled
        # Planning -> Running, Failed, Cancelled
        # Running -> Reviewing, Paused, Completing, Failed, Cancelled
        # Reviewing -> Running, Paused, Failed, Cancelled
        # Paused -> Running, Cancelled
        # Completing -> Finished, Failed
        # Finished, Failed, Cancelled -> (terminal)
        valid_transitions = {
            None: [ProjectStatus.PLANNING, ProjectStatus.CANCELLED],
            ProjectStatus.CREATED: [ProjectStatus.PLANNING, ProjectStatus.CANCELLED],
            ProjectStatus.PLANNING: [ProjectStatus.RUNNING, ProjectStatus.FAILED, ProjectStatus.CANCELLED],
            ProjectStatus.RUNNING: [
                ProjectStatus.REVIEWING,
                ProjectStatus.PAUSED,
                ProjectStatus.COMPLETING,
                ProjectStatus.FAILED,
                ProjectStatus.CANCELLED,
            ],
            ProjectStatus.REVIEWING: [
                ProjectStatus.RUNNING,
                ProjectStatus.PAUSED,
                ProjectStatus.FAILED,
                ProjectStatus.CANCELLED,
            ],
            ProjectStatus.PAUSED: [ProjectStatus.RUNNING, ProjectStatus.CANCELLED],
            ProjectStatus.COMPLETING: [ProjectStatus.FINISHED, ProjectStatus.FAILED],
        }

        allowed_transitions = valid_transitions.get(current_status, [])
        return new_status in allowed_transitions


class DefaultLifecycleCoordinator(LifecycleCoordinator):
    """
    Default implementation of lifecycle coordination.

    Coordinates runtime and project lifecycles.
    """

    def __init__(
        self,
        runtime_lifecycle_manager: RuntimeLifecycleManager | None = None,
        project_lifecycle_manager: ProjectLifecycleManager | None = None,
    ):
        """
        Initialize the lifecycle coordinator.

        Args:
            runtime_lifecycle_manager: Runtime lifecycle manager.
            project_lifecycle_manager: Project lifecycle manager.
        """
        self.runtime_lifecycle_manager = runtime_lifecycle_manager or DefaultRuntimeLifecycleManager()
        self.project_lifecycle_manager = project_lifecycle_manager or DefaultProjectLifecycleManager()

    async def coordinate_runtime_lifecycle(self, action: str, **kwargs: Any) -> None:
        """
        Coordinate runtime lifecycle actions.

        Args:
            action: The action to perform.
            **kwargs: Additional arguments.
        """
        if action == "initialize":
            await self.runtime_lifecycle_manager.initialize()
        elif action == "start":
            await self.runtime_lifecycle_manager.start()
        elif action == "pause":
            reason = kwargs.get("reason", "Unknown")
            await self.runtime_lifecycle_manager.pause(reason)
        elif action == "resume":
            await self.runtime_lifecycle_manager.resume()
        elif action == "shutdown":
            reason = kwargs.get("reason", "Unknown")
            await self.runtime_lifecycle_manager.shutdown(reason)

    async def coordinate_project_lifecycle(
        self,
        project_id: uuid.UUID,
        action: str,
        **kwargs: Any,
    ) -> None:
        """
        Coordinate project lifecycle actions.

        Args:
            project_id: The project.
            action: The action to perform.
            **kwargs: Additional arguments.
        """
        if action == "start":
            await self.project_lifecycle_manager.start_project(project_id)
        elif action == "pause":
            reason = kwargs.get("reason", "Unknown")
            await self.project_lifecycle_manager.pause_project(project_id, reason)
        elif action == "resume":
            await self.project_lifecycle_manager.resume_project(project_id)
        elif action == "cancel":
            reason = kwargs.get("reason", "Unknown")
            await self.project_lifecycle_manager.cancel_project(project_id, reason)
        elif action == "complete":
            await self.project_lifecycle_manager.complete_project(project_id)
        elif action == "fail":
            error = kwargs.get("error", "Unknown error")
            await self.project_lifecycle_manager.fail_project(project_id, error)


class LifecycleCoordinationModule:
    """
    Lifecycle Coordination Module.

    Coordinates runtime and project lifecycles.
    """

    def __init__(
        self,
        lifecycle_coordinator: LifecycleCoordinator | None = None,
        runtime_lifecycle_manager: RuntimeLifecycleManager | None = None,
        project_lifecycle_manager: ProjectLifecycleManager | None = None,
        event_bus: EventBus | None = None,
        kernel_id: uuid.UUID | None = None,
    ):
        """
        Initialize the lifecycle coordination module.

        Args:
            lifecycle_coordinator: Lifecycle coordinator.
            runtime_lifecycle_manager: Runtime lifecycle manager.
            project_lifecycle_manager: Project lifecycle manager.
            event_bus: Event bus for publishing events.
            kernel_id: Optional kernel ID.
        """
        self.lifecycle_coordinator = lifecycle_coordinator or DefaultLifecycleCoordinator(
            runtime_lifecycle_manager=runtime_lifecycle_manager or DefaultRuntimeLifecycleManager(
                event_bus=event_bus,
                runtime_state_manager=None,
                kernel_id=kernel_id,
            ),
            project_lifecycle_manager=project_lifecycle_manager,
        )

    async def coordinate_runtime_lifecycle(self, action: str, **kwargs: Any) -> None:
        """
        Coordinate runtime lifecycle.

        Args:
            action: The action.
            **kwargs: Additional arguments.
        """
        await self.lifecycle_coordinator.coordinate_runtime_lifecycle(action, **kwargs)

    async def coordinate_project_lifecycle(
        self,
        project_id: uuid.UUID,
        action: str,
        **kwargs: Any,
    ) -> None:
        """
        Coordinate project lifecycle.

        Args:
            project_id: The project.
            action: The action.
            **kwargs: Additional arguments.
        """
        await self.lifecycle_coordinator.coordinate_project_lifecycle(
            project_id, action, **kwargs
        )