# Grace Deployment Guide

## Quick Start (Development)

```bash
# Set environment
export GRACE_PORT=8000
export OFFLINE_MODE=false
export LOG_LEVEL=INFO

# Start Grace
python serve.py
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Version: http://localhost:8000/version

---

## Production Deployment

### Environment Variables

```bash
# Core Configuration
GRACE_PORT=8000                    # API port
GRACE_ENV=production               # Environment (dev/staging/prod)
LOG_LEVEL=WARNING                  # Logging level

# Feature Flags
OFFLINE_MODE=false                 # Disable external calls
DRY_RUN=false                      # Boot only, no services
CI=false                           # CI mode detection

# Database
GRACE_DB_PATH=databases/grace.db   # Main database path

# API Gateway
RATE_LIMIT_PER_MIN=60             # Rate limit
RATE_LIMIT_BURST=10               # Burst size

# Observability
ENABLE_GOLDEN_SIGNALS=true        # Enable monitoring
ENABLE_METRICS_EXPORT=true        # Export metrics
```

### Docker Deployment

```bash
# Build image
docker build -t grace:2.2.0 .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GRACE_ENV=production \
  -e LOG_LEVEL=WARNING \
  -v ./databases:/app/databases \
  --name grace-api \
  grace:2.2.0
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n grace
kubectl logs -n grace -l app=grace-api
```

### Uvicorn (Production Server)

```bash
# Single worker
uvicorn backend.misc.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level warning

# Multiple workers (recommended)
uvicorn backend.misc.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning \
  --access-log
```

### Gunicorn + Uvicorn Workers

```bash
gunicorn backend.misc.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level warning
```

---

## Health Checks

### Liveness Probe
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T15:30:00Z",
  "version": "2.2.0"
}
```

### Readiness Probe
```bash
curl http://localhost:8000/version
```

Verify `overall_progress >= 90` and all critical capabilities enabled.

---

## Monitoring

### Golden Signals
```bash
curl http://localhost:8000/api/enterprise/observability/golden-signals
```

**Monitor**:
- P95 latency < 200ms
- Error rate < 1%
- CPU < 80%, Memory < 85%

### MTTR Tracking
```bash
curl http://localhost:8000/api/guardian/healer/stats
```

**Monitor**: MTTR < 120 seconds

### System Metrics
```bash
curl http://localhost:8000/api/metrics/health
```

---

## Backup & Recovery

### Create Backup
```bash
curl -X POST http://localhost:8000/api/enterprise/dr/backup?backup_type=full
```

### List Restore Points
```bash
curl http://localhost:8000/api/enterprise/dr/stats
```

### Restore from Backup
```bash
curl -X POST http://localhost:8000/api/enterprise/dr/restore/{backup_id}
```

**RTO**: 15 minutes  
**RPO**: 60 minutes

---

## Scaling

### Horizontal Scaling

```bash
# Add workers
uvicorn backend.misc.main:app --workers 8

# Or use Kubernetes HPA
kubectl autoscale deployment grace-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

### Load Balancing

Use nginx or cloud load balancer:
```nginx
upstream grace {
    server grace-1:8000;
    server grace-2:8000;
    server grace-3:8000;
}
```

---

## Security

### API Keys
```bash
# Create tenant to get API key
curl -X POST http://localhost:8000/api/enterprise/tenants?name=MyCompany&tier=pro
```

Use API key in requests:
```bash
curl -H "X-API-Key: gk_your_key_here" http://localhost:8000/api/...
```

### Rate Limits
- Default: 60 req/min, burst 10
- Per-tenant quotas enforced
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Limit`

---

## Troubleshooting

### Boot Issues
```bash
# Run boot probe
export OFFLINE_MODE=true
export DRY_RUN=true
python scripts/test_boot_probe.py
```

### Import Issues
```bash
# Run import test
python scripts/test_imports.py
```

### Database Issues
```bash
# Check migrations
alembic current
alembic upgrade head
```

### Anti-Pattern Detection
```bash
# Scan for code issues
python scripts/detect_anti_patterns.py
```

---

## Performance Tuning

### Database Optimization
- All queries have `.limit()` 
- Pagination implemented
- Database-level filtering

### Memory Management
- Default limits: 100 items per query
- Streaming JSON parsing
- Async operations throughout

### Caching
- Redis for session data
- Query result caching
- Rate limiter state

---

## Version Management

### Check Version
```bash
cat VERSION
# 2.2.0
```

### Bump Version
```bash
# Patch: 2.2.0 → 2.2.1
python scripts/bump_version.py patch

# Minor: 2.2.0 → 2.3.0
python scripts/bump_version.py minor

# Major: 2.2.0 → 3.0.0
python scripts/bump_version.py major
```

Automatically updates: VERSION, pyproject.toml, __version__.py, main.py, CHANGELOG.md

---

**Deployment Status**: Production Ready (Backend)  
**Last Updated**: 2025-11-17  
**Version**: 2.2.0
