# packages/db — Drizzle ORM & Database Guidelines

This package manages the **PostgreSQL** operational database for **peleton.me** using **Drizzle ORM** with **Bun**. It defines schemas, migrations, relations, and seed scripts for transactional data (users, companies, Strava OAuth connections).

---

## 1. Schema Design & Type Inference

All PostgreSQL schemas are written in TypeScript under `src/schema/` and re-exported through `src/schema/index.ts`.

### 1.1 Invariant Rules for Tables
1. **Always export type inferences**: Export both `$inferSelect` and `$inferInsert` types alongside table definitions:
   ```typescript
   import { pgTable, serial, text, timestamp, boolean } from "drizzle-orm/pg-core";

   export const companies = pgTable("company", {
     id: serial("id").primaryKey(),
     orgNumber: text("org_number").notNull().unique(),
     name: text("name").notNull(),
     postalCode: text("postal_code"),
     companyType: text("company_type"),
     companyCategory: text("company_category"),
     showNameConsent: boolean("show_name_consent").default(false).notNull(),
     createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
     updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
   });

   export type Company = typeof companies.$inferSelect;
   export type NewCompany = typeof companies.$inferInsert;
   ```
2. **Explicit Foreign Key Deletions**: Declare cascade/set-null policies explicitly (e.g. `onDelete: 'cascade'`).
3. **Timezones**: Always store timestamps with timezone (`{ withTimezone: true }`).

### 1.2 Connection Pooling & Neon Compatibility
In `src/index.ts`, prepared statements are disabled (`prepare: false`) to ensure compatibility with serverless connection pooling (Neon, Supabase PgBouncer, and local Docker Postgres):
```typescript
const client = postgres(connectionString, { prepare: false });
export const db = drizzle(client, { schema });
```

---

## 2. Migration & Development Workflow

All database operations are orchestrated via `just` commands with Doppler secret injection:

| Command | Action | Underlying Tool |
|---|---|---|
| `just db-generate` | Generate SQL migration files from schema diffs | `drizzle-kit generate` |
| `just db-migrate` | Apply pending SQL migrations to active database | `bun run src/migrate.ts` |
| `just db-push` | Push schema changes directly (dev prototyping) | `drizzle-kit push` |
| `just db-seed` | Seed database with initial mock users and companies | `bun run src/seed.ts` |
| `just db-studio` | Open Drizzle Studio visual editor | `drizzle-kit studio` |

---

## 3. Directory Layout

```
packages/db/
├── src/
│   ├── schema/
│   │   ├── companies.ts     # Company & employer schemas
│   │   ├── users.ts         # User profiles & settings
│   │   ├── strava.ts        # Strava OAuth encrypted credentials
│   │   └── index.ts         # Aggregated schema re-exports
│   ├── index.ts             # Drizzle client instance & db export
│   ├── migrate.ts           # Migration runner script
│   └── seed.ts              # Database seeding script
├── drizzle.config.ts        # Drizzle Kit configuration
├── package.json             # Package scripts & dependencies
└── tsconfig.json            # TypeScript configuration
```

---

## 4. Testing Framework & Standards

- **Runner**: `bun test`
- **Command**: `cd packages/db && bun test`
- **Scope**:
  - Verify all schema definitions and column types are properly declared.
  - Verify relations and foreign key references resolve without circular dependency issues.
  - Test migration and seed utility scripts in CI.
