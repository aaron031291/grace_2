# RAG Pipeline - Architecture Integration

## How RAG Connects to Grace's Architecture

The RAG pipeline is integrated into Grace's architecture through multiple layers, connecting to the Service Mesh, Domain System, and Infrastructure components.

## Complete Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    GRACE COMPLETE ARCHITECTURE                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 1: APPLICATION LAYER                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Frontend → API Routes → Chat/Vision/Speech Endpoints           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  Layer 2: DOMAIN LAYER (Synergistic Architecture)                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Domain Registry    Event Bus    Shared Memory    Orchestrator  │ │
│  │ - Auto-discovery   - Pub/Sub    - Collective     - Workflows   │ │
│  │ - Registration     - Events     - Intelligence   - Multi-step  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  Layer 3: INFRASTRUCTURE LAYER (Service Mesh)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Service Mesh       API Gateway    Load Balancer  Discovery     │ │
│  │ - S2S comms        - Circuit      - Round-robin  - Health      │ │
│  │ - Retries          - breakers     - Least-conn   - checks      │ │
│  │ - Failover         - Rate limit   - Hash-based   - Registry    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  Layer 4: KNOWLEDGE LAYER (RAG Pipeline + World Model)              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                                                                 │ │
│  │  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐  │ │
│  │  │ RAG Service  │──────│ Vector Store │──────│  Embedding  │  │ │
│  │  │ - Retrieval  │      │ - Faiss/     │      │  Service    │  │ │
│  │  │ - Citations  │      │   Chroma     │      │ - OpenAI    │  │ │
│  │  │ - Context    │      │ - Semantic   │      │ - Local     │  │ │
│  │  └──────────────┘      │   search     │      │   models    │  │ │
│  │         ↓               └──────────────┘      └─────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │           World Model (Grace's Knowledge)                │  │ │
│  │  │  - Self-knowledge   - System knowledge                   │  │ │
│  │  │  - User knowledge   - Domain knowledge                   │  │ │
│  │  │  - Temporal knowledge                                    │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  │         ↓                                                       │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │        MCP Integration (External Access)                  │  │ │
│  │  │  - Resources (grace://*)                                  │  │ │
│  │  │  - Tools (query, ask, add)                               │  │ │
│  │  │  - LLM/Tool integration                                   │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  Layer 5: SERVICE LAYER                                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Model Orchestrator   Unified LLM   Capability System           │ │
│  │ Speech/TTS          Vision         Learning Systems            │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Initialization Flow

The system initializes in this order (from [`backend/main.py`](../backend/main.py:102)):

```python
@app.on_event("startup")
async def startup():
    # 1. Model System (lines 103-120)
    from backend.unified_llm import unified_llm
    from backend.model_capability_system import capability_system
    await unified_llm.initialize()
    await capability_system.manage_cache()
    
    # 2. Domain System (lines 122-127)
    from backend.domains import initialize_domain_system
    await initialize_domain_system()
    # → Domain Registry
    # → Event Bus
    # → Shared Memory
    # → Orchestrator
    
    # 3. Infrastructure Layer (lines 130-135)
    from backend.infrastructure import initialize_infrastructure
    await initialize_infrastructure()
    # → Service Discovery
    # → API Gateway
    # → Load Balancer
    # → Service Mesh
    
    # 4. World Model + RAG (lines 138-144)
    from backend.world_model import initialize_world_model
    await initialize_world_model()
    # → Grace World Model
    # → RAG Service
    # → MCP Integration
```

## RAG Integration Points

### 1. Service Mesh Integration

**Location**: [`backend/infrastructure/service_mesh.py`](../backend/infrastructure/service_mesh.py:26)

RAG services are accessible through the service mesh for:
- Automatic service discovery
- Load balancing across multiple RAG instances
- Circuit breakers for fault tolerance
- Request retries and failover

**How to call RAG through service mesh**:
```python
from backend.infrastructure import service_mesh

# Route RAG request through mesh
result = await service_mesh.call_service(
    capability="knowledge_retrieval",
    path="/api/vectors/search/rag",
    method="POST",
    data={"query": "What is Grace?", "top_k": 5}
)
```

### 2. Domain System Integration

**Location**: [`backend/domains/__init__.py`](../backend/domains/__init__.py:1)

RAG integrates with the domain system through:

#### A. Domain Registry
```python
from backend.domains import domain_registry

# RAG services can register as domain capabilities
await domain_registry.register_domain(
    domain_id="knowledge",
    capabilities=["semantic_search", "rag_retrieval", "context_generation"],
    endpoints={
        "search": "/api/vectors/search",
        "rag": "/api/vectors/search/rag"
    }
)
```

#### B. Event Bus (Pub/Sub)
```python
from backend.domains import domain_event_bus

# Subscribe to knowledge requests
def handle_knowledge_request(event):
    query = event.data.get("query")
    # Trigger RAG retrieval
    
domain_event_bus.subscribe("knowledge.request", handle_knowledge_request)

# Publish knowledge events
await domain_event_bus.publish(
    event_type="knowledge.retrieved",
    data={"query": query, "results": results}
)
```

#### C. Shared Memory
```python
from backend.domains import shared_domain_memory

# Contribute RAG results to shared memory
await shared_domain_memory.contribute(
    domain_id="knowledge",
    key="rag_context",
    value=context_data,
    confidence=0.95,
    tags=["semantic", "retrieval"]
)

# Access context from other domains
context = shared_domain_memory.retrieve("rag_context")
```

### 3. World Model Integration

**Location**: [`backend/world_model/grace_world_model.py`](../backend/world_model/grace_world_model.py:55)

The World Model uses RAG for semantic queries:

```python
from backend.world_model import grace_world_model

# World model internally uses RAG service
async def query(query: str, category: str = None):
    # Uses RAG service for semantic search
    from backend.services.rag_service import rag_service
    
    rag_results = await rag_service.retrieve(
        query=query,
        top_k=5,
        requested_by='world_model'
    )
    
    # Match with world knowledge
    return knowledge_items
```

### 4. API Route Integration

**Direct API Access**:
```
POST /api/vectors/search                    # Semantic search
POST /api/vectors/search/rag                # RAG with citations
POST /api/vectors/embed                     # Generate embeddings
GET  /world-model/query                     # Query world model
GET  /world-model/mcp/manifest              # MCP capabilities
POST /world-model/mcp/tool                  # Call MCP tools
```

**Through Service Mesh**:
```python
# Internal services call RAG through mesh
result = await service_mesh.call_service(
    capability="knowledge",
    path="/search/rag",
    data={"query": user_question}
)
```

## Data Flow Example: User Question → RAG → Response

```
1. User asks: "What are Grace's capabilities?"
   ↓
2. Request arrives at /api/chat endpoint
   ↓
3. Routed through Service Mesh
   ↓
4. Domain Orchestrator identifies need for knowledge
   ↓
5. Event published to domain_event_bus: "knowledge.request"
   ↓
6. RAG Service receives event/call
   ↓
7. RAG Service flow:
   a. Query → Embedding Service → Generate vector
   b. Vector → Vector Store → Semantic search
   c. Results → World Model → Match knowledge
   d. Context → Format with citations
   ↓
8. Results contributed to Shared Domain Memory
   ↓
9. Response routed back through Service Mesh
   ↓
10. LLM uses RAG context to generate answer
   ↓
11. Response delivered to user
```

## Integration Patterns

### Pattern 1: Direct Service Integration
```python
from backend.services.rag_service import rag_service

# Initialize once at startup
await rag_service.initialize()

# Use directly
context = await rag_service.retrieve_with_citations(query)
```

### Pattern 2: Service Mesh Integration
```python
from backend.infrastructure import service_mesh

# Call through mesh (automatic discovery, load balancing, retries)
result = await service_mesh.call_service(
    capability="rag",
    path="/retrieve",
    data={"query": question}
)
```

### Pattern 3: Domain Event Integration
```python
from backend.domains import domain_event_bus

# Publish request
await domain_event_bus.publish(
    event_type="knowledge.request",
    domain_id="knowledge",
    data={"query": question, "requester": "chat_domain"}
)

# Subscribe to results
def handle_knowledge_response(event):
    context = event.data["context"]
    # Use context
    
domain_event_bus.subscribe("knowledge.response", handle_knowledge_response)
```

### Pattern 4: Shared Memory Integration
```python
from backend.domains import shared_domain_memory

# Store RAG context for other domains
await shared_domain_memory.contribute(
    domain_id="knowledge",
    key=f"query_{query_id}",
    value={"context": context, "citations": citations},
    expires_in=3600  # 1 hour TTL
)

# Access from another domain
cached_context = shared_domain_memory.retrieve(f"query_{query_id}")
```

### Pattern 5: MCP External Integration
```python
from backend.world_model import mcp_integration

# External tools/LLMs access via MCP
manifest = mcp_integration.get_mcp_manifest()

# Call MCP tool
result = await mcp_integration.handle_tool_call(
    'query_world_model',
    {'query': 'autonomous capabilities', 'top_k': 5}
)
```

## Component Relationships

### RAG Service Dependencies
```
RAG Service
├── Embedding Service (converts text to vectors)
├── Vector Store (semantic search)
├── World Model (knowledge matching)
└── Service Mesh (communication layer)
```

### World Model Dependencies
```
World Model
├── RAG Service (semantic queries)
├── Vector Store (indexing)
├── MCP Integration (external access)
└── Domain System (knowledge sharing)
```

### MCP Integration Dependencies
```
MCP Integration
├── World Model (knowledge source)
├── RAG Service (retrieval)
└── API Routes (REST access)
```

## Configuration

### Service Registration
Each RAG component registers with the service discovery:

```python
from backend.infrastructure import service_discovery

# RAG Service registration
await service_discovery.register_service(
    service_id="rag_service_1",
    service_type="knowledge",
    capabilities=["semantic_search", "context_retrieval", "rag"],
    host="localhost",
    port=8000,
    health_endpoint="/api/vectors/health"
)
```

### Domain Registration
```python
from backend.domains import domain_registry

# Knowledge domain registration
await domain_registry.register_domain(
    domain_id="knowledge",
    domain_name="Knowledge Retrieval",
    capabilities=["rag", "semantic_search", "embeddings"],
    health_check_endpoint="/world-model/stats"
)
```

## Monitoring & Observability

### Service Mesh Metrics
```python
# Get RAG service metrics through mesh
stats = service_mesh.get_stats()
# Returns: requests_routed, failures_prevented, services_managed

# Check topology
topology = service_mesh.get_service_topology()
# Shows all services, health status, connections
```

### Domain Metrics
```python
from backend.domains import domain_registry

# Get knowledge domain stats
stats = domain_registry.get_domain_stats("knowledge")
# Returns: events_published, memory_contributions, health
```

### RAG Service Metrics
```python
from backend.services.rag_service import rag_service

# Direct metrics
# Tracked internally: queries, avg response time, cache hits
```

## Best Practices for Integration

### 1. Use Service Mesh for External Calls
```python
# ✅ Good: Through mesh (automatic retries, load balancing)
result = await service_mesh.call_service(capability="rag", ...)

# ❌ Avoid: Direct HTTP calls
response = requests.post("http://localhost:8000/api/vectors/search")
```

### 2. Use Domain Events for Cross-Domain Communication
```python
# ✅ Good: Publish event
await domain_event_bus.publish("knowledge.needed", data={...})

# ❌ Avoid: Direct function calls across domains
result = other_domain.some_function()
```

### 3. Use Shared Memory for Context Sharing
```python
# ✅ Good: Contribute to shared memory
await shared_domain_memory.contribute("knowledge", "context", data)

# ❌ Avoid: Global variables
global_context = data
```

### 4. Initialize in Correct Order
```python
# Required order:
# 1. Models
# 2. Domains
# 3. Infrastructure (Service Mesh)
# 4. World Model + RAG
```

## Summary

The RAG pipeline connects to Grace's architecture through:

1. **Service Mesh** - All service-to-service communication
2. **Domain System** - Event pub/sub, shared memory, orchestration
3. **World Model** - Central knowledge hub using RAG
4. **MCP** - External tool and LLM access
5. **API Routes** - Direct REST access

This creates a **layered, resilient, observable architecture** where RAG is both:
- **A service** (providing semantic search capabilities)
- **A consumer** (using infrastructure for communication)
- **A knowledge hub** (through World Model integration)

All components work together to provide Grace with semantic understanding and context retrieval capabilities across all domains.