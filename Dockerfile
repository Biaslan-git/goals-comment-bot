# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies to .venv
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    mkdir -p /data && \
    chown -R botuser:botuser /app /data

# Copy virtual environment from builder
COPY --from=builder --chown=botuser:botuser /app/.venv /app/.venv

# Copy application code
COPY --chown=botuser:botuser *.py ./

# Switch to non-root user
USER botuser

# Set Python path to use venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run the multi-bot manager directly via Python (not uv)
CMD ["python", "main_multi.py"]
