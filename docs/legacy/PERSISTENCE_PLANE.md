# Persistence Plane

## Purpose

The Persistence Plane is the data storage and retrieval layer of the AutoForge AI platform. It is responsible for all durable state — storing, indexing, and retrieving the data that the Control Plane and Data Plane depend on. The Persistence Plane is the "memory" of the platform, ensuring that no data is lost and that every component can access the data it needs.

## Responsibilities

- **Durable Storage** — Persist all platform data durably and reliably
- **Data Indexing** — Maintain indexes for efficient data retrieval
- **Data Integrity** — Ensure data consistency, referential integrity, and validation
- **Backup & Recovery** — Manage backups and support point-in-time recovery
- **Data Lifecycle** — Manage data retention, archival, and purging
- **Access Control** — Enforce data access policies

## Design Goals

1. **Durability First** — Data is never lost. Writes are acknowledged only after durable persistence.
2. **Consistent Reads** — Once a write is acknowledged, subsequent reads return the written data.
3. **Operational Simplicity** — The Persistence Plane is the simplest plane — it stores and retrieves data without business logic.
4. **Pluggable Backends** — Storage backends are swappable (PostgreSQL, S3, Redis) without affecting other planes.

## Core Concepts

### Persistence Plane Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Persistence Plane                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Storage Layer                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │Relational│  │ Document │  │  Object  │  │  Key-│ │   │
│  │  │ (Postgres)│  │ (JSON)   │  │ Storage  │  │ Value│ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  │(Redis)│ │   │
│  │                                            └──────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Index Layer                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │ Primary  │  │ Secondary│  │  Full-   │  │Vector│ │   │
│  │  │ Keys     │  │ Indexes  │  │  Text    │  │Index  │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Lifecycle Layer                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │ Backup   │  │ Archival │  │ Retention│  │Purge │ │   │
│  │  │ Manager  │  │ Manager  │  │  Manager │  │Manager│ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Storage Types

| Storage Type | Technology | Data Stored | Characteristics |
|---|---|---|---|
| **Relational** | PostgreSQL | State (tasks, projects, workflows), metadata (artifacts, reviews), audit trails | ACID compliant, strongly consistent, relational queries |
| **Document** | PostgreSQL JSONB | Artifact metadata, event payloads, configuration | Schema-flexible, indexed JSON queries |
| **Object Storage** | S3 / MinIO | Artifact content (code, docs, diagrams), checkpoints, logs | High throughput, cost-effective for large blobs |
| **Key-Value** | Redis | Cache (state, model responses, sessions), queues (scheduling, retry) | Low latency, TTL-based expiration |
| **Vector** | pgvector / Pinecone | Embeddings for semantic search, knowledge graph embeddings | Similarity search, high-dimensional |

### Data Ownership

| Data Type | Primary Store | Cache | Backup Frequency |
|---|---|---|---|
| **Task State** | PostgreSQL | Redis | Continuous (WAL) |
| **Project State** | PostgreSQL | Redis | Continuous (WAL) |
| **Artifact Metadata** | PostgreSQL | Redis | Continuous (WAL) |
| **Artifact Content** | Object Storage | None | Hourly |
| **Event Log** | PostgreSQL | None | Continuous (WAL) |
| **Checkpoints** | Object Storage | None | Per checkpoint |
| **Cache Data** | Redis | N/A | Not backed up |
| **Queue Data** | Redis | N/A | Not backed up |
| **Graph Data** | PostgreSQL / Graph DB | Redis | Continuous (WAL) |
| **Audit Logs** | PostgreSQL | None | Daily |

## Ownership Boundaries

| Component | Owns | Does Not Own |
|---|---|---|
| **Relational Store** | Structured data, relationships, constraints | File content, large blobs |
| **Object Storage** | File content, checkpoints, logs | Structured queries, relationships |
| **Cache** | Temporary data, session state | Durable data, authoritative state |
| **Index Layer** | Index definitions, index data | Source data, query execution |
| **Lifecycle Layer** | Backup schedules, retention policies | Data content, access control |

