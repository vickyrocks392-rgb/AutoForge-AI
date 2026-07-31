"""
Kernel Factory

Provides factory functions for creating and configuring the Kernel
with all its dependencies properly wired together.
"""

from __future__ import annotations

from typing import Any

from autoforge_kernel.kernel import Kernel
from autoforge_kernel.interfaces import (
    # Services
    RuntimeStateManager,
    EventBus,
    MemoryEngine,
    KnowledgeEngine,
    ModelRouter,
    ExecutionContinuityManager,
    ConnectorLayer,
    ObservabilityService,
    SecurityService,
    # Platform Engines
    StrategicEngine,
    WorkflowEngine,
    ExecutionEngine,
    ReviewEngine,
)
from autoforge_kernel.request_intake import RequestIntakeModule
from autoforge_kernel.intent_analysis import IntentAnalysisModule
from autoforge_kernel.planning_coordination import PlanningCoordinationModule
from autoforge_kernel.orchestration import OrchestrationModule
from autoforge_kernel.infrastructure import InfrastructureCoordinationModule
from autoforge_kernel.recovery import RecoveryModuleWrapper
from autoforge_kernel.approval import ApprovalCoordinatorModule
from autoforge_kernel.completion import CompletionModuleWrapper
from autoforge_kernel.lifecycle import LifecycleCoordinationModule


