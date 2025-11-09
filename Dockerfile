# Grace AI - Backend Dockerfile
# Multi-stage build for optimized production image

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.13-slim

LABEL maintainer="Grace AI <grace@example.com>"
LABEL description="Grace - Autonomous AI Learning System with Amp API Integration"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 grace && \
    chown -R grace:grace /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/grace/.local

# Copy application code
COPY --chown=grace:grace backend/ ./backend/
COPY --chown=grace:grace alembic/ ./alembic/
COPY --chown=grace:grace alembic.ini .
COPY --chown=grace:grace .env.example .

# Create required directories
RUN mkdir -p \
    logs \
    storage/provenance \
    storage/web_knowledge \
    storage/exports \
    sandbox/knowledge_tests \
    sandbox/api_tests \
    config \
    databases && \
    chown -R grace:grace logs storage sandbox config databases

# Switch to non-root user
USER grace

# Set Python path
ENV PATH=/home/grace/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
