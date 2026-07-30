"""
Approval Coordinator Module

Responsible for managing human approval gates.
This module implements the Approval Coordinator component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    ApprovalCoordinator,
    EventBus,
    RuntimeStateManager,
)


class DefaultApprovalCoordinator(ApprovalCoordinator):
    """
    Default implementation of approval coordination.

    Manages human approval gates and processes approval decisions.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
    ):
        """
        Initialize the approval coordinator.

        Args:
            event_bus: Event bus for publishing events.
            runtime_state_manager: Runtime state manager.
        """
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager
        self.pending_approvals: dict[uuid.UUID, dict[str, Any]] = {}

    async def request_approval(
        self,
        project_id: uuid.UUID,
        approval_context: dict[str, Any],
    ) -> uuid.UUID:
        """
        Request human approval.

        Args:
            project_id: The project.
            approval_context: The approval context.

        Returns:
            Approval ID.
        """
        # Generate approval ID
        approval_id = uuid.uuid4()

        # Store approval request
        self.pending_approvals[approval_id] = {
            "approval_id": approval_id,
            "project_id": project_id,
            "context": approval_context,
            "status": "pending",
            "created_at": uuid.uuid4(),  # TODO: Use proper timestamp
        }

        # Update project state to Reviewing
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Reviewing",
                metadata={"approval_id": str(approval_id)},
            )

        # Publish approval.required event
        if self.event_bus:
            await self._publish_event(
                event_type="created",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={
                    "approval_id": str(approval_id),
                    "approval_context": approval_context,
                },
            )

        return approval_id

    async def process_decision(
        self,
        approval_id: uuid.UUID,
        decision: str,
        feedback: str | None = None,
        modifications: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process an approval decision.

        Args:
            approval_id: The approval request identifier.
            decision: The decision (approved, rejected, modified).
            feedback: Optional human feedback.
            modifications: Optional modifications to the plan.

        Returns:
            Dictionary containing status and next_actions.
        """
        # Validate approval ID
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval {approval_id} not found")

        # Get approval request
        approval_request = self.pending_approvals[approval_id]
        project_id = approval_request["project_id"]

        # Update approval status
        approval_request["status"] = decision
        approval_request["decision"] = decision
        approval_request["feedback"] = feedback
        approval_request["modifications"] = modifications
        approval_request["decided_at"] = uuid.uuid4()  # TODO: Use proper timestamp

        # Publish approval.decided event
        if self.event_bus:
            await self._publish_event(
                event_type="completed",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={
                    "approval_id": str(approval_id),
                    "decision": decision,
                    "feedback": feedback,
                },
            )

        # Process decision
        if decision == "approved":
            # Resume execution
            if self.runtime_state_manager:
                await self.runtime_state_manager.transition_state(
                    project_id=project_id,
                    new_status="Running",
                )

            return {
                "status": "approved",
                "next_actions": ["resume_execution"],
            }

        elif decision == "rejected":
            # Fail project
            if self.runtime_state_manager:
                await self.runtime_state_manager.transition_state(
                    project_id=project_id,
                    new_status="Failed",
                    metadata={"reason": "Approval rejected"},
                )

            return {
                "status": "rejected",
                "next_actions": ["fail_project"],
            }

        elif decision == "modified":
            # Create remediation plan
            if self.runtime_state_manager:
                await self.runtime_state_manager.transition_state(
                    project_id=project_id,
                    new_status="Running",
                    metadata={"modifications": modifications},
                )

            return {
                "status": "modified",
                "next_actions": ["create_remediation_plan", "resume_execution"],
                "modifications": modifications,
            }

        else:
            raise ValueError(f"Unknown decision: {decision}")

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


class ApprovalCoordinatorModule:
    """
    Approval Coordinator Module.

    Manages human approval gates.
    """

    def __init__(
        self,
        approval_coordinator: ApprovalCoordinator | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
    ):
        """
        Initialize the approval coordinator module.

        Args:
            approval_coordinator: Approval coordinator.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
        """
        self.approval_coordinator = approval_coordinator or DefaultApprovalCoordinator(
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
        )

    async def request_approval(
        self,
        project_id: uuid.UUID,
        approval_context: dict[str, Any],
    ) -> uuid.UUID:
        """
        Request human approval.

        Args:
            project_id: The project.
            approval_context: The approval context.

        Returns:
            Approval ID.
        """
        return await self.approval_coordinator.request_approval(project_id, approval_context)

    async def process_decision(
        self,
        approval_id: uuid.UUID,
        decision: str,
        feedback: str | None = None,
        modifications: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process an approval decision.

        Args:
            approval_id: The approval ID.
            decision: The decision.
            feedback: Optional feedback.
            modifications: Optional modifications.

        Returns:
            Result dictionary.
        """
        return await self.approval_coordinator.process_decision(
            approval_id, decision, feedback, modifications
        )