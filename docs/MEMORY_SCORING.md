# Memory Scoring System - Architecture & Formulas

## Overview

The Memory Scoring System provides trust-based memory management for Grace's cognition layer. All outputs from loops (reflection, hunter, meta, causal, etc.) flow through this system with automatic trust scoring, decay, and garbage collection.

## Architecture

```
GraceLoopOutput
      ↓
LoopMemoryBank.store()
      ↓
MemoryScoreModel.score_on_write()
      ↓
[Trust Computation]
  - Provenance (component reputation + model certainty)
  - Consensus (quality score / specialist agreement)
  - Governance (constitutional compliance)
  - Usage (starts at 0)
      ↓
[Storage] → cognition_memory_artifacts table
      ↓
[Indexing] → cognition_memory_index table
      ↓
MemoryRef returned
```

## Trust Scoring Formulas

### Initial Trust Score (on Write)

**Total Trust = Σ(signal × weight)**

```python
trust_score = (
    provenance × 0.30 +
    consensus  × 0.25 +
    governance × 0.30 +
    usage      × 0.15
)
```

**Provenance Signal:**
```python
provenance = component_reputation × 0.6 + confidence × 0.4
```

Component reputations:
- `governance`: 0.95
- `parliament`: 0.93
- `quorum`: 0.92
- `hunter`: 0.90
- `specialist`: 0.88
- `reflection`: 0.85
- `causal`: 0.85
- `meta`: 0.80
- `temporal`: 0.75
- `default`: 0.70

**Consensus Signal:**
```python
consensus = quality_score (if available)
         or confidence (fallback)
```

**Governance Signal:**
```python
governance = 1.0  (if constitutional_compliance)
          or 0.3  (if violation)

# Penalties:
if requires_approval: governance *= 0.8
if errors: governance *= 0.7
if policy_violation: governance *= 0.5
if policy_review: governance *= 0.8
```

**Usage Signal:**
```python
usage = 0.0  (initially, grows with use)
```

### Trust Updates (on Read)

**Success Boost:**
```python
boost = 0.05 / (1 + success_count × 0.1)  # Diminishing returns
```

**Failure Penalty:**
```python
penalty = -0.08 / (1 + failure_count × 0.05)  # Diminishing severity
```

**Consistency Bonus** (if access_count > 5):
```python
if success_rate > 0.8:
    bonus = +0.02
```

**Usage Signal Update:**
```python
success_rate = success_count / access_count
frequency_score = min(1.0, access_count / 20.0)
usage_signal = success_rate × 0.7 + frequency_score × 0.3
```

### Decay Curves

Memory artifacts decay over time based on their type:

**1. Hyperbolic Decay** (slow decay for reasoning):
```python
decay_factor = 1 / (1 + k × time_elapsed)
where k = 1 / half_life_hours
```
- Used for: reasoning, decisions, reflections
- Half-life: 7-10 days
- Never reaches zero

**2. Exponential Decay** (fast decay for telemetry):
```python
decay_factor = e^(-λ × time_elapsed)
where λ = ln(2) / half_life_hours
```
- Used for: actions, predictions
- Half-life: 3-4 days
- Rapid falloff

**3. Linear Decay** (uniform decay for observations):
```python
decay_factor = max(0, 1 - (time_elapsed / total_lifetime))
where total_lifetime = half_life_hours × 2
```
- Used for: observations, generations
- Half-life: 1-2 days
- Reaches zero at 2× half-life

### Memory Ranking (on Retrieval)

**Final Rank Score:**
```python
rank = (
    trust_score     × 0.40 +  # After decay
    relevance_score × 0.35 +  # Semantic similarity
    recency_score   × 0.15 +  # Time-based
    importance      × 0.10    # User hint
)
```

**Recency Score:**
```python
age_hours = time_since_creation
recency = 1.0 / (1.0 + age_hours / 168.0)  # Decay over weeks
```

## Database Schema

### cognition_memory_artifacts

