# apps/api — FastAPI Middleware Guidelines

This service serves as the core API middleware for **peleton.me**, bridging transactional operations (PostgreSQL) and high-performance lakehouse analytics (DuckDB/MotherDuck) to the TanStack frontend. It is deployed as a containerized service on **Render**.

---

## 1. Dual-Database Architectural Pattern

FastAPI routes interact with two distinct data storage tiers depending on the domain:

```
FastAPI Middleware
├── Operational Routes (/api/v1/users, /api/v1/companies)
│   └── Dependency: Depends(get_db) -> PostgreSQL (SQLAlchemy Session)
└── Analytics Routes (/api/v1/weather, /api/v1/traffic)
    └── Dependency: Depends(get_duckdb_connection) -> DuckDB/MotherDuck (Polars DataFrame)
```

### 1.1 PostgreSQL (Transactional Tier)
- **Engine & Session**: Defined in `peleton_api/core/database.py`. Lazy-loaded via `get_engine()` and `get_session_local()`.
- **Dependency**: Always inject via `db: Session = Depends(get_db)`.
- **Models**: Defined in `peleton_api/models/models.py`.
- **Purpose**: Users, companies, Strava OAuth credentials, operational state.

### 1.2 DuckDB / MotherDuck (Lakehouse Analytics Tier)
- **Connection**: Defined in `peleton_api/core/database.py` via `get_duckdb_connection()`.
- **Read-Only**: Must ALWAYS connect with `read_only=True` to prevent write-lock conflicts with Dagster pipelines.
- **Connection String Logic**:
  - If `MOTHERDUCK_TOKEN` is set, connects to MotherDuck cloud: `md:?motherduck_token={token}`.
  - Otherwise, connects to the local DuckDB database specified in `LOCAL_DUCKDB_PATH` (`/app/data/dev.duckdb`).
- **Purpose**: Open data telemetry (MET Frost weather, Vegvesen travel times and traffic volumes, commute metrics).

---

## 2. Standard Pattern for Analytics Endpoints (DuckDB + Polars)

All analytical endpoints exposing lakehouse tables must adhere to this standard pattern:

```python
from typing import Optional
import duckdb
import polars as pl
from fastapi import APIRouter, Depends, HTTPException, Query
from peleton_api.core.config import settings
from peleton_api.core.database import get_duckdb_connection
from peleton_api.schemas.weather import WeatherResponse

router = APIRouter()

@router.get("/", response_model=WeatherResponse)
def get_weather_data(
    location: Optional[str] = Query(None, description="Location ID filter"),
    days: int = Query(7, ge=1, le=365, description="Days of history"),
    limit: int = Query(100, ge=1, le=settings.max_page_limit),
    con: duckdb.DuckDBPyConnection = Depends(get_duckdb_connection),
):
    try:
        query = f"SELECT * FROM {settings.weather_table_name}"
        conditions, params = [], []

        if location:
            conditions.append("LOWER(location_id) = LOWER(?)")
            params.append(location)

        if days:
            conditions.append("reference_time >= CURRENT_TIMESTAMP - (INTERVAL '1 day' * ?)")
            params.append(days)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY reference_time DESC LIMIT ?"
        params.append(limit)

        # 1. Execute query and fetch directly as Polars DataFrame
        df: pl.DataFrame = con.sql(query, params=params).pl()

        if df.is_empty() and location:
            raise HTTPException(status_code=404, detail=f"No data for location '{location}'")

        # 2. Return typed response matching Pydantic schema
        return {
            "count": len(df),
            "filters": {"location": location, "days": days, "limit": limit},
            "data": df.to_dicts()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
```

### Key Analytical Rules:
1. **Never string-interpolate user input**: Always use `?` parameter placeholders for DuckDB query values.
2. **Zero-Copy Polars**: Convert query results using `.pl()` rather than Python dictionaries directly from DuckDB. Polars handles high-throughput serialization efficiently.
3. **Explicit Response Envelopes**: Return structured metadata (`count`, `filters`, `data`) and declare `response_model` in endpoint decorators.

---

## 3. Directory Layout & Conventions

```
apps/api/
├── peleton_api/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/       # Route handlers (companies.py, users.py, weather.py)
│   ├── core/
│   │   ├── config.py            # Settings loaded from environment
│   │   └── database.py          # SQLAlchemy engine & DuckDB connection factory
│   ├── models/
│   │   └── models.py            # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic v2 schemas (request & response models)
│   └── main.py                  # FastAPI app definition, CORS, lifespan, router inclusion
├── tests/
│   ├── conftest.py              # TestClient fixture, dependency override helpers
│   └── test_*.py                # Component and integration tests
├── pyproject.toml               # Dependencies managed via uv
└── Dockerfile                   # Container definition for Render deployment
```

---

## 4. Testing Framework & Standards

- **Framework**: `pytest` + `httpx.TestClient`.
- **Command**: `cd apps/api && uv run pytest`

### In-Memory DuckDB Fixture Pattern
For testing analytics endpoints without relying on an external DuckDB file or MotherDuck token:

```python
import duckdb
import pytest
from fastapi.testclient import TestClient
from peleton_api.core.database import get_duckdb_connection
from peleton_api.main import app

@pytest.fixture
def mock_duckdb():
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE bronze_weather_met_frost (
            location_id VARCHAR,
            reference_time TIMESTAMP,
            element_id VARCHAR,
            value DOUBLE,
            unit VARCHAR,
            ingested_at TIMESTAMP
        );
        INSERT INTO bronze_weather_met_frost VALUES
        ('Forus', '2026-10-20 12:00:00', 'air_temperature', 14.5, 'degC', '2026-10-20 12:05:00');
    """)
    yield con
    con.close()

def test_weather_endpoint_success(client: TestClient, mock_duckdb):
    app.dependency_overrides[get_duckdb_connection] = lambda: mock_duckdb
    try:
        response = client.get("/api/v1/weather/?location=Forus")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["data"][0]["location_id"] == "Forus"
    finally:
        app.dependency_overrides.clear()
```

---

## 5. Render Production Deployment

- **Port**: Render injects `$PORT`. The entrypoint must bind to `0.0.0.0:$PORT`.
- **Healthcheck**: Configured to `/health`. Must return `{"status": "ok", "service": "peleton-api"}` with HTTP 200.
- **CORS**: Ensure `CORSMiddleware` allows Vercel production frontend domain and local development origins.
- **Environment Variables**: Managed via Doppler / Render Environment dashboard:
  - `DATABASE_URL`
  - `MOTHERDUCK_TOKEN`
  - `LOCAL_DUCKDB_PATH`
