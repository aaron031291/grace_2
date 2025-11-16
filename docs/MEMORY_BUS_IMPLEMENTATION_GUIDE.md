# Memory Bus Implementation Guide

## Quick Start: Using RAG as Central Memory Bus

Grace's RAG pipeline is now the **central memory bus** for all 20+ domains and kernels. This guide shows you how to integrate.

---

## For Domain/Kernel Developers

### 1. Publishing Knowledge (Write to Memory Bus)

```python
from backend.domains import domain_event_bus
from backend.services.metadata_standards import create_artifact_metadata, Priority

# When your domain learns something, publish an artifact
await domain_event_bus.publish(
    event_type="knowledge.artifact.created",
    domain_id="your_domain",
    data={
        "artifact_type": "insight",
        "title": "New Discovery",
        "content": "Detailed description of what you learned...",
        "metadata": create_artifact_metadata(
            domain_id="your_domain",
            artifact_type="insight",
            priority=Priority.NORMAL,
            confidence=0.85,
            tags=["discovery", "pattern"],
            # Add custom fields
            source_file="analysis.py",
            pattern_id="PATTERN-123"
        )
    }
)
```

**Automatic Processing**:
- ✅ Auto-embedded by embedding service
- ✅ Auto-indexed in vector store
- ✅ Available for semantic search
- ✅ Accessible via world model if confidence > 0.8

### 2. Querying Knowledge (Read from Memory Bus)

```python
from backend.services.rag_mesh_integration import mesh_rag_search
from backend.services.metadata_standards import MetadataFilter

# Query through service mesh (automatic retries, circuit breakers)
results = await mesh_rag_search(
    query="How do we handle failures?",
    max_tokens=2000,
    top_k=10
)

# Filter by your domain
filter = (MetadataFilter()
    .domain("your_domain")
    .confidence_min(0.8)
    .time_window_hours(24)
    .build())

domain_results = await mesh_rag_search(
    query="recent incidents",
    filters=filter
)

# High-priority items only
from backend.services.metadata_standards import query_high_confidence

critical = await mesh_rag_search(
    query="critical issues",
    filters=query_high_confidence()
)
```

### 3. Capturing Learning (Feedback Loop)

```python
from backend.services.closed_loop_learning import capture_execution_outcome

# After executing any task/plan
await capture_execution_outcome(
    task_description="Deploy new feature",
    approach="Blue-green deployment",
    success=True,
    narrative="Deployed successfully with zero downtime",
    learning_points=[
        "Pre-warming cache reduced latency",
        "Health checks caught issue before user impact"
    ],
    metrics={
        "downtime_seconds": 0,
        "deploy_time_minutes": 12,
        "rollback_needed": False
    },
    domain_id="your_domain",
    confidence=0.95
)
```

**Automatic Processing**:
- ✅ Event published (insight.generated)
- ✅ Narrative embedded and indexed
- ✅ Added to world model
- ✅ Future queries can access this learning

### 4. Publishing Structured Summaries

```python
from backend.world_model import (
    publish_mission_summary,
    publish_incident_summary,
    publish_insight_summary
)

# Mission completed
await publish_mission_summary(
    domain_id="your_domain",
    mission_title="Optimize Database Queries",
    outcome="Reduced query time by 80%",
    mission_id="MISSION-001",
    confidence=0.92,
    duration_seconds=3600,
    steps_completed=5
)

# Incident resolved
await publish_incident_summary(
    domain_id="your_domain",
    incident_title="Memory Leak Detected",
    resolution_summary="Identified and fixed memory leak in caching layer",
    root_cause="Unclosed database connections",
    fix_applied="Implemented connection pooling",
    confidence=0.95,
    severity="high"
)

# Insight generated
await publish_insight_summary(
    domain_id="your_domain",
    insight_title="Pattern Detected",
    insight_text="Requests spike every Monday 9am, pre-scaling recommended",
    confidence=0.88,
    tags=["pattern", "scaling", "optimization"]
)
```

---

## For LLM/Agent Developers

### Standard Collective Intelligence Pattern

