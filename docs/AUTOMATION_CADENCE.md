# Grace Automation Cadence System

## Overview

Grace's learning triage agent adapts its execution cadence based on system state - fast loops during boot for critical infrastructure issues, slower loops during steady state for efficiency.

## Cadence Modes

### 1. Boot Phase (Fast Loop)

**Duration**: From startup until "GRACE IS READY"  
**Interval**: 15 seconds  
**Focus**: Critical infrastructure issues only  
**Priority Threshold**: 0.7 (high)

**Filtered Domains**:
- ✅ `guardian` - Guardian issues
- ✅ `system` - System-level errors
- ✅ `kernel` - Kernel boot failures
- ❌ Other domains (skipped during boot)

**Purpose**:
- Rapid response to boot-blocking issues
- HTM anomalies during startup
- Guardian boot check failures
- Port conflicts, network issues
- Critical configuration errors

### 2. Steady State (Slow Loop)

**Duration**: After "GRACE IS READY"  
**Interval**: 3-5 minutes (variable)  
**Focus**: All issues  
**Priority Threshold**: 0.3 (medium)

**All Domains Processed**:
- Guardian, HTM, RAG, remote access, agents, system

**Purpose**:
- Continuous improvement
- Learning from all failures
- Pattern recognition across domains
- Non-critical optimization

---

## Boot Phase Behavior

### Timeline

```
[0s]    Grace starts
        └─> Learning Triage Agent: BOOT PHASE
            └─> Interval: 15s
            └─> Threshold: 0.7 (critical only)
            └─> Domains: guardian, system, kernel
            
[15s]   First triage (boot phase)
        └─> Process critical infrastructure events only
        └─> Launch missions for urgent clusters
        
[30s]   Second triage (boot phase)
[45s]   Third triage (boot phase)
...

[~60s]  All chunks booted successfully
        └─> Event published: grace.boot.complete
        
[~75s]  Learning Triage Agent: TRANSITION TO STEADY STATE
        ⚡ Boot phase complete after N triage cycles
        ⚡ New interval: 180s (3-5 min variable)
        ⚡ Priority threshold: 0.3 (lower bar)
```

### Boot Phase Example

```
[0s] BOOT STARTS
[LEARNING-TRIAGE] [BOOT] Processing 3 events (interval: 15s)
  → Cluster: guardian:high:error (urgency: 0.85)
  → Infrastructure: YES ✓
  → Launch mission: mission_boot_001

[15s] BOOT CONTINUES
[LEARNING-TRIAGE] [BOOT] Processing 5 events (interval: 15s)
  → Cluster: rag:medium:anomaly (urgency: 0.65)
  → Infrastructure: NO ✗
  → Skipped (not infrastructure)

[30s] BOOT CONTINUES
[LEARNING-TRIAGE] [BOOT] Processing 2 events (interval: 15s)
  → Cluster: system:critical:error (urgency: 0.95)
  → Infrastructure: YES ✓
  → Launch mission: mission_boot_002

[60s] BOOT COMPLETE
================================================================================
[LEARNING-TRIAGE] ⚡ TRANSITION TO STEADY STATE
[LEARNING-TRIAGE] Boot phase complete after 4 triage cycles
[LEARNING-TRIAGE] New interval: 180s (3-5 min variable)
[LEARNING-TRIAGE] Priority threshold: 0.3 (lower bar)
================================================================================
```

---

## Steady State Behavior

### Timeline

```
[0s]    Transition complete
        └─> Learning Triage Agent: STEADY STATE
            └─> Interval: 180s (base, varies 180-300s)
            └─> Threshold: 0.3 (medium)
            └─> Domains: all
            
[180s]  First steady triage
        └─> Process ALL events
        └─> Launch missions for medium+ priority
        └─> Next interval: random(180, 300) → 240s
        
[420s]  Second steady triage (180 + 240)
        └─> Process ALL events
        └─> Next interval: random(180, 300) → 195s
        
[615s]  Third steady triage
...
```

