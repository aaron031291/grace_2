# Grace AI System - Complete Docker Image
# Includes: 9 Domain Kernels, 311+ APIs, 100+ Autonomous Subsystems

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY .env.example /app/.env

# Create necessary directories
RUN mkdir -p /app/databases /app/logs /app/ml_artifacts /app/storage /app/reports

# Expose backend port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Grace backend with all subsystems
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
