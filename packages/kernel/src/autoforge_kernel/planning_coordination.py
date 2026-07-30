"""
Planning Coordination Module

Responsible for coordinating planning performed by Platform Engines.
This module implements the Planning Coordination component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    PlanningCoordinator,
    Request,
    IntentAnalysisResult,
    StrategicPlan,
    ExecutableWorkflow,
    StrategicEngine,
    WorkflowEngine,
)


class DefaultPlanningCoordinator(PlanningCoordinator):
    """
    Default implementation of planning coordination.

    Coordinates Strategic Engine and Workflow Engine to produce strategic plan
    and executable workflow.
    """

    def __init__(
        self,
        strategic_engine: StrategicEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        event_bus: Any | None = None,
    ):
        """
        Initialize the planning coordinator.

        Args:
            strategic_engine: Strategic Engine for strategic planning.
            workflow_engine: Workflow Engine for execution planning.
            event_bus: Event bus for publishing events.
        """
        self.strategic_engine = strategic_engine
        self.workflow_engine = workflow_engine
        self.event_bus = event_bus

    async def coordinate_planning(
        self,
        request: Request,
        intent_analysis: IntentAnalysisResult,
    ) -> tuple[StrategicPlan, ExecutableWorkflow]:
        """
        Coordinate planning to produce strategic plan and executable workflow.

        Args:
            request: The original request.
            intent_analysis: Intent analysis result.

        Returns:
            Tuple of (strategic_plan, executable_workflow).
        """
        # Step 1: Invoke Strategic Engine to produce strategic plan
        strategic_plan = await self._coordinate_strategic_planning(request, intent_analysis)

        # Step 2: Invoke Workflow Engine to produce executable workflow
        executable_workflow = await self._coordinate_execution_planning(strategic_plan, intent_analysis)

        # Step 3: Validate planning outputs
        self._validate_planning_outputs(strategic_plan, executable_workflow)

        # Step 4: Publish plan.created event
        if self.event_bus:
            await self._publish_plan_created_event(strategic_plan, executable_workflow)

        return strategic_plan, executable_workflow

    async def _coordinate_strategic_planning(
        self,
        request: Request,
        intent_analysis: IntentAnalysisResult,
    ) -> StrategicPlan:
        """
        Coordinate strategic planning with Strategic Engine.

        Args:
            request: The original request.
            intent_analysis: Intent analysis result.

        Returns:
            Strategic plan.
        """
        if not self.strategic_engine:
            raise RuntimeError("Strategic Engine not configured")

        # Prepare context for Strategic Engine
        context = {
            "request": request.to_dict(),
            "intent_analysis": intent_analysis.to_dict(),
        }

        # Invoke Strategic Engine
        strategic_plan = await self.strategic_engine.create_strategic_plan(
            request=request,
            intent_analysis=intent_analysis,
            context=context,
        )

        return strategic_plan

    async def _coordinate_execution_planning(
        self,
        strategic_plan: StrategicPlan,
        intent_analysis: IntentAnalysisResult,
    ) -> ExecutableWorkflow:
        """
        Coordinate execution planning with Workflow Engine.

        Args:
            strategic_plan: The strategic plan.
            intent_analysis: Intent analysis result.

        Returns:
            Executable workflow.
        """
        if not self.workflow_engine:
            raise RuntimeError("Workflow Engine not configured")

        # Prepare context for Workflow Engine
        context = {
            "strategic_plan": strategic_plan.to_dict(),
            "intent_analysis": intent_analysis.to_dict(),
        }

        # Invoke Workflow Engine
        executable_workflow = await self.workflow_engine.create_executable_workflow(
            strategic_plan=strategic_plan,
            context=context,
        )

        return executable_workflow

    def _validate_planning_outputs(
        self,
        strategic_plan: StrategicPlan,
        executable_workflow: ExecutableWorkflow,
    ) -> None:
        """
        Validate planning outputs for completeness and consistency.

        Args:
            strategic_plan: The strategic plan.
            executable_workflow: The executable workflow.

        Raises:
            ValueError: If planning outputs are invalid.
        """
        # Validate strategic plan
        if not strategic_plan.requirements:
            raise ValueError("Strategic plan must include requirements")

        if not strategic_plan.acceptance_criteria:
            raise ValueError("Strategic plan must include acceptance criteria")

        # Validate executable workflow
        if not executable_workflow.loops:
            raise ValueError("Executable workflow must include loops")

        if not executable_workflow.task_graph:
            raise ValueError("Executable workflow must include task graph")

        # Validate consistency
        if executable_workflow.estimated_duration < 0:
            raise ValueError("Executable workflow estimated duration cannot be negative")

        if executable_workflow.estimated_cost < 0:
            raise ValueError("Executable workflow estimated cost cannot be negative")

    async def _publish_plan_created_event(
        self,
        strategic_plan: StrategicPlan,
        executable_workflow: ExecutableWorkflow,
    ) -> None:
        """
        Publish plan.created event.

        Args:
            strategic_plan: The strategic plan.
            executable_workflow: The executable workflow.
        """
        if not self.event_bus:
            return

        from autoforge_events.base import BaseEvent as DomainBaseEvent
        from autoforge_events.event_types import EventCategory, EventType

        event = DomainBaseEvent(
            event_type=EventType.CREATED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=strategic_plan.plan_id,
            aggregate_type="StrategicPlan",
            metadata={
                "plan_id": str(strategic_plan.plan_id),
                "workflow_id": str(executable_workflow.workflow_id),
                "loop_count": len(executable_workflow.loops),
                "estimated_duration": executable_workflow.estimated_duration,
                "estimated_cost": executable_workflow.estimated_cost,
            },
        )

        await self.event_bus.publish(event)

    async def request_replanning(
        self,
        workflow_id: uuid.UUID,
        execution_context: dict[str, Any],
    ) -> ExecutableWorkflow:
        """
        Request replanning from Workflow Engine.

        Args:
            workflow_id: The workflow to replan.
            execution_context: Current execution context.

        Returns:
            Updated executable workflow.
        """
        if not self.workflow_engine:
            raise RuntimeError("Workflow Engine not configured")

        # Invoke Workflow Engine for replanning
        updated_workflow = await self.workflow_engine.replan(
            workflow_id=workflow_id,
            execution_context=execution_context,
        )

        # Publish replanning event
        if self.event_bus:
            from autoforge_events.base import BaseEvent as DomainBaseEvent
            from autoforge_events.event_types import EventCategory, EventType

            event = DomainBaseEvent(
                event_type=EventType.UPDATED,
                event_category=EventCategory.SYSTEM_EVENT,
                aggregate_id=workflow_id,
                aggregate_type="ExecutableWorkflow",
                metadata={
                    "workflow_id": str(workflow_id),
                    "reason": "replanning",
                },
            )

            await self.event_bus.publish(event)

        return updated_workflow


class PlanningCoordinationModule:
    """
    Planning Coordination Module.

    Coordinates planning performed by Platform Engines.
    """

    def __init__(
        self,
        planning_coordinator: PlanningCoordinator | None = None,
        strategic_engine: StrategicEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        event_bus: Any | None = None,
    ):
        """
        Initialize the planning coordination module.

        Args:
            planning_coordinator: Planning coordinator.
            strategic_engine: Strategic Engine.
            workflow_engine: Workflow Engine.
            event_bus: Event bus for publishing events.
        """
        self.planning_coordinator = planning_coordinator or DefaultPlanningCoordinator(
            strategic_engine=strategic_engine,
            workflow_engine=workflow_engine,
            event_bus=event_bus,
        )

    async def coordinate_planning(
        self,
        request: Request,
        intent_analysis: IntentAnalysisResult,
    ) -> tuple[StrategicPlan, ExecutableWorkflow]:
        """
        Coordinate planning to produce strategic plan and executable workflow.

        Args:
            request: The original request.
            intent_analysis: Intent analysis result.

        Returns:
            Tuple of (strategic_plan, executable_workflow).
        """
        return await self.planning_coordinator.coordinate_planning(request, intent_analysis)

    async def request_replanning(
        self,
        workflow_id: uuid.UUID,
        execution_context: dict[str, Any],
    ) -> ExecutableWorkflow:
        """
        Request replanning from Workflow Engine.

        Args:
            workflow_id: The workflow to replan.
            execution_context: Current execution context.

        Returns:
            Updated executable workflow.
        """
        return await self.planning_coordinator.request_replanning(workflow_id, execution_context)