### Steady State Example

```
[LEARNING-TRIAGE] [STEADY] Processing 12 events (interval: 240s)
  → Cluster: agent:medium:error (urgency: 0.55)
  → Priority threshold: 0.3 ✓
  → Launch mission: mission_steady_001
  
  → Cluster: remote_access:low:blocked (urgency: 0.25)
  → Priority threshold: 0.3 ✗
  → Skipped (below threshold)
  
  → Cluster: rag:high:degradation (urgency: 0.75)
  → Priority threshold: 0.3 ✓
  → Launch mission: mission_steady_002

Next triage in: 285s (4m 45s)
```

---

## Mission Prioritization

### Scoring System

**Combined Score** = (Risk × 0.4) + (Impact × 0.6)

#### Risk Score (0.0 - 1.0)

**Domain Risk**:
```python
{
    'guardian': 0.9,      # Very high risk
    'system': 0.8,        # High risk
    'agent': 0.6,         # Medium-high risk
    'remote_access': 0.5, # Medium risk
    'rag': 0.4,           # Medium-low risk
    'unknown': 0.5        # Default medium
}
```

**Severity Multiplier**:
```python
{
    'critical': 1.5,  # 50% increase
    'high': 1.2,      # 20% increase
    'medium': 1.0,    # No change
    'low': 0.7        # 30% decrease
}
```

**Example**:
```
Domain: guardian (0.9)
Severity: critical (1.5x)
Risk Score = min(1.0, 0.9 × 1.5) = 1.0
```

#### Impact Score (0.0 - 1.0)

**Components**:
```python
# Event count (max at 10 events)
count_score = min(1.0, event_count / 10)

# Urgency from triage
urgency = context.get('urgency_score', priority)

# Recurrence
recurrence = context.get('recurrence_score', 0.5)

# Combined
impact = (count_score × 0.3) + (urgency × 0.4) + (recurrence × 0.3)
```

**Example**:
```
Event count: 8 → count_score = 0.8
Urgency: 0.75
Recurrence: 0.60

Impact = (0.8 × 0.3) + (0.75 × 0.4) + (0.60 × 0.3)
       = 0.24 + 0.30 + 0.18
       = 0.72
```

#### Combined Example

```
Risk Score: 1.0
Impact Score: 0.72

Combined Score = (1.0 × 0.4) + (0.72 × 0.6)
               = 0.40 + 0.432
               = 0.832

Priority: HIGH (will execute first)
```

---

## Mission Suspension

### When Missions Are Suspended

1. **Guardian Request**
   - Critical system issue requires resources
   - Guardian calls for suspension of low-value missions

2. **Governance Request**
   - High-risk operation needs full resources
   - Low-value missions suspended temporarily

3. **Resource Constraints**
   - Max concurrent missions reached
   - Only highest combined_score missions run

### Suspension Logic

```python
# Can only suspend PENDING missions
if mission.status == 'pending':
    mission.suspended = True
    mission.suspension_reason = reason
    stats['missions_suspended'] += 1
```

### Suspension Example

```
[MISSION-LAUNCHER] Processing 5 pending missions
  Mission A: combined_score = 0.85 (running)
  Mission B: combined_score = 0.72 (running)
  Mission C: combined_score = 0.45 (pending)
  Mission D: combined_score = 0.32 (pending)
  Mission E: combined_score = 0.15 (pending)

[GUARDIAN] Requests suspension of low-value missions

[MISSION-LAUNCHER] Suspending missions with score < 0.4
  Mission D: SUSPENDED (score 0.32, reason: guardian_resource_request)
  Mission E: SUSPENDED (score 0.15, reason: guardian_resource_request)

[MISSION-LAUNCHER] 2 missions active, 1 pending (not suspended), 2 suspended
```

---

## Configuration

### Cadence Settings

