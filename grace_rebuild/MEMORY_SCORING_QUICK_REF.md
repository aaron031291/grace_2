# Memory Scoring - Quick Reference

## Import

```python
from backend.cognition import (
    loop_memory_bank,
    memory_integration,
    GraceLoopOutput,
    OutputType,
    GCPolicy,
    TrustReason
)
```

## Store Memory

```python
# Method 1: Direct
output = GraceLoopOutput(
    loop_id="loop_1",
    component="reflection",
    output_type=OutputType.REASONING,
    result={"analysis": "..."},
    confidence=0.9
)
ref = await loop_memory_bank.store(output)

# Method 2: Helper
ref_str = await memory_integration.store_reasoning(
    loop_id="loop_1",
    component="reflection",
    result={"analysis": "..."},
    confidence=0.9
)
```

## Retrieve Memories

```python
# By component
hits = await loop_memory_bank.read(
    query={"component": "reflection"},
    k=10,
    filters={"min_trust": 0.7}
)

# Helper method
memories = await memory_integration.recall_by_component(
    component="reflection",
    k=10,
    min_trust=0.6
)

# Access results
for hit in hits:
    print(f"{hit.memory_ref}: trust={hit.trust_score:.3f}")
    print(f"Result: {hit.output.result}")
```

## Update Trust

```python
# On successful use
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    outcome="success"
)

# On failure
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    outcome="failure"
)

# Manual boost
await loop_memory_bank.update_trust(
    memory_ref="mem_abc123",
    delta=0.1,
    reason=TrustReason.MANUAL_BOOST
)

# Helper methods
await memory_integration.mark_successful_use("mem_abc123")
await memory_integration.mark_failed_use("mem_abc123")
await memory_integration.boost_trust("mem_abc123", amount=0.1)
```

## Garbage Collection

```python
policy = GCPolicy(
    name="daily_gc",
    min_trust_threshold=0.2,
    max_age_hours=720,  # 30 days
    delete_threshold=0.1,
    dry_run=False
)

stats = await loop_memory_bank.garbage_collect(policy)
```

## Trust History

```python
history = await loop_memory_bank.get_trust_history("mem_abc123")
for event in history:
    print(f"{event['timestamp']}: {event['old_trust']:.3f} → {event['new_trust']:.3f}")
```

## Component Stats

```python
stats = await memory_integration.get_component_stats("reflection")
# Returns: count, avg_trust, avg_confidence, avg_rank, total_accesses
```

## Decorator

```python
@remember_output(component="hunter", output_type="decision")
async def make_decision(task):
    return {"decision": "approve"}
```

## Trust Formulas

```python
# Initial trust
trust = (
    provenance * 0.30 +
    consensus  * 0.25 +
    governance * 0.30 +
    usage      * 0.15
)

# Provenance
provenance = component_reputation * 0.6 + confidence * 0.4

# Success boost
boost = 0.05 / (1 + success_count * 0.1)

# Failure penalty
penalty = -0.08 / (1 + failure_count * 0.05)

# Final rank
rank = trust * 0.40 + relevance * 0.35 + recency * 0.15 + importance * 0.10
```

## Decay Curves

- **Hyperbolic** (reasoning): `1 / (1 + k*t)` - slow decay
- **Exponential** (actions): `e^(-λt)` - fast decay  
- **Linear** (observations): `max(0, 1 - t/T)` - uniform decay

## Run Tests

```bash
# Migration
python migrate_memory_scoring.py

# Tests
pytest tests/test_memory_scoring.py -v
```