```python
from backend.services.rag_service import rag_service
from backend.model_orchestrator import model_orchestrator
from backend.services.rag_prompt_template import RAGPromptTemplate

async def answer_with_collective_intelligence(
    question: str,
    domain: str = None
) -> Dict[str, Any]:
    """
    Standard pattern for RAG-augmented responses
    
    1. Retrieve context (RAG)
    2. Build prompt (Template)
    3. Generate answer (Orchestrator)
    4. Return with citations
    """
    
    # Step 1: Retrieve context with citations
    rag_context = await rag_service.retrieve_with_citations(
        query=question,
        source_types=["world_model", "domain_summary", "execution_outcome"],
        filters={"domain_id": domain} if domain else None,
        max_tokens=2000,
        top_k=10
    )
    
    # Step 2: Build prompt using unified template
    prompt = RAGPromptTemplate.build_prompt(
        question=question,
        context_chunks=[
            {"text": chunk} 
            for chunk in rag_context["context"].split("\n\n")
        ],
        citations=rag_context["citations"],
        mode="conversational"
    )
    
    # Step 3: Model orchestrator selects best LLM
    response = await model_orchestrator.generate(
        prompt=prompt,
        domain=domain or "general",
        task_type="qa"
    )
    
    # Step 4: Package with citations
    return RAGPromptTemplate.build_response_with_citations(
        answer_text=response["text"],
        citations=rag_context["citations"]
    )
```

### Use This Pattern Everywhere

```python
# Remote access
answer = await answer_with_collective_intelligence(
    question="What's our system status?",
    domain="core"
)

# Mission planning
context = await answer_with_collective_intelligence(
    question="How should we approach this deployment?",
    domain="orchestrator"
)

# Self-reflection
reflection = await answer_with_collective_intelligence(
    question="What have I learned about failures?",
    domain="network"
)

# External MCP client
# (same knowledge, different protocol)
```

---

## Architecture Summary

### Memory Flow

```
Domain/Kernel Event
    ↓
knowledge.artifact.created
    ↓
Summary Pipeline (auto-processing)
    ↓
├─→ Embedding Service (vectorize)
├─→ Vector Store (index)
└─→ World Model (curate if confidence > 0.8)
    ↓
Single Searchable Brain
    ↓
├─→ RAG Service (retrieval + citations)
├─→ World Model (structured queries)
└─→ MCP (external access)
    ↓
Unified LLM (with context)
    ↓
Response with Citations
    ↓
Execution
    ↓
Closed-Loop Learning
    ↓
Back to Memory Bus (feedback loop)
```

### Key Components

| Component | Purpose | File |
|-----------|---------|------|
| **Vector Store** | Raw memory pool | [`backend/services/vector_store.py`](../backend/services/vector_store.py) |
| **World Model** | Curated knowledge graph | [`backend/world_model/grace_world_model.py`](../backend/world_model/grace_world_model.py) |
| **RAG Service** | Retrieval + citations | [`backend/services/rag_service.py`](../backend/services/rag_service.py) |
| **Summary Pipeline** | Auto-ingest summaries | [`backend/world_model/world_model_summary_pipeline.py`](../backend/world_model/world_model_summary_pipeline.py) |
| **Prompt Template** | Unified prompts | [`backend/services/rag_prompt_template.py`](../backend/services/rag_prompt_template.py) |
| **Mesh Integration** | Service mesh access | [`backend/services/rag_mesh_integration.py`](../backend/services/rag_mesh_integration.py) |
| **Closed-Loop Learning** | Execution feedback | [`backend/services/closed_loop_learning.py`](../backend/services/closed_loop_learning.py) |
| **Metadata Standards** | Consistent structure | [`backend/services/metadata_standards.py`](../backend/services/metadata_standards.py) |
| **MCP Integration** | External access | [`backend/world_model/mcp_integration.py`](../backend/world_model/mcp_integration.py) |

---

## Initialization

Add to [`backend/main.py`](../backend/main.py) startup:

```python
@app.on_event("startup")
async def startup_memory_bus():
    """Initialize complete memory bus"""
    
    # Initialize RAG mesh integration
    from backend.services.rag_mesh_integration import rag_mesh_integration
    await rag_mesh_integration.initialize()
    print("[OK] RAG registered with service mesh")
    
    # Initialize closed-loop learning
    from backend.services.closed_loop_learning import closed_loop_learning
    await closed_loop_learning.initialize()
    print("[OK] Closed-loop learning active")
    
    # Initialize world model summary pipeline
    from backend.world_model import world_model_summary_pipeline
    await world_model_summary_pipeline.initialize()
    print("[OK] World model summary pipeline active")
```