## Communication Between Planes

```
┌──────────────┐    Read/Write     ┌──────────────┐
│  Control     │◀────────────────▶│ Persistence  │
│  Plane       │                  │   Plane      │
└──────────────┘                  └──────────────┘
                                        ▲
                                        │ Read/Write
                                        ▼
┌──────────────┐                  ┌──────────────┐
│   Data       │◀────────────────▶│              │
│   Plane      │   Read/Write     │              │
└──────────────┘                  └──────────────┘
```

- **Control Plane → Persistence Plane**: State reads and writes (task state, project state, queue state)
- **Data Plane → Persistence Plane**: Data reads and writes (artifact content, tool results, cache data)
- **Persistence Plane → All**: Query results, write acknowledgments, error responses

## Data Integrity

### Write-Ahead Log (WAL)
All writes go through a write-ahead log before being applied. This ensures that no write is lost even if the system crashes between the write and the application.

### Constraints
Referential integrity is enforced at the database level. Foreign key constraints ensure that referenced entities exist.

### Validation
Data is validated before storage. Invalid data is rejected with a descriptive error.

### Checksums
Artifact content is stored with SHA-256 checksums. Integrity is verified on read.

## Backup & Recovery

### Backup Types
- **Continuous** — WAL archiving for point-in-time recovery
- **Hourly** — Artifact content snapshots
- **Daily** — Full database backup
- **Weekly** — Full system backup (database + object storage)

### Recovery
- **Point-in-Time** — Restore database to any point within the retention window
- **Full Restore** — Restore entire system from latest backup
- **Selective Restore** — Restore specific projects or data types

### Retention
- **Active data** — Retained for duration of project + 30 days
- **Archived data** — Retained for 1 year
- **Audit data** — Retained for 7 years (compliance)
- **Backups** — Daily backups retained for 30 days; weekly backups retained for 1 year

## Failure Modes

| Failure Mode | Impact | Mitigation |
|---|---|---|
| **Database Corruption** | Data loss | Point-in-time recovery from WAL |
| **Storage Outage** | Cannot read/write data | Read replicas; cache fallback for reads |
| **Backup Failure** | No recovery point | Alert on backup failure; retry with backoff |
| **Data Inconsistency** | Conflicting data | Constraint enforcement; periodic consistency checks |
| **Slow Queries** | Degraded performance | Query optimization; read replicas; caching |

## Observability

- Storage utilization by type and project
- Query latency by query type and storage backend
- Backup success/failure rate and duration
- Replication lag for read replicas
- Cache hit/miss ratio
- All storage operations produce structured logs

## Security Considerations

- Data is encrypted at rest (AES-256)
- Data is encrypted in transit (TLS 1.3)
- Access control is enforced at the storage backend level
- Audit logs are append-only and cannot be modified
- Backup data is encrypted with separate keys
- Data retention policies comply with regulatory requirements

## Scalability Considerations

- Relational database supports read replicas for read scaling
- Object storage scales horizontally with no practical limit
- Cache layer can be clustered for capacity
- Data is partitioned by project for isolation
- Indexes are maintained for common query patterns
- Connection pooling is used to manage database connections

## Future Implementation Notes

- The Persistence Plane should support multi-region replication for disaster recovery
- The Persistence Plane should support data tiering (hot/warm/cold) for cost optimization
- The Persistence Plane should support schema migration tooling for zero-downtime updates
- The Persistence Plane should support data anonymization for development environments

## Open Questions

- Should the Persistence Plane support multi-master replication for active-active regions?
- How should the Persistence Plane handle schema changes that require data migration?
- Should the Persistence Plane support data federation for querying across multiple storage backends?
- How should the Persistence Plane handle data sovereignty requirements?
- Should the Persistence Plane support event-driven data export for external systems?