"""
Kernel Core - Executive Orchestrator

The Kernel is the single entry point for all platform requests and the central
coordination layer that transforms user intent into completed software engineering
projects.

This module implements the main Kernel class that coordinates all internal modules
and external Platform Engines.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Coroutine
from enum import Enum

from autoforge_models.project import Project
from autoforge_models.task import Task
from autoforge_models.artifact import Artifact
from autoforge_models.checkpoint import Checkpoint
from autoforge_models.review import Review
from autoforge_models.employee import Employee
from autoforge_models.model_profile import ModelProfile
from autoforge_models.execution_session import ExecutionSession
from autoforge_models.memory_entry import MemoryEntry
from autoforge_models.knowledge import KnowledgeNode
from autoforge_models.quality_gate import QualityGate
from autoforge_models.event import BaseEvent

from autoforge_events.base import BaseEvent as DomainBaseEvent
from autoforge_events.event_types import EventCategory, EventType

from autoforge_kernel.interfaces import (
    # Request and Intent Models
    Request,
    IntentAnalysisResult,
    StrategicPlan,
    ExecutableWorkflow,
    # Service Interfaces
    RuntimeStateManager,
    EventBus,
    MemoryEngine,
    KnowledgeEngine,
    ModelRouter,
    ExecutionContinuityManager,
    ConnectorLayer,
    ObservabilityService,
    SecurityService,
    # Platform Engine Interfaces
    StrategicEngine,
    WorkflowEngine,
    ExecutionEngine,
    ReviewEngine,
    # Kernel Internal Interfaces
    RequestValidator,
    RequestNormalizer,
    ProjectInitializer,
    IdentifierGenerator,
    IntentAnalyzer,
    PlanningCoordinator,
    OrchestrationEngine,
    LoopOrchestrator,
    WorkerDispatchCoordinator,
    InfrastructureCoordinator,
    FailureDetector,
    RecoveryCoordinator,
    ApprovalCoordinator,
    CompletionModule,
    LifecycleCoordinator,
    RuntimeLifecycleManager,
    ProjectLifecycleManager,
    RecoveryModule,
)


class KernelRuntimeStatus(str, Enum):
    """Runtime status for the Kernel."""

    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    PROCESSING = "processing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"


class Kernel:
    """
    The AutoForge AI Kernel - Executive Orchestrator.

    The Kernel is the single entry point for all platform requests and the central
    coordination layer that transforms user intent into completed software engineering
    projects.

    The Kernel owns execution orchestration. Everything else provides capabilities.
    The Kernel never directly performs engineering work. Instead, it coordinates
    infrastructure, engineering workflows, and specialist workers.

    Attributes:
        kernel_id: Unique identifier for this Kernel instance.
        version: Kernel version.
        status: Current runtime status.
        config: Kernel configuration.
    """

    def __init__(
        self,
        kernel_id: uuid.UUID | None = None,
        version: str = "0.1.0",
        config: dict[str, Any] | None = None,
        # Service dependencies (injected)
        runtime_state_manager: RuntimeStateManager | None = None,
        event_bus: EventBus | None = None,
        memory_engine: MemoryEngine | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        model_router: ModelRouter | None = None,
        execution_continuity_manager: ExecutionContinuityManager | None = None,
        connector_layer: ConnectorLayer | None = None,
        observability_service: ObservabilityService | None = None,
        security_service: SecurityService | None = None,
        # Platform Engine dependencies (injected)
        strategic_engine: StrategicEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        execution_engine: ExecutionEngine | None = None,
        review_engine: ReviewEngine | None = None,
        # Internal module dependencies (injected)
        request_validator: RequestValidator | None = None,
        request_normalizer: RequestNormalizer | None = None,
        project_initializer: ProjectInitializer | None = None,
        identifier_generator: IdentifierGenerator | None = None,
        intent_analyzer: IntentAnalyzer | None = None,
        planning_coordinator: PlanningCoordinator | None = None,
        orchestration_engine: OrchestrationEngine | None = None,
        loop_orchestrator: LoopOrchestrator | None = None,
        worker_dispatch_coordinator: WorkerDispatchCoordinator | None = None,
        infrastructure_coordinator: InfrastructureCoordinator | None = None,
        failure_detector: FailureDetector | None = None,
        recovery_coordinator: RecoveryCoordinator | None = None,
        approval_coordinator: ApprovalCoordinator | None = None,
        completion_module: CompletionModule | None = None,
        lifecycle_coordinator: LifecycleCoordinator | None = None,
        runtime_lifecycle_manager: RuntimeLifecycleManager | None = None,
        project_lifecycle_manager: ProjectLifecycleManager | None = None,
        recovery_module: RecoveryModule | None = None,
    ):
        """
        Initialize the Kernel.

        All dependencies are injected to enable loose coupling and testability.
        """
        # Kernel identity
        self.kernel_id = kernel_id or uuid.uuid4()
        self.version = version
        self.config = config or {}
        self.status = KernelRuntimeStatus.CREATED
        self.created_at = datetime.now(timezone.utc)

        # Service dependencies
        self.runtime_state_manager = runtime_state_manager
        self.event_bus = event_bus
        self.memory_engine = memory_engine
        self.knowledge_engine = knowledge_engine
        self.model_router = model_router
        self.execution_continuity_manager = execution_continuity_manager
        self.connector_layer = connector_layer
        self.observability_service = observability_service
        self.security_service = security_service

        # Platform Engine dependencies
        self.strategic_engine = strategic_engine
        self.workflow_engine = workflow_engine
        self.execution_engine = execution_engine
        self.review_engine = review_engine

        # Internal module dependencies
        self.request_validator = request_validator
        self.request_normalizer = request_normalizer
        self.project_initializer = project_initializer
        self.identifier_generator = identifier_generator
        self.intent_analyzer = intent_analyzer
        self.planning_coordinator = planning_coordinator
        self.orchestration_engine = orchestration_engine
        self.loop_orchestrator = loop_orchestrator
        self.worker_dispatch_coordinator = worker_dispatch_coordinator
        self.infrastructure_coordinator = infrastructure_coordinator
        self.failure_detector = failure_detector
        self.recovery_coordinator = recovery_coordinator
        self.approval_coordinator = approval_coordinator
        self.completion_module = completion_module
        self.lifecycle_coordinator = lifecycle_coordinator
        self.runtime_lifecycle_manager = runtime_lifecycle_manager
        self.project_lifecycle_manager = project_lifecycle_manager
        self.recovery_module = recovery_module

        # Active projects tracking
        self.active_projects: dict[uuid.UUID, dict[str, Any]] = {}

        # Event handlers registry
        self._event_handlers: dict[EventType, list[Coroutine]] = {}

    # ========================================================================
    # Public Kernel Interface (Section 6 of Specification)
    # ========================================================================

    async def submit_request(
        self,
        request: Request,
    ) -> dict[str, Any]:
        """
        Submit a request to the Kernel.

        This is the main entry point for all platform requests.

        Args:
            request: The user's request.

        Returns:
            Dictionary containing project_id, status, estimated_duration, estimated_cost.
        """
        # Validate request
        if self.request_validator:
            is_valid, errors = await self.request_validator.validate(request)
            if not is_valid:
                raise ValueError(f"Invalid request: {', '.join(errors)}")

        # Normalize request
        if self.request_normalizer:
            request = await self.request_normalizer.normalize(request)

        # Initialize project
        if self.project_initializer:
            project = await self.project_initializer.initialize(request)
        else:
            raise RuntimeError("Project initializer not configured")

        project_id = project.id

        # Generate identifiers
        correlation_id = None
        workflow_id = None
        if self.identifier_generator:
            correlation_id = self.identifier_generator.generate_correlation_id()
            workflow_id = self.identifier_generator.generate_workflow_id()

        # Create project in state manager
        if self.runtime_state_manager:
            await self.runtime_state_manager.create_project(project)

        # Track active project
        self.active_projects[project_id] = {
            "project": project,
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "status": "created",
            "created_at": datetime.now(timezone.utc),
        }

        # Publish project.created event
        await self._publish_event(
            event_type=EventType.CREATED,
            event_category=EventCategory.PROJECT,
            aggregate_id=project_id,
            aggregate_type="Project",
            correlation_id=correlation_id,
            metadata={
                "project_name": project.name,
                "request_text": request.request_text[:100],
            },
        )

        # Begin orchestration (async, don't block)
        # In a real implementation, this would be scheduled as a background task
        # For now, we'll just return the project info
        return {
            "project_id": project_id,
            "status": "created",
            "estimated_duration": 0.0,
            "estimated_cost": 0.0,
        }

    async def get_status(self, project_id: uuid.UUID) -> dict[str, Any]:
        """
        Get the current status of a project.

        Args:
            project_id: The project to query.

        Returns:
            Dictionary containing status, progress, current_phase, etc.
        """
        if self.runtime_state_manager:
            project = await self.runtime_state_manager.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            state = await self.runtime_state_manager.get_project_state(project_id)
            return {
                "project_id": project_id,
                "status": state.get("status", "unknown"),
                "progress": state.get("progress", 0.0),
                "current_phase": state.get("current_phase", "unknown"),
                "active_tasks": state.get("running_count", 0),
                "estimated_completion": state.get("estimated_duration"),
                "metrics": {
                    "duration": state.get("actual_duration", 0.0),
                    "cost": state.get("actual_cost", 0.0),
                    "token_usage": state.get("token_usage", 0),
                },
            }
        else:
            raise RuntimeError("Runtime state manager not configured")

    async def pause(self, project_id: uuid.UUID, reason: str) -> None:
        """
        Pause a running project.

        Args:
            project_id: The project to pause.
            reason: Reason for pausing.
        """
        if self.project_lifecycle_manager:
            await self.project_lifecycle_manager.pause_project(project_id, reason)
        else:
            raise RuntimeError("Project lifecycle manager not configured")

    async def resume(self, project_id: uuid.UUID) -> None:
        """
        Resume a paused project.

        Args:
            project_id: The project to resume.
        """
        if self.project_lifecycle_manager:
            await self.project_lifecycle_manager.resume_project(project_id)
        else:
            raise RuntimeError("Project lifecycle manager not configured")

    async def cancel(self, project_id: uuid.UUID, reason: str) -> None:
        """
        Cancel a project.

        Args:
            project_id: The project to cancel.
            reason: Reason for cancellation.
        """
        if self.project_lifecycle_manager:
            await self.project_lifecycle_manager.cancel_project(project_id, reason)
        else:
            raise RuntimeError("Project lifecycle manager not configured")

    async def submit_approval_decision(
        self,
        approval_id: uuid.UUID,
        decision: str,
        feedback: str | None = None,
        modifications: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Submit a human approval decision.

        Args:
            approval_id: The approval request identifier.
            decision: The decision (approved, rejected, modified).
            feedback: Optional human feedback.
            modifications: Optional modifications to the plan.

        Returns:
            Dictionary containing status and next_actions.
        """
        if self.approval_coordinator:
            result = await self.approval_coordinator.process_decision(
                approval_id, decision, feedback, modifications
            )
            return result
        else:
            raise RuntimeError("Approval coordinator not configured")

    # ========================================================================
    # Runtime Lifecycle (Section 9 of Specification)
    # ========================================================================

    async def initialize(self) -> None:
        """
        Initialize the Kernel runtime.

        This method initializes all components and prepares the Kernel to accept requests.
        """
        self.status = KernelRuntimeStatus.STARTING

        # Initialize lifecycle coordinator
        if self.lifecycle_coordinator:
            await self.lifecycle_coordinator.coordinate_runtime_lifecycle("initialize")

        # Initialize runtime lifecycle manager
        if self.runtime_lifecycle_manager:
            await self.runtime_lifecycle_manager.initialize()

        # Connect to infrastructure services
        if self.runtime_state_manager:
            # Verify connection to Runtime State Manager
            pass

        if self.event_bus:
            # Subscribe to events
            await self._subscribe_to_events()

        # Publish kernel.starting event
        await self._publish_event(
            event_type=EventType.STARTED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"version": self.version},
        )

        self.status = KernelRuntimeStatus.READY

    async def start(self) -> None:
        """Start the Kernel runtime."""
        if self.runtime_lifecycle_manager:
            await self.runtime_lifecycle_manager.start()
        else:
            self.status = KernelRuntimeStatus.READY

    async def pause_runtime(self, reason: str) -> None:
        """
        Pause the Kernel runtime.

        Args:
            reason: Reason for pausing.
        """
        self.status = KernelRuntimeStatus.PAUSED

        if self.runtime_lifecycle_manager:
            await self.runtime_lifecycle_manager.pause(reason)

        await self._publish_event(
            event_type=EventType.PAUSED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

    async def resume_runtime(self) -> None:
        """Resume the Kernel runtime."""
        self.status = KernelRuntimeStatus.READY

        if self.runtime_lifecycle_manager:
            await self.runtime_lifecycle_manager.resume()

        await self._publish_event(
            event_type=EventType.RESUMED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
        )

    async def shutdown(self, reason: str) -> None:
        """
        Shutdown the Kernel runtime.

        Args:
            reason: Reason for shutdown.
        """
        self.status = KernelRuntimeStatus.STOPPING

        # Save checkpoints for all active projects
        for project_id in self.active_projects:
            if self.execution_continuity_manager:
                # Save checkpoint
                pass

        # Publish kernel.stopping event
        await self._publish_event(
            event_type=EventType.CANCELLED,
            event_category=EventCategory.SYSTEM_EVENT,
            aggregate_id=self.kernel_id,
            aggregate_type="Kernel",
            metadata={"reason": reason},
        )

        # Shutdown runtime lifecycle manager
        if self.runtime_lifecycle_manager:
            await self.runtime_lifecycle_manager.shutdown(reason)

        self.status = KernelRuntimeStatus.STOPPED

    def get_runtime_status(self) -> str:
        """Get the current runtime status."""
        return self.status.value

    # ========================================================================
    # Internal Methods
    # ========================================================================

    async def _publish_event(
        self,
        event_type: EventType,
        event_category: EventCategory,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        correlation_id: uuid.UUID | None = None,
        causation_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish an event to the Event Bus.

        Args:
            event_type: The type of event.
            event_category: The category of event.
            aggregate_id: The ID of the aggregate this event relates to.
            aggregate_type: The type of the aggregate.
            correlation_id: Optional correlation ID.
            causation_id: Optional causation ID.
            metadata: Optional metadata.
        """
        if not self.event_bus:
            return

        event = DomainBaseEvent(
            event_type=event_type,
            event_category=event_category,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            metadata=metadata or {},
        )

        await self.event_bus.publish(event)

    async def _subscribe_to_events(self) -> None:
        """Subscribe to events from the Event Bus."""
        if not self.event_bus:
            return

        # Subscribe to loop events
        await self.event_bus.subscribe(
            event_types=[
                EventType.COMPLETED,
                EventType.CHANGES_REQUESTED,
                EventType.REJECTED,
                EventType.FAILED,
            ],
            handler=self._handle_loop_event,
        )

        # Subscribe to task events
        await self.event_bus.subscribe(
            event_types=[
                EventType.COMPLETED,
                EventType.FAILED,
                EventType.PAUSED,
                EventType.BLOCKED,
            ],
            handler=self._handle_task_event,
        )

        # Subscribe to approval events
        await self.event_bus.subscribe(
            event_types=[
                EventType.APPROVED,
                EventType.REJECTED,
                EventType.CHANGES_REQUESTED,
            ],
            handler=self._handle_approval_event,
        )

    async def _handle_loop_event(self, event: DomainBaseEvent) -> None:
        """Handle loop lifecycle events."""
        # Implementation will be added in orchestration module
        pass

    async def _handle_task_event(self, event: DomainBaseEvent) -> None:
        """Handle task lifecycle events."""
        # Implementation will be added in orchestration module
        pass

    async def _handle_approval_event(self, event: DomainBaseEvent) -> None:
        """Handle approval events."""
        # Implementation will be added in approval module
        pass

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        """String representation of the Kernel."""
        return (
            f"Kernel("
            f"kernel_id={self.kernel_id}, "
            f"version={self.version}, "
            f"status={self.status.value}, "
            f"active_projects={len(self.active_projects)}"
            f")"
        )