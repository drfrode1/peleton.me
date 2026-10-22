# apps/web — TanStack Frontend Guidelines

This application is the user-facing web interface for **peleton.me**, providing interactive dashboards, active commuting metrics, and open data visualization. It is built with **React 19**, **TanStack Router**, **TanStack Query v5**, **Tailwind CSS v4**, and **Vite (Bun)**, deployed to **Vercel**.

---

## 1. Core Architectural Pillars

### 1.1 TanStack Router (File-Based Routing)
- **Directory**: `src/routes/`
- **Auto-generation**: Route tree is generated automatically into `src/routeTree.gen.ts` by `@tanstack/router-plugin/vite`. **NEVER edit `routeTree.gen.ts` directly**.
- **Root Layout**: `src/routes/__root.tsx` defines the persistent shell (navigation, footer, dark theme container, and outlet).
- **Route Definitions**: Use `createFileRoute('/path')({...})`.

### 1.2 TanStack Query v5 (`queryOptions` Factory Pattern)
All API data fetching must follow the centralized `queryOptions` factory pattern. This allows sharing query keys, fetch logic, and cache configurations across route loaders and React components without code duplication.

```typescript
// src/lib/queries/weather.ts
import { queryOptions } from '@tanstack/react-query';
import { fetchWeatherObservations, WeatherFilters } from '../api/weather';

export const weatherQueryOptions = (filters: WeatherFilters = {}) =>
  queryOptions({
    queryKey: ['weather', filters],
    queryFn: () => fetchWeatherObservations(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
```

### 1.3 Route Loader Prefetching
Preload data before the route renders using `ensureQueryData()` inside route loaders. This ensures instant page transitions without layout shifts:

```typescript
// src/routes/dashboard.tsx
import { createFileRoute } from '@tanstack/react-router';
import { useSuspenseQuery } from '@tanstack/react-query';
import { weatherQueryOptions } from '../lib/queries/weather';

export const Route = createFileRoute('/dashboard')({
  loader: ({ context: { queryClient } }) =>
    queryClient.ensureQueryData(weatherQueryOptions({ days: 7 })),
  component: DashboardPage,
});

function DashboardPage() {
  const { data } = useSuspenseQuery(weatherQueryOptions({ days: 7 }));
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Weather Observations</h1>
      <p>Loaded {data.count} records from lakehouse.</p>
    </div>
  );
}
```

---

## 2. API Communication with FastAPI Middleware

- **Base URL**: Configured via `import.meta.env.VITE_API_URL` (defaults to `http://localhost:8000` locally, and the Render backend URL on Vercel).
- **Typed API Clients**: Place client functions under `src/lib/api/`:
  - Do not call raw `fetch()` directly in UI components.
  - Return typed responses that mirror FastAPI Pydantic response models:

```typescript
// src/lib/api/weather.ts
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

export async function fetchWeatherObservations(filters: WeatherFilters = {}): Promise<WeatherResponse> {
  const params = new URLSearchParams();
  if (filters.location) params.set('location', filters.location);
  if (filters.days) params.set('days', filters.days.toString());
  if (filters.limit) params.set('limit', filters.limit.toString());

  const res = await fetch(`${API_URL}/api/v1/weather/?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch weather: ${res.statusText} (${res.status})`);
  }
  return res.json();
}
```

---

## 3. Styling & UI Design Standards

- **Tailwind CSS v4**: Uses the new CSS-first Vite plugin `@tailwindcss/vite` (`@import "tailwindcss";` in `src/index.css`).
- **Design Tokens**:
  - Backgrounds: Dark aesthetic using `bg-slate-950` / `bg-slate-900`.
  - Brand Accent: Emerald / Mint tones (`text-emerald-400`, `bg-emerald-500`).
  - Cards & Borders: Semi-transparent borders with backdrop blurs (`border-slate-800`, `bg-slate-900/50 backdrop-blur-md`).
- **Icons**: Always use `lucide-react`.
- **Animations**: Use `motion` for micro-interactions and transitions.

---

## 4. Directory Layout

```
apps/web/
├── public/                 # Static assets (favicons, svg icons)
├── src/
│   ├── assets/             # Bundled static images
│   ├── components/         # Reusable UI widgets and layout blocks
│   ├── lib/
│   │   ├── api/            # Typed fetch clients for FastAPI endpoints
│   │   └── queries/        # TanStack queryOptions definitions
│   ├── routes/             # TanStack Router file-based route definitions
│   │   ├── __root.tsx      # App shell, nav header, footer, router context
│   │   └── index.tsx       # Landing page route
│   ├── routeTree.gen.ts    # Auto-generated by TanStack router plugin
│   ├── index.css           # Tailwind v4 theme and global styles
│   └── main.tsx            # App bootstrap (QueryClient, RouterProvider)
├── package.json            # Bun package definition
├── tsconfig.json           # Strict TypeScript configuration
├── vercel.json             # Vercel SPA routing rewrites
└── vite.config.ts          # Vite configuration with router, react, and tailwind plugins
```

---

## 5. Testing Framework & Standards

- **Runner**: `bun test` or Vitest.
- **Command**: `cd apps/web && bun test`
- **Testing Approach**:
  - Test pure API client functions and query option builders.
  - Test custom hooks and components wrapped in `QueryClientProvider` with a fresh `QueryClient({ defaultOptions: { queries: { retry: false } } })`.
  - Avoid snapshot testing of full DOM trees; prefer testing user interactions and accessible roles.

---

## 6. Vercel Production Deployment

- **Routing**: `vercel.json` contains SPA URL rewriting to route all client requests to `/index.html`:
  ```json
  {
    "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
  }
  ```
- **Build Command**: `bun run build` (`tsc -b && vite build`).
- **Environment Variables**: Configure `VITE_API_URL` in the Vercel Project Settings pointing to the deployed Render FastAPI middleware.
