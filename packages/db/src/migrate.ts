import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";

const connectionString = process.env.DATABASE_URL;

async function runMigrations() {
  if (!connectionString) {
    throw new Error("❌ DATABASE_URL missing in environment variables");
  }

  console.log("⏳ Running database migrations...");

  // TypeScript vet nå at connectionString garantert er en string
  const sql = postgres(connectionString, { max: 1 });
  const db = drizzle(sql);

  await migrate(db, { migrationsFolder: "./migrations" });

  console.log("✅ Migrations completed successfully!");
  await sql.end();
}

runMigrations().catch((err) => {
  console.error("❌ Migration failed:", err);
  process.exit(1);
});