class KernelFactory:
    """
    Factory for creating Kernel instances.

    This factory wires together all Kernel components and their dependencies,
    providing a single point of configuration for the Kernel.
    """

    def __init__(
        self,
        # Service dependencies
        runtime_state_manager: RuntimeStateManager | None = None,
        event_bus: EventBus | None = None,
        memory_engine: MemoryEngine | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        model_router: ModelRouter | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        connector_layer: ConnectorLayer | None = None,
        observability_service: ObservabilityService | None = None,
        security_service: SecurityService | None = None,
        # Platform Engine dependencies
        strategic_engine: StrategicEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        execution_engine: ExecutionEngine | None = None,
        review_engine: ReviewEngine | None = None,
        # Kernel configuration
        kernel_id: str | None = None,
        version: str = "0.1.0",
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize the kernel factory.

        Args:
            runtime_state_manager: Runtime state manager service.
            event_bus: Event bus service.
            memory_engine: Memory engine service.
            knowledge_engine: Knowledge engine service.
            model_router: Model router service.
            execution_continuity_manager: Execution continuity manager service.
            connector_layer: Connector layer service.
            observability_service: Observability service.
            security_service: Security service.
            strategic_engine: Strategic Engine.
            workflow_engine: Workflow Engine.
            execution_engine: Execution Engine.
            review_engine: Review Engine.
            kernel_id: Optional kernel ID.
            version: Kernel version.
            config: Optional kernel configuration.
        """
        # Store service dependencies
        self.runtime_state_manager = runtime_state_manager
        self.event_bus = event_bus
        self.memory_engine = memory_engine
        self.knowledge_engine = knowledge_engine
        self.model_router = model_router
        self.execution_continuity_manager = execution_continuity_manager
        self.connector_layer = connector_layer
        self.observability_service = observability_service
        self.security_service = security_service

        # Store Platform Engine dependencies
        self.strategic_engine = strategic_engine
        self.workflow_engine = workflow_engine
        self.execution_engine = execution_engine
        self.review_engine = review_engine

        # Store Kernel configuration
        self.kernel_id = kernel_id
        self.version = version
        self.config = config or {}

    def create_kernel(self) -> Kernel:
        """
        Create a Kernel instance with all dependencies wired.

        Returns:
            Configured Kernel instance.
        """
        # Create internal modules
        request_intake_module = RequestIntakeModule(event_bus=self.event_bus)
        intent_analysis_module = IntentAnalysisModule(knowledge_engine=self.knowledge_engine)
        planning_coordination_module = PlanningCoordinationModule(
            strategic_engine=self.strategic_engine,
            workflow_engine=self.workflow_engine,
            event_bus=self.event_bus,
        )
        orchestration_module = OrchestrationModule(
            execution_engine=self.execution_engine,
            review_engine=self.review_engine,
            event_bus=self.event_bus,
            runtime_state_manager=self.runtime_state_manager,
            execution_continuity_manager=self.execution_continuity_manager,
            model_router=self.model_router,
        )
        infrastructure_module = InfrastructureCoordinationModule(
            runtime_state_manager=self.runtime_state_manager,
            event_bus=self.event_bus,
            memory_engine=self.memory_engine,
            knowledge_engine=self.knowledge_engine,
            model_router=self.model_router,
            execution_continuity_manager=self.execution_continuity_manager,
            connector_layer=self.connector_layer,
            observability_service=self.observability_service,
            security_service=self.security_service,
        )
        recovery_module = RecoveryModuleWrapper(
            event_bus=self.event_bus,
            runtime_state_manager=self.runtime_state_manager,
            execution_continuity_manager=self.execution_continuity_manager,
        )
        approval_module = ApprovalCoordinatorModule(
            event_bus=self.event_bus,
            runtime_state_manager=self.runtime_state_manager,
        )
        completion_module = CompletionModuleWrapper(
            review_engine=self.review_engine,
            event_bus=self.event_bus,
            runtime_state_manager=self.runtime_state_manager,
        )
        # Convert kernel_id from string to UUID if needed
        kernel_id_uuid = None
        if self.kernel_id:
            import uuid as uuid_module
            kernel_id_uuid = uuid_module.UUID(self.kernel_id) if isinstance(self.kernel_id, str) else self.kernel_id

        lifecycle_module = LifecycleCoordinationModule(
            event_bus=self.event_bus,
            kernel_id=kernel_id_uuid,
        )

        # Create Kernel with all dependencies
        kernel = Kernel(
            kernel_id=kernel_id_uuid,
            version=self.version,
            config=self.config,
            # Service dependencies
            runtime_state_manager=self.runtime_state_manager,
            event_bus=self.event_bus,
            memory_engine=self.memory_engine,
            knowledge_engine=self.knowledge_engine,
            model_router=self.model_router,
            execution_continuity_manager=self.execution_continuity_manager,
            connector_layer=self.connector_layer,
            observability_service=self.observability_service,
            security_service=self.security_service,
            # Platform Engine dependencies
            strategic_engine=self.strategic_engine,
            workflow_engine=self.workflow_engine,
            execution_engine=self.execution_engine,
            review_engine=self.review_engine,
            # Internal module dependencies
            request_validator=request_intake_module.validator,
            request_normalizer=request_intake_module.normalizer,
            project_initializer=request_intake_module.initializer,
            identifier_generator=request_intake_module.identifier_generator,
            intent_analyzer=intent_analysis_module.intent_analyzer,
            planning_coordinator=planning_coordination_module.planning_coordinator,
            orchestration_engine=orchestration_module.orchestration_engine,
            loop_orchestrator=orchestration_module.orchestration_engine.loop_orchestrator,
            worker_dispatch_coordinator=orchestration_module.orchestration_engine.worker_dispatch_coordinator,
            infrastructure_coordinator=infrastructure_module.infrastructure_coordinator,
            failure_detector=recovery_module.recovery_module.failure_detector,
            recovery_coordinator=recovery_module.recovery_module.recovery_coordinator,
            approval_coordinator=approval_module.approval_coordinator,
            completion_module=completion_module.completion_module,
            lifecycle_coordinator=lifecycle_module.lifecycle_coordinator,
            runtime_lifecycle_manager=lifecycle_module.lifecycle_coordinator.runtime_lifecycle_manager,
            project_lifecycle_manager=lifecycle_module.lifecycle_coordinator.project_lifecycle_manager,
            recovery_module=recovery_module.recovery_module,
        )

        return kernel


def create_kernel(
    # Service dependencies
    runtime_state_manager: RuntimeStateManager | None = None,
    event_bus: EventBus | None = None,
    memory_engine: MemoryEngine | None = None,
    knowledge_engine: KnowledgeEngine | None = None,
    model_router: ModelRouter | None = None,
    execution_continuity_manager: ExecutionContinuityManager | None = None,
    connector_layer: ConnectorLayer | None = None,
    observability_service: ObservabilityService | None = None,
    security_service: SecurityService | None = None,
    # Platform Engine dependencies
    strategic_engine: StrategicEngine | None = None,
    workflow_engine: WorkflowEngine | None = None,
    execution_engine: ExecutionEngine | None = None,
    review_engine: ReviewEngine | None = None,
    # Kernel configuration
    kernel_id: str | None = None,
    version: str = "0.1.0",
    config: dict[str, Any] | None = None,
) -> Kernel:
    """
    Create a Kernel instance with all dependencies wired.

    This is a convenience function that creates a KernelFactory and
    uses it to create a Kernel instance.

    Args:
        runtime_state_manager: Runtime state manager service.
        event_bus: Event bus service.
        memory_engine: Memory engine service.
        knowledge_engine: Knowledge engine service.
        model_router: Model router service.
        execution_continuity_manager: Execution continuity manager service.
        connector_layer: Connector layer service.
        observability_service: Observability service.
        security_service: Security service.
        strategic_engine: Strategic Engine.
        workflow_engine: Workflow Engine.
        execution_engine: Execution Engine.
        review_engine: Review Engine.
        kernel_id: Optional kernel ID.
        version: Kernel version.
        config: Optional kernel configuration.

    Returns:
        Configured Kernel instance.
    """
    factory = KernelFactory(
        runtime_state_manager=runtime_state_manager,
        event_bus=event_bus,
        memory_engine=memory_engine,
        knowledge_engine=knowledge_engine,
        model_router=model_router,
        execution_continuity_manager=execution_continuity_manager,
        connector_layer=connector_layer,
        observability_service=observability_service,
        security_service=security_service,
        strategic_engine=strategic_engine,
        workflow_engine=workflow_engine,
        execution_engine=execution_engine,
        review_engine=review_engine,
        kernel_id=kernel_id,
        version=version,
        config=config,
    )

    return factory.create_kernel()