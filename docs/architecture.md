# Architecture

```mermaid
flowchart LR
    A[CMS Provider Data API] --> B[Raw Parquet + checksum manifests]
    C[CMS Cost Report Data API] --> B
    B --> D[Normalized staging tables]
    D --> E[(DuckDB relational warehouse)]
    E --> F[Hospital KPI mart]
    E --> G[State summary mart]
    E --> H[Data-quality results]
    F --> I[Power BI implementation kit]
    G --> I
    F --> J[Excel comparison report]
    H --> J
```

The raw snapshots are immutable within a run. Manifests record the URL, retrieval timestamp,
row count, schema, and SHA-256 checksum. DuckDB creates a hospital dimension plus patient-
experience, outcome, MSPB, and cost-report facts. Reporting marts are exported as CSV and
Parquet for Power BI and Excel.

