"""
Completion Module

Responsible for validating completion and finalizing projects.
This module implements the Completion component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    CompletionModule,
    EventBus,
    RuntimeStateManager,
    ReviewEngine,
)


class DefaultCompletionModule(CompletionModule):
    """
    Default implementation of completion validation and finalization.

    Validates completion and finalizes projects.
    """

    def __init__(
        self,
        review_engine: ReviewEngine | None = None,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
    ):
        """
        Initialize the completion module.

        Args:
            review_engine: Review Engine for final review.
            event_bus: Event bus for publishing events.
            runtime_state_manager: Runtime state manager.
        """
        self.review_engine = review_engine
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager

    async def validate_completion(self, project_id: uuid.UUID) -> dict[str, Any]:
        """
        Validate that a project is complete.

        Args:
            project_id: The project to validate.

        Returns:
            Validation result.
        """
        validation_result = {
            "valid": True,
            "acceptance_criteria_met": True,
            "quality_gates_passed": True,
            "artifacts_complete": True,
            "dependencies_satisfied": True,
            "metrics_within_thresholds": True,
            "errors": [],
            "warnings": [],
        }

        # Validate acceptance criteria
        # In a real implementation, this would check against stored acceptance criteria
        acceptance_criteria_met = True
        if not acceptance_criteria_met:
            validation_result["acceptance_criteria_met"] = False
            validation_result["valid"] = False
            validation_result["errors"].append("Acceptance criteria not met")

        # Validate quality gates
        # In a real implementation, this would check all quality gates
        quality_gates_passed = True
        if not quality_gates_passed:
            validation_result["quality_gates_passed"] = False
            validation_result["valid"] = False
            validation_result["errors"].append("Quality gates not passed")

        # Validate artifact completeness
        # In a real implementation, this would check all required artifacts
        artifacts_complete = True
        if not artifacts_complete:
            validation_result["artifacts_complete"] = False
            validation_result["valid"] = False
            validation_result["errors"].append("Artifacts incomplete")

        # Validate dependency satisfaction
        # In a real implementation, this would check all task dependencies
        dependencies_satisfied = True
        if not dependencies_satisfied:
            validation_result["dependencies_satisfied"] = False
            validation_result["valid"] = False
            validation_result["errors"].append("Dependencies not satisfied")

        # Validate metrics thresholds
        # In a real implementation, this would check cost, duration, quality metrics
        metrics_within_thresholds = True
        if not metrics_within_thresholds:
            validation_result["metrics_within_thresholds"] = False
            validation_result["warnings"].append("Metrics outside thresholds")

        return validation_result

    async def finalize_project(self, project_id: uuid.UUID) -> dict[str, Any]:
        """
        Finalize a completed project.

        Args:
            project_id: The project to finalize.

        Returns:
            Finalization result.
        """
        # Validate completion first
        validation_result = await self.validate_completion(project_id)

        if not validation_result["valid"]:
            return {
                "success": False,
                "error": "Project validation failed",
                "validation_result": validation_result,
            }

        # Update project state to Completing
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Completing",
            )

        # Perform final review if review engine is available
        if self.review_engine:
            try:
                # In a real implementation, this would perform a final review
                pass
            except Exception:
                # Review failed, but continue with finalization
                pass

        # Update project state to Finished
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Finished",
                metadata={"finished_at": str(uuid.uuid4())},  # TODO: Use proper timestamp
            )

        # Publish project.finished event
        if self.event_bus:
            await self._publish_event(
                event_type="completed",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={
                    "validation_result": validation_result,
                },
            )

        return {
            "success": True,
            "project_id": str(project_id),
            "validation_result": validation_result,
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


class CompletionModuleWrapper:
    """
    Completion Module Wrapper.

    Validates completion and finalizes projects.
    """

    def __init__(
        self,
        completion_module: CompletionModule | None = None,
        review_engine: ReviewEngine | None = None,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
    ):
        """
        Initialize the completion module wrapper.

        Args:
            completion_module: Completion module.
            review_engine: Review Engine.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
        """
        self.completion_module = completion_module or DefaultCompletionModule(
            review_engine=review_engine,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
        )

    async def validate_completion(self, project_id: uuid.UUID) -> dict[str, Any]:
        """
        Validate completion.

        Args:
            project_id: The project.

        Returns:
            Validation result.
        """
        return await self.completion_module.validate_completion(project_id)

    async def finalize_project(self, project_id: uuid.UUID) -> dict[str, Any]:
        """
        Finalize project.

        Args:
            project_id: The project.

        Returns:
            Finalization result.
        """
        return await self.completion_module.finalize_project(project_id)