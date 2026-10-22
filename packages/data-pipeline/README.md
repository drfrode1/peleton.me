# peleton-data-pipeline

Dagster orchestrator and lakehouse ingestion pipeline for **peleton.me**.

## Architecture & Responsibilities
- **Lakehouse Orchestration**: Implements a medallion lakehouse pattern.
  - **Bronze**: Raw JSON payloads archived in Cloudflare R2 / S3 object storage.
  - **Silver**: Cleaned, typed, deduplicated tables stored in DuckDB (local development) and MotherDuck (production).
  - **Gold**: Aggregated commuter metrics and spatial telemetry.
- **Data Sources**:
  - MET Norway Frost API (Weather observations)
  - Statens Vegvesen Datex II (Travel times)
  - Statens Vegvesen Trafikkdata (Traffic volumes)

## Getting Started
```bash
# Sync virtual environment with uv
uv sync

# Launch Dagster webserver UI
uv run dagster dev

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

For complete asset guidelines and AI coding patterns, see [`GEMINI.md`](./GEMINI.md).
