# RAG as Grace's Central Memory Bus

## Overview

Grace's RAG pipeline serves as the **central memory bus** for all domains and kernels. Every component writes to one searchable brain, reads from one collective intelligence.

```
┌─────────────────────────────────────────────────────────────┐
│                   GRACE MEMORY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         ALL DOMAINS & KERNELS (20+)                  │   │
│  │  Network | ML | Security | Temporal | Parliament... │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │ publish artifacts                 │
│                         ↓                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           KNOWLEDGE MEMORY BUS (RAG)                 │   │
│  │  - knowledge.artifact.created events                 │   │
│  │  - Auto-embedding & indexing                         │   │
│  │  - Unified vector store                              │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
│         ┌───────────────┴───────────────┐                   │
│         ↓                               ↓                    │
│  ┌──────────────┐              ┌──────────────────┐        │
│  │ Vector Store │              │   World Model    │        │
│  │ (Raw Memory) │              │ (Curated Facts)  │        │
│  │ - Everything │              │ - Structured     │        │
│  │ - Searchable │              │ - Tagged         │        │
│  └──────────────┘              │ - Confidence     │        │
│         ↑                      └──────────────────┘        │
│         │                               ↑                    │
│         └───────────────┬───────────────┘                   │
│                         │ unified retrieval                  │
│                         ↓                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  UNIFIED LLM + MODEL ORCHESTRATOR                    │   │
│  │  - RAG context + citations                           │   │
│  │  - Best model selection (15+ LLMs)                   │   │
│  │  - Collective intelligence responses                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ↓ feedback                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       LEARNING LOOP (Closed-Loop)                    │   │
│  │  - Capture outcomes                                  │   │
│  │  - Publish new artifacts                             │   │
│  │  - Feed back to memory bus                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. RAG as Memory Bus for Every Domain

### Publishing Knowledge Artifacts

**Every domain/kernel publishes via event bus**:

```python
from backend.domains import domain_event_bus

# Domain publishes artifact
await domain_event_bus.publish(
    event_type="knowledge.artifact.created",
    domain_id="network",
    data={
        "artifact_type": "incident_resolution",
        "title": "Link Failure Resolved",
        "content": "Hardware failure detected. Automatic failover to backup link successful.",
        "metadata": {
            "confidence": 0.95,
            "priority": "high",
            "tags": ["network", "failover", "resolved"],
            "incident_id": "INC-001"
        }
    }
)
```

### Automatic Vector Integration

**Vector integration handles everything automatically**:

```python
# In backend/world_model/world_model_summary_pipeline.py
# Already subscribes to knowledge.artifact.created

async def _handle_knowledge_discovered(self, event):
    """Auto-embed, chunk, and index"""
    data = event.data
    
    # Auto-ingest to vector store (chunking + embedding)
    await vector_store.add_text(
        content=data["content"],
        source=f"{data['domain_id']}/{data['artifact_type']}",
        metadata=data.get("metadata", {})
    )
    
    # Also add to world model if high confidence
    if data.get("metadata", {}).get("confidence", 0) > 0.8:
        await grace_world_model.add_knowledge(
            category='domain',
            content=data["content"],
            source=data["domain_id"],
            confidence=data["metadata"]["confidence"],
            tags=data["metadata"].get("tags", [])
        )
```

### One Searchable Brain

All knowledge from all domains lands in the same vector store:

```python
from backend.services.rag_service import rag_service

# Search across ALL domains
results = await rag_service.retrieve(
    query="How do we handle failures?",
    top_k=10
)

# Search specific domain
results = await rag_service.retrieve(
    query="network incidents",
    filters={"domain_id": "network"},
    top_k=10
)
```

---

## 2. World Model as Canonical Knowledge Graph

### Two-Tier Architecture

**Vector Store** = Raw memory pool (everything)
**World Model** = Curated knowledge graph (facts with metadata)

```python
from backend.world_model import grace_world_model

