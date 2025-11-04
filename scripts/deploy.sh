#!/bin/bash
# Grace Production Deployment Script

set -e

echo "============================================================"
echo "Grace Production Deployment"
echo "============================================================"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Error: docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Error: docker-compose required"; exit 1; }

# Environment setup
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env with production values!"
    echo "   - Set GRACE_JWT_SECRET"
    echo "   - Set DATABASE_URL"
    echo "   - Set ALLOWED_ORIGINS"
    exit 1
fi

# Build images
echo "[1/5] Building Docker images..."
docker-compose build

# Initialize database
echo "[2/5] Initializing database..."
docker-compose run --rm backend python reset_db.py

# Seed initial data
echo "[3/5] Seeding default configuration..."
# Trusted sources will auto-initialize on startup
echo "   Trusted sources: Will initialize on first run"

# Run tests
echo "[4/5] Running smoke tests..."
docker-compose run --rm backend pytest tests/test_chat.py -v

# Start services
echo "[5/5] Starting Grace..."
docker-compose up -d

echo ""
echo "============================================================"
echo "Deployment Complete!"
echo "============================================================"
echo ""
echo "Grace is now running at:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Docs:     http://localhost:8000/docs"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop:      docker-compose down"
echo ""