---

## Best Practices

### ✅ DO:
- Publish artifacts with standard metadata
- Use `MetadataBuilder` for consistent structure
- Use `mesh_rag_search()` instead of direct calls
- Capture outcomes with `capture_execution_outcome()`
- Use unified prompt templates
- Filter queries with `MetadataFilter`

### ❌ DON'T:
- Bypass the memory bus (write to vector store directly)
- Use inconsistent metadata keys
- Make direct HTTP calls to RAG (use service mesh)
- Forget to capture learning from executions
- Build custom prompts (use templates)
- Query without appropriate filters

---

## Monitoring

### Check Memory Bus Health

```python
from backend.services.rag_mesh_integration import rag_mesh_integration

health = await rag_mesh_integration.get_rag_health()
# Returns:
# - status: healthy/degraded/unhealthy
# - components: rag_service, vector_store, embedding_service, world_model
# - stats: total_vectors, indexed_embeddings, backend
```

### Check Learning Stats

```python
from backend.services.closed_loop_learning import closed_loop_learning

stats = closed_loop_learning.get_stats()
# Returns:
# - outcomes_captured
# - insights_generated
# - knowledge_items_created
```

### Check Summary Pipeline

```python
from backend.world_model import world_model_summary_pipeline

stats = world_model_summary_pipeline.get_stats()
# Returns:
# - summaries_processed
# - failed_ingestions
# - success_rate
```

---

## Complete Example: Network Domain Integration

```python
"""
Example: Network domain fully integrated with memory bus
"""

from backend.domains import domain_event_bus
from backend.services.metadata_standards import MetadataBuilder, Priority
from backend.services.closed_loop_learning import capture_execution_outcome
from backend.world_model import publish_incident_summary
from backend.services.rag_mesh_integration import mesh_rag_search

class NetworkDomain:
    """Network domain using memory bus"""
    
    async def handle_link_failure(self, link_id: str):
        """Handle link failure with full memory bus integration"""
        
        # 1. Publish detection
        await domain_event_bus.publish(
            event_type="knowledge.artifact.created",
            domain_id="network",
            data={
                "title": f"Link Failure: {link_id}",
                "content": f"Link {link_id} failed, initiating failover",
                "metadata": (MetadataBuilder("network")
                    .priority(Priority.HIGH)
                    .confidence(1.0)
                    .tags(["incident", "link_failure"])
                    .custom("link_id", link_id)
                    .build())
            }
        )
        
        # 2. Query past solutions
        past_solutions = await mesh_rag_search(
            query=f"How to handle link {link_id} failures?",
            filters={"domain_id": "network", "tags__contains": ["resolved"]},
            max_tokens=1000
        )
        
        # 3. Execute fix
        result = await self.execute_failover(link_id, context=past_solutions)
        
        # 4. Capture learning
        await capture_execution_outcome(
            task_description=f"Resolve link failure {link_id}",
            approach="Automatic failover",
            success=result.success,
            narrative=result.summary,
            learning_points=result.lessons,
            metrics=result.metrics,
            domain_id="network"
        )
        
        # 5. Publish structured summary
        if result.success:
            await publish_incident_summary(
                domain_id="network",
                incident_title=f"Link {link_id} Failure Resolved",
                resolution_summary="Automatic failover successful",
                root_cause=result.root_cause,
                fix_applied="Switched to backup link",
                confidence=0.95,
                priority="high",
                auto_remediated=True
            )
        
        return result
```

---

## API Endpoints Reference

All memory bus operations available via REST:

```bash
# Publish (via domain events or direct)
POST /api/vectors/embed
POST /world-model/add-knowledge

# Query
POST /api/vectors/search/rag
POST /world-model/query
GET  /world-model/self-knowledge
GET  /world-model/system-knowledge

# MCP
GET  /world-model/mcp/manifest
GET  /world-model/mcp/resource?uri=grace://self
POST /world-model/mcp/tool

# Mesh
POST /api/infrastructure/mesh/call
GET  /api/infrastructure/mesh/topology
GET  /api/infrastructure/mesh/stats

# Health
GET  /api/vectors/health
GET  /world-model/stats
```

---

## Complete Integration Checklist

