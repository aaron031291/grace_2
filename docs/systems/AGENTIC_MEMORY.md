# Agentic Memory - Intelligent Memory Broker

## Core Principle

**Memory is NOT passive storage - it's an active, intelligent agent.**

Domains **NEVER** access raw storage directly. All memory requests go through the **agentic memory broker**, which applies:
- Governance policies
- Trust-based access control  
- Context-aware ranking
- Domain isolation
- Usage pattern learning
- Audit logging

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    10 DOMAINS                             │
│  Core │ Self-Heal │ Knowledge │ ML │ Security │ ...      │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼ request_memory()
┌──────────────────────────────────────────────────────────┐
│              AGENTIC MEMORY BROKER                        │
│                                                            │
│  1. Validate Request (quotas, permissions)                │
│  2. Trust Check (determine access level)                  │
│  3. Retrieve Candidates (from storage)                    │
│  4. Apply Governance Filters (policy-aware)               │
│  5. Context Ranking (semantic relevance)                  │
│  6. Log Access (immutable log)                            │
│  7. Learn Pattern (optimize future requests)              │
│  8. Return with Explanation                               │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                MEMORY STORAGE                             │
│  Episodic │ Semantic │ Procedural │ Working Memory       │
└──────────────────────────────────────────────────────────┘
```

## Memory Types

### 1. **Episodic Memory**
- Event sequences and experiences
- "What happened when"
- Timeline-based retrieval
- Examples: Healing cycles, incidents, decisions

### 2. **Semantic Memory**
- Facts, concepts, and knowledge
- "What we know"
- Tag and concept-based retrieval
- Examples: System facts, learned patterns, documentation

### 3. **Procedural Memory**
- Skills and how-to knowledge
- "How to do things"
- Playbooks, procedures, best practices
- Examples: Recovery playbooks, automation scripts

### 4. **Working Memory**
- Short-term, current context
- "What we're thinking about now"
- Temporary, fast access
- Examples: Current cycle state, active plans

## Access Levels

### FULL
- Complete access to own domain's memories
- No filtering (except expired entries)
- Fastest retrieval

### CROSS_DOMAIN  
- Access to memories across all domains
- Requires trust score >= 0.8
- Additional governance checks
- Used for: Cross-domain correlation, learning

### RESTRICTED
- Limited to own domain
- Sensitive content filtered
- Additional policy checks
- Default for new/untrusted actors

### DENIED
- No access
- Governance block
- Quota exceeded
- Logged as violation

## Request Flow Example

### Step 1: Domain Requests Memory

```python
# Self-healing domain requests recent successful playbooks
from backend.agent_core import DomainAdapter

response = await self.request_memory(
    memory_type="procedural",
    query="successful latency reduction playbooks",
    context={
        "service": "api_cluster",
        "issue_type": "latency_spike",
        "time_of_day": "peak_hours"
    },
    limit=5
)
```

### Step 2: Agentic Memory Processes

```
[Validate] ✓ Quota OK (self_heal: 15/50 requests this minute)
[Trust Check] Trust score: 0.92 → Access level: FULL
[Retrieve] Found 47 procedural memories
[Filter] Applied policies: none (full access to own domain)
[Rank] Context alignment:
  - playbook_scale_up: 0.92 (recent success, same service, peak context)
  - playbook_warm_cache: 0.85 (similar issue, different service)
  - playbook_restart: 0.62 (older, different context)
[Log] Signed access to immutable log
[Learn] Pattern: self_heal often requests "latency" procedurals during peak
[Return] Top 5 ranked by relevance
```

### Step 3: Domain Receives Response

```python
{
    "memories": [
        {
            "id": "mem_self_heal_1705334400",
            "content": {
                "playbook": "scale_up_instances",
                "steps": [...],
                "success_rate": 0.88,
                "avg_duration": 85
            },
            "tags": ["latency", "scaling", "api_cluster"],
            "timestamp": "2025-01-15T14:30:00Z",
            "relevance": 0.92,
            "domain": "self_heal"
        },
        ...
    ],
    "total_found": 47,
    "filtered": 0,
    "access_level": "full",
    "explanation": "Retrieved 5 procedural memories | Access level: full | Avg relevance: 0.84",
    "policies_applied": []
}
```

## Governance Policies

### Policy 1: Domain Isolation

**Rule:** Domains can only access their own memories unless cross-domain approved.

```python
# Domain A requesting domain B's memories
if access_level != CROSS_DOMAIN and memory.domain != requesting_domain:
    filter_out()  # Blocked by domain isolation
