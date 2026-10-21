import { defineConfig } from "drizzle-kit";

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("❌ DATABASE_URL is missing in the environment variables!");
}

export default defineConfig({
  // Use a wildcard to match all schema files inside src/schema/
  schema: "./src/schema/index.ts",
  out: "./migrations",
  dialect: "postgresql",
  dbCredentials: {
    url: databaseUrl,
  },
});