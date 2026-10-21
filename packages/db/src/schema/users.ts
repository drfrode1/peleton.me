import { boolean, integer, pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";
import { companies } from "./companies";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  authUserId: text("auth_user_id").unique(),
  email: text("email").notNull().unique(),
  name: text("name"),
  companyEmail: text("company_email"),
  verifiedCompany: boolean("verified_company").default(false).notNull(),
  companyId: integer("company_id").references(() => companies.id, { onDelete: "set null" }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});