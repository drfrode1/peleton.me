# peleton-api

FastAPI backend and analytics middleware for **peleton.me**.

## Architecture & Responsibilities
- **Middleware Role**: Bridges transactional application data (PostgreSQL) and analytical lakehouse data (DuckDB/MotherDuck) to the TanStack frontend.
- **Analytics Queries**: Leverages DuckDB parameterized SQL queries and exports zero-copy Polars DataFrames (`.pl()`) for fast serialization.
- **Deployment**: Runs on **Render** as a Docker container (`render.yaml`).

## Getting Started
```bash
# Sync virtual environment with uv
uv sync

# Run development server
uv run uvicorn peleton_api.main:app --reload --port 8000

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

For complete architectural patterns and AI coding rules, see [`GEMINI.md`](./GEMINI.md).
