# AutoForge Knowledge Platform

Implements the Knowledge Platform Specification v1.0 for the AutoForge AI OS.

## Overview

The Knowledge Platform is a comprehensive knowledge management subsystem that provides:

- **Knowledge Retrieval**: Multi-strategy retrieval (semantic, keyword, hybrid, multi-source)
- **Knowledge Fusion**: Conflict detection, resolution, and consensus building
- **Trust Scoring**: Multi-factor trust evaluation for sources and content
- **Citation Management**: Citation generation, validation, formatting, and provenance tracking
- **Validation**: Fact-checking, cross-referencing, consistency checking, and contradiction detection
- **Context Assembly**: Intelligent context window management
- **Research Briefs**: Automated research brief generation from validated knowledge
- **Caching**: Performance optimization through intelligent caching

## Architecture

The Knowledge Platform follows a strict interface-first architecture with dependency injection:

```
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Core Components                                             │
│  • Knowledge Engine                                          │
│  • Knowledge Router                                          │
│  • Source Connector Manager                                  │
│  • Query Processor                                           │
│  • Source Registry                                           │
│  • Knowledge Event Publisher                                 │
├─────────────────────────────────────────────────────────────┤
│  Subsystems                                                  │
│  • Retrieval (Pipeline + Strategies + Rank/Filter/Dedup)    │
│  • Fusion (Conflict Resolution + Consensus + Merge)          │
│  • Trust Scoring (Source + Content + Historical + Expert)    │
│  • Citation (Generation + Validation + Formatting + Index)   │
│  • Validation (Fact-check + Cross-ref + Consistency + More)  │
│  • Context Assembly                                          │
│  • Research Brief Generation                                 │
│  • Caching                                                   │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install autoforge-knowledge-platform
```

## Quick Start

```python
from autoforge_knowledge_platform import (
    KnowledgeEngine,
    QueryProcessor,
    SourceRegistry,
)

# Initialize components
query_processor = QueryProcessor()
source_registry = SourceRegistry()
knowledge_engine = KnowledgeEngine(
    query_processor=query_processor,
    source_registry=source_registry,
)

# Register a knowledge source
source = KnowledgeSource(
    name="Documentation",
    type="documentation",
    domain="backend",
    trust_score=0.9,
)
await source_registry.register_source(source)

# Query knowledge
result = await knowledge_engine.query({
    "query": "How to implement authentication?",
    "sources": [source.id],
})
```

## Components

### Core Components

- **KnowledgeEngine**: Main orchestration component for knowledge operations
- **KnowledgeRouter**: Routes queries to appropriate retrieval strategies
- **SourceConnectorManager**: Manages connections to knowledge sources
- **QueryProcessor**: Processes and normalizes knowledge queries
- **SourceRegistry**: Manages knowledge source registration and lookup
- **KnowledgeEventPublisher**: Publishes knowledge events to the Event Platform

### Retrieval Subsystem

- **RetrievalPipeline**: Orchestrates the retrieval process
- **SemanticRetrieval**: Vector-based semantic search
- **KeywordRetrieval**: Traditional keyword-based search
- **HybridRetrieval**: Combines semantic and keyword approaches
- **MultiSourceRetrieval**: Parallel retrieval from multiple sources
- **RankEngine**: Ranks results by relevance and trust
- **FilterEngine**: Filters results by criteria
- **DeduplicationEngine**: Removes duplicate results

### Fusion Subsystem

- **KnowledgeFusion**: Combines knowledge from multiple sources
- **ConflictResolver**: Resolves conflicts between sources
- **ConsensusBuilder**: Builds consensus across sources
- **MergeEngine**: Merges complementary information
- **ContradictionDetector**: Detects contradictions between sources

### Trust Scoring Subsystem

- **TrustScorer**: Main trust scoring orchestrator
- **SourceTrustEvaluator**: Evaluates source trustworthiness
- **ContentTrustScorer**: Scores individual knowledge items
- **HistoricalAccuracyTracker**: Tracks source accuracy over time
- **ExpertEndorsementWeighter**: Weights expert-endorsed content
- **RecencyWeighter**: Weights recent content
- **CommunityValidationIntegrator**: Incorporates community signals

### Citation Subsystem

- **CitationManager**: Manages citations and provenance
- **CitationGenerator**: Generates citations for knowledge
- **CitationValidator**: Validates citation accuracy
- **CitationFormatter**: Formats citations in various styles
- **CitationIndexer**: Indexes citations for retrieval
- **ProvenanceTracker**: Tracks knowledge provenance

### Validation Subsystem

- **KnowledgeValidator**: Validates knowledge accuracy and consistency
- **FactChecker**: Verifies factual claims
- **CrossReferencer**: Cross-references across sources
- **ConsistencyChecker**: Checks internal consistency
- **OutdatedDetector**: Detects outdated information
- **ContradictionFlagger**: Flags contradictory information

### Supporting Components

- **ContextAssembler**: Assembles context for retrieval
- **ResearchBriefGenerator**: Generates research briefs
- **KnowledgeCache**: Caches knowledge for performance

## Models

- **KnowledgeItem**: Represents a piece of knowledge
- **KnowledgeSource**: Represents a knowledge source
- **Citation**: Represents a citation
- **Evidence**: Represents supporting evidence
- **TrustScore**: Represents a trust score
- **ConfidenceScore**: Represents a confidence score
- **RetrievalResult**: Represents retrieval results
- **ResearchBrief**: Represents a research brief

## Interfaces

All components implement interfaces for dependency injection and testability:

- IKnowledgeEngine
- IKnowledgeRouter
- ISourceConnectorManager
- IRetrievalPipeline
- IKnowledgeFusion
- ITrustScorer
- ICitationManager
- IKnowledgeValidator
- IContextAssembler
- IResearchBriefGenerator
- IKnowledgeCache
- IQueryProcessor
- ISourceRegistry
- IKnowledgeEventPublisher

## Design Principles

- **Interface-First**: All components implement interfaces
- **Dependency Injection**: All dependencies injected via constructors
- **Provider Agnostic**: No hardcoded providers
- **Local-First**: No external dependencies required
- **No Circular Dependencies**: Clean dependency graph

## Specification Compliance

This implementation is fully compliant with the Knowledge Platform Specification v1.0 (frozen).

See [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) for detailed compliance information.

## License

MIT License

## Version

1.0.0