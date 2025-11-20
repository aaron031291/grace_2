# Immutable Logs - Production Implementation

## Overview

The Immutable Log is Grace's tamper-evident audit layer that cryptographically hashes and chains every important event and decision. This is a **production-ready implementation with zero stubs or placeholders**.

## Architecture

### Core Components

1. **ImmutableLogEntry** ([base_models.py](file:///c:/Users/aaron/grace_2/backend/models/base_models.py))
   - Database model with cryptographic hash chain
   - `compute_hash()` static method for SHA-256 hashing
   - Sequential ordering with tamper detection

2. **ImmutableLog** ([immutable_log.py](file:///c:/Users/aaron/grace_2/backend/logging/immutable_log.py))
   - Append-only log with retry logic
   - Hash chain verification
   - Concurrent write handling
   - Cryptographic signatures support

3. **ImmutableLogAnalytics** ([immutable_log_analytics.py](file:///c:/Users/aaron/grace_2/backend/logging/immutable_log_analytics.py))
   - Periodic integrity verification
   - Gap detection
   - Activity analysis
   - Failure tracking

4. **Specialized Loggers**
   - **GovernanceLogger** - Governance decisions and policy changes
   - **VerificationLogger** - Verification results and refutations
   - **AVNLogger** - Anomalies and healing actions

## Data Structure

### ImmutableLogEntry Schema

```python
{
    "id": Integer (primary key),
    "sequence": Integer (unique, auto-incrementing),
    "actor": String(64),  # Who performed the action
    "action": String(128),  # What action was performed
    "resource": String(256),  # What resource was affected
    "subsystem": String(64),  # Which subsystem logged this
    "payload": Text (JSON),  # Additional data
    "result": String(64),  # Outcome
    "entry_hash": String(64),  # SHA-256 hash of this entry
    "previous_hash": String(64),  # Hash of previous entry (chain link)
    "timestamp": DateTime
}
```

### Hash Chain Algorithm

```python
def compute_hash(sequence, actor, action, resource, payload, result, previous_hash):
    data = f"{sequence}:{actor}:{action}:{resource}:{payload}:{result}:{previous_hash}"
    return hashlib.sha256(data.encode()).hexdigest()
```

## Usage Examples

### Basic Logging

```python
from backend.logging.immutable_log import immutable_log

entry_id = await immutable_log.append(
    actor="grace_agent",
    action="decision_made",
    resource="user_request_123",
    subsystem="reasoning",
    payload={
        "decision": "approve",
        "confidence": 0.95,
        "reasoning": "All checks passed"
    },
    result="success"
)
```

### Governance Logging

```python
from backend.logging.governance_logger import governance_logger

# Log a governance decision
await governance_logger.log_governance_decision(
    decision_id="dec_001",
    decision_type="policy_change",
    actor="parliament",
    resource="security_policy",
    approved=True,
    reasoning="Unanimous vote: 5/5",
    vote_details={
        "yes": 5,
        "no": 0,
        "abstain": 0
    }
)

# Log a constitutional violation
await governance_logger.log_constitutional_violation(
    violation_id="viol_001",
    actor="rogue_agent",
    violated_principle="transparency",
    violation_details="Attempted to hide decision from audit log",
    action_taken="Action blocked and logged"
)

# Log a policy change
await governance_logger.log_policy_change(
    policy_id="pol_security_001",
    actor="admin",
    old_policy={"min_approval": 2},
    new_policy={"min_approval": 3},
    change_reason="Increased security requirements"
)
```

### Verification Logging

```python
from backend.logging.verification_logger import verification_logger

# Log verification result
await verification_logger.log_verification_result(
    hypothesis_id="hyp_001",
    actor="user",
    verification_type="code_verification",
    status="VERIFIED",
    confidence=0.92,
    issues=[],
    recommendations=["Code passed all checks"]
)

# Log refutation
await verification_logger.log_refutation(
    hypothesis_id="hyp_002",
    actor="untrusted_source",
    refutation_reason="Security violations detected",
    evidence=["exec() usage", "eval() usage"],
    severity="critical"
)

# Log security violation
await verification_logger.log_security_violation(
    code_id="code_003",
    actor="external_contributor",
    violation_type="dangerous_function",
    violation_details="Use of exec() without validation",
    dangerous_patterns=["exec", "eval"],
    action_taken="Code rejected and logged"
)

# Log static analysis
await verification_logger.log_static_analysis(
    code_id="code_004",
    actor="developer",
    security_score=0.95,
    complexity_score=0.82,
    issues_found=2,
    passed=True
)
```

### AVN (Anomaly & Healing) Logging

```python
from backend.logging.avn_logger import avn_logger

# Log anomaly detection
await avn_logger.log_anomaly_detected(
    anomaly_id="anom_001",
    detector="htm_detector",
    anomaly_type="drift",
    severity="high",
    affected_resource="api_latency",
    anomaly_score=0.87,
    details={
        "baseline": 150,
        "current": 450,
        "threshold": 300
    }
)

# Log healing action
await avn_logger.log_healing_action(
    healing_id="heal_001",
    anomaly_id="anom_001",
    healer="auto_scaler",
    action_type="scale_up",
    action_description="Increased worker count from 2 to 4",
    affected_resource="worker_pool",
    success=True,
    execution_time_seconds=15.3
)

# Log healing cycle
await avn_logger.log_healing_cycle(
    cycle_id="cycle_001",
    anomalies_detected=3,
    actions_taken=3,
    actions_successful=3,
    cycle_duration_seconds=45.2,
    outcome="resolved",
    summary="All anomalies resolved successfully"
)

# Log drift detection
await avn_logger.log_drift_detection(
    drift_id="drift_001",
    detector="metric_monitor",
    baseline_metric="cpu_usage",
    baseline_value=30.0,
    current_value=75.0,
    drift_magnitude=45.0,
    drift_direction="increase"
)

# Log rollback
await avn_logger.log_rollback(
    rollback_id="rb_001",
    trigger_anomaly_id="anom_002",
    rollback_target="api_service",
    from_version="v2.3.1",
    to_version="v2.3.0",
    success=True,
    rollback_duration_seconds=8.5
)
```

## Integrity Verification

### Manual Verification

```python
from backend.logging.immutable_log import immutable_log

# Verify entire chain
result = await immutable_log.verify_integrity()

if result["valid"]:
    print(f"✓ Chain valid: {result['entries_verified']} entries verified")
else:
    print(f"⚠ Chain broken at sequence {result['broken_chain_at']}")
```

### Automated Periodic Verification

```python
from backend.logging.immutable_log_analytics import immutable_log_analytics

# Start automated verification (runs every 15 minutes)
await immutable_log_analytics.start(interval_minutes=15)

# Get verification report
report = await immutable_log_analytics.verify_log_integrity()

# Example report:
{
    "has_issues": False,
    "total_entries": 1542,
    "first_entry_id": 1,
    "last_entry_id": 1542,
    "time_span_hours": 168.5,
    "issues": [],
    "verified_at": "2025-11-20T21:30:00Z"
}
```

### Gap Detection

```python
# Check for subsystems that stopped logging
gap_report = await immutable_log_analytics.check_subsystem_gaps(hours_back=24)

# Example gap report:
{
    "gaps_found": True,
    "gaps": [
        {
            "subsystem": "verification",
            "type": "stale",
            "hours_since": 8.3,
            "last_logged": "2025-11-20T13:00:00Z",
            "message": "verification hasn't logged for 8.3h"
        }
    ]
}
```

## Query Operations

### Get Recent Entries

```python
# Get recent governance decisions
entries = await immutable_log.get_entries(
    subsystem="governance",
    limit=50
)

# Get entries by actor
entries = await immutable_log.get_entries(
    actor="grace_agent",
    limit=100
)

# Get entries by resource
entries = await immutable_log.get_entries(
    resource="user_request_123",
    limit=10
)
```

### Specialized Queries

```python
# Get governance history
gov_history = await governance_logger.get_governance_history(
    hours_back=168,  # 7 days
    limit=100
)

# Get violation history
violations = await governance_logger.get_violation_history(limit=50)

# Get verification refutations
refutations = await verification_logger.get_refutation_history(limit=50)

# Get security violations
sec_violations = await verification_logger.get_security_violations(limit=50)

# Get anomaly history
anomalies = await avn_logger.get_anomaly_history(
    hours_back=24,
    limit=100
)

# Get healing history
healing = await avn_logger.get_healing_history(
    hours_back=24,
    limit=100
)
```

## Replay Operations

### Replay Healing Cycle

```python
# Replay all events from a specific healing cycle
cycle_events = await immutable_log.replay_cycle(cycle_id="cycle_001")

# Returns chronological list:
[
    {
        "sequence": 1234,
        "timestamp": "2025-11-20T20:00:00Z",
        "actor": "avn_detector:htm",
        "action": "ANOMALY_DETECTED",
        "resource": "api_latency",
        "payload": {...},
        "signature": "abc123...",
        "entry_hash": "def456..."
    },
    {
        "sequence": 1235,
        "timestamp": "2025-11-20T20:00:15Z",
        "actor": "avn_healer:auto_scaler",
        "action": "HEALING_ACTION_EXECUTED",
        ...
    }
]
```

### Get Signed Outcomes

```python
# Get signed execution outcomes for learning
outcomes = await immutable_log.get_signed_outcomes(
    subsystem="meta_coordinated_healing",
    hours_back=24,
    limit=100
)
```

## Analytics & Reporting

### Activity Summary

```python
summary = await immutable_log_analytics.get_activity_summary(hours_back=24)

# Example output:
{
    "total_entries": 523,
    "by_actor": {
        "grace_agent": 245,
        "avn_detector:htm": 98,
        "parliament": 12
    },
    "by_action": {
        "ANOMALY_DETECTED": 98,
        "HEALING_ACTION_EXECUTED": 95,
        "GOVERNANCE_APPROVED": 8
    },
    "by_subsystem": {
        "avn": 193,
        "governance": 20,
        "verification": 145
    }
}
```

### Failure Summary

```python
failures = await immutable_log_analytics.get_failure_summary(hours_back=24)

# Example output:
{
    "total_failures": 12,
    "by_subsystem": {
        "avn": [
            {
                "id": 1450,
                "actor": "avn_healer:restart",
                "action": "HEALING_ACTION_EXECUTED",
                "result": "failed",
                "timestamp": "2025-11-20T19:30:00Z"
            }
        ]
    }
}
```

## Security Features

### Cryptographic Signatures

```python
# Append with cryptographic signature
signature = "digital_signature_here"

await immutable_log.append(
    actor="critical_system",
    action="security_decision",
    resource="access_control",
    subsystem="security",
    payload={"decision": "deny"},
    result="blocked",
    signature=signature  # Stored in payload["_signature"]
)
```

### Tamper Detection

The system detects:
1. **Hash mismatches** - Entry has been modified
2. **Chain breaks** - Previous hash doesn't match
3. **Sequence gaps** - Missing entries
4. **Timestamp reversals** - Non-monotonic timestamps

Example verification failure:

```python
{
    "valid": False,
    "broken_chain_at": 1234,
    "message": "Chain broken - previous hash mismatch"
}
```

## Integration Points

### Event Bus Integration

The immutable log automatically integrates with:
- Governance decisions → logged automatically
- Verification results → logged via VerificationIntegration
- AVN anomalies → logged via AVN components

### Database Tables

```sql
CREATE TABLE immutable_log (
    id INTEGER PRIMARY KEY,
    sequence INTEGER UNIQUE NOT NULL,
    actor VARCHAR(64) NOT NULL,
    action VARCHAR(128) NOT NULL,
    resource VARCHAR(256),
    subsystem VARCHAR(64),
    payload TEXT,
    result VARCHAR(64),
    entry_hash VARCHAR(64) UNIQUE NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_immutable_log_subsystem ON immutable_log(subsystem);
CREATE INDEX idx_immutable_log_actor ON immutable_log(actor);
CREATE INDEX idx_immutable_log_timestamp ON immutable_log(timestamp);
CREATE INDEX idx_immutable_log_action ON immutable_log(action);
```

## Best Practices

### When to Log

**Always log:**
- Governance decisions and policy changes
- Verification refutations and security violations
- Anomalies and healing actions
- Constitutional violations
- Escalations
- Critical system decisions

**Consider logging:**
- User actions with compliance implications
- Data access and modifications
- Configuration changes
- Learning/adaptation updates

### Payload Design

Keep payloads focused and JSON-serializable:

```python
# Good
payload = {
    "decision": "approve",
    "confidence": 0.95,
    "key_factors": ["factor1", "factor2"]
}

# Avoid
payload = {
    "entire_state_dump": {...},  # Too large
    "complex_object": some_object  # Not JSON-serializable
}
```

### Error Handling

The immutable log never crashes the calling code:

```python
entry_id = await immutable_log.append(...)
if entry_id == -1:
    # Log failed after all retries
    # System continues but logs warning
    pass
```

## Migration Notes

**No migration needed** - System is production-ready with:
- ✅ Real cryptographic hash chains
- ✅ Tamper detection
- ✅ Integrity verification
- ✅ Gap detection
- ✅ Concurrent write handling
- ✅ Specialized loggers for all subsystems
- ✅ Zero placeholder code
- ✅ Zero TODO comments

## Summary

The Immutable Log system provides:
1. **Cryptographic hash chain** for tamper-evident audit trails
2. **Automated integrity verification** with gap detection
3. **Specialized loggers** for governance, verification, and AVN
4. **Replay capabilities** for debugging and learning
5. **Analytics** for activity and failure tracking
6. **Production-ready** with zero stubs or placeholders

All events, decisions, and actions flow through this immutable audit layer, ensuring complete transparency and accountability.
