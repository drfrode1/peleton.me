# packages/data-pipeline — Dagster Lakehouse Guidelines

This package contains the **Dagster** orchestrator and data pipeline for **peleton.me**. It ingests telemetry and open data from national APIs (MET Norway Frost, Statens Vegvesen Datex II and Trafikkdata) into a serverless medallion lakehouse architecture.

---

## 1. Medallion Lakehouse Architecture

The pipeline implements the Medallion lakehouse pattern:

```
[MET Frost / Vegvesen APIs]
             │
             ▼
┌────────────────────────────────────────┐
│ Bronze Layer                           │
│ - Raw API payloads in Cloudflare R2    │
│ - Partitioned JSON / Parquet files     │
│ - Archived via archive_bronze_payload  │
└──────────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ Silver Layer                           │
│ - Cleaned, typed, deduplicated tables  │
│ - DuckDB / MotherDuck columnar storage │
│ - Timezone normalized (Europe/Oslo)    │
└──────────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│ Gold Layer                             │
│ - Commuter aggregations & ESG metrics  │
│ - Privacy-first H3 spatial hex bins    │
└────────────────────────────────────────┘
```

### 1.1 Bronze Archiving Standard
All raw external API responses must be archived to S3/R2 object storage using `archive_bronze_payload`:
- **Key Pattern**: `bronze/{domain}/{source}/{entity}/location={loc}/year={YYYY}/month={MM}/day={DD}/{entity}_{HHMMSS}.json`
- **Bucket**: `R2_BUCKET_NAME` (`peleton-r2-bucket` locally on SeaweedFS/MinIO, Cloudflare R2 in production).

### 1.2 Silver Lakehouse Storage
- **Local Dev**: Writes to `LOCAL_DUCKDB_PATH` (`/app/data/dev.duckdb` shared with `apps/api` via Docker volume `duckdb_data`).
- **Production**: Writes directly to **MotherDuck** (`md:peleton_db?token={MOTHERDUCK_TOKEN}`) via `MotherDuckResource`.
- **Deduplication**: When ingesting incremental or snapshot data, use temporary tables and `DELETE WHERE (location_id, ...) IN (SELECT ... FROM temp_table)` before inserting.

---

## 2. Dagster Asset Standards

All pipeline logic must be structured as Dagster **Software-Defined Assets** (`@asset`):

```python
from dagster import asset, AssetExecutionContext, ResourceParam, Output
from typing import Any
import polars as pl
import duckdb

@asset(
    group_name="traffic",
    description="Loads Bronze traffic snapshots into the Silver DuckDB analytics table."
)
def silver_traffic_volumes_vegvesen(
    context: AssetExecutionContext,
    bronze_traffic_volumes_vegvesen: str,
) -> Output[int]:
    # Use DuckDB for SQL transformations and deduplication
    ...
```

### Invariants:
1. **Resource Injection**: Always access S3/R2 and MotherDuck via Dagster resources (`s3`, `motherduck`), never raw global clients.
2. **Vectorized Transforms**: Use **Polars** (`polars as pl`) for all in-memory data munging, parsing, and datetime conversions.
3. **Timezones**: Always localize timestamps explicitly using `Europe/Oslo` or UTC before storing.
4. **Configuration**: Location definitions, coordinates, and TRP sensor IDs must be stored in `config/locations.yaml` and loaded via `config_loader.py`.

---

## 3. Directory Layout

```
packages/data-pipeline/
├── data_pipeline/
│   ├── assets/              # Dagster assets (weather_frost.py, traffic_volumes.py, travel_times.py)
│   ├── config/              # YAML config definitions (locations.yaml)
│   ├── utils/               # Storage utilities, config loaders (storage.py, config_loader.py)
│   ├── definitions.py       # Dagster Definitions entrypoint (assets, jobs, schedules, resources)
│   └── resources.py         # MotherDuck and S3 resource definitions
├── tests/
│   ├── conftest.py          # Pytest fixtures and mocks
│   └── test_*.py            # Pipeline unit & asset tests
├── pyproject.toml           # Python package config (uv)
└── Dockerfile.dev           # Development container running Dagster webserver
```

---

## 4. Testing Framework & Standards

- **Runner**: `pytest`
- **Command**: `cd packages/data-pipeline && uv run pytest`

### Testing Software-Defined Assets
Assets should be tested using Dagster's `materialize()` utility or by direct function invocation with mocked resources:

```python
import pytest
from dagster import materialize
from data_pipeline.utils.storage import archive_bronze_payload
from unittest.mock import MagicMock

def test_archive_bronze_payload():
    mock_s3 = MagicMock()
    key = archive_bronze_payload(
        s3_client=mock_s3,
        bucket="test-bucket",
        domain="weather",
        source="met_frost",
        entity="observations",
        location_id="Forus",
        payload={"sample": "data"}
    )
    assert key.startswith("bronze/weather/met_frost/observations/location=Forus/")
    assert mock_s3.put_object.called
```

---

## 5. Environment Variables & Secret Configuration

Managed via Doppler:
- `MOTHERDUCK_TOKEN`: Secret token for cloud MotherDuck connection.
- `LOCAL_DUCKDB_PATH`: File path for local DuckDB database (default: `/app/data/dev.duckdb`).
- `R2_ENDPOINT`: Cloudflare R2 S3 endpoint URL (or `http://minio:8333` locally).
- `R2_ACCESS_KEY_ID`: Cloudflare R2 access key.
- `R2_SECRET_ACCESS_KEY`: Cloudflare R2 secret access key.
- `R2_BUCKET_NAME`: Target bucket (default: `peleton-r2-bucket`).
- `FROST_CLIENT_ID`, `FROST_CLIENT_SECRET`: MET Frost API credentials.
- `VEGVESEN_USERNAME`, `VEGVESEN_PASSWORD`: Vegvesen Datex credentials.
