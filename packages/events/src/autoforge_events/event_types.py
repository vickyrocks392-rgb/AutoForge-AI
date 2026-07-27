"""
Event type definitions for the AutoForge AI platform.

Defines the canonical ``EventCategory`` and ``EventType`` enumerations
used by every event in the system.
"""

from __future__ import annotations

from enum import Enum


class EventCategory(str, Enum):
    """
    High-level category for a domain event.

    Categories group related event types together and are used for
    routing, filtering, and subscription patterns in the Event Bus.
    """

    PROJECT = "project"
    """Events related to project lifecycle (create, archive, etc.)."""

    TASK = "task"
    """Events related to task lifecycle (create, start, complete, etc.)."""

    EXECUTION = "execution"
    """Events related to execution sessions (start, complete, fail, etc.)."""

    ARTIFACT = "artifact"
    """Events related to artifacts (create, update, etc.)."""

    MEMORY = "memory"
    """Events related to memory entries (store, update, delete, etc.)."""


class EventType(str, Enum):
    """
    The specific type of a domain event.

    Each value represents a distinct occurrence in the system.
    Event types are strongly typed — they are not generic strings.
    """

    # ------------------------------------------------------------------
    # Project events
    # ------------------------------------------------------------------
    PROJECT_CREATED = "project.created"
    """A new project was created."""

    PROJECT_UPDATED = "project.updated"
    """An existing project was updated."""

    PROJECT_ARCHIVED = "project.archived"
    """A project was archived (soft-deleted)."""

    PROJECT_DELETED = "project.deleted"
    """A project was permanently deleted."""

    # ------------------------------------------------------------------
    # Task events
    # ------------------------------------------------------------------
    TASK_CREATED = "task.created"
    """A new task was created within a project."""

    TASK_UPDATED = "task.updated"
    """An existing task was updated."""

    TASK_QUEUED = "task.queued"
    """A task was queued and is waiting for scheduling."""

    TASK_READY = "task.ready"
    """All task dependencies are satisfied; the task is ready to execute."""

    TASK_STARTED = "task.started"
    """A task has begun execution."""

    TASK_PAUSED = "task.paused"
    """A task was paused (e.g. waiting for external input)."""

    TASK_RESUMED = "task.resumed"
    """A paused task was resumed."""

    TASK_COMPLETED = "task.completed"
    """A task completed successfully."""

    TASK_FAILED = "task.failed"
    """A task failed with an error."""

    TASK_CANCELLED = "task.cancelled"
    """A task was cancelled before completion."""

    TASK_BLOCKED = "task.blocked"
    """A task is blocked by an unresolved dependency."""

    TASK_DELETED = "task.deleted"
    """A task was deleted."""

    # ------------------------------------------------------------------
    # Execution events
    # ------------------------------------------------------------------
    EXECUTION_STARTED = "execution.started"
    """An execution session has started."""

    EXECUTION_COMPLETED = "execution.completed"
    """An execution session completed successfully."""

    EXECUTION_FAILED = "execution.failed"
    """An execution session failed with an error."""

    EXECUTION_PAUSED = "execution.paused"
    """An execution session was paused."""

    EXECUTION_RESUMED = "execution.resumed"
    """A paused execution session was resumed."""

    EXECUTION_CANCELLED = "execution.cancelled"
    """An execution session was cancelled."""

    EXECUTION_TIMED_OUT = "execution.timed_out"
    """An execution session exceeded its time limit."""

    # ------------------------------------------------------------------
    # Artifact events
    # ------------------------------------------------------------------
    ARTIFACT_CREATED = "artifact.created"
    """A new artifact was produced."""

    ARTIFACT_UPDATED = "artifact.updated"
    """An existing artifact was updated."""

    ARTIFACT_DELETED = "artifact.deleted"
    """An artifact was deleted."""

    # ------------------------------------------------------------------
    # Memory events
    # ------------------------------------------------------------------
    MEMORY_STORED = "memory.stored"
    """A new memory entry was stored."""

    MEMORY_UPDATED = "memory.updated"
    """An existing memory entry was updated."""

    MEMORY_DELETED = "memory.deleted"
    """A memory entry was deleted."""

    MEMORY_RETRIEVED = "memory.retrieved"
    """A memory entry was retrieved (read access)."""