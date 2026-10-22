FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install curl for container healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency and metadata files first
COPY pyproject.toml uv.lock* README.md ./

# Copy package source directory
COPY peleton_api ./peleton_api

# Install production package system-wide
RUN uv pip install --system .

# Copy remaining project files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "peleton_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
