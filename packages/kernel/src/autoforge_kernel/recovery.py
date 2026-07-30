"""
Recovery Module

Responsible for handling failures and coordinating recovery.
This module implements the Recovery component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    RecoveryModule,
    FailureDetector,
    RecoveryCoordinator,
    EventBus,
    RuntimeStateManager,
    ExecutionContinuityManager,
)


class DefaultFailureDetector(FailureDetector):
    """
    Default implementation of failure detection.

    Detects failures across all components.
    """

    async def detect_failure(self, event: Any) -> dict[str, Any] | None:
        """
        Detect if an event represents a failure.

        Args:
            event: The event to check.

        Returns:
            Failure details if detected, None otherwise.
        """
        # Check if event is a failure event
        if hasattr(event, "event_type"):
            from autoforge_events.event_types import EventType

            if event.event_type in [EventType.FAILED, EventType.CANCELLED]:
                return {
                    "failure_id": uuid.uuid4(),
                    "source": event.aggregate_type,
                    "error": event.metadata.get("error", "Unknown error"),
                    "severity": "error",
                    "recoverable": True,
                    "timestamp": event.occurred_at,
                    "event": event,
                }

        return None

    async def classify_failure(self, failure: dict[str, Any]) -> dict[str, Any]:
        """
        Classify a failure by source, severity, and recoverability.

        Args:
            failure: The failure details.

        Returns:
            Classified failure.
        """
        error = failure.get("error", "").lower()

        # Classify by source
        if "provider" in error or "model" in error or "llm" in error:
            source = "llm_failure"
        elif "tool" in error or "connector" in error:
            source = "tool_failure"
        elif "agent" in error or "worker" in error:
            source = "agent_failure"
        elif "infrastructure" in error or "service" in error:
            source = "infrastructure_failure"
        elif "external" in error or "network" in error:
            source = "external_failure"
        else:
            source = "unknown"

        # Classify by severity
        severity = failure.get("severity", "error")

        # Classify by recoverability
        if source in ["llm_failure", "tool_failure", "external_failure"]:
            recoverable = True
        elif source == "infrastructure_failure":
            recoverable = True
        else:
            recoverable = False

        return {
            **failure,
            "source": source,
            "severity": severity,
            "recoverable": recoverable,
        }


class DefaultRecoveryCoordinator(RecoveryCoordinator):
    """
    Default implementation of recovery coordination.

    Coordinates recovery from failures.
    """

    def __init__(
        self,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
    ):
        """
        Initialize the recovery coordinator.

        Args:
            execution_continuity_manager: Execution continuity manager.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
        """
        self.execution_continuity_manager = execution_continuity_manager
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager

    async def coordinate_recovery(
        self,
        project_id: uuid.UUID,
        failure: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Coordinate recovery from a failure.

        Args:
            project_id: The project.
            failure: The failure details.

        Returns:
            Recovery result.
        """
        # Classify failure
        classified_failure = await self.classify_failure(failure)

        # Publish failure detected event
        if self.event_bus:
            await self._publish_event(
                event_type="failed",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={
                    "failure_id": str(classified_failure.get("failure_id")),
                    "source": classified_failure.get("source"),
                    "error": classified_failure.get("error"),
                },
            )

        # Attempt recovery if failure is recoverable
        if classified_failure.get("recoverable") and self.execution_continuity_manager:
            try:
                recovery_result = await self.execution_continuity_manager.recover(
                    failure_context=classified_failure
                )

                if recovery_result.get("success"):
                    # Publish recovery completed event
                    if self.event_bus:
                        await self._publish_event(
                            event_type="completed",
                            event_category="project",
                            aggregate_id=project_id,
                            aggregate_type="Project",
                            metadata={
                                "recovery_strategy": recovery_result.get("strategy", "unknown"),
                            },
                        )

                    return {
                        "success": True,
                        "recovery_strategy": recovery_result.get("strategy", "unknown"),
                        "result": recovery_result,
                    }
            except Exception as e:
                # Recovery failed
                pass

        # Recovery failed or not recoverable
        if self.event_bus:
            await self._publish_event(
                event_type="failed",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={
                    "recovery_failed": True,
                    "error": "Recovery failed or not recoverable",
                },
            )

        return {
            "success": False,
            "error": "Recovery failed or not recoverable",
        }

    async def _publish_event(
        self,
        event_type: str,
        event_category: str,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish an event.

        Args:
            event_type: The event type.
            event_category: The event category.
            aggregate_id: The aggregate ID.
            aggregate_type: The aggregate type.
            metadata: Optional metadata.
        """
        if not self.event_bus:
            return

        from autoforge_events.base import BaseEvent as DomainBaseEvent
        from autoforge_events.event_types import EventCategory, EventType

        # Map string to enum
        try:
            evt_type = EventType[event_type.upper()]
        except KeyError:
            evt_type = EventType.SYSTEM_EVENT

        try:
            evt_category = EventCategory[event_category.upper()]
        except KeyError:
            evt_category = EventCategory.SYSTEM_EVENT

        event = DomainBaseEvent(
            event_type=evt_type,
            event_category=evt_category,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            metadata=metadata or {},
        )

        await self.event_bus.publish(event)


class DefaultRecoveryModule(RecoveryModule):
    """
    Default implementation of the recovery module.
    """

    def __init__(
        self,
        failure_detector: FailureDetector | None = None,
        recovery_coordinator: RecoveryCoordinator | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
    ):
        """
        Initialize the recovery module.

        Args:
            failure_detector: Failure detector.
            recovery_coordinator: Recovery coordinator.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
            execution_continuity_manager: Execution continuity manager.
        """
        self.failure_detector = failure_detector or DefaultFailureDetector()
        self.recovery_coordinator = recovery_coordinator or DefaultRecoveryCoordinator(
            execution_continuity_manager=execution_continuity_manager,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
        )
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager

    async def handle_failure(
        self,
        project_id: uuid.UUID,
        failure: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Handle a failure and coordinate recovery.

        Args:
            project_id: The project.
            failure: The failure details.

        Returns:
            Recovery result.
        """
        return await self.recovery_coordinator.coordinate_recovery(project_id, failure)

    async def restore_from_checkpoint(
        self,
        project_id: uuid.UUID,
        checkpoint_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Restore a project from a checkpoint.

        Args:
            project_id: The project.
            checkpoint_id: The checkpoint to restore from.

        Returns:
            Restoration result.
        """
        if not self.execution_continuity_manager:
            return {
                "success": False,
                "error": "Execution continuity manager not configured",
            }

        try:
            result = await self.execution_continuity_manager.restore_checkpoint(checkpoint_id)

            if result.get("success"):
                # Update project state
                if self.runtime_state_manager:
                    # Update project state to reflect restoration
                    pass

                # Publish checkpoint restored event
                if self.event_bus:
                    await self._publish_event(
                        event_type="completed",
                        event_category="project",
                        aggregate_id=project_id,
                        aggregate_type="Project",
                        metadata={
                            "checkpoint_id": str(checkpoint_id),
                            "restored": True,
                        },
                    )

                return {
                    "success": True,
                    "checkpoint_id": str(checkpoint_id),
                    "result": result,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _publish_event(
        self,
        event_type: str,
        event_category: str,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish an event.

        Args:
            event_type: The event type.
            event_category: The event category.
            aggregate_id: The aggregate ID.
            aggregate_type: The aggregate type.
            metadata: Optional metadata.
        """
        if not self.event_bus:
            return

        from autoforge_events.base import BaseEvent as DomainBaseEvent
        from autoforge_events.event_types import EventCategory, EventType

        # Map string to enum
        try:
            evt_type = EventType[event_type.upper()]
        except KeyError:
            evt_type = EventType.SYSTEM_EVENT

        try:
            evt_category = EventCategory[event_category.upper()]
        except KeyError:
            evt_category = EventCategory.SYSTEM_EVENT

        event = DomainBaseEvent(
            event_type=evt_type,
            event_category=evt_category,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            metadata=metadata or {},
        )

        await self.event_bus.publish(event)


class RecoveryModuleWrapper:
    """
    Recovery Module Wrapper.

    Coordinates failure detection and recovery.
    """

    def __init__(
        self,
        recovery_module: RecoveryModule | None = None,
        failure_detector: FailureDetector | None = None,
        recovery_coordinator: RecoveryCoordinator | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
    ):
        """
        Initialize the recovery module wrapper.

        Args:
            recovery_module: Recovery module.
            failure_detector: Failure detector.
            recovery_coordinator: Recovery coordinator.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
            execution_continuity_manager: Execution continuity manager.
        """
        self.recovery_module = recovery_module or DefaultRecoveryModule(
            failure_detector=failure_detector,
            recovery_coordinator=recovery_coordinator,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
            execution_continuity_manager=execution_continuity_manager,
        )

    async def handle_failure(
        self,
        project_id: uuid.UUID,
        failure: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Handle a failure.

        Args:
            project_id: The project.
            failure: The failure details.

        Returns:
            Recovery result.
        """
        return await self.recovery_module.handle_failure(project_id, failure)

    async def restore_from_checkpoint(
        self,
        project_id: uuid.UUID,
        checkpoint_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Restore from checkpoint.

        Args:
            project_id: The project.
            checkpoint_id: The checkpoint.

        Returns:
            Restoration result.
        """
        return await self.recovery_module.restore_from_checkpoint(project_id, checkpoint_id)