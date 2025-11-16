# Complete Guardian System - Full Integration Map

## The Complete Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRACE - Living Organism                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: INFRASTRUCTURE (NEW!)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Service Mesh (Coordinates Everything)                    │  │
│  │  ├─ Service Discovery (Auto-finds services)               │  │
│  │  ├─ API Gateway (Smart routing, retries, circuit breaking)│ │
│  │  ├─ Load Balancer (Distributes traffic)                  │  │
│  │  └─ Health Monitoring (Continuous health checks)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↕ (integrates with)                                   │
│  Layer 2: DOMAIN SYSTEM (NEW!)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  10 Domain Ports (8200-8209) - Grouped APIs              │  │
│  │  ├─ Domain Registry (Auto-discovery)                      │  │
│  │  ├─ Event Bus (Pub/Sub communication)                     │  │
│  │  ├─ Shared Memory (Collective learning)                   │  │
│  │  └─ Orchestrator (Multi-domain workflows)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↕ (integrates with)                                   │
│  Layer 3: KERNELS (EXISTING + ENHANCED)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  20 Kernel Ports (8100-8149) - Isolated kernels          │  │
│  │  ├─ Kernel Port Manager (Port assignments)                │  │
│  │  ├─ Network Healing Playbooks (Auto-fix issues)           │  │
│  │  └─ Guardian (Orchestrates healing)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↕ (integrates with)                                   │
│  Layer 4: MAIN API (EXISTING)                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Main Grace API (Port 8000/8017) - Entry point           │  │
│  │  └─ All routes, services, existing functionality          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Everything Merges

### Integration Flow

```
User Request
    ↓
Main API (8017) - Entry point
    ↓
Service Mesh - Intelligent routing
    ↓
API Gateway - Circuit breaker, retries, rate limiting
    ↓
Service Discovery - Find best service
    ↓
Load Balancer - Select instance
    ↓
Domain (8200-8209) - Grouped APIs
    ↓
Kernel (8100-8149) - Specialized processing
    ↓
Response flows back up
```

### Example: Chat Request

```python
# 1. User sends: POST /chat
#    → Hits Main API (8017)

# 2. Main API routes through Service Mesh:
result = await service_mesh.call_service(
    capability='chat',
    path='/generate',
    method='POST',
    data={'message': 'Hello'}
)

# 3. Service Mesh orchestrates:
#    a) Service Discovery finds: ai_domain (8202)
#    b) Load Balancer selects: best instance
#    c) API Gateway checks: circuit breaker OK, rate limit OK
#    d) Gateway routes to: http://localhost:8202/chat/generate

# 4. AI Domain (8202) processes:
#    - Uses AI kernels (8132, 8133, 8134)
#    - Publishes event: 'chat.request_processed'
#    - Contributes to shared memory

# 5. Other domains react automatically:
#    - Memory domain (subscribed) stores conversation
#    - Monitoring domain (subscribed) tracks metrics
#    - All via event bus!

# 6. Response returns through mesh:
#    Gateway → Mesh → Main API → User

# 7. Post-processing (automatic):
#    - Gateway records metrics
#    - Discovery updates service health
#    - Load balancer adjusts weights
#    - Shared memory learns from interaction
```

---

## Integration Points

### 1. Service Discovery ↔ Domain Registry

```python
# Service Discovery auto-discovers domains
await service_discovery._discover_domains()

# Finds:
# - ai_domain on 8202
# - memory_domain on 8201
# - governance_domain on 8203
# etc.

# Builds capability map:
{
  'chat': ['ai_domain'],
  'memory': ['memory_domain'],
  'search': ['memory_domain', 'librarian_kernel']
}
```

### 2. Service Discovery ↔ Kernel Port Manager

```python
# Service Discovery auto-discovers kernels
await service_discovery._discover_kernels()

# Finds:
# - librarian_kernel on 8130
# - self_healing_kernel on 8131
# - coding_agent_kernel on 8132
# etc.
```

### 3. API Gateway ↔ Network Healing

```python
# Gateway detects service failure
if circuit_breaker.state == "open":
    # Trigger healing
    from backend.domains import domain_event_bus, DomainEvent
    
    await domain_event_bus.publish(DomainEvent(
        event_type='healing.needed',
        source_domain='api_gateway',
        data={'service_id': service_id, 'issue': 'circuit_open'}
    ))
    
# Guardian (subscribed) automatically heals it!
```

### 4. Load Balancer ↔ Health Monitoring

```python
# Load balancer uses real-time health
service = service_discovery.find_service('chat')

# Returns healthiest instance based on:
# - Health status (from continuous checks)
# - Response time (from metrics)
# - Current load (from tracking)
# - Failure count (from circuit breakers)
```

