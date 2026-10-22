import { describe, expect, it } from 'bun:test';
import { fetchStravaStatus, connectStrava, disconnectStrava } from './strava';

describe('Strava API Client', () => {
  it('should request status and parse response', async () => {
    const originalFetch = globalThis.fetch;
    (globalThis as unknown as { fetch: unknown }).fetch = async () =>
      new Response(
        JSON.stringify({
          connected: true,
          athlete_id: '998877',
          scopes: 'read,activity:read_all',
          connected_at: '2026-10-22T12:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );

    try {
      const status = await fetchStravaStatus('http://localhost:8000');
      expect(status.connected).toBe(true);
      expect(status.athlete_id).toBe('998877');
      expect(status.scopes).toBe('read,activity:read_all');
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  it('should call connect and return authorizationUrl', async () => {
    const originalFetch = globalThis.fetch;
    (globalThis as unknown as { fetch: unknown }).fetch = async () =>
      new Response(
        JSON.stringify({
          authorization_url: 'https://www.strava.com/oauth/authorize?test=1',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );

    try {
      const result = await connectStrava('http://localhost:8000');
      expect(result.authorization_url).toContain('https://www.strava.com/oauth/authorize');
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  it('should call disconnect with POST and return revocation status', async () => {
    const originalFetch = globalThis.fetch;
    (globalThis as unknown as { fetch: unknown }).fetch = async (_url: unknown, init?: RequestInit) => {
      expect(init?.method).toBe('POST');
      return new Response(
        JSON.stringify({
          connected: false,
          provider_revoked: true,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    };

    try {
      const result = await disconnectStrava('http://localhost:8000');
      expect(result.connected).toBe(false);
      expect(result.provider_revoked).toBe(true);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});
