# @peleton/db

Drizzle ORM schema, migrations, and seed scripts for PostgreSQL transactional data.

## Architecture & Responsibilities
- **ORM & Type Inferences**: Powered by Drizzle ORM and Postgres.js with Bun.
- **Transactional State**: Manages users, company entities, and Strava OAuth credentials.
- **Connection Compatibility**: Configured with `prepare: false` for compatibility with Neon serverless connection pooling and local Docker Postgres.

## Getting Started
```bash
# Push schema changes directly (dev)
just db-push

# Generate SQL migrations
just db-generate

# Run pending SQL migrations
just db-migrate

# Seed database with initial data
just db-seed

# Run schema unit tests
bun test

# Run TypeScript typechecks
bun run typecheck
```

For schema rules and conventions, see [`GEMINI.md`](./GEMINI.md).