# Add curated fact to world model
# Automatically also indexes in vector store
knowledge_id = await grace_world_model.add_knowledge(
    category='domain',  # domain, self, system, user, temporal
    content='Grace uses blue-green deployment for zero-downtime releases',
    source='deployment_logs',
    confidence=0.95,
    tags=['deployment', 'best-practice', 'zero-downtime'],
    metadata={
        'domain_id': 'orchestrator',
        'verified': True,
        'success_rate': 0.98
    }
)
```

### Query Both Layers

```python
# Query raw vector store (everything)
raw_results = await rag_service.retrieve(query="deployment strategies")

# Query world model (curated facts)
facts = await grace_world_model.query(
    query="deployment strategies",
    category='domain',
    min_confidence=0.8
)

# Combined approach (recommended)
context = await rag_service.retrieve_with_citations(
    query="What are our deployment best practices?",
    source_types=["world_model", "domain_summary"],
    max_tokens=2000
)
```

---

## 3. Unified LLM = Orchestrator + RAG Context

### Standard Pattern for Collective Responses

**Use this pattern everywhere** (remote access, mission planning, self-reflection):

```python
from backend.services.rag_service import rag_service
from backend.model_orchestrator import model_orchestrator
from backend.services.rag_prompt_template import RAGPromptTemplate

async def collective_response(question: str, domain: str = None) -> Dict[str, Any]:
    """
    Standard pattern for collective intelligence responses
    
    1. Retrieve context with citations (RAG)
    2. Select best model (Orchestrator)
    3. Generate with citations
    """
    
    # Step 1: RAG retrieval with metadata filtering
    filters = {"domain_id": domain} if domain else None
    
    rag_context = await rag_service.retrieve_with_citations(
        query=question,
        source_types=["world_model", "domain_summary", "execution_outcome"],
        filters=filters,
        max_tokens=2000,
        top_k=10
    )
    
    # Step 2: Build prompt using unified template
    prompt = RAGPromptTemplate.build_prompt(
        question=question,
        context_chunks=[{"text": c} for c in rag_context["context"].split("\n\n")],
        citations=rag_context["citations"],
        mode="conversational",
        system_context=f"Domain: {domain}" if domain else None
    )
    
    # Step 3: Model orchestrator selects best LLM (from 15+ models)
    response = await model_orchestrator.generate(
        prompt=prompt,
        domain=domain or "general",
        task_type="qa",
        quality_target=0.85
    )
    
    # Step 4: Package response with citations
    return {
        "answer": response["text"],
        "citations": rag_context["citations"],
        "formatted_citations": RAGPromptTemplate.format_citations(rag_context["citations"]),
        "model_used": response.get("model"),
        "confidence": response.get("confidence", 0.8),
        "sources": rag_context["sources"]
    }
```

### Use Everywhere

```python
# Remote access answer
answer = await collective_response(
    question="What's our current system status?",
    domain="core"
)

# Mission planning
plan_context = await collective_response(
    question="How should we approach this deployment?",
    domain="orchestrator"
)

# Self-reflection
reflection = await collective_response(
    question="What have I learned about network failures?",
    domain="network"
)
```

---

## 4. Learning Feedback Loop

### Capture → Publish → Ingest → Available for RAG

```python
from backend.services.closed_loop_learning import capture_execution_outcome

# After any execution
async def execute_and_learn(task, approach):
    """Execute task and capture learning"""
    
    # 1. Execute
    result = await execute_task(task, approach)
    
    # 2. Capture outcome
    outcome_result = await capture_execution_outcome(
        task_description=task.description,
        approach=approach,
        success=result.success,
        narrative=result.summary,
        learning_points=result.lessons,
        metrics=result.metrics,
        domain_id=task.domain,
        confidence=result.confidence
    )
    
    # 3. Automatically:
    #    - Published as insight.generated event
    #    - Ingested to vector store
    #    - Added to world model
    #    - Available for future RAG queries
    
    return result