### 5. Service Mesh ↔ Domain Events

```python
# Mesh publishes telemetry events
await domain_event_bus.publish(DomainEvent(
    event_type='mesh.request_routed',
    source_domain='service_mesh',
    data={
        'from': 'main_api',
        'to': 'ai_domain',
        'latency_ms': 45
    }
))

# Monitoring domain (subscribed) tracks it
# Shared memory learns patterns
```

---

## What Each Layer Provides

### Layer 1: Infrastructure (NEW)
**Service Mesh** - Orchestrates everything
- Routes requests intelligently
- Handles failures gracefully
- Provides observability

**Service Discovery** - Finds services automatically
- Auto-discovers domains and kernels
- Tracks health continuously
- Maps capabilities

**API Gateway** - Protects services
- Circuit breakers prevent cascade failures
- Rate limiting protects from overload
- Automatic retries handle transient failures

**Load Balancer** - Distributes traffic
- Multiple strategies (round-robin, least-connections, health-aware)
- Real-time load tracking
- Automatic failover

### Layer 2: Domain System (NEW)
**Domains** - Logical groupings
- 10 domain ports for organized APIs
- Cryptographic tracking
- Domain-level isolation

**Event Bus** - Communication backbone
- Pub/sub messaging
- Loose coupling
- Automatic collaboration

**Shared Memory** - Collective intelligence
- Cross-domain learning
- Knowledge sharing
- Continuous improvement

**Orchestrator** - Complex workflows
- Multi-domain coordination
- Atomic transactions
- Automatic rollback

### Layer 3: Kernels (EXISTING + ENHANCED)
**Kernel Ports** - Isolated processes
- 20 dedicated ports
- Individual health monitoring
- Network healing

**Guardian** - System protection
- Auto-remediation
- Playbook execution
- Network healing

### Layer 4: Main API (EXISTING)
**Entry Point** - User-facing
- All routes available
- Backward compatible
- Simple access

---

## Deployment Architecture

### Development (Current - Port 8017)
```
Main API: 8017
    ↓ uses
Service Mesh (in-process)
    ↓ discovers
Domains: 8200-8209 (when we add them)
Kernels: 8100-8149 (when we add them)
```

### Production (Future)
```
Internet
    ↓
Load Balancer (nginx/haproxy)
    ↓
Main API: 8000 (multiple instances)
    ↓
Service Mesh
    ↓
┌─────────────┬───────────────┬────────────────┐
Domains       Kernels         External Services
8200-8209     8100-8149       Redis, Postgres, etc.
```

---

## Request Flow Example: Complex Operation

**Scenario:** User uploads document for analysis

```
1. POST /documents/analyze
   ↓
2. Main API (8017)
   Receives request
   ↓
3. Service Mesh
   Determines workflow needs:
   - Data processing (data_domain)
   - AI analysis (ai_domain)
   - Storage (memory_domain)
   - Verification (governance_domain)
   ↓
4. Domain Orchestrator
   Creates multi-domain workflow:
   
   Step 1: Data Domain (8207)
   → Ingestion API ingests document
   → Returns: document_id
   
   Step 2: AI Domain (8202) - depends on step 1
   → API Gateway routes request
   → Service Discovery finds ai_domain
   → Circuit breaker: OK
   → Rate limiter: OK
   → Load Balancer selects: ai_domain instance
   → AI analyzes document
   → Publishes event: 'ml.analysis_complete'
   → Returns: analysis_results
   
   Step 3: Memory Domain (8201) - depends on step 2
   → Stores document + analysis
   → Event Bus notified (subscribers act automatically)
   → Returns: storage_id
   
   Step 4: Governance Domain (8203) - depends on step 3
   → Verifies compliance
   → Cryptographically signs approval
   → Returns: verification_proof
   ↓
5. Automatic Post-Processing:
   
   - Memory Domain (subscribed to ml.analysis_complete):
     "Stores analysis for future reference"
   
   - Monitoring Domain (subscribed to all events):
     "Tracks latency, success rate, resource usage"
   
   - Shared Memory:
     "Learns: This workflow pattern works well"
   
   - AI Domain contributes:
     "Found optimization: cache similar documents"
   
   - Next time this workflow runs:
     "Uses cached results, 10x faster!"
   ↓
6. Response to User
   Full results with cryptographic proof
```

---

## Synergistic Benefits

### 1. Automatic Failover
```
Service fails
    ↓
Circuit breaker opens
    ↓
Service Discovery marks unhealthy
    ↓
Load Balancer routes to backup
    ↓
Event Bus notifies healing domain
    ↓
Guardian auto-heals failed service
    ↓
Service recovers
    ↓
Circuit breaker closes
    ↓
Service Discovery marks healthy
    ↓
Back in rotation!

ALL AUTOMATIC!
```

