"""
Engine Orchestration Module

Responsible for coordinating execution of the Executable Workflow through
the Execution Engine. This module implements the Engine Orchestration
component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    OrchestrationEngine,
    LoopOrchestrator,
    WorkerDispatchCoordinator,
    Request,
    IntentAnalysisResult,
    StrategicPlan,
    ExecutableWorkflow,
    ExecutionEngine,
    ReviewEngine,
    EventBus,
    RuntimeStateManager,
    ExecutionContinuityManager,
    ModelRouter,
)


class DefaultOrchestrationEngine(OrchestrationEngine):
    """
    Default implementation of the orchestration engine.

    Coordinates execution of the Executable Workflow through the Execution Engine.
    """

    def __init__(
        self,
        execution_engine: ExecutionEngine | None = None,
        review_engine: ReviewEngine | None = None,
        loop_orchestrator: LoopOrchestrator | None = None,
        worker_dispatch_coordinator: WorkerDispatchCoordinator | None = None,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        model_router: ModelRouter | None = None,
    ):
        """
        Initialize the orchestration engine.

        Args:
            execution_engine: Execution Engine for executing loops.
            review_engine: Review Engine for reviewing artifacts.
            loop_orchestrator: Loop orchestrator.
            worker_dispatch_coordinator: Worker dispatch coordinator.
            event_bus: Event bus for publishing events.
            runtime_state_manager: Runtime state manager for state operations.
            execution_continuity_manager: Execution continuity manager for recovery.
            model_router: Model router for model selection.
        """
        self.execution_engine = execution_engine
        self.review_engine = review_engine
        self.loop_orchestrator = loop_orchestrator or DefaultLoopOrchestrator(
            execution_engine=execution_engine,
            review_engine=review_engine,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
        )
        self.worker_dispatch_coordinator = worker_dispatch_coordinator or DefaultWorkerDispatchCoordinator(
            execution_engine=execution_engine,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
            model_router=model_router,
        )
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager
        self.execution_continuity_manager = execution_continuity_manager
        self.model_router = model_router

    async def orchestrate(
        self,
        project_id: uuid.UUID,
        executable_workflow: ExecutableWorkflow,
    ) -> None:
        """
        Orchestrate execution of an executable workflow.

        Args:
            project_id: The project to orchestrate.
            executable_workflow: The executable workflow to execute.
        """
        # Update project state to Running
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Running",
                metadata={"workflow_id": str(executable_workflow.workflow_id)},
            )

        # Publish project.running event
        if self.event_bus:
            await self._publish_event(
                event_type="started",
                event_category="project",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={"workflow_id": str(executable_workflow.workflow_id)},
            )

        # Execute each loop in the workflow
        for loop in executable_workflow.loops:
            loop_type = loop.get("type", "unknown")
            loop_context = {
                "project_id": str(project_id),
                "workflow_id": str(executable_workflow.workflow_id),
                "loop": loop,
            }

            # Orchestrate the loop
            loop_result = await self.loop_orchestrator.orchestrate_loop(
                project_id=project_id,
                loop_type=loop_type,
                loop_context=loop_context,
            )

            # Handle loop completion
            await self.handle_loop_completion(project_id, loop_result)

    async def handle_loop_completion(
        self,
        project_id: uuid.UUID,
        loop_result: dict[str, Any],
    ) -> None:
        """
        Handle completion of an engineering loop.

        Args:
            project_id: The project.
            loop_result: The loop result.
        """
        status = loop_result.get("status", "unknown")

        if status == "complete":
            # Loop completed successfully
            if self.event_bus:
                await self._publish_event(
                    event_type="completed",
                    event_category="loop",
                    aggregate_id=project_id,
                    aggregate_type="Project",
                    metadata={"loop_type": loop_result.get("loop_type")},
                )

        elif status == "remediate":
            # Loop requires remediation
            await self._handle_remediation(project_id, loop_result)

        elif status == "escalate":
            # Loop requires human intervention
            await self._handle_escalation(project_id, loop_result)

        elif status == "failed":
            # Loop failed
            await self.handle_failure(project_id, loop_result)

    async def handle_failure(
        self,
        project_id: uuid.UUID,
        failure: dict[str, Any],
    ) -> None:
        """
        Handle a failure during execution.

        Args:
            project_id: The project.
            failure: The failure details.
        """
        # Publish failure event
        if self.event_bus:
            await self._publish_event(
                event_type="failed",
                event_category="loop",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={"error": failure.get("error", "Unknown error")},
            )

        # Attempt recovery if execution continuity manager is available
        if self.execution_continuity_manager:
            try:
                recovery_result = await self.execution_continuity_manager.recover(
                    failure_context=failure
                )
                if recovery_result.get("success"):
                    # Resume execution
                    pass
            except Exception:
                # Recovery failed, escalate to human
                pass

    async def _handle_remediation(self, project_id: uuid.UUID, loop_result: dict[str, Any]) -> None:
        """
        Handle loop remediation.

        Args:
            project_id: The project.
            loop_result: The loop result.
        """
        # Get remediation tasks
        remediation_tasks = loop_result.get("remediation_tasks", [])

        # Dispatch workers for remediation tasks
        for task in remediation_tasks:
            await self.worker_dispatch_coordinator.dispatch_worker(
                project_id=project_id,
                task=task,
            )

    async def _handle_escalation(self, project_id: uuid.UUID, loop_result: dict[str, Any]) -> None:
        """
        Handle loop escalation to human.

        Args:
            project_id: The project.
            loop_result: The loop result.
        """
        # Update project state to Reviewing
        if self.runtime_state_manager:
            await self.runtime_state_manager.transition_state(
                project_id=project_id,
                new_status="Reviewing",
            )

        # Publish escalation event
        if self.event_bus:
            await self._publish_event(
                event_type="escalated",
                event_category="loop",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={"reason": loop_result.get("reason", "Unknown")},
            )

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


class DefaultLoopOrchestrator(LoopOrchestrator):
    """
    Default implementation of loop orchestration.
    """

    def __init__(
        self,
        execution_engine: ExecutionEngine | None = None,
        review_engine: ReviewEngine | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
    ):
        """
        Initialize the loop orchestrator.

        Args:
            execution_engine: Execution Engine.
            review_engine: Review Engine.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
        """
        self.execution_engine = execution_engine
        self.review_engine = review_engine
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager

    async def orchestrate_loop(
        self,
        project_id: uuid.UUID,
        loop_type: str,
        loop_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Orchestrate a single engineering loop.

        Args:
            project_id: The project.
            loop_type: The type of loop.
            loop_context: The loop context.

        Returns:
            Loop result.
        """
        if not self.execution_engine:
            raise RuntimeError("Execution Engine not configured")

        # Update loop state
        if self.runtime_state_manager:
            await self.runtime_state_manager.update_project(
                project=None,  # TODO: Update with actual project state
            )

        # Execute the loop
        loop_result = await self.execution_engine.execute_loop(
            loop_type=loop_type,
            loop_input=loop_context,
            context=loop_context,
        )

        # Add loop type to result
        loop_result["loop_type"] = loop_type

        return loop_result