# High-value summaries become structured facts
if result.confidence > 0.9:
    await grace_world_model.add_knowledge(
        category='domain',
        content=f"Successful approach: {approach} for {task.type}",
        source=f"{task.domain}_execution",
        confidence=result.confidence,
        tags=['solution', 'verified', task.type]
    )
```

### Governance Integration

Track knowledge

 contributions:

```python
from backend.domains import shared_domain_memory

# Domains contribute knowledge
await shared_domain_memory.contribute(
    domain_id="network",
    key="incident_resolutions",
    value=incident_data,
    confidence=0.95,
    tags=["incident", "resolved"]
)

# Governance tracks collective intelligence
stats = shared_domain_memory.get_domain_stats("network")
# Returns: contributions, confidence_avg, most_accessed, etc.

# Metric: which domains contribute most helpful knowledge
contribution_scores = {
    domain: stats["contributions_count"] * stats["average_confidence"]
    for domain, stats in shared_domain_memory.get_all_stats().items()
}
```

---

## 5. Domain-Specific RAG Views

### Metadata Filtering

Each domain can query shared pool + its own slice:

```python
from backend.services.metadata_standards import MetadataFilter

# Network domain's view
network_filter = (MetadataFilter()
    .domain("network")
    .confidence_min(0.8)
    .time_window_hours(168)  # Last week
    .has_tag("incident")
    .build())

network_knowledge = await rag_service.retrieve(
    query="recent network issues",
    filters=network_filter
)

# Cross-domain query (shared pool)
cross_domain_filter = (MetadataFilter()
    .priority_min(Priority.HIGH)
    .confidence_min(0.9)
    .time_window_hours(24)
    .build())

critical_knowledge = await rag_service.retrieve(
    query="critical incidents",
    filters=cross_domain_filter
)
```

---

## 6. Mesh-Aware Routing

### Any Kernel Can Hit RAG via Service Mesh

```python
from backend.infrastructure import service_mesh

# Automatic health checks, retries, circuit breakers
async def kernel_query_knowledge(query: str, kernel_id: str):
    """Any kernel queries RAG through mesh"""
    
    result = await service_mesh.call_service(
        capability="rag",
        path="/search/rag",
        method="POST",
        data={
            "query": query,
            "max_tokens": 2000,
            "source_types": ["world_model", "domain_summary"],
            "requested_by": kernel_id
        }
    )
    
    return result
```

### Service Registration

```python
# RAG automatically registered at startup
from backend.services.rag_mesh_integration import rag_mesh_integration

await rag_mesh_integration.initialize()
# Registers:
# - capability="rag" (semantic search, context retrieval)
# - capability="world_model" (structured knowledge graph)
# - Health signals from all components
# - Circuit breakers, retry logic
```

---

## 7. MCP Exposure

### External LLMs as First-Class Citizens

```python
from backend.world_model import mcp_integration

# Initialize MCP (already done at startup)
await mcp_integration.initialize()

# External tools can now:
# 1. Query world model
manifest = mcp_integration.get_mcp_manifest()

# 2. Access resources
self_knowledge = await mcp_integration.handle_resource_request('grace://self')
system_knowledge = await mcp_integration.handle_resource_request('grace://system')
domain_knowledge = await mcp_integration.handle_resource_request('grace://domain/network')

# 3. Call tools
search_result = await mcp_integration.handle_tool_call(
    'query_world_model',
    {'query': 'deployment strategies', 'top_k': 5}
)

answer = await mcp_integration.handle_tool_call(
    'ask_grace',
    {'question': 'What are your capabilities?'}
)
```

### External Integration Example

```python
# External LLM (Claude, GPT-4) can query Grace's collective intelligence

# Via REST API
POST /world-model/mcp/tool
{
    "tool_name": "query_world_model",
    "parameters": {
        "query": "How does Grace handle network failures?",
        "category": "domain",
        "top_k": 5
    }
}

