const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface StravaStatus {
  connected: boolean;
  athlete_id: string | null;
  scopes: string | null;
  connected_at: string | null;
}

export interface StravaConnectResult {
  authorization_url: string;
}

export interface StravaDisconnectResult {
  connected: boolean;
  provider_revoked: boolean;
}

export async function fetchStravaStatus(baseUrl = API_URL): Promise<StravaStatus> {
  const res = await fetch(`${baseUrl}/api/v1/strava/status`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to load Strava status: ${res.statusText} (${res.status})`);
  }
  return res.json();
}

export async function connectStrava(baseUrl = API_URL): Promise<StravaConnectResult> {
  const res = await fetch(`${baseUrl}/api/v1/strava/connect`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to initiate Strava connect: ${res.statusText} (${res.status})`);
  }
  return res.json();
}

export async function disconnectStrava(baseUrl = API_URL): Promise<StravaDisconnectResult> {
  const res = await fetch(`${baseUrl}/api/v1/strava/disconnect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to disconnect Strava: ${res.statusText} (${res.status})`);
  }
  return res.json();
}
