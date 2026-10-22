default:
    @just --list

# Verify all required developer tools are installed
check-tools:
    @echo "🔍 Checking developer environment..."
    @command -v bun >/dev/null 2>&1 || (echo "❌ Missing 'bun'. Install via: brew install bun OR curl -fsSL https://bun.sh/install | bash" && exit 1)
    @command -v uv >/dev/null 2>&1 || (echo "❌ Missing 'uv'. Install via: brew install uv OR curl -LsSf https://astral.sh/uv/install.sh | sh" && exit 1)
    @command -v doppler >/dev/null 2>&1 || (echo "❌ Missing 'doppler'. Install via: brew install dopplerhq/cli/doppler" && exit 1)
    @command -v docker >/dev/null 2>&1 || (echo "❌ Missing 'docker'. Install Docker Desktop or Colima." && exit 1)
    @command -v vercel >/dev/null 2>&1 || (echo "❌ Missing 'vercel'. Install via: bun add -g vercel" && exit 1)
    @echo "✅ All required CLI tools are installed!"

# Verify Doppler secrets (or issue warning if local fallback will be used)
check-secrets:
    @echo "🔒 Checking Doppler configuration..."
    @doppler secrets get DATABASE_URL >/dev/null 2>&1 || (echo "⚠️  Warning: 'DATABASE_URL' missing in Doppler (will default to local Postgres in Docker)")
    @doppler secrets get MOTHERDUCK_TOKEN >/dev/null 2>&1 || (echo "⚠️  Warning: 'MOTHERDUCK_TOKEN' missing in Doppler (will default to local DuckDB)")
    @echo "✅ Secrets check passed!"

# Full onboarding setup: verifies tools, installs project dependencies across monorepo, and sets up Doppler
setup: check-tools
    @echo "📦 Installing root and workspace dependencies..."
    bun install
    @echo "🐍 Syncing Python virtual environments with uv..."
    cd apps/api && uv sync
    cd packages/data-pipeline && uv sync
    @just setup-doppler
    @echo "🚀 Setup complete! Run 'just dev' to start all services."

# Setup Doppler CLI authorization locally once
setup-doppler:
    @if ! doppler me > /dev/null 2>&1; then \
        echo "Not logged into Doppler. Starting login..."; \
        doppler login; \
    else \
        echo "Already logged into Doppler."; \
    fi
    @doppler setup

# Run web dev natively on host with secrets injected straight into memory
dev-web:
    doppler run -- sh -c "cd apps/web && bun run dev"

# Run full Docker Compose environment (web: 3000, api: 8000, data-pipeline: 3001, postgres: 5432, minio: 9000/9001)
dev: check-secrets
    doppler run -- docker compose up --build

# Stop all running containers and remove networks
down:
    docker compose down

# Clean stop including volume wipe (resets local Postgres & MinIO data)
down-clean:
    docker compose down -v

# ------------------------------------------------------------------------------
# DATABASE MANAGEMENT (Drizzle ORM & Postgres)
# ------------------------------------------------------------------------------

# Push Drizzle schema directly to active PostgreSQL database
db-push:
    doppler run -- bun --filter @peleton/db db:push

# Generate SQL migration files from Drizzle schema
db-generate:
    doppler run -- bun --filter @peleton/db db:generate

# Execute pending SQL migrations
db-migrate:
    doppler run -- bun --filter @peleton/db db:migrate

# Open Drizzle Studio GUI to inspect/edit database records
db-studio:
    doppler run -- bun --filter @peleton/db db:studio

# Seed local database with initial mock data
db-seed:
    doppler run -- bun --filter @peleton/db db:seed

# ------------------------------------------------------------------------------
# TESTING & QUALITY CHECKS
# ------------------------------------------------------------------------------

# Run automated tests across all services and packages
test: test-api test-pipeline test-web test-db
    @echo "✅ All test suites passed!"

# Run FastAPI backend tests
test-api:
    @echo "🧪 Running API tests (pytest)..."
    cd apps/api && uv run pytest

# Run Dagster data pipeline tests
test-pipeline:
    @echo "🧪 Running Data Pipeline tests (pytest)..."
    cd packages/data-pipeline && uv run pytest

# Run Web frontend tests
test-web:
    @echo "🧪 Running Web frontend tests..."
    cd apps/web && bun test

# Run Database schema tests
test-db:
    @echo "🧪 Running Database tests..."
    cd packages/db && bun test

# Run typechecks and linter checks across all services
check:
    @echo "🧹 Checking TypeScript types for web & db..."
    doppler run -- sh -c "cd apps/web && bun run typecheck"
    doppler run -- bun --filter @peleton/db typecheck
    @echo "🐍 Checking Python code for API with ruff..."
    cd apps/api && uv run ruff check .
    @echo "📊 Checking Python code for Data Pipeline with ruff..."
    cd packages/data-pipeline && uv run ruff check .
    @echo "✅ All checks passed!"

# Production Vercel Deploy
deploy-prod:
    cd apps/web && bunx vercel --prod