```python
# Boot phase interval (seconds)
boot_interval = 15

# Steady state base interval (seconds)
steady_interval = 180

# Steady state varies between (seconds)
steady_min = 180  # 3 minutes
steady_max = 300  # 5 minutes
```

### Priority Thresholds

```python
# Boot phase: only critical issues
boot_priority_threshold = 0.7

# Steady state: medium+ issues
steady_priority_threshold = 0.3
```

### Mission Limits

```python
# Max concurrent missions
max_concurrent_missions = 3

# Auto-recovery on failure
auto_recover_on_failure = True
```

---

## Statistics & Monitoring

### Triage Stats

```json
{
  "events_processed": 1250,
  "clusters_created": 45,
  "missions_launched": 28,
  "missions_suspended": 5,
  "triage_count": 67,
  "boot_phase": false,
  "last_triage": "2025-01-20T15:30:00Z"
}
```

### Mission Stats

```json
{
  "missions_launched": 28,
  "missions_completed": 22,
  "missions_failed": 3,
  "missions_suspended": 5,
  "active_missions": 2,
  "pending_missions": 1
}
```

### API Endpoints

```bash
# Check current phase
GET /api/learning-feedback/status
{
  "triage_agent": {
    "boot_phase": false,
    "current_interval": 240,
    "triage_count": 67
  }
}

# Get prioritized missions
GET /api/learning-feedback/missions
[
  {
    "mission_id": "mission_abc",
    "combined_score": 0.85,
    "risk_score": 1.0,
    "impact_score": 0.75,
    "status": "running"
  },
  ...
]

# Suspend mission
POST /api/learning-feedback/missions/{id}/suspend
{
  "reason": "Guardian resource request",
  "suspended_by": "admin"
}
```

---

## Best Practices

### Boot Phase

✅ **Do**:
- Monitor critical infrastructure clusters
- Launch high-urgency missions immediately
- Keep missions focused on boot-blocking issues

❌ **Don't**:
- Launch learning missions for non-infrastructure
- Process low-priority clusters
- Run long-running missions during boot

### Steady State

✅ **Do**:
- Process all domains
- Use combined scoring for prioritization
- Allow 3-5 min variable intervals
- Suspend low-value missions when needed

❌ **Don't**:
- Ignore medium-priority clusters
- Run too many concurrent missions
- Keep suspended missions indefinitely

### Mission Prioritization

✅ **Do**:
- Trust the combined score
- Review suspended missions periodically
- Resume when resources available

❌ **Don't**:
- Override scoring without reason
- Suspend high-score missions
- Ignore Guardian suspension requests

---

## Transition Log Example

```
[0s] BOOT STARTS
[LEARNING-TRIAGE] Boot phase: 15s interval
[LEARNING-TRIAGE] Subscriptions: 30
[LEARNING-TRIAGE] Autonomous diagnosis: Active

[15s] [BOOT] Triage #1
[30s] [BOOT] Triage #2
[45s] [BOOT] Triage #3
[60s] [BOOT] Triage #4

[60s] BOOT COMPLETE
================================================================================
[LEARNING-TRIAGE] ⚡ TRANSITION TO STEADY STATE
[LEARNING-TRIAGE] Boot phase complete after 4 triage cycles
[LEARNING-TRIAGE] New interval: 180s (3-5 min variable)
[LEARNING-TRIAGE] Priority threshold: 0.3 (lower bar)
================================================================================

[240s] [STEADY] Triage #5 (180s after transition)
[525s] [STEADY] Triage #6 (285s interval)
[720s] [STEADY] Triage #7 (195s interval)
[1005s] [STEADY] Triage #8 (285s interval)
```

---

**Status**: ✅ Active  
**Auto-Start**: Yes (Chunk 6.7)  
**Phase Transition**: Automatic on "GRACE IS READY"  
**Mission Prioritization**: Risk/Impact scoring  
**Suspension**: Guardian/governance controlled