class DefaultWorkerDispatchCoordinator(WorkerDispatchCoordinator):
    """
    Default implementation of worker dispatch coordination.
    """

    def __init__(
        self,
        execution_engine: ExecutionEngine | None = None,
        event_bus: Any | None = None,
        runtime_state_manager: Any | None = None,
        model_router: Any | None = None,
    ):
        """
        Initialize the worker dispatch coordinator.

        Args:
            execution_engine: Execution Engine.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
            model_router: Model router.
        """
        self.execution_engine = execution_engine
        self.event_bus = event_bus
        self.runtime_state_manager = runtime_state_manager
        self.model_router = model_router

    async def dispatch_worker(
        self,
        project_id: uuid.UUID,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Dispatch a worker for a task.

        Args:
            project_id: The project.
            task: The task to dispatch.

        Returns:
            Task result.
        """
        if not self.execution_engine:
            raise RuntimeError("Execution Engine not configured")

        # Select model if model router is available
        if self.model_router:
            try:
                model = await self.model_router.select_model(task=task)
                task["model"] = model.to_dict()
            except Exception:
                # Model selection failed, continue without model
                pass

        # Dispatch worker
        result = await self.execution_engine.dispatch_worker(
            worker_type=task.get("worker_type", "default"),
            task=task,
            context={"project_id": str(project_id)},
        )

        # Publish worker dispatched event
        if self.event_bus:
            await self._publish_event(
                event_type="started",
                event_category="task",
                aggregate_id=project_id,
                aggregate_type="Project",
                metadata={"task_id": task.get("task_id")},
            )

        return result

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


class OrchestrationModule:
    """
    Orchestration Module.

    Coordinates execution of the Executable Workflow.
    """

    def __init__(
        self,
        orchestration_engine: OrchestrationEngine | None = None,
        execution_engine: ExecutionEngine | None = None,
        review_engine: ReviewEngine | None = None,
        event_bus: EventBus | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        model_router: ModelRouter | None = None,
    ):
        """
        Initialize the orchestration module.

        Args:
            orchestration_engine: Orchestration engine.
            execution_engine: Execution Engine.
            review_engine: Review Engine.
            event_bus: Event bus.
            runtime_state_manager: Runtime state manager.
            execution_continuity_manager: Execution continuity manager.
            model_router: Model router.
        """
        self.orchestration_engine = orchestration_engine or DefaultOrchestrationEngine(
            execution_engine=execution_engine,
            review_engine=review_engine,
            event_bus=event_bus,
            runtime_state_manager=runtime_state_manager,
            execution_continuity_manager=execution_continuity_manager,
            model_router=model_router,
        )

    async def orchestrate(
        self,
        project_id: uuid.UUID,
        executable_workflow: ExecutableWorkflow,
    ) -> None:
        """
        Orchestrate execution of an executable workflow.

        Args:
            project_id: The project.
            executable_workflow: The executable workflow.
        """
        await self.orchestration_engine.orchestrate(project_id, executable_workflow)

    async def handle_loop_completion(
        self,
        project_id: uuid.UUID,
        loop_result: dict[str, Any],
    ) -> None:
        """
        Handle loop completion.

        Args:
            project_id: The project.
            loop_result: The loop result.
        """
        await self.orchestration_engine.handle_loop_completion(project_id, loop_result)

    async def handle_failure(
        self,
        project_id: uuid.UUID,
        failure: dict[str, Any],
    ) -> None:
        """
        Handle failure.

        Args:
            project_id: The project.
            failure: The failure details.
        """
        await self.orchestration_engine.handle_failure(project_id, failure)