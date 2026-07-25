# Memory

## Purpose

The Memory package provides state management, persistence, and context storage for the AutoForge AI platform. It enables services to maintain state across workflow steps and recover from failures.

## Responsibility

- Manage short-term and long-term memory for workflows
- Persist workflow state for recovery and audit
- Provide vector storage for semantic context retrieval
- Implement caching strategies for performance optimization

## Future Contents

- In-memory cache for active workflow state
- Persistent storage adapters (PostgreSQL, Redis)
- Vector store integration for semantic search
- State serialization and checkpointing
- Context window management for AI agents
- Memory pruning and garbage collection