### 2. Intelligent Learning
```
Gateway tracks request patterns
    ↓
Contributes to Shared Memory
    ↓
"Route X is slow on Tuesdays"
    ↓
Load Balancer learns
    ↓
Adjusts weights on Tuesdays
    ↓
Problem prevented before it happens!
```

### 3. Distributed Tracing
```
Request enters mesh
    ↓
Gateway assigns trace_id
    ↓
Each hop adds cryptographic signature:
  - Main API (8017) → sign_1
  - Service Mesh → sign_2  
  - AI Domain (8202) → sign_3
  - AI Kernel (8132) → sign_4
    ↓
Complete audit trail
Tamper-proof
Verifiable
```

---

## Files Created

```
backend/infrastructure/
├── __init__.py                 # Infrastructure package
├── service_discovery.py        # Auto-discovery
├── api_gateway.py             # Gateway + circuit breakers
├── load_balancer.py           # Load balancing strategies
└── service_mesh.py            # Service mesh coordinator

backend/routes/
└── infrastructure_api.py      # Infrastructure APIs

Documentation:
└── COMPLETE_GUARDIAN_SYSTEM.md  # This file
```

---

## API Endpoints (NEW)

### Service Discovery
```
GET  /infrastructure/discovery/services          - All services
GET  /infrastructure/discovery/service/{id}      - Service details
GET  /infrastructure/discovery/by-capability/{c} - Find by capability
GET  /infrastructure/discovery/stats             - Statistics
```

### API Gateway
```
POST /infrastructure/gateway/route               - Route request
GET  /infrastructure/gateway/stats               - Gateway stats
GET  /infrastructure/gateway/request-history     - Request history
GET  /infrastructure/gateway/circuit-breakers    - Circuit breaker status
```

### Load Balancer
```
GET  /infrastructure/load-balancer/stats         - LB statistics
POST /infrastructure/load-balancer/set-weight/{id} - Set weights
```

### Service Mesh
```
POST /infrastructure/mesh/call                   - Call through mesh
GET  /infrastructure/mesh/topology               - Mesh topology
GET  /infrastructure/mesh/stats                  - Mesh statistics
GET  /infrastructure/mesh/health                 - Mesh health
```

### Overview
```
GET  /infrastructure/overview                    - Complete overview
POST /infrastructure/initialize                  - Initialize infrastructure
```

---

## Integration with Existing System

### Current Grace (Running)
```python
# backend/main.py - Add these lines:

from backend.routes.infrastructure_api import router as infrastructure_router
app.include_router(infrastructure_router)

# In startup event:
from backend.infrastructure import initialize_infrastructure
await initialize_infrastructure()
print("[OK] Infrastructure layer initialized")
```

**That's it! 2 lines of code.**

### What Happens Automatically

**On startup:**
1. Service Mesh initializes
2. Service Discovery scans for:
   - Existing domains (from domain registry)
   - Existing kernels (from kernel port manager)
   - Existing services
3. Starts continuous health monitoring
4. Infrastructure layer READY

**During operation:**
1. All requests can use service mesh
2. Automatic failover on failures
3. Circuit breakers protect services
4. Load balancing distributes traffic
5. Health-based routing ensures reliability

---

## Usage Examples

### Example 1: Route Request Through Mesh

```bash
curl -X POST http://localhost:8017/infrastructure/mesh/call \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "chat",
    "path": "/generate",
    "method": "POST",
    "data": {"message": "Hello"}
  }'
```

**What happens:**
- Service Mesh finds service with 'chat' capability
- API Gateway checks circuit breaker & rate limit
- Load Balancer selects best instance
- Request routed automatically
- Response returned with full telemetry

### Example 2: View Service Topology

```bash
curl http://localhost:8017/infrastructure/mesh/topology
```

**Returns:**
```json
{
  "services": [
    {
      "id": "domain_ai_domain",
      "type": "domain",
      "endpoint": "localhost:8202",
      "health": "healthy",
      "load": 0.45,
      "response_time": 120
    },
    {
      "id": "kernel_librarian_kernel",
      "type": "kernel",
      "endpoint": "localhost:8130",
      "health": "healthy",
      "load": 0.20,
      "response_time": 45
    }
  ],
  "capabilities": {
    "chat": ["domain_ai_domain"],
    "search": ["domain_memory_domain", "kernel_librarian_kernel"]
  },
  "health_summary": {
    "healthy": 25,
    "degraded": 2,
    "unhealthy": 0
  }
}
```

### Example 3: Check Infrastructure Health

```bash
curl http://localhost:8017/infrastructure/mesh/health
```

