import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error(
    "❌ DATABASE_URL is missing in the environment variables! Ensure it is supplied via Doppler or Docker Compose."
  );
}

// Disable prepared statements for compatibility across local Postgres and Neon connection pooling
const client = postgres(connectionString, { prepare: false });

export const db = drizzle(client, { schema });
export * from "./schema";