```sql
CREATE TABLE cognition_memory_artifacts (
    id INTEGER PRIMARY KEY,
    memory_ref TEXT UNIQUE,
    loop_id TEXT,
    component TEXT,
    output_type TEXT,
    
    -- Content
    result_data TEXT,  -- JSON
    reasoning_chain_id TEXT,
    
    -- Trust scores
    trust_score REAL,
    provenance_score REAL,
    consensus_score REAL,
    governance_score REAL,
    usage_score REAL,
    
    -- Decay
    decay_curve TEXT,  -- hyperbolic, exponential, linear
    half_life_hours REAL,
    
    -- Usage tracking
    access_count INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    last_accessed_at TIMESTAMP,
    
    -- Quality
    confidence REAL,
    quality_score REAL,
    importance REAL,
    
    -- Governance
    constitutional_compliance BOOLEAN,
    requires_approval BOOLEAN,
    
    -- Metadata
    domain TEXT,
    category TEXT,
    policy_tags TEXT,  -- JSON
    metadata TEXT,  -- JSON
    
    -- Lifecycle
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_archived BOOLEAN,
    is_deleted BOOLEAN,
    
    -- Verification
    verification_envelope_id TEXT,
    audit_log_id INTEGER
);
```

### cognition_trust_events

```sql
CREATE TABLE cognition_trust_events (
    id INTEGER PRIMARY KEY,
    artifact_id INTEGER REFERENCES cognition_memory_artifacts(id),
    
    event_type TEXT,  -- initial, reinforcement, penalty, decay, manual
    reason TEXT,
    
    old_trust_score REAL,
    new_trust_score REAL,
    delta REAL,
    
    -- Signal changes
    provenance_delta REAL,
    consensus_delta REAL,
    governance_delta REAL,
    usage_delta REAL,
    
    actor TEXT,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP
);
```

### cognition_memory_index

```sql
CREATE TABLE cognition_memory_index (
    id INTEGER PRIMARY KEY,
    artifact_id INTEGER REFERENCES cognition_memory_artifacts(id),
    
    index_type TEXT,  -- keyword, tag, concept, component
    index_value TEXT,
    weight REAL,
    
    created_at TIMESTAMP
);
```

### cognition_gc_log

```sql
CREATE TABLE cognition_gc_log (
    id INTEGER PRIMARY KEY,
    
    policy_name TEXT,
    artifacts_scanned INTEGER,
    artifacts_archived INTEGER,
    artifacts_deleted INTEGER,
    
    threshold_trust REAL,
    threshold_age_hours REAL,
    
    duration_ms INTEGER,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP
);
```

## API Usage

### Store Memory

```python
from backend.cognition import loop_memory_bank, GraceLoopOutput, OutputType

# Create output
output = GraceLoopOutput(
    loop_id="reflection_loop_42",
    component="reflection",
    output_type=OutputType.REASONING,
    result={"analysis": "detailed reasoning chain..."},
    confidence=0.92,
    quality_score=0.88,
    constitutional_compliance=True,
    importance=0.8
)

# Store
ref = await loop_memory_bank.store(
    output=output,
    domain="cognition",
    category="reasoning"
)

print(f"Stored: {ref.memory_ref} with trust={ref.trust_score:.3f}")
```

### Read Memories

```python
# Read by component
hits = await loop_memory_bank.read(
    query={"component": "reflection"},
    k=10,
    apply_decay=True
)

for hit in hits:
    print(f"{hit.memory_ref}: trust={hit.trust_score:.3f}, rank={hit.rank_score:.3f}")
    print(f"  Result: {hit.output.result}")

# Read with filters
hits = await loop_memory_bank.read(
    query={"output_type": "reasoning"},
    filters={
        "domain": "cognition",
        "min_trust": 0.7,
        "constitutional_compliance": True
    },
    k=20
)
```

### Update Trust

```python
# Successful use
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    outcome="success",
    reason=TrustReason.SUCCESSFUL_USE
)

# Failed use
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    outcome="failure",
    reason=TrustReason.FAILED_USE
)

# Manual adjustment
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    delta=0.1,  # Boost by 0.1
    reason=TrustReason.MANUAL_BOOST,
    actor="admin"
)
```

### Garbage Collection

