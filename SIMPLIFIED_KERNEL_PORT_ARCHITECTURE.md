# Simplified Kernel Port Architecture

## Concept

**Kernels:** Each gets dedicated port for isolation and debugging  
**APIs:** All on main port 8000 for simplicity  
**Result:** Best of both worlds

## Architecture

```
┌─────────────────────────────────────┐
│   Main Grace API (Port 8000)        │
│   - All API routes                  │
│   - Health aggregation              │
│   - Simple deployment               │
└──────────────┬──────────────────────┘
               │
               │ Talks to kernels via internal HTTP
               │
    ┌──────────┼──────────┬──────────────┐
    │          │          │              │
    ▼          ▼          ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│ Kernel │ │ Kernel │ │ Kernel   │ │ Kernel   │
│ 8100   │ │ 8101   │ │ 8130     │ │ 8131     │
│ Msg    │ │ Log    │ │ Librarian│ │ Self-Heal│
│ Bus    │ │        │ │          │ │          │
└────────┘ └────────┘ └──────────┘ └──────────┘
```

## Kernel Ports (8100-8149)

### Tier 1: Core (8100-8109)
- **8100** - Message Bus
- **8101** - Immutable Log

### Tier 2: Governance (8110-8119)
- **8110** - Governance Kernel
- **8111** - Crypto Kernel
- **8112** - Trust Framework Kernel
- **8113** - Policy Engine
- **8114** - Compliance Monitor
- **8115** - Audit Trail

### Tier 3: Execution (8120-8129)
- **8120** - Scheduler Kernel
- **8121** - Task Executor
- **8122** - Workflow Engine
- **8123** - State Machine

### Tier 4: Agentic (8130-8139)
- **8130** - Librarian Kernel
- **8131** - Self-Healing Kernel
- **8132** - Coding Agent Kernel
- **8133** - Learning Kernel
- **8134** - Research Kernel

### Tier 5: Services (8140-8149)
- **8140** - Telemetry Service
- **8141** - Metrics Aggregator
- **8142** - Alert Service

## Main API (Port 8000)

**All routes stay on port 8000:**
- `/auth/*` - Authentication
- `/chat/*` - Chat endpoints
- `/memory/*` - Memory tables
- `/librarian/*` - Librarian (routes to kernel 8130)
- `/guardian/*` - Guardian
- `/kernel-ports/*` - Kernel management
- `/network-healer/*` - Network healing
- ... all other routes

## Communication Pattern

### API → Kernel
```python
# Example: Chat API needs Librarian Kernel
async def chat_with_librarian():
    # Main API on 8000 makes internal request
    response = await http_client.get("http://localhost:8130/search")
    return response
```

### Kernel Health Check
```python
# Guardian checks each kernel
for kernel_port in [8100, 8101, 8130, 8131]:
    health = await http_client.get(f"http://localhost:{kernel_port}/health")
```

## Benefits

### 1. Kernel Isolation
- Each kernel runs independently
- One kernel crash doesn't affect others
- Easy to restart individual kernels

### 2. Simple API
- All routes on one port (8000)
- No routing complexity
- Standard FastAPI app

### 3. Easy Debugging
```bash
# Check specific kernel
curl http://localhost:8130/health  # Librarian

# Check main API
curl http://localhost:8000/health  # Everything

# Restart just one kernel (via Guardian)
curl -X POST http://localhost:8000/network-healer/heal \
  -d '{"component_name": "librarian_kernel"}'
```

### 4. Manageable Scale
- 20 kernel ports (not 100)
- Network healing focuses on kernels
- APIs share main port resources

## Deployment

### Development
```bash
# Start main API
python serve.py  # Port 8000

# Kernels auto-start with their ports
# Guardian monitors all kernel ports
```

### Production
```bash
# Main API behind load balancer
nginx → localhost:8000

# Kernels internal only
# Not exposed externally
```

## Guardian Integration

**Guardian monitors kernel health:**
- Every 60s health check on kernel ports
- Auto-restart failed kernels
- Network healing playbooks
- Kernel-level metrics

**Guardian doesn't monitor APIs:**
- APIs are routes, not separate processes
- API failures handled by main app

## Network Healing

**Applies to kernels only:**
```json
{
  "component_name": "librarian_kernel",
  "port": 8130,
  "issue_type": "port_not_listening",
  "action": "restart_component"
}
```

**Playbooks:**
1. RestartComponentPlaybook → restart kernel
2. ClearPortPlaybook → clear stuck kernel port
3. DiagnoseNetworkPlaybook → diagnose kernel issues
4. RebindPortPlaybook → move kernel to new port

## Implementation Simplicity

### What You Build
✅ Kernel launcher (starts each kernel on its port)  
✅ Main API (aggregates all routes)  
✅ Kernel health checker (Guardian integration)  
✅ Network healing (for kernels)  

### What You Skip
❌ API port registry (all APIs on 8000)  
❌ API routing complexity  
❌ API-level health checks (main app handles)  
❌ 80 extra ports  

## Example: Librarian Kernel

### Kernel Code (runs on 8130)
```python
# backend/kernels/librarian_kernel_service.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "kernel": "librarian"}

@app.get("/search")
async def search(query: str):
    # Librarian logic here
    return {"results": [...]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8130)
```

### Main API (routes to kernel)
```python
# backend/routes/librarian_api.py
from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/librarian")

@router.get("/search")
async def search(query: str):
    # Route to kernel
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8130/search",
            params={"query": query}
        )
        return response.json()
```

## Comparison

| Aspect | All-in-One (Before) | Full Microservices | **Hybrid (Recommended)** |
|--------|-------------------|-------------------|------------------------|
| Ports | 1 (8000) | 100+ | 21 (8000 + 20 kernels) |
| Complexity | Low | Very High | **Medium** |
| Kernel Isolation | None | Full | **Full** |
| API Simplicity | High | Low | **High** |
| Debugging | Hard | Easy | **Easy (kernels)** |
| Network Healing | Limited | Comprehensive | **Comprehensive (kernels)** |
| Deployment | Simple | Complex | **Simple** |

## Migration Path

### Phase 1: Extract Core Kernels (Week 1)
1. Librarian → 8130
2. Self-Healing → 8131
3. Coding Agent → 8132

### Phase 2: Extract Governance (Week 2)
4. Governance → 8110
5. Trust Framework → 8112

### Phase 3: Extract Services (Week 3)
6. Message Bus → 8100
7. Immutable Log → 8101

### Phase 4: Monitoring & Healing (Week 4)
8. Guardian integration
9. Network healing playbooks
10. Health monitoring

## Monitoring

### Kernel-Level
```bash
# Check all kernels
curl http://localhost:8000/kernel-ports/health-check

# Check specific kernel
curl http://localhost:8130/health
```

### API-Level
```bash
# Check main API (includes all routes)
curl http://localhost:8000/health
```

## Conclusion

**This hybrid approach gives you:**
- ✅ Kernel isolation and debugging (the hard stuff)
- ✅ API simplicity (the easy stuff)
- ✅ Network healing power
- ✅ Reasonable complexity
- ✅ Clear migration path

**Recommendation:** START HERE. Add more later if needed.
