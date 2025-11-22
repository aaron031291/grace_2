# Grace Backend Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r grace && useradd -r -g grace grace

# Set work directory
WORKDIR /app

# Install Python dependencies
FROM base as dependencies

COPY pyproject.toml ./
COPY requirements*.txt ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install uvicorn[standard]

# Production stage
FROM dependencies as production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/databases /app/logs /app/storage /app/ml_artifacts && \
    chown -R grace:grace /app

# Switch to non-root user
USER grace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default environment variables
ENV GRACE_PORT=8000 \
    GRACE_ENV=production \
    PYTHONPATH=/app

# Start the application
CMD ["python", "server.py"]