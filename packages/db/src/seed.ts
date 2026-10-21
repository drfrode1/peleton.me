import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error("❌ DATABASE_URL environment variable is required for seeding.");
}

// Disable prefetch for migration and seed scripts
const client = postgres(connectionString, { max: 1 });
const db = drizzle(client, { schema });

async function seed() {
  console.log("🌱 Starting database seed...");

  // 1. Clean existing records (delete users first to respect foreign key constraints)
  console.log("🧹 Clearing existing data...");
  await db.delete(schema.users);
  await db.delete(schema.companies);

  // 2. Insert test companies (matching Brønnøysundregistrene structure)
  console.log("🏢 Seeding companies...");
  const insertedCompanies = await db
    .insert(schema.companies)
    .values([
      {
        orgNumber: "923456789",
        name: "Equinor ASA",
        postalCode: "4035",
        companyType: "AS",
        companyCategory: "Energi og utvinning",
        showNameConsent: true,
      },
      {
        orgNumber: "987654321",
        name: "Peleton Commute AS",
        postalCode: "4330",
        companyType: "AS",
        companyCategory: "Programvarevareutvikling",
        showNameConsent: true,
      },
    ])
    .returning();

  const eqnrCompany = insertedCompanies[0];
  const peletonCompany = insertedCompanies[1];

  // 3. Insert test users linked to companies
  console.log("👤 Seeding users...");
  await db.insert(schema.users).values([
    {
      email: "test.user@peleton.me",
      name: "Test Rider",
      companyEmail: "test.user@equinor.com",
      verifiedCompany: true,
      companyId: eqnrCompany.id,
    },
    {
      email: "admin@peleton.me",
      name: "Peleton Admin",
      companyEmail: "admin@peleton.me",
      verifiedCompany: true,
      companyId: peletonCompany.id,
    },
  ]);

  console.log("✅ Database seeding completed successfully!");
}

seed()
  .catch((err) => {
    console.error("❌ Seeding failed:", err);
    process.exit(1);
  })
  .finally(async () => {
    await client.end();
  });