```

**Override:** Set `include_cross_domain=True` and have trust score >= 0.8

### Policy 2: Sensitive Content

**Rule:** Memories tagged "sensitive" require higher access level.

```python
if "sensitive" in memory.tags and access_level == RESTRICTED:
    filter_out()  # Blocked for restricted access
```

### Policy 3: Time Expiry

**Rule:** Memories can have expiration times.

```python
if memory.metadata["max_age_hours"] and age > max_age:
    filter_out()  # Expired
```

**Use case:** Temporary working memory, time-sensitive decisions

### Policy 4: Rate Limiting

**Rule:** Each domain has request quota (per minute).

```python
domain_quotas = {
    "knowledge": 200,  # High quota (search-heavy)
    "ml": 150,         # Medium (training data)
    "self_heal": 50,   # Lower (episodic lookups)
    ...
}
```

## Context-Aware Ranking

Memories are ranked by **4 factors**:

### 1. Recency (30% weight)
- Newer memories score higher
- Decay over 1 week
- `score = max(0, 1 - age_hours / 168)`

### 2. Access Frequency (20% weight)
- Popular memories are useful
- Saturates at 100 accesses
- `score = min(1.0, access_count / 100)`

### 3. Tag Matching (30% weight)
- Semantic similarity
- Query terms in memory tags
- `score = tag_matches / total_tags`

### 4. Context Alignment (20% weight)
- Request context matches memory metadata
- Key-value matching
- `score = matching_keys / total_context_keys`

### Example

```
Query: "latency reduction playbooks"
Context: {"service": "api_cluster", "time": "peak"}

Memory 1:
  Tags: ["latency", "scaling", "api_cluster"]  # 3/3 match
  Age: 2 hours  # Very recent
  Access count: 45  # Popular
  Metadata: {"service": "api_cluster", "time": "peak"}  # 2/2 match
  → Total score: 0.92

Memory 2:
  Tags: ["latency", "cache"]  # 1/2 match
  Age: 72 hours  # Older
  Access count: 12  # Less popular
  Metadata: {"service": "cache_cluster"}  # 0/2 match
  → Total score: 0.54
```

## Cross-Domain Memory

### Use Case: Learning from Other Domains

Knowledge domain wants to learn from self-healing outcomes:

```python
response = await self.request_memory(
    memory_type="episodic",
    query="successful automated recoveries",
    context={"result": "success"},
    limit=20,
    include_cross_domain=True  # Request cross-domain access
)
```

**Agentic Memory Processing:**

1. **Trust Check:** Knowledge domain trust score = 0.85 ✓  
2. **Access Level:** CROSS_DOMAIN granted  
3. **Retrieve:** Scan self_heal, security, ml domains  
4. **Filter:** Remove sensitive playbooks (policy applied)  
5. **Return:** 18 memories (2 filtered by governance)

```python
{
    "memories": [...],  # From self_heal, ml domains
    "total_found": 20,
    "filtered": 2,  # Sensitive playbooks removed
    "access_level": "cross_domain",
    "policies_applied": ["sensitive_content_filter"]
}
```

## Learning from Access Patterns

Agentic memory learns and optimizes:

### Pattern 1: Frequent Queries

```
Domain: self_heal
Pattern: "latency playbooks" queried 45 times
Context: Always during {"time": "peak_hours"}
Optimization: Pre-rank latency playbooks during peak
```

### Pattern 2: Cross-Domain Correlations

```
When knowledge domain queries "threat patterns",
they also query security domain memories 80% of time
Optimization: Suggest cross-domain search proactively
```

### Pattern 3: Temporal Patterns

```
ML domain requests training data at 02:00 daily
Optimization: Pre-cache overnight for faster morning access
```

## Usage Examples

### Example 1: Store Healing Outcome

```python
# Self-healing domain stores outcome
await self.store_memory(
    memory_type="episodic",
    content={
        "cycle_id": "cycle_20250115_143000",
        "playbook": "scale_up_instances",
        "result": "success",
        "duration_seconds": 85.3,
        "service": "api_cluster"
    },
    tags=["healing", "latency", "scaling", "success"]
)
```

### Example 2: Retrieve Similar Incidents

```python
# Knowledge domain learning from incidents
response = await self.request_memory(
    memory_type="episodic",
    query="database failures last 30 days",
    context={
        "issue_type": "database",
        "severity": "high"
    },
    limit=10,
    include_cross_domain=True  # Learn from security domain too
)

