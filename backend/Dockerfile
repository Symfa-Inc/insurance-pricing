FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Build from the repository root to use the workspace lockfile.
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml
RUN uv sync --locked --no-dev --no-install-workspace

# Copy application code
COPY backend/src/ backend/src/
COPY backend/models/ backend/models/

# Install the project itself
RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "insurance_pricing.main:app", "--host", "0.0.0.0", "--port", "8000"]
