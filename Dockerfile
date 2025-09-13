FROM python:3.10-slim-bookworm

# Base env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps:
# - curl: install uv
# - awscli: S3 sync in pipeline (optional at runtime but included as requested)
# - ca-certificates: TLS for Mongo/HTTPS
# - libgomp1: required by scikit-learn wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    awscli \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern Python package/dependency manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy only project metadata first for better Docker layer caching
COPY pyproject.toml uv.lock README.md /app/

# Install dependencies into a project-local virtual environment
RUN uv sync --frozen --no-install-project

# Ensure the venv is used for subsequent commands and at runtime
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

# Copy the rest of the application code
COPY . /app

# Create writable dirs used at runtime
RUN mkdir -p /app/prediction_output /app/Artifacts /app/logs \
    && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

# Default app port (overridable at runtime)
ENV PORT=8000

# Document common ports
EXPOSE 8000 8080

# Run with a configurable port
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]