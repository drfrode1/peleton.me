# @peleton/web

TanStack React 19 web application for **peleton.me**.

## Architecture & Responsibilities
- **Frontend Stack**: Built with React 19, TanStack Router (file-based routing), TanStack Query v5, Tailwind CSS v4, and Vite (running on Bun).
- **Lakehouse Consumption**: Consumes the FastAPI middleware analytics endpoints via type-safe API clients and the centralized `queryOptions` pattern with route loader prefetching.
- **Deployment**: Deployed on **Vercel** (`vercel.json`).

## Getting Started
```bash
# Install dependencies
bun install

# Start Vite dev server (localhost:3000)
bun run dev

# Run TypeScript typechecks
bun run typecheck

# Run unit tests
bun test

# Build for production
bun run build
```

For full routing, caching, and UI conventions, see [`GEMINI.md`](./GEMINI.md).
