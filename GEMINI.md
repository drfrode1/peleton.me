# peleton.me — Project Architecture & AI Engineering Guidelines

Welcome to **peleton.me**, the national platform for active commuting telemetry translating bike data into health, traffic, and ESG metrics. The platform is designed as a **100% serverless lakehouse** powered by Dagster, DuckDB/MotherDuck, Cloudflare R2, FastAPI, and TanStack React 19.

---

## 1. Monorepo Map & Service Boundaries

```
peleton.me/
├── apps/
│   ├── api/             # FastAPI middleware (REST API, analytics query layer, operational endpoints)
│   └── web/             # TanStack frontend (TanStack Router, Query, React 19, Tailwind v4)
├── packages/
│   ├── data-pipeline/   # Dagster orchestrator (MET Frost, Vegvesen Datex/Trafikkdata, Lakehouse)
│   └── db/              # Drizzle ORM (PostgreSQL schema, migrations, seed data)
├── docker-compose.yml   # Local dev infrastructure (PostgreSQL, SeaweedFS/MinIO, DuckDB volumes)
├── doppler.yaml         # Doppler secret management project binding
└── justfile             # Monorepo command runner (setup, dev, test, db, check)
```

### Scoped Subdirectory Instructions
When working within specific subdirectories, consult the dedicated instructions:
- **API Middleware**: [`apps/api/GEMINI.md`](./apps/api/GEMINI.md)
- **Frontend Application**: [`apps/web/GEMINI.md`](./apps/web/GEMINI.md)
- **Data Pipeline & Lakehouse**: [`packages/data-pipeline/GEMINI.md`](./packages/data-pipeline/GEMINI.md)
- **Database & Drizzle ORM**: [`packages/db/GEMINI.md`](./packages/db/GEMINI.md)

---

## 2. Environment & Infrastructure Matrix

| Layer | Local Development | Production Environment |
|---|---|---|
| **Secret Management** | Doppler CLI (`doppler run`) | Doppler Integrations / Cloud Dashboard |
| **Frontend** | Bun + Vite HMR (`localhost:3000`) | **Vercel** (`vercel.json`) |
| **API Middleware** | Docker / Uvicorn reload (`localhost:8000`) | **Render** (`render.yaml`, Docker runtime) |
| **Data Lakehouse** | Local DuckDB (`dev.duckdb`) | **MotherDuck** (`md:peleton_db?token=...`) |
| **Object Storage (Bronze)** | SeaweedFS / MinIO S3 API (`localhost:9000`) | **Cloudflare R2** (`peleton-r2-bucket`) |
| **Operational Database** | Docker PostgreSQL 16 Alpine (`localhost:5432`)| Managed PostgreSQL (Neon / Supabase) |
| **Orchestrator** | Dagster Webserver (`localhost:3001`) | Dagster Cloud / Containerized worker |

---

## 3. The Golden Path: Lakehouse to Frontend Flow

The core architecture exposes analytical lakehouse data to the end user via a strict 4-step pipeline:

```
[External Open Data APIs]
(MET Frost, Vegvesen Trafikkdata, Datex II)
            │
            ▼
┌───────────────────────────────┐
│ 1. Dagster Data Pipeline      │
│    - Bronze: Raw JSON in R2   │
│    - Silver: DuckDB/MotherDuck│
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 2. DuckDB / MotherDuck        │
│    - Parquet / Columnar Tables │
│    - Read-Only Lakehouse Query│
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 3. FastAPI Middleware         │
│    - Parameterized SQL Queries │
│    - Polars DataFrame (.pl()) │
│    - Pydantic v2 Serialization│
│    - /api/v1 REST Endpoints   │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 4. TanStack Frontend          │
│    - TanStack Query v5 Hooks  │
│    - TanStack Router Loaders  │
│    - React 19 UI & Visuals    │
└───────────────────────────────┘
```