for memory in response["memories"]:
    # Analyze patterns across domains
    print(f"Incident: {memory['content']['title']}")
    print(f"Domain: {memory['domain']}")
    print(f"Resolution: {memory['content']['resolution']}")
```

### Example 3: Procedural Knowledge Retrieval

```python
# Transcendence domain needs deployment playbook
response = await self.request_memory(
    memory_type="procedural",
    query="canary deployment with rollback",
    context={
        "environment": "production",
        "risk_level": "high"
    },
    limit=3
)

playbook = response["memories"][0]["content"]
# Use highest-ranked playbook
```

## Audit & Compliance

Every memory access is logged to immutable log:

```python
# Immutable log entry
{
    "sequence": 5042,
    "actor": "self_heal",
    "action": "memory_accessed",
    "resource": "self_heal",
    "payload": {
        "request_id": "self_heal_1705334425",
        "memory_type": "procedural",
        "query": "successful latency reduction playbooks",
        "access_level": "full",
        "results_count": 5,
        "applied_policies": [],
        "cross_domain": false
    },
    "result": "accessed",
    "signature": "f8a4c9b2...",
    "timestamp": "2025-01-15T14:33:45Z"
}
```

**Audit Questions Answered:**

- Who accessed what memories?
- What policies were applied?
- Were any governance violations?
- What was filtered and why?
- Cross-domain access patterns?

## Statistics & Monitoring

```python
from backend.agentic_memory import agentic_memory

stats = agentic_memory.get_stats()

# {
#     "total_requests": 1247,
#     "by_domain": {
#         "self_heal": 156,
#         "knowledge": 482,
#         "ml": 309,
#         ...
#     },
#     "by_type": {
#         "episodic": 445,
#         "semantic": 512,
#         "procedural": 223,
#         "working": 67
#     },
#     "filtered_count": 38,
#     "cross_domain_requests": 94,
#     "working_memory_size": 3847,
#     "patterns_learned": 23,
#     "domains_active": 8
# }
```

## Benefits

### 1. **Single Policy-Aware Substrate**
- One place to apply governance
- Consistent trust enforcement
- No policy fragmentation

### 2. **Domain Isolation with Flexibility**
- Domains isolated by default
- Cross-domain when approved
- No direct storage access

### 3. **Intelligent Retrieval**
- Context-aware ranking
- Semantic search
- Relevance scoring

### 4. **Continuous Learning**
- Access pattern optimization
- Query prediction
- Relevance tuning

### 5. **Complete Auditability**
- Every access logged
- Governance trail
- Compliance ready

### 6. **No Splintering**
- Single memory service
- Unified governance
- Consistent behavior

## Configuration

```python
# Domain quotas (requests per minute)
MEMORY_QUOTAS = {
    "knowledge": 200,  # Search-heavy
    "ml": 150,
    "transcendence": 120,
    "self_heal": 50,
    "default": 50
}

# Cross-domain access threshold
CROSS_DOMAIN_TRUST_THRESHOLD = 0.8

# Ranking weights
RANKING_WEIGHTS = {
    "recency": 0.30,
    "frequency": 0.20,
    "tag_matching": 0.30,
    "context_alignment": 0.20
}

# Memory expiry defaults
DEFAULT_EPISODIC_MAX_AGE_HOURS = 168  # 1 week
DEFAULT_WORKING_MAX_AGE_HOURS = 24    # 1 day
```

---

**Memory is now agentic - an intelligent broker that ensures all 10 domains access memory through a single, policy-aware substrate with governance, trust, and audit built in.**
