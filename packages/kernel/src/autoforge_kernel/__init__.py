"""
AutoForge AI Kernel - Executive Orchestrator

The Kernel is the single entry point for all platform requests and the central
coordination layer that transforms user intent into completed software engineering
projects.

This package provides the complete Kernel implementation including:
- Request Intake
- Intent Analysis
- Planning Coordination
- Engine Orchestration
- Service Orchestration
- Lifecycle Coordination
"""

from autoforge_kernel.kernel import Kernel
from autoforge_kernel.interfaces import (
    # Request Intake
    Request,
    RequestValidator,
    RequestNormalizer,
    ProjectInitializer,
    IdentifierGenerator,
    # Intent Analysis
    IntentAnalyzer,
    IntentAnalysisResult,
    # Planning
    PlanningCoordinator,
    StrategicPlan,
    ExecutableWorkflow,
    # Orchestration
    OrchestrationEngine,
    LoopOrchestrator,
    WorkerDispatchCoordinator,
    # Infrastructure
    InfrastructureCoordinator,
    # Recovery
    RecoveryModule,
    FailureDetector,
    RecoveryCoordinator,
    # Approval
    ApprovalCoordinator,
    # Completion
    CompletionModule,
    # Lifecycle
    LifecycleCoordinator,
    RuntimeLifecycleManager,
    ProjectLifecycleManager,
    # Services (interfaces)
    RuntimeStateManager,
    EventBus,
    MemoryEngine,
    KnowledgeEngine,
    ModelRouter,
    ExecutionContinuityManager,
    ConnectorLayer,
    ObservabilityService,
    SecurityService,
    # Platform Engines (interfaces)
    StrategicEngine,
    WorkflowEngine,
    ExecutionEngine,
    ReviewEngine,
)

__version__ = "0.1.0"

__all__ = [
    "Kernel",
    # Request Intake
    "Request",
    "RequestValidator",
    "RequestNormalizer",
    "ProjectInitializer",
    "IdentifierGenerator",
    # Intent Analysis
    "IntentAnalyzer",
    "IntentAnalysisResult",
    # Planning
    "PlanningCoordinator",
    "StrategicPlan",
    "ExecutableWorkflow",
    # Orchestration
    "OrchestrationEngine",
    "LoopOrchestrator",
    "WorkerDispatchCoordinator",
    # Infrastructure
    "InfrastructureCoordinator",
    # Recovery
    "RecoveryModule",
    "FailureDetector",
    "RecoveryCoordinator",
    # Approval
    "ApprovalCoordinator",
    # Completion
    "CompletionModule",
    # Lifecycle
    "LifecycleCoordinator",
    "RuntimeLifecycleManager",
    "ProjectLifecycleManager",
    # Services (interfaces)
    "RuntimeStateManager",
    "EventBus",
    "MemoryEngine",
    "KnowledgeEngine",
    "ModelRouter",
    "ExecutionContinuityManager",
    "ConnectorLayer",
    "ObservabilityService",
    "SecurityService",
    # Platform Engines (interfaces)
    "StrategicEngine",
    "WorkflowEngine",
    "ExecutionEngine",
    "ReviewEngine",
]