### For Each Domain/Kernel:

- [ ] Publish artifacts via `knowledge.artifact.created` events
- [ ] Use `MetadataBuilder` or `create_artifact_metadata()`
- [ ] Query via `mesh_rag_search()` instead of direct calls
- [ ] Capture outcomes with `capture_execution_outcome()`
- [ ] Publish important summaries with `publish_*_summary()`
- [ ] Use unified prompt templates for responses
- [ ] Subscribe to relevant `insight.generated` events
- [ ] Monitor contribution stats via shared memory

### For LLM/Agent Integrations:

- [ ] Use `answer_with_collective_intelligence()` pattern
- [ ] Include domain context in queries
- [ ] Return responses with citations
- [ ] Feed outcomes back to closed-loop learning
- [ ] Use model orchestrator for best LLM selection

### For External Tools:

- [ ] Access via MCP protocol (`/world-model/mcp/*`)
- [ ] Use standard tools: `query_world_model`, `ask_grace`
- [ ] Respect confidence scores in responses
- [ ] Contribute knowledge via `add_knowledge` tool

---

## Files Modified/Created

### Core Enhancements:
1. [`backend/services/vector_store.py`](../backend/services/vector_store.py) - Added `add_text()`, `count()`, `list_collections()`
2. [`backend/world_model/world_model_summary_pipeline.py`](../backend/world_model/world_model_summary_pipeline.py) - New file
3. [`backend/services/rag_prompt_template.py`](../backend/services/rag_prompt_template.py) - New file
4. [`backend/services/rag_mesh_integration.py`](../backend/services/rag_mesh_integration.py) - New file
5. [`backend/services/closed_loop_learning.py`](../backend/services/closed_loop_learning.py) - New file
6. [`backend/services/metadata_standards.py`](../backend/services/metadata_standards.py) - New file

### Documentation:
7. [`docs/RAG_PIPELINE_AND_MCP_GUIDE.md`](RAG_PIPELINE_AND_MCP_GUIDE.md) - User guide
8. [`docs/RAG_ARCHITECTURE_INTEGRATION.md`](RAG_ARCHITECTURE_INTEGRATION.md) - Architecture
9. [`docs/RAG_AS_MEMORY_BUS.md`](RAG_AS_MEMORY_BUS.md) - Memory bus concept
10. [`docs/RAG_ENHANCEMENTS_COMPLETE.md`](RAG_ENHANCEMENTS_COMPLETE.md) - Enhancement summary
11. [`docs/MEMORY_BUS_IMPLEMENTATION_GUIDE.md`](MEMORY_BUS_IMPLEMENTATION_GUIDE.md) - This guide

### Tests:
12. [`scripts/test_rag_pipeline_complete.py`](../scripts/test_rag_pipeline_complete.py) - Test suite

---

## Quick Reference

```python
# WRITE TO MEMORY BUS
from backend.domains import domain_event_bus
await domain_event_bus.publish("knowledge.artifact.created", ...)

# READ FROM MEMORY BUS
from backend.services.rag_mesh_integration import mesh_rag_search
results = await mesh_rag_search(query="...", filters={...})

# STRUCTURED KNOWLEDGE
from backend.world_model import publish_incident_summary
await publish_incident_summary(domain_id="...", ...)

# FEEDBACK LOOP
from backend.services.closed_loop_learning import capture_execution_outcome
await capture_execution_outcome(task_description="...", ...)

# UNIFIED RESPONSE
from backend.services.rag_prompt_template import RAGPromptTemplate
prompt = RAGPromptTemplate.build_prompt(question, chunks, citations)

# STANDARD METADATA
from backend.services.metadata_standards import MetadataBuilder, Priority
metadata = MetadataBuilder("domain").priority(Priority.HIGH).build()
```

---

## Summary

Grace's RAG pipeline is now:
- ✅ **Central memory bus** for all 20+ domains
- ✅ **Unified searchable brain** (one vector store)
- ✅ **Two-tier knowledge** (raw + curated)
- ✅ **Mesh-integrated** (retries, circuit breakers)
- ✅ **Closed-loop learning** (execution → knowledge)
- ✅ **Externally accessible** (MCP protocol)
- ✅ **Metadata-disciplined** (rich filtered queries)

**Every domain writes once, knowledge available everywhere, collective intelligence emerges.**