1. **Ingest & Transform**: Dagster fetches external data, archives raw JSON payloads to Cloudflare R2 (Bronze), cleans and deduplicates records, and loads them into DuckDB/MotherDuck tables (Silver).
2. **Lakehouse Storage**: DuckDB / MotherDuck stores analytical data in columnar format, optimized for analytical aggregations (weather, traffic, travel times).
3. **API Serving Layer**: FastAPI connects to DuckDB / MotherDuck in read-only mode via `get_duckdb_connection`. Endpoints query with parameterized SQL, extract results as high-performance Polars DataFrames (`.pl()`), validate through Pydantic v2 schemas, and serve via `/api/v1/...`.
4. **Frontend Consumption**: TanStack Router routes use `queryClient.ensureQueryData()` in route loaders with centralized `queryOptions` from TanStack Query v5, providing instant navigation, serverless prefetching, and typed state.

---

## 4. Testing Framework Enforcement

Testing is mandatory for every service and package. No code should be merged or deployed without automated test coverage.

### Component Test Runners
- **`apps/api`**: `pytest` + `pytest-asyncio` + `httpx.TestClient`.
  - Analytical endpoints must test against in-memory DuckDB (`duckdb.connect(":memory:")`) using FastAPI dependency overrides.
  - Run via: `cd apps/api && uv run pytest`
- **`packages/data-pipeline`**: `pytest` + Dagster testing utilities.
  - Assets tested via `dagster.materialize()` or direct invocation with mock S3 and HTTP clients.
  - Run via: `cd packages/data-pipeline && uv run pytest`
- **`apps/web`**: `bun test` / Vitest + `@testing-library/react`.
  - Tests route loaders, custom hooks, and UI components wrapped in `QueryClientProvider`.
  - Run via: `cd apps/web && bun test`
- **`packages/db`**: `bun test`.
  - Validates Drizzle schema definitions, relations, and migration consistency.
  - Run via: `cd packages/db && bun test`

### Centralized Justfile Recipes
Always verify using the monorepo test commands:
```bash
just test           # Run all test suites across all components
just test-api       # Run FastAPI pytest suite
just test-pipeline  # Run Dagster pytest suite
just test-web       # Run TanStack web test suite
just test-db        # Run Drizzle database schema tests
just check          # Run linters (oxlint, ruff) and TypeScript typechecks
```

---

## 5. Secret Management & Environment Standards

- **Doppler is Mandatory**: Secrets are NEVER stored in plain-text `.env` files in git repositories.
- Use `doppler run -- <command>` or standard `just` commands.
- Local development fallback variables are specified in `docker-compose.yml` with sensible dev defaults.
- Key secrets managed by Doppler:
  - `DATABASE_URL`: PostgreSQL connection string (supports Neon pooling and local Postgres).
  - `MOTHERDUCK_TOKEN`: MotherDuck cloud token (if omitted, falls back to `LOCAL_DUCKDB_PATH`).
  - `LOCAL_DUCKDB_PATH`: Path to local DuckDB file (defaults to `/app/data/dev.duckdb` in Docker).
  - `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`: Cloudflare R2 / SeaweedFS S3 credentials.
  - `FROST_CLIENT_ID`, `FROST_CLIENT_SECRET`: MET Norway Frost API credentials.
  - `VEGVESEN_USERNAME`, `VEGVESEN_PASSWORD`: Statens Vegvesen Datex credentials.

---

## 6. AI Coding Rules & Architectural Invariants

1. **Idiomatic Framework Usage**:
   - Use FastAPI dependency injection (`Depends`) for both PostgreSQL sessions and DuckDB connections.
   - Use Polars (`.pl()`) for DuckDB data transformation before Pydantic response modeling.
   - Use TanStack Query's `queryOptions` pattern for all data fetching in the web app.
   - Use Dagster Software-Defined Assets (`@asset`) with explicit dependencies, never unstructured scripts.
   - Use Drizzle ORM type inference (`$inferSelect`, `$inferInsert`) in the database package.
2. **Strict Type Safety**:
   - No `any` in TypeScript.
   - Pydantic v2 schemas for all API request parameters, query filters, and response bodies.
   - Python type annotations on all function signatures.
3. **Lakehouse Isolation**:
   - DuckDB connections in FastAPI MUST be opened with `read_only=True` to prevent lock contention with Dagster ingestion pipelines.
   - Transactional data (users, companies, authentication) belongs in PostgreSQL.
   - Analytical time-series, telemetry, and parquet lakehouse data belongs in DuckDB / MotherDuck.
4. **Zero-Secret Leaks**:
   - Never log API keys, tokens, or plaintext connection strings.
   - Never commit `.env`, `.env.local`, or secret values.
