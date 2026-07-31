"""
Approval Coordinator Module

Responsible for managing human approval gates.
This module implements the Approval Coordinator component of the Kernel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from autoforge_events.event_types import EventCategory, EventType

from autoforge_kernel.interfaces import (
    ApprovalCoordinator,
    EventBus,
    RuntimeStateManager,
)
from autoforge_kernel.event_utils import publish_event, make_timestamp


class DefaultApprovalCoordinator(ApprovalCoordinator):
    """
    Default implementation of approval coordination.

    Manages human approval gates and processes approval decisions.
    Implements the full approval flow per Kernel Specification v1.0 Section 23:
    - Stage 1: Identify Approval Requirement
    - Stage 2: Prepare Approval Context
    - Stage 3: Request Approval
    - Stage 4: Human Review
    - Stage 5: Process Decision
    - Stage 6: Timeout Handling
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
        self.approval_timeout_seconds: int = 3600  # Default 1 hour

    async def request_approval(
        self,
        project_id: uuid.UUID,
        approval_context: dict[str, Any],
    ) -> uuid.UUID:
        """
        Request human approval.

        Implements Stages 1-3 of the approval flow:
        1. Identify approval requirement
        2. Prepare approval context
        3. Request approval

        Args:
            project_id: The project.
            approval_context: The approval context.

        Returns:
            Approval ID.
        """
        # Generate approval ID
        approval_id = uuid.uuid4()

        # Stage 1: Identify Approval Requirement
        # Determine approval policy from context
        approval_policy = approval_context.get("approval_policy", {})
        policy_type = approval_policy.get("type", "single")
        timeout_seconds = approval_policy.get("timeout_seconds", self.approval_timeout_seconds)
        escalation_chain = approval_policy.get("escalation_chain", [])

        # Stage 2: Prepare Approval Context
        # Gather and format context for human review
        prepared_context = self._prepare_approval_context(approval_context)
        created_at = make_timestamp()

        # Store approval request
        self.pending_approvals[approval_id] = {
            "approval_id": approval_id,
            "project_id": project_id,
            "context": prepared_context,
            "status": "pending",
            "policy_type": policy_type,
            "timeout_seconds": timeout_seconds,
            "escalation_chain": escalation_chain,
            "escalation_level": 0,
            "created_at": created_at,
            "decided_at": None,
            "decision": None,
            "feedback": None,
            "modifications": None,
        }

        # Update project state to Reviewing
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Reviewing",
                metadata={"approval_id": str(approval_id)},
            )

        # Stage 3: Request Approval - Publish approval.required event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.APPROVAL_REQUIRED,
            event_category=EventCategory.APPROVAL,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={
                "approval_id": str(approval_id),
                "approval_context": prepared_context,
                "timeout_seconds": timeout_seconds,
                "policy_type": policy_type,
            },
        )

        return approval_id

    def _prepare_approval_context(self, approval_context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for human review (Stage 2).

        Args:
            approval_context: Raw approval context.

        Returns:
            Formatted approval context.
        """
        return {
            "type": approval_context.get("type", "unknown"),
            "description": approval_context.get("description", "No description provided"),
            "task_description": approval_context.get("task_description", ""),
            "task_input": approval_context.get("task_input", {}),
            "task_output": approval_context.get("task_output", {}),
            "quality_metrics": approval_context.get("quality_metrics", {}),
            "risk_assessment": approval_context.get("risk_assessment", "unknown"),
            "alternatives": approval_context.get("alternatives", []),
            "recommendation": approval_context.get("recommendation", ""),
            "cost": approval_context.get("cost", 0.0),
            "duration": approval_context.get("duration", 0.0),
            "approval_policy": approval_context.get("approval_policy", {}),
        }

    async def process_decision(
        self,
        approval_id: uuid.UUID,
        decision: str,
        feedback: str | None = None,
        modifications: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process an approval decision (Stage 5).

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

        # Record decision
        decided_at = make_timestamp()
        approval_request["status"] = decision
        approval_request["decision"] = decision
        approval_request["feedback"] = feedback
        approval_request["modifications"] = modifications
        approval_request["decided_at"] = decided_at

        # Publish approval.decided event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.APPROVAL_DECIDED,
            event_category=EventCategory.APPROVAL,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={
                "approval_id": str(approval_id),
                "decision": decision,
                "feedback": feedback,
                "decided_at": decided_at,
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

        elif decision == "escalate":
            # Escalate to next approver
            return await self._handle_escalation(approval_id)

        else:
            raise ValueError(f"Unknown decision: {decision}")

    async def _handle_escalation(self, approval_id: uuid.UUID) -> dict[str, Any]:
        """
        Handle approval escalation.

        Args:
            approval_id: The approval request identifier.

        Returns:
            Escalation result.
        """
        approval_request = self.pending_approvals.get(approval_id)
        if not approval_request:
            raise ValueError(f"Approval {approval_id} not found")

        escalation_chain = approval_request.get("escalation_chain", [])
        current_level = approval_request.get("escalation_level", 0)

        if current_level < len(escalation_chain):
            # Escalate to next approver
            next_approver = escalation_chain[current_level]
            approval_request["escalation_level"] = current_level + 1
            approval_request["status"] = "escalated"

            # Publish approval.escalated event
            await publish_event(
                event_bus=self.event_bus,
                event_type=EventType.APPROVAL_ESCALATED,
                event_category=EventCategory.APPROVAL,
                aggregate_id=approval_request["project_id"],
                aggregate_type="Project",
                metadata={
                    "approval_id": str(approval_id),
                    "escalated_to": next_approver,
                    "escalation_level": current_level + 1,
                },
            )

            return {
                "status": "escalated",
                "next_actions": ["wait_for_approval"],
                "escalated_to": next_approver,
            }
        else:
            # Escalation chain exhausted, apply default policy
            return await self._handle_timeout(approval_id)

    async def _handle_timeout(self, approval_id: uuid.UUID) -> dict[str, Any]:
        """
        Handle approval timeout (Stage 6).

        Args:
            approval_id: The approval request identifier.

        Returns:
            Timeout handling result.
        """
        approval_request = self.pending_approvals.get(approval_id)
        if not approval_request:
            raise ValueError(f"Approval {approval_id} not found")

        project_id = approval_request["project_id"]
        policy_type = approval_request.get("policy_type", "single")

        # Publish approval.timeout event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.APPROVAL_TIMEOUT,
            event_category=EventCategory.APPROVAL,
            aggregate_id=project_id,
            aggregate_type="Project",
            metadata={
                "approval_id": str(approval_id),
                "policy_type": policy_type,
            },
        )

        # Apply default policy based on risk
        risk = approval_request.get("context", {}).get("risk_assessment", "unknown")
        if risk in ["low", "unknown"]:
            # Auto-approve for low risk
            return await self.process_decision(
                approval_id, "approved",
                feedback="Auto-approved due to timeout (low risk)"
            )
        else:
            # Auto-reject for high risk
            return await self.process_decision(
                approval_id, "rejected",
                feedback="Auto-rejected due to timeout (high risk)"
            )

    async def check_timeouts(self) -> list[dict[str, Any]]:
        """
        Check all pending approvals for timeouts.

        Returns:
            List of timeout results.
        """
        timeout_results = []
        now = datetime.now(timezone.utc)

        for approval_id, approval_request in list(self.pending_approvals.items()):
            if approval_request.get("status") != "pending":
                continue

            created_at_str = approval_request.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except (ValueError, TypeError):
                continue

            timeout_seconds = approval_request.get("timeout_seconds", self.approval_timeout_seconds)
            elapsed = (now - created_at).total_seconds()

            if elapsed >= timeout_seconds:
                result = await self._handle_timeout(approval_id)
                timeout_results.append({
                    "approval_id": str(approval_id),
                    "project_id": str(approval_request["project_id"]),
                    "result": result,
                })

        return timeout_results


class ApprovalCoordinatorModule:
    """
    Approval Coordinator Module.

    Manages human approval gates.
    """

    def __init__(
        self,
        approval_coordinator: ApprovalCoordinator | None = None,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
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

    async def check_timeouts(self) -> list[dict[str, Any]]:
        """
        Check all pending approvals for timeouts.

        Returns:
            List of timeout results.
        """
        return await self.approval_coordinator.check_timeouts()