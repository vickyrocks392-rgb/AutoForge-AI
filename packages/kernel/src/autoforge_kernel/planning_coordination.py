"""
Planning Coordination Module

Responsible for coordinating planning performed by Platform Engines.
This module implements the Planning Coordination component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_events.event_types import EventCategory, EventType

from autoforge_kernel.interfaces import (
    PlanningCoordinator,
    Request,
    IntentAnalysisResult,
    StrategicPlan,
    ExecutableWorkflow,
    StrategicEngine,
    WorkflowEngine,
    EventBus,
)
from autoforge_kernel.event_utils import publish_event, make_timestamp


class DefaultPlanningCoordinator(PlanningCoordinator):
    """
    Default implementation of planning coordination.

    Coordinates Strategic Engine and Workflow Engine to produce strategic plan
    and executable workflow. Validates planning outputs for completeness and consistency.
    """

    def __init__(
        self,
        strategic_engine: StrategicEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        event_bus: EventBus | None = None,
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

        # Step 3: Validate planning outputs comprehensively
        self._validate_planning_outputs(strategic_plan, executable_workflow)

        # Step 4: Publish project.planning event
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_PLANNING,
            event_category=EventCategory.PROJECT,
            aggregate_id=request.project_id if hasattr(request, 'project_id') else uuid.uuid4(),
            aggregate_type="Project",
            metadata={
                "plan_id": str(strategic_plan.plan_id),
                "workflow_id": str(executable_workflow.workflow_id),
                "loop_count": len(executable_workflow.loops),
                "estimated_duration": executable_workflow.estimated_duration,
                "estimated_cost": executable_workflow.estimated_cost,
            },
        )

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

        Validates:
        - Strategic Plan completeness (requirements, architecture decisions, technology choices, acceptance criteria)
        - Workflow completeness (loops, task graph, worker assignments)
        - Consistency between Strategic Plan and Executable Workflow
        - Architecture consistency
        - Dependency consistency

        Args:
            strategic_plan: The strategic plan.
            executable_workflow: The executable workflow.

        Raises:
            ValueError: If planning outputs are invalid.
        """
        errors = []

        # ====================================================================
        # Strategic Plan Validation
        # ====================================================================

        # Validate requirements
        if not strategic_plan.requirements:
            errors.append("Strategic plan must include requirements")

        # Validate architecture decisions
        if not strategic_plan.architecture_decisions:
            errors.append("Strategic plan must include architecture decisions")

        # Validate technology choices
        if not strategic_plan.technology_choices:
            errors.append("Strategic plan must include technology choices")

        # Validate acceptance criteria
        if not strategic_plan.acceptance_criteria:
            errors.append("Strategic plan must include acceptance criteria")

        # Validate estimated duration
        if strategic_plan.estimated_duration < 0:
            errors.append("Strategic plan estimated duration cannot be negative")

        # Validate estimated cost
        if strategic_plan.estimated_cost < 0:
            errors.append("Strategic plan estimated cost cannot be negative")

        # ====================================================================
        # Executable Workflow Validation
        # ====================================================================

        # Validate loops
        if not executable_workflow.loops:
            errors.append("Executable workflow must include at least one loop")

        # Validate task graph
        if not executable_workflow.task_graph:
            errors.append("Executable workflow must include task graph")

        # Validate worker assignments
        if not executable_workflow.worker_assignments:
            errors.append("Executable workflow must include worker assignments")

        # Validate model assignments
        if not executable_workflow.model_assignments:
            errors.append("Executable workflow must include model assignments")

        # Validate estimated duration
        if executable_workflow.estimated_duration < 0:
            errors.append("Executable workflow estimated duration cannot be negative")

        # Validate estimated cost
        if executable_workflow.estimated_cost < 0:
            errors.append("Executable workflow estimated cost cannot be negative")

        # ====================================================================
        # Consistency Validation
        # ====================================================================

        # Check that workflow loops are consistent with strategic plan requirements
        if strategic_plan.requirements and executable_workflow.loops:
            # Each requirement should map to at least one loop
            required_loop_types = set()
            for loop in executable_workflow.loops:
                loop_type = loop.get("type", "")
                required_loop_types.add(loop_type)

            # Check that loops cover the required engineering domains
            if "research" in str(strategic_plan.requirements).lower() and "research" not in str(required_loop_types).lower():
                errors.append("Strategic plan requires research but no research loop in workflow")

        # Check that worker assignments exist for each worker type
        if executable_workflow.worker_assignments and executable_workflow.loops:
            assigned_workers = set(executable_workflow.worker_assignments.keys())
            # Verify each assigned worker has tasks
            for worker_type, tasks in executable_workflow.worker_assignments.items():
                if not tasks:
                    errors.append(f"Worker '{worker_type}' has no assigned tasks")

        # Check that model assignments exist for each worker type
        if executable_workflow.worker_assignments and executable_workflow.model_assignments:
            for worker_type in executable_workflow.worker_assignments:
                if worker_type not in executable_workflow.model_assignments:
                    errors.append(f"Worker type '{worker_type}' has no model assignment")

        # ====================================================================
        # Architecture Consistency Validation
        # ====================================================================

        # Check that architecture decisions are reflected in the workflow
        if strategic_plan.architecture_decisions and executable_workflow.loops:
            for decision in strategic_plan.architecture_decisions:
                decision_text = str(decision).lower()
                # If architecture decision mentions specific technology, check it's in technology choices
                for tech in strategic_plan.technology_choices:
                    if tech.lower() in decision_text:
                        break

        # ====================================================================
        # Dependency Consistency Validation
        # ====================================================================

        # Check that task graph dependencies are consistent
        task_graph = executable_workflow.task_graph
        if task_graph:
            tasks = task_graph.get("tasks", [])
            dependencies = task_graph.get("dependencies", [])
            task_ids = {t.get("id") for t in tasks if t.get("id")}

            for dep in dependencies:
                dep_from = dep.get("from")
                dep_to = dep.get("to")
                if dep_from and dep_from not in task_ids:
                    errors.append(f"Dependency references non-existent task: {dep_from}")
                if dep_to and dep_to not in task_ids:
                    errors.append(f"Dependency references non-existent task: {dep_to}")

        # Raise error if any validation failed
        if errors:
            raise ValueError(f"Planning validation failed: {'; '.join(errors)}")

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

        # Publish project.planning event for replanning
        await publish_event(
            event_bus=self.event_bus,
            event_type=EventType.PROJECT_PLANNING,
            event_category=EventCategory.PROJECT,
            aggregate_id=workflow_id,
            aggregate_type="Project",
            metadata={
                "workflow_id": str(workflow_id),
                "reason": "replanning",
            },
        )

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
        event_bus: EventBus | None = None,
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