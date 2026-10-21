import { integer, pgTable, serial, text, timestamp, varchar } from 'drizzle-orm/pg-core';
import { users } from './users';

export const stravaConnections = pgTable('strava_connection', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().unique().references(() => users.id, { onDelete: 'cascade' }),
  athleteId: text('athlete_id').notNull().unique(),
  accessTokenCiphertext: text('access_token_ciphertext').notNull(),
  accessTokenIv: varchar('access_token_iv', { length: 24 }).notNull(),
  accessTokenTag: varchar('access_token_tag', { length: 24 }).notNull(),
  refreshTokenCiphertext: text('refresh_token_ciphertext').notNull(),
  refreshTokenIv: varchar('refresh_token_iv', { length: 24 }).notNull(),
  refreshTokenTag: varchar('refresh_token_tag', { length: 24 }).notNull(),
  scopes: text('scopes').notNull(),
  tokenExpiresAt: timestamp('token_expires_at').notNull(),
  connectedAt: timestamp('connected_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export type StravaConnection = typeof stravaConnections.$inferSelect;
export type NewStravaConnection = typeof stravaConnections.$inferInsert;