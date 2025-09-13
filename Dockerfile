FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies (curl for uv installer, awscli for runtime)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl awscli \
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

# Default command
EXPOSE 8000
CMD ["python", "app.py"]