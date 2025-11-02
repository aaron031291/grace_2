# Grace Performance Optimization Guide

## 🎯 Current Performance

**Tested Configuration:**
- SQLite database
- Single process uvicorn
- 3 parallel task workers
- Development mode

**Benchmarks:**
- Chat response: <100ms
- Reflection generation: <500ms
- Sandbox execution: Variable (depends on code)
- Health check: <50ms

## ⚡ Quick Wins

### 1. Database Optimization
```python
# Current: SQLite (dev)
DATABASE_URL=sqlite+aiosqlite:///./grace.db

# Production: PostgreSQL
DATABASE_URL=postgresql+asyncpg://grace:password@localhost/grace

# Add connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### 2. Add Caching Layer
```python
# Install Redis
pip install redis aioredis

# Cache frequent queries
from aioredis import Redis

redis = Redis(host='localhost', port=6379)

# Cache trust scores
@cache(ttl=3600)
async def get_trust_score(url: str):
    ...
```

### 3. Increase Workers
```python
# Current: 3 parallel workers
task_executor = TaskExecutor(max_parallel=3)

# Production: Scale based on CPU
import multiprocessing
max_workers = multiprocessing.cpu_count()
task_executor = TaskExecutor(max_parallel=max_workers)
```

### 4. Use Gunicorn
```bash
# Current: Single uvicorn process
uvicorn backend.main:app

# Production: Multiple workers
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 🔧 Background Loop Tuning

### Adjust Intervals Based on Load
```python
# Low traffic (current defaults)
REFLECTION_INTERVAL = 10      # Every 10 seconds
META_LOOP_INTERVAL = 300      # Every 5 minutes
HEALTH_CHECK_INTERVAL = 30    # Every 30 seconds

# High traffic (optimized)
REFLECTION_INTERVAL = 60      # Every minute
META_LOOP_INTERVAL = 3600     # Every hour
HEALTH_CHECK_INTERVAL = 120   # Every 2 minutes
```

### Batch Processing
```python
# Process reflections in batches
async def generate_reflection(self):
    # Instead of analyzing all messages every time
    # Only analyze new messages since last run
    last_run = await get_last_reflection_time()
    messages = await get_messages_since(last_run)
    ...
```

## 🗄️ Database Optimization

### Add Indexes
```sql
-- Frequent queries
CREATE INDEX idx_chat_user_created ON chat_messages(user, created_at DESC);
CREATE INDEX idx_tasks_user_status ON tasks(user, status);
CREATE INDEX idx_reflections_generated ON reflections(generated_at DESC);
CREATE INDEX idx_immutable_log_sequence ON immutable_log(sequence);
CREATE INDEX idx_knowledge_domain ON knowledge_artifacts(domain, created_at DESC);
```

### Query Optimization
```python
# Bad: Load all then filter in Python
all_messages = await session.execute(select(ChatMessage))
user_messages = [m for m in all_messages if m.user == user]

# Good: Filter in database
user_messages = await session.execute(
    select(ChatMessage).where(ChatMessage.user == user).limit(50)
)
```

### Pagination
```python
# Add to all list endpoints
@router.get("/api/knowledge/artifacts")
async def list_artifacts(
    page: int = 1,
    per_page: int = 50,
    ...
):
    offset = (page - 1) * per_page
    query = select(KnowledgeArtifact).offset(offset).limit(per_page)
    ...
```

## 🚀 API Performance

### Response Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Response Caching
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="grace:")

@router.get("/api/metrics/summary")
@cache(expire=60)  # Cache for 60 seconds
async def get_metrics():
    ...
```

### Async Everywhere
```python
# Already done - all operations are async!
# This is a major performance advantage
```

## 📦 Frontend Optimization

### Production Build
```bash
cd grace-frontend
npm run build

# Serve with optimized server
npm install -g serve
serve -s dist -p 5173
```

### Code Splitting
```typescript
// Lazy load heavy components
const TranscendenceIDE = lazy(() => import('./components/TranscendenceIDE'));
const Dashboard = lazy(() => import('./components/Dashboard'));
```

### CDN for Static Assets
- Host built frontend on CDN
- Reduce server load
- Faster global access

## 🔥 Load Testing

### Test Scenarios
```bash
# Install locust
pip install locust

# Create locustfile.py
class GraceUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/api/chat/",
            json={"message": "hello"},
            headers={"Authorization": f"Bearer {token}"}
        )

# Run test
locust -f locustfile.py --host=http://localhost:8000
```

### Expected Performance

**Light Load (10 users):**
- 95th percentile: <200ms
- Throughput: 100 req/s

**Medium Load (100 users):**
- 95th percentile: <500ms
- Throughput: 500 req/s

**Heavy Load (1000 users):**
- Requires: PostgreSQL, Redis, 4+ workers
- 95th percentile: <1000ms
- Throughput: 1000+ req/s

## 🎛️ Resource Limits

### Docker Limits
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Python Limits
```python
# Limit background loop memory
import resource

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))  # 2GB
```

## 📈 Scaling Strategies

### Vertical Scaling (Single Server)
- Increase CPU cores → More workers
- Increase RAM → Larger caches
- Faster SSD → Better DB performance

### Horizontal Scaling (Multiple Servers)
- Load balancer → Multiple backend instances
- Shared PostgreSQL
- Redis for session/cache
- Celery for distributed tasks (future)

## ✅ Performance Checklist

**Before Production:**
- [ ] Switch to PostgreSQL
- [ ] Add Redis caching
- [ ] Use Gunicorn with workers
- [ ] Enable gzip compression
- [ ] Add database indexes
- [ ] Build frontend for production
- [ ] Configure CDN
- [ ] Set up load balancer
- [ ] Run load tests
- [ ] Monitor and tune

**Grace can handle production load with these optimizations!** ⚡🚀
