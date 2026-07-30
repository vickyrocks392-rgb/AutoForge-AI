"""
Infrastructure Coordination Module

Responsible for coordinating Shared Platform Services throughout execution.
This module implements the Infrastructure Coordination component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    InfrastructureCoordinator,
    RuntimeStateManager,
    EventBus,
    MemoryEngine,
    KnowledgeEngine,
    ModelRouter,
    ExecutionContinuityManager,
    ConnectorLayer,
    ObservabilityService,
    SecurityService,
)


class DefaultInfrastructureCoordinator(InfrastructureCoordinator):
    """
    Default implementation of infrastructure coordination.

    Coordinates Shared Platform Services throughout execution.
    """

    def __init__(
        self,
        runtime_state_manager: RuntimeStateManager | None = None,
        event_bus: EventBus | None = None,
        memory_engine: MemoryEngine | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        model_router: ModelRouter | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        connector_layer: ConnectorLayer | None = None,
        observability_service: ObservabilityService | None = None,
        security_service: SecurityService | None = None,
    ):
        """
        Initialize the infrastructure coordinator.

        Args:
            runtime_state_manager: Runtime state manager.
            event_bus: Event bus.
            memory_engine: Memory engine.
            knowledge_engine: Knowledge engine.
            model_router: Model router.
            execution_continuity_manager: Execution continuity manager.
            connector_layer: Connector layer.
            observability_service: Observability service.
            security_service: Security service.
        """
        self.runtime_state_manager = runtime_state_manager
        self.event_bus = event_bus
        self.memory_engine = memory_engine
        self.knowledge_engine = knowledge_engine
        self.model_router = model_router
        self.execution_continuity_manager = execution_continuity_manager
        self.connector_layer = connector_layer
        self.observability_service = observability_service
        self.security_service = security_service

    async def coordinate_services(self, lifecycle_point: str, context: dict[str, Any]) -> None:
        """
        Coordinate infrastructure services at a lifecycle point.

        Args:
            lifecycle_point: The lifecycle point (e.g., "project_start", "loop_start").
            context: The execution context.
        """
        # Coordinate services based on lifecycle point
        if lifecycle_point == "project_start":
            await self._coordinate_project_start(context)
        elif lifecycle_point == "project_end":
            await self._coordinate_project_end(context)
        elif lifecycle_point == "loop_start":
            await self._coordinate_loop_start(context)
        elif lifecycle_point == "loop_end":
            await self._coordinate_loop_end(context)
        elif lifecycle_point == "task_start":
            await self._coordinate_task_start(context)
        elif lifecycle_point == "task_end":
            await self._coordinate_task_end(context)
        elif lifecycle_point == "failure":
            await self._coordinate_failure(context)
        elif lifecycle_point == "recovery":
            await self._coordinate_recovery(context)

    async def _coordinate_project_start(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at project start.

        Args:
            context: The execution context.
        """
        project_id = context.get("project_id")
        if not project_id:
            return

        # Load project context from memory
        if self.memory_engine:
            try:
                memory_context = await self.memory_engine.load_context(uuid.UUID(project_id))
                context["memory_context"] = memory_context
            except Exception:
                # Memory engine not available, continue
                pass

        # Retrieve domain knowledge
        if self.knowledge_engine:
            try:
                knowledge = await self.knowledge_engine.research(
                    topic=context.get("request_text", ""),
                    context=context,
                )
                context["knowledge"] = knowledge
            except Exception:
                # Knowledge engine not available, continue
                pass

        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="project.started",
                    value=1.0,
                    tags={"project_id": project_id},
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_project_end(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at project end.

        Args:
            context: The execution context.
        """
        project_id = context.get("project_id")
        if not project_id:
            return

        # Store project memory
        if self.memory_engine:
            try:
                await self.memory_engine.store_memory(
                    project_id=uuid.UUID(project_id),
                    memory=context.get("project_memory", {}),
                )
            except Exception:
                # Memory engine not available, continue
                pass

        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="project.completed",
                    value=1.0,
                    tags={"project_id": project_id},
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_loop_start(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at loop start.

        Args:
            context: The execution context.
        """
        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="loop.started",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "loop_type": context.get("loop_type", ""),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_loop_end(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at loop end.

        Args:
            context: The execution context.
        """
        # Persist loop state
        if self.memory_engine:
            try:
                await self.memory_engine.persist_state(
                    project_id=uuid.UUID(context.get("project_id", "")),
                    state=context.get("loop_state", {}),
                )
            except Exception:
                # Memory engine not available, continue
                pass

        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="loop.completed",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "loop_type": context.get("loop_type", ""),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_task_start(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at task start.

        Args:
            context: The execution context.
        """
        # Select model if needed
        if self.model_router and "task" in context:
            try:
                model = await self.model_router.select_model(task=context["task"])
                context["selected_model"] = model.to_dict()
            except Exception:
                # Model router not available, continue
                pass

        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="task.started",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "task_id": context.get("task_id", ""),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_task_end(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at task end.

        Args:
            context: The execution context.
        """
        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="task.completed",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "task_id": context.get("task_id", ""),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass

    async def _coordinate_failure(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at failure.

        Args:
            context: The execution context.
        """
        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="failure.detected",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "failure_type": context.get("failure_type", "unknown"),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass

        # Log security event
        if self.security_service:
            try:
                await self.security_service.audit(
                    event="failure.detected",
                    context=context,
                )
            except Exception:
                # Security service not available, continue
                pass

    async def _coordinate_recovery(self, context: dict[str, Any]) -> None:
        """
        Coordinate services at recovery.

        Args:
            context: The execution context.
        """
        # Emit observability metric
        if self.observability_service:
            try:
                await self.observability_service.emit_metric(
                    metric_name="recovery.completed",
                    value=1.0,
                    tags={
                        "project_id": context.get("project_id", ""),
                        "recovery_strategy": context.get("recovery_strategy", "unknown"),
                    },
                )
            except Exception:
                # Observability service not available, continue
                pass


class InfrastructureCoordinationModule:
    """
    Infrastructure Coordination Module.

    Coordinates Shared Platform Services throughout execution.
    """

    def __init__(
        self,
        infrastructure_coordinator: InfrastructureCoordinator | None = None,
        runtime_state_manager: RuntimeStateManager | None = None,
        event_bus: EventBus | None = None,
        memory_engine: MemoryEngine | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        model_router: ModelRouter | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        connector_layer: ConnectorLayer | None = None,
        observability_service: ObservabilityService | None = None,
        security_service: SecurityService | None = None,
    ):
        """
        Initialize the infrastructure coordination module.

        Args:
            infrastructure_coordinator: Infrastructure coordinator.
            runtime_state_manager: Runtime state manager.
            event_bus: Event bus.
            memory_engine: Memory engine.
            knowledge_engine: Knowledge engine.
            model_router: Model router.
            execution_continuity_manager: Execution continuity manager.
            connector_layer: Connector layer.
            observability_service: Observability service.
            security_service: Security service.
        """
        self.infrastructure_coordinator = infrastructure_coordinator or DefaultInfrastructureCoordinator(
            runtime_state_manager=runtime_state_manager,
            event_bus=event_bus,
            memory_engine=memory_engine,
            knowledge_engine=knowledge_engine,
            model_router=model_router,
            execution_continuity_manager=execution_continuity_manager,
            connector_layer=connector_layer,
            observability_service=observability_service,
            security_service=security_service,
        )

    async def coordinate_services(self, lifecycle_point: str, context: dict[str, Any]) -> None:
        """
        Coordinate infrastructure services at a lifecycle point.

        Args:
            lifecycle_point: The lifecycle point.
            context: The execution context.
        """
        await self.infrastructure_coordinator.coordinate_services(lifecycle_point, context)