### Example 4: Monitor Circuit Breakers

```bash
curl http://localhost:8017/infrastructure/gateway/circuit-breakers
```

---

## Complete Feature Matrix

| Feature | Before | After Integration |
|---------|--------|-------------------|
| **Service Discovery** | Manual | ✅ Automatic |
| **Load Balancing** | None | ✅ Health-aware |
| **Circuit Breakers** | None | ✅ Automatic |
| **Rate Limiting** | Manual | ✅ Per-service |
| **Health Monitoring** | Basic | ✅ Continuous |
| **Failover** | Manual | ✅ Automatic |
| **Retry Logic** | Per-route | ✅ Built-in |
| **Request Tracing** | Logs | ✅ Full tracing |
| **Domain Events** | None | ✅ Pub/Sub |
| **Shared Learning** | None | ✅ Collective memory |
| **Multi-domain Workflows** | Manual | ✅ Orchestrated |
| **Cryptographic Audit** | Partial | ✅ Complete |

---

## Backwards Compatibility

### Old Way Still Works
```python
# Direct route call (existing code)
@app.get("/chat")
async def chat():
    # ... existing logic ...
    return result
```

### New Way Also Works
```python
# Through service mesh (new code)
@app.get("/chat")
async def chat():
    result = await service_mesh.call_service(
        capability='chat',
        path='/generate'
    )
    return result
```

**Both coexist! Migrate gradually.**

---

## Deployment Scenarios

### Scenario 1: Current (All-in-One)
```
Grace (8017)
└── Everything in one process
```

**Integration:**
- Add infrastructure layer (in-process)
- Service mesh manages internal routing
- No external dependencies

### Scenario 2: Domain-Separated
```
Main API (8017)
    ↓
Service Mesh
    ↓
Domains (8200-8209) - Separate processes
```

**Integration:**
- Service Discovery finds domains automatically
- Gateway routes between processes
- Health monitoring per domain

### Scenario 3: Full Distributed
```
Load Balancer
    ↓
Main APIs (8000-8004) - Multiple instances
    ↓
Service Mesh
    ↓
Domains (8200-8209) - Multiple instances each
    ↓
Kernels (8100-8149) - Dedicated processes
```

**Integration:**
- Service Discovery finds ALL instances
- Load Balancer distributes across instances
- Circuit breakers protect each service
- Complete enterprise architecture

---

## Monitoring & Observability

### Single Dashboard View

```bash
curl http://localhost:8017/infrastructure/overview
```

**Shows:**
```json
{
  "service_discovery": {
    "total_services": 30,
    "by_type": {"domain": 10, "kernel": 20},
    "by_health": {"healthy": 28, "degraded": 2}
  },
  "api_gateway": {
    "total_requests": 15420,
    "success_rate": 98.5,
    "circuit_breaker_blocks": 3,
    "rate_limit_blocks": 12
  },
  "load_balancer": {
    "total_routed": 15420,
    "strategy": "health_aware"
  },
  "service_mesh": {
    "requests_routed": 15420,
    "failures_prevented": 15
  }
}
```

---

## Integration Checklist

### ✅ Already Built
- [x] Network healing playbooks
- [x] Kernel port manager
- [x] Domain registry
- [x] Domain event bus
- [x] Shared memory
- [x] Domain orchestrator
- [x] Service discovery
- [x] API gateway
- [x] Load balancer
- [x] Service mesh

### 📝 To Integrate (Simple!)

**1. Add infrastructure to main.py:**
```python
from backend.routes.infrastructure_api import router as infrastructure_router
app.include_router(infrastructure_router)

# In startup:
from backend.infrastructure import initialize_infrastructure
await initialize_infrastructure()
```

**2. Test:**
```bash
python serve.py
curl http://localhost:8017/infrastructure/overview
```

**3. Start using:**
```python
# In any route
from backend.infrastructure import service_mesh

result = await service_mesh.call_service(
    capability='chat',
    path='/generate'
)
```

---

## The Complete Integration

```
YOUR CURRENT GRACE (8017)
    +
DOMAIN SYSTEM (registry, events, memory, orchestrator)
    +
INFRASTRUCTURE (service mesh, gateway, load balancer, discovery)
    =
COMPLETE ENTERPRISE-GRADE SYSTEM

With:
✅ Auto-discovery
✅ Auto-healing
✅ Auto-scaling (load balancing)
✅ Auto-learning (shared memory)
✅ Auto-failover (circuit breakers)
✅ Complete observability
✅ Cryptographic audit trails
✅ Zero manual intervention
```

**Grace becomes a SELF-MANAGING, SELF-HEALING, SELF-LEARNING ORGANISM!** 🚀
