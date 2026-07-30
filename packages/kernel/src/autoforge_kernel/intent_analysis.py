"""
Intent Analysis Module

Responsible for understanding user intent and classifying requests.
This module implements the Intent Analysis component of the Kernel.
"""

from __future__ import annotations

import uuid
from typing import Any

from autoforge_kernel.interfaces import (
    IntentAnalyzer,
    IntentAnalysisResult,
    Request,
)


class DefaultIntentAnalyzer(IntentAnalyzer):
    """
    Default implementation of intent analysis.

    Analyzes user intent and classifies requests.
    """

    def __init__(
        self,
        knowledge_engine: Any | None = None,
    ):
        """
        Initialize the intent analyzer.

        Args:
            knowledge_engine: Knowledge engine for domain context.
        """
        self.knowledge_engine = knowledge_engine

    async def analyze(self, request: Request) -> IntentAnalysisResult:
        """
        Analyze user intent.

        Args:
            request: The request to analyze.

        Returns:
            Intent analysis result.
        """
        # Analyze request text to determine intent
        request_text = request.request_text.lower()

        # Classify request type
        request_type = self._classify_request_type(request_text)

        # Determine scope
        scope = self._determine_scope(request_text, request)

        # Extract constraints
        constraints = self._extract_constraints(request_text, request)

        # Identify required engineering loops
        required_loops = self._identify_required_loops(request_type, request_text)

        # Determine approval policy
        approval_policy = self._determine_approval_policy(request_type, constraints)

        # Calculate confidence
        confidence = self._calculate_confidence(request_type, request_text)

        # Generate reasoning
        reasoning = self._generate_reasoning(request_type, scope, required_loops)

        return IntentAnalysisResult(
            request_type=request_type,
            scope=scope,
            constraints=constraints,
            required_loops=required_loops,
            approval_policy=approval_policy,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _classify_request_type(self, request_text: str) -> str:
        """
        Classify the type of request.

        Args:
            request_text: The request text (lowercase).

        Returns:
            Request type.
        """
        # Keywords for different request types
        research_keywords = ["research", "investigate", "analyze", "study", "explore", "find out"]
        implementation_keywords = ["build", "create", "implement", "develop", "code", "write"]
        review_keywords = ["review", "evaluate", "assess", "audit", "check"]
        deployment_keywords = ["deploy", "release", "publish", "launch"]
        testing_keywords = ["test", "verify", "validate", "check tests"]

        # Check for keywords
        if any(keyword in request_text for keyword in research_keywords):
            return "research"

        if any(keyword in request_text for keyword in review_keywords):
            return "review"

        if any(keyword in request_text for keyword in deployment_keywords):
            return "deployment"

        if any(keyword in request_text for keyword in testing_keywords):
            return "testing"

        if any(keyword in request_text for keyword in implementation_keywords):
            return "implementation"

        # Default to implementation
        return "implementation"

    def _determine_scope(self, request_text: str, request: Request) -> str:
        """
        Determine the scope and complexity of the request.

        Args:
            request_text: The request text.
            request: The full request.

        Returns:
            Scope description.
        """
        # Simple heuristic-based scope determination
        word_count = len(request_text.split())

        if word_count < 20:
            return "small"
        elif word_count < 100:
            return "medium"
        else:
            return "large"

    def _extract_constraints(self, request_text: str, request: Request) -> dict[str, Any]:
        """
        Extract constraints from the request.

        Args:
            request_text: The request text.
            request: The full request.

        Returns:
            Dictionary of constraints.
        """
        constraints = {}

        # Extract from context
        if "budget" in request.context:
            constraints["budget"] = request.context["budget"]

        if "timeline" in request.context:
            constraints["timeline"] = request.context["timeline"]

        if "quality" in request.context:
            constraints["quality"] = request.context["quality"]

        if "compliance" in request.context:
            constraints["compliance"] = request.context["compliance"]

        # Extract from configuration
        if "language" in request.configuration:
            constraints["language"] = request.configuration["language"]

        if "framework" in request.configuration:
            constraints["framework"] = request.configuration["framework"]

        if "deployment_target" in request.configuration:
            constraints["deployment_target"] = request.configuration["deployment_target"]

        return constraints

    def _identify_required_loops(self, request_type: str, request_text: str) -> list[str]:
        """
        Identify required engineering loops.

        Args:
            request_type: The type of request.
            request_text: The request text.

        Returns:
            List of required engineering loops.
        """
        # Map request types to required loops
        loop_map = {
            "research": ["research_loop"],
            "implementation": ["research_loop", "architecture_loop", "coding_loop", "review_loop", "testing_loop"],
            "review": ["review_loop"],
            "deployment": ["deployment_loop"],
            "testing": ["testing_loop"],
        }

        return loop_map.get(request_type, ["research_loop", "architecture_loop", "coding_loop", "review_loop", "testing_loop"])

    def _determine_approval_policy(self, request_type: str, constraints: dict[str, Any]) -> dict[str, Any]:
        """
        Determine the approval policy for the request.

        Args:
            request_type: The type of request.
            constraints: The constraints.

        Returns:
            Approval policy.
        """
        # Default approval policy
        policy = {
            "require_approval": False,
            "approval_gates": [],
            "timeout_seconds": 3600,
        }

        # High-risk request types require approval
        if request_type in ["deployment", "review"]:
            policy["require_approval"] = True
            policy["approval_gates"] = ["pre_execution", "post_execution"]

        # Check for compliance constraints
        if "compliance" in constraints:
            policy["require_approval"] = True
            policy["approval_gates"].append("compliance_check")

        # Deduplicate approval gates
        policy["approval_gates"] = list(set(policy["approval_gates"]))

        return policy

    def _calculate_confidence(self, request_type: str, request_text: str) -> float:
        """
        Calculate confidence in the analysis.

        Args:
            request_type: The type of request.
            request_text: The request text.

        Returns:
            Confidence score (0.0-1.0).
        """
        # Simple heuristic-based confidence calculation
        confidence = 0.8  # Base confidence

        # Increase confidence for clear keywords
        if request_type != "implementation":
            confidence += 0.1

        # Decrease confidence for very short or very long requests
        word_count = len(request_text.split())
        if word_count < 5:
            confidence -= 0.2
        elif word_count > 500:
            confidence -= 0.1

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def _generate_reasoning(self, request_type: str, scope: str, required_loops: list[str]) -> str:
        """
        Generate reasoning for the analysis.

        Args:
            request_type: The type of request.
            scope: The scope.
            required_loops: The required loops.

        Returns:
            Reasoning string.
        """
        reasoning = f"Request classified as '{request_type}' with '{scope}' scope. "
        reasoning += f"Required engineering loops: {', '.join(required_loops)}."

        return reasoning


class IntentAnalysisModule:
    """
    Intent Analysis Module.

    Coordinates intent analysis for requests.
    """

    def __init__(
        self,
        intent_analyzer: IntentAnalyzer | None = None,
        knowledge_engine: Any | None = None,
    ):
        """
        Initialize the intent analysis module.

        Args:
            intent_analyzer: Intent analyzer.
            knowledge_engine: Knowledge engine for domain context.
        """
        self.intent_analyzer = intent_analyzer or DefaultIntentAnalyzer(
            knowledge_engine=knowledge_engine
        )

    async def analyze_intent(self, request: Request) -> IntentAnalysisResult:
        """
        Analyze the intent of a request.

        Args:
            request: The request to analyze.

        Returns:
            Intent analysis result.
        """
        return await self.intent_analyzer.analyze(request)