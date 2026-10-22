import { describe, expect, it } from "bun:test";
import { getTableColumns } from "drizzle-orm";
import { companies, stravaConnections, users } from "../src/schema";

describe("Database Schemas", () => {
  it("should define company table with expected columns", () => {
    const columns = getTableColumns(companies);
    expect(columns).toBeDefined();
    expect(columns.id).toBeDefined();
    expect(columns.orgNumber).toBeDefined();
    expect(columns.name).toBeDefined();
    expect(columns.showNameConsent).toBeDefined();
  });

  it("should define user table with expected columns", () => {
    const columns = getTableColumns(users);
    expect(columns).toBeDefined();
    expect(columns.id).toBeDefined();
    expect(columns.email).toBeDefined();
    expect(columns.companyId).toBeDefined();
  });

  it("should define strava_connection table with foreign key to users", () => {
    const columns = getTableColumns(stravaConnections);
    expect(columns).toBeDefined();
    expect(columns.id).toBeDefined();
    expect(columns.userId).toBeDefined();
    expect(columns.athleteId).toBeDefined();
    expect(columns.accessTokenCiphertext).toBeDefined();
  });
});
