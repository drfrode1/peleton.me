FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency and metadata files first (including README.md)
COPY pyproject.toml uv.lock* README.md ./

# Copy the package source directory
COPY peleton_api ./peleton_api

# Install dependencies AND the local package system-wide
RUN uv pip install --system -e .

# Copy the rest of the project files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "peleton_api.main:app", "--host", "0.0.0.0", "--port", "8000"]