# Response includes citations to Grace's internal knowledge
{
    "tool": "query_world_model",
    "results": [
        {
            "knowledge_id": "abc123",
            "content": "Grace uses automatic failover...",
            "confidence": 0.95,
            "source": "network_domain",
            "tags": ["network", "failover", "resilience"]
        }
    ]
}
```

---

## Complete Integration Example

### Scenario: Network Failure → Learning → Future Use

```python
# 1. INCIDENT OCCURS
# Network domain detects failure
incident = {
    "type": "link_failure",
    "affected_systems": ["router_01"],
    "detected_at": datetime.utcnow()
}

# 2. DOMAIN PUBLISHES ARTIFACT
from backend.domains import domain_event_bus
from backend.services.metadata_standards import create_artifact_metadata

await domain_event_bus.publish(
    event_type="knowledge.artifact.created",
    domain_id="network",
    data={
        "artifact_type": "incident_detection",
        "title": "Link Failure Detected",
        "content": f"Router link failure detected: {incident}",
        "metadata": create_artifact_metadata(
            domain_id="network",
            artifact_type="incident",
            priority=Priority.HIGH,
            confidence=1.0,
            tags=["incident", "network", "link_failure"]
        )
    }
)

# 3. AUTO-RESOLUTION EXECUTED
outcome = await network_domain.execute_failover(incident)

# 4. LEARNING CAPTURED
from backend.services.closed_loop_learning import capture_execution_outcome

await capture_execution_outcome(
    task_description="Resolve link failure",
    approach="Automatic failover to backup link",
    success=True,
    narrative="Backup link activated successfully, zero downtime",
    learning_points=[
        "Automatic failover works reliably",
        "Backup link capacity sufficient",
        "Monitoring detected issue within 2 seconds"
    ],
    metrics={
        "downtime_seconds": 0,
        "failover_time_seconds": 1.8,
        "detection_time_seconds": 2.1
    },
    domain_id="network",
    confidence=0.98
)

# 5. KNOWLEDGE PROMOTED TO WORLD MODEL
from backend.world_model import publish_incident_summary

await publish_incident_summary(
    domain_id="network",
    incident_title="Link Failure - Auto-Resolved",
    resolution_summary="Automatic failover successful, zero downtime",
    root_cause="Hardware failure on router_01 link",
    fix_applied="Activated backup link, scheduled hardware replacement",
    confidence=0.95,
    priority="high",
    tags=["network", "failover", "auto-resolved"]
)

# 6. FUTURE QUERY CAN ACCESS THIS KNOWLEDGE
# Days later, another kernel asks:
from backend.services.rag_mesh_integration import mesh_rag_search

results = await mesh_rag_search(
    query="How does Grace handle network link failures?",
    filters=query_by_domain("network", confidence_min=0.9),
    max_tokens=2000
)

# Response includes:
# - Original incident detection
# - Execution outcome with metrics
# - World model curated fact
# - All with citations and confidence scores

# 7. UNIFIED LLM GENERATES ANSWER
answer = await collective_response(
    question="How does Grace handle network failures?",
    domain="network"
)

# Answer includes:
# "Based on our experience [1], Grace uses automatic failover to backup links.
# In a recent incident [2], this resolved a link failure in 1.8 seconds with
# zero downtime. The system has a 98% confidence [3] in this approach..."
#
# Citations:
# [1] Network domain knowledge (confidence: 0.95)
# [2] Execution outcome: exec_network_001 (confidence: 0.98)
# [3] World model fact: knowledge_def456 (confidence: 0.95)
```

---

## Summary: One Memory Bus for All

**Write Once, Available Everywhere**:
- Domains publish artifacts once
- Automatic embedding & indexing
- Available via RAG, world model, MCP
- Unified LLM uses for responses
- Learning feeds back into system

**Benefits**:
1. **No Duplication**: One vector store, one truth
2. **Collective Intelligence**: All domains contribute
3. **Consistent Access**: Same RAG pattern everywhere
4. **Automatic Learning**: Outcomes become knowledge
5. **Rich Queries**: Metadata-filtered semantic search
6. **External Access**: MCP for external LLMs

**Grace's knowledge is**: Searchable, Citable, Collective, Ever-Growing, Accessible to All.