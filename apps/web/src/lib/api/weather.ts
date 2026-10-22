const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface WeatherObservation {
  location_id: string;
  reference_time: string;
  element_id: string;
  value: number;
  unit: string;
  ingested_at: string;
}

export interface WeatherResponse {
  count: number;
  filters: {
    location?: string;
    days?: number;
    limit?: number;
  };
  data: WeatherObservation[];
}

export interface WeatherFilters {
  location?: string;
  days?: number;
  limit?: number;
}

export function buildWeatherQueryUrl(filters: WeatherFilters = {}, baseUrl = API_URL): string {
  const params = new URLSearchParams();
  if (filters.location) params.set('location', filters.location);
  if (filters.days) params.set('days', filters.days.toString());
  if (filters.limit) params.set('limit', filters.limit.toString());

  const queryString = params.toString();
  return `${baseUrl}/api/v1/weather/${queryString ? `?${queryString}` : ''}`;
}

export async function fetchWeatherObservations(
  filters: WeatherFilters = {},
  baseUrl = API_URL
): Promise<WeatherResponse> {
  const url = buildWeatherQueryUrl(filters, baseUrl);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch weather: ${res.statusText} (${res.status})`);
  }
  return res.json();
}