```python
from backend.cognition import GCPolicy

# Archive low-trust items
policy = GCPolicy(
    name="nightly_gc",
    min_trust_threshold=0.2,  # Archive below 0.2
    max_age_hours=720,  # 30 days
    delete_threshold=0.1,  # Delete below 0.1
    dry_run=False
)

stats = await loop_memory_bank.garbage_collect(policy)
print(f"GC: scanned={stats['scanned']}, archived={stats['archived']}, deleted={stats['deleted']}")
```

### Trust History

```python
history = await loop_memory_bank.get_trust_history("mem_abc123")

for event in history:
    print(f"{event['timestamp']}: {event['event_type']}")
    print(f"  {event['old_trust']:.3f} → {event['new_trust']:.3f} (Δ={event['delta']:+.3f})")
    print(f"  Reason: {event['reason']}")
```

## Integration with Memory Service

The LoopMemoryBank integrates with the existing `memory_service.py`:

```python
# In memory_service.py or specialized service
from backend.cognition import loop_memory_bank

async def store_reasoning_output(output: GraceLoopOutput):
    """Store reasoning output with trust scoring"""
    return await loop_memory_bank.store(
        output=output,
        domain="reasoning",
        category=output.output_type.value
    )

async def retrieve_relevant_memories(component: str, k: int = 10):
    """Retrieve memories for a component"""
    return await loop_memory_bank.read(
        query={"component": component},
        filters={"constitutional_compliance": True},
        k=k,
        apply_decay=True
    )
```

## Decay Recommendations

| Output Type | Decay Curve  | Half-Life | Rationale                          |
|-------------|--------------|-----------|-------------------------------------|
| reasoning   | Hyperbolic   | 7 days    | Long-lived insights, slow decay     |
| decision    | Hyperbolic   | 5 days    | Stable decisions, gradual aging     |
| reflection  | Hyperbolic   | 10 days   | Meta-insights, very long-lived      |
| observation | Linear       | 2 days    | Raw data, uniform aging             |
| action      | Exponential  | 3 days    | Context-dependent, rapid staleness  |
| prediction  | Exponential  | 4 days    | Time-sensitive, degrades quickly    |
| generation  | Linear       | 1 day     | Ephemeral outputs, short-lived      |

## Trust Evolution Examples

### Example 1: High-Quality Reflection

```
Initial:  0.78 (high component rep, high confidence)
+5 uses:  0.83 (successful usage boosts)
+10 uses: 0.86 (consistency bonus)
+7 days:  0.74 (hyperbolic decay applied)
```

### Example 2: Low-Quality Observation

```
Initial:  0.42 (low component rep, medium confidence)
+2 uses:  0.45 (some usage benefit)
+2 fails: 0.38 (failure penalties)
+2 days:  0.19 (linear decay to near-zero)
→ Archived by GC
```

### Example 3: Constitutional Violation

```
Initial:  0.35 (governance penalty: 0.3)
+1 use:   0.36 (minimal benefit due to low base)
→ Requires manual review before further use
```

## Performance Considerations

1. **Indexing**: All queries use indexes on component, output_type, domain, category
2. **Decay**: Applied on-read to avoid expensive batch updates
3. **GC**: Run periodically (e.g., nightly) to archive/delete low-trust items
4. **Trust Events**: Logged asynchronously to avoid blocking writes

## Testing

Run comprehensive tests:

```bash
cd grace_rebuild
pytest tests/test_memory_scoring.py -v
```

Tests cover:
- Trust score computation
- Decay curves (all types)
- Read/write operations
- Trust updates
- Garbage collection
- Full lifecycle integration

## Future Enhancements

1. **Vector Similarity**: Add embedding-based relevance scoring
2. **Specialist Consensus**: Compute consensus from quorum votes
3. **Adaptive Decay**: Adjust half-life based on usage patterns
4. **Trust Clustering**: Identify high-trust vs low-trust regions
5. **Provenance Chains**: Track reasoning dependencies

---

**Status**: ✅ Complete and production-ready

**Components Delivered**:
- `MemoryScoreModel.py` - Trust & decay scoring engine
- `LoopMemoryBank.py` - Unified memory API
- `models.py` - Database schema (4 tables)
- `tests/test_memory_scoring.py` - Comprehensive test suite
- `MEMORY_SCORING.md` - This documentation

**Integration**: Wire into existing loops via `loop_memory_bank.store(output)`
