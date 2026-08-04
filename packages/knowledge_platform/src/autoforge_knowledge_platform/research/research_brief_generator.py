"""
Research Brief Generator

Generates research briefs from validated knowledge as defined in the Knowledge Platform Specification v1.0.
"""

from __future__ import annotations

from typing import Any, Dict, List
from autoforge_knowledge_platform.interfaces.knowledge_interfaces import IResearchBriefGenerator
from autoforge_knowledge_platform.models import KnowledgeItem, ResearchBrief


class ResearchBriefGenerator(IResearchBriefGenerator):
    """
    Generates research briefs from validated knowledge.
    
    As defined in Knowledge Platform Specification v1.0, Section 7.10.
    """
    
    def __init__(
        self,
        context_assembler: Any,
        citation_manager: Any,
        knowledge_validator: Any,
    ):
        """Initialize Research Brief Generator with dependencies."""
        self.context_assembler = context_assembler
        self.citation_manager = citation_manager
        self.knowledge_validator = knowledge_validator
    
    async def generate_brief(
        self,
        query: Dict[str, Any],
        validated_knowledge: List[KnowledgeItem],
    ) -> ResearchBrief:
        """
        Generate research brief from validated knowledge.
        
        Args:
            query: Query parameters
            validated_knowledge: Validated knowledge items
            
        Returns:
            ResearchBrief: Generated research brief
        """
        # Assemble context
        context = await self.context_assembler.assemble_context(
            validated_knowledge,
            query,
        )
        
        # Generate summary
        summary = await self._generate_summary(context["knowledge_items"])
        
        # Generate key findings
        key_findings = await self._extract_key_findings(context["knowledge_items"])
        
        # Generate citations
        citations = await self._generate_citations(context["knowledge_items"])
        
        # Calculate confidence
        confidence = await self._calculate_confidence(context["knowledge_items"])
        
        # Create research brief
        brief = ResearchBrief(
            query=query.get("query", ""),
            summary=summary,
            key_findings=key_findings,
            citations=citations,
            knowledge_items=context["knowledge_items"],
            confidence=confidence,
            metadata={
                "total_sources": len(set(s for item in context["knowledge_items"] for s in item.sources)),
                "total_items": len(context["knowledge_items"]),
            },
        )
        
        return brief
    
    async def _generate_summary(self, knowledge_items: List[KnowledgeItem]) -> str:
        """Generate summary from knowledge items."""
        # Simplified summary generation
        # In production, use LLM or extractive summarization
        if not knowledge_items:
            return "No knowledge available."
        
        # Combine content from top items
        top_items = knowledge_items[:5]
        summary_parts = [item.content[:200] for item in top_items]
        
        return " ".join(summary_parts)
    
    async def _extract_key_findings(self, knowledge_items: List[KnowledgeItem]) -> List[str]:
        """Extract key findings from knowledge items."""
        # Simplified key findings extraction
        # In production, use NLP to extract key points
        findings = []
        for item in knowledge_items[:10]:
            findings.append(item.content[:150])
        return findings
    
    async def _generate_citations(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """Generate citations for knowledge items."""
        citations = []
        for item in knowledge_items:
            for source_id in item.sources:
                citations.append({
                    "knowledge_item_id": item.id,
                    "source_id": source_id,
                })
        return citations
    
    async def _calculate_confidence(self, knowledge_items: List[KnowledgeItem]) -> float:
        """Calculate overall confidence score."""
        if not knowledge_items:
            return 0.0
        
        # Average trust score
        avg_trust = sum(item.trust_score for item in knowledge_items) / len(knowledge_items)
        
        # Average validation confidence
        avg_validation = sum(item.validation_confidence for item in knowledge_items) / len(knowledge_items)
        
        # Combined confidence
        confidence = (avg_trust * 0.6 + avg_validation * 0.4)
        
        return confidence