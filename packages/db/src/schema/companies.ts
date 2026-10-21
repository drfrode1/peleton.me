import { boolean, pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";

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