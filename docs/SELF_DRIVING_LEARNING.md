# Grace Self-Driving Learning Feedback Loop

## Overview

Grace's self-driving learning feedback loop continuously monitors the entire system, autonomously diagnoses issues, clusters patterns, and launches learning missions to improve itself - all fully traceable through immutable logs and RAG context.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Self-Driving Learning Loop                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               CONTINUOUS SENSING                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Guardian Missions  │  HTM Anomalies  │  RAG Health      │  │
│  │  Remote Access      │  Agent Outcomes │  System Events   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           MESSAGE BUS (Event Streams)                     │  │
│  │  • mission.created        • htm.anomaly.detected          │  │
│  │  • rag.retrieval.failed   • agent.task.failed             │  │
│  │  • remote_access.blocked  • error.unhandled               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         LEARNING TRIAGE AGENT (30s intervals)            │  │
│  │  • Buffers events                                         │  │
│  │  • Clusters by: domain + severity + pattern              │  │
│  │  • Calculates urgency & recurrence scores                │  │
│  │  • Decides when to launch missions                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              EVENT CLUSTERS                               │  │
│  │  guardian:high:error       (urgency: 0.85)               │  │
│  │  htm:medium:anomaly        (urgency: 0.65)               │  │
│  │  remote_access:high:blocked (urgency: 0.90)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      LEARNING MISSION LAUNCHER                            │  │
│  │  • Launches missions for high-urgency clusters           │  │
│  │  • Retrieves RAG context                                 │  │
│  │  • Executes learning strategies                          │  │
│  │  • Max 3 concurrent missions                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           LEARNING EXECUTION                              │  │
│  │  Web Scraper  │  GitHub Miner  │  RAG Retrieval          │  │
│  │  Pattern Analysis  │  Knowledge Application               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │     TRACEABILITY & KNOWLEDGE STORAGE                      │  │
│  │  Immutable Log  │  RAG Context  │  Mission History        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Event Emitters

**Location**: `backend/learning_systems/event_emitters.py`

Structured event emitters for all Grace subsystems:

- **GuardianEventEmitter**: Mission events, errors, warnings
- **HTMEventEmitter**: Anomaly detection, pattern analysis
- **RAGEventEmitter**: Retrieval health, confidence issues
- **RemoteAccessEventEmitter**: Firefox, GitHub, action failures
- **AgentEventEmitter**: Task failures, build errors, remediation
- **SystemEventEmitter**: Boot failures, service degradation

**Usage**:
```python
from backend.learning_systems.event_emitters import guardian_events

await guardian_events.emit_mission_failed(
    mission_id="mission_abc",
    error="Network timeout"
)
```

### 2. Learning Triage Agent

**Location**: `backend/learning_systems/learning_triage_agent.py`

Autonomous diagnosis system that:
- Subscribes to 30+ event types
- Buffers events (processed every 30s)
- Clusters by domain + severity + pattern
- Calculates urgency & recurrence scores
- Auto-launches missions for high-priority clusters

**Event Subscriptions**:
```
Guardian: mission.created, mission.resolved, mission.failed, guardian.error
HTM: htm.anomaly.detected, htm.pattern.unusual, htm.degradation
RAG: rag.health.degraded, rag.retrieval.failed, rag.confidence.low
Remote: remote_access.action.failed, firefox.browse.failed, github.rate_limit
Agents: agent.task.failed, coding_agent.build.failed, self_healing.remediation.failed
System: kernel.boot.failed, service.degraded, error.unhandled
```

**Clustering Algorithm**:
```python
cluster_key = f"{domain}:{severity}:{pattern_type}"

# Example clusters:
# - guardian:high:error
# - htm:medium:anomaly
# - remote_access:critical:blocked
```

**Urgency Calculation**:
```python
urgency = severity_weight * 0.6 + recurrence_weight * 0.4

# Severity weights:
critical: 1.0
high: 0.8
medium: 0.5
low: 0.2

# Mission launch conditions:
- urgency >= 0.7, OR
- event_count >= 5, OR
- severity == 'critical'
```

### 3. Learning Mission Launcher

**Location**: `backend/learning_systems/learning_mission_launcher.py`

Executes learning missions:
- Max 3 concurrent missions
- Priority-based queue
- RAG context retrieval
- Multiple learning strategies
- Full traceability

**Mission Types**:
- `autonomous_learning`: Learn from clustered events
- `knowledge_gap`: Fill detected knowledge gaps
- `pattern_learning`: Learn recurring patterns
- `generic_learning`: General learning tasks

**Learning Strategies**:
```python
# 1. Web learning
await web_orchestrator.learn_and_apply(
    topic="kubernetes pod failures resolution",
    learning_type='web',
    max_sources=3
)

# 2. GitHub learning
await github_miner.learn_from_trending(
    category='python',
    max_repos=2
)

# 3. RAG retrieval
rag_context = await rag_system.retrieve(
    query="error resolution patterns",
    top_k=5
)
```

### 4. Event Clusters

**Data Structure**:
```python
@dataclass
class EventCluster:
    domain: str
    severity: str
    pattern_type: str
    event_count: int
    first_seen: datetime
    last_seen: datetime
    events: List[Dict]
    learning_mission_id: Optional[str]
    resolved: bool
```

**Lifecycle**:
1. First event → Create cluster
2. Similar events → Add to cluster
3. Urgency threshold → Launch mission
4. Mission assigned → `learning_mission_id` set
5. Resolution → `resolved = True`
6. Cleanup → Delete after 24h if resolved

## Boot Sequence

**Chunk 6.7**: Self-Driving Learning Feedback Loop

```
[CHUNK 6.7] Self-Driving Learning Feedback Loop...
  [OK] Learning Mission Launcher: Active
  [OK] Max concurrent missions: 3
  [OK] Learning Triage Agent: Active
  [OK] Event subscriptions: 30
  [OK] Triage interval: 30 seconds
  [OK] Event Emitters: Active (6 emitter types)

  🔄 Self-Driving Feedback Loop:
    • Continuous event sensing (Guardian, HTM, RAG, agents)
    • Autonomous diagnosis & clustering
    • Auto-launch learning missions
    • Full traceability (immutable log + RAG)
```

## API Endpoints

### Dashboard
```bash
GET /api/learning-feedback/dashboard

Response:
{
  "overview": {
    "status": "active",
    "health_score": 87
  },
  "statistics": {
    "events_processed": 1250,
    "clusters_created": 15,
    "active_clusters": 3,
    "missions_launched": 8,
    "missions_completed": 6
  },
  "current_state": {
    "top_clusters": [...],
    "active_missions": [...],
    "pending_missions": [...]
  }
}
```

### Get Clusters
```bash
GET /api/learning-feedback/clusters

Response:
[
  {
    "cluster_key": "guardian:high:error",
    "event_count": 12,
    "urgency_score": 0.85,
    "recurrence_score": 0.72,
    "learning_mission_id": "mission_a3f2"
  }
]
```

### Get Missions
```bash
GET /api/learning-feedback/missions?status=running

Response:
[
  {
    "mission_id": "mission_a3f2",
    "mission_type": "autonomous_learning",
    "description": "Learn to resolve error in guardian domain",
    "priority": 0.85,
    "status": "running"
  }
]
```

## Event Flow Example

### Scenario: Repeated GitHub Rate Limit Errors

1. **Event Emission**:
```python
from backend.learning_systems.event_emitters import remote_access_events

await remote_access_events.emit_github_rate_limit(
    remaining=5,
    reset_time="2025-01-20T15:30:00Z"
)
```

2. **Triage Agent Receives Event**:
```
[LEARNING-TRIAGE] Event received: github.rate_limit
Domain: remote_access
Severity: high (remaining < 10)
Pattern: blocked
```

3. **Event Clustering**:
```
Cluster key: remote_access:high:blocked
Events: 1 → 2 → 3 → 4 → 5
Urgency: 0.50 → 0.65 → 0.75 → 0.82 → 0.88
```

4. **Mission Launch Triggered** (event #3, urgency ≥ 0.7):
```
[LEARNING-TRIAGE] 🚀 Launching learning mission
Cluster: remote_access:high:blocked
Urgency: 0.75
Description: Learn to resolve blocked in remote_access domain
```

5. **Mission Execution**:
```
[MISSION-LAUNCHER] Executing mission: mission_b7a1
Query: "remote_access blocked resolution best practices"
Web sources: 3 (GitHub rate limit docs, API best practices)
GitHub repos: 0 (not relevant)
```

6. **Knowledge Application**:
```
Learned:
- Implement exponential backoff
- Cache GitHub API responses
- Use conditional requests (If-None-Match)
- Monitor rate limit headers
```

7. **Cluster Resolution**:
```
[LEARNING-TRIAGE] Cluster resolved: remote_access:high:blocked
Mission: mission_b7a1
Knowledge acquired: True
```

## Traceability

### Immutable Log
Every action logged:
```json
{
  "category": "learning_triage",
  "subcategory": "mission_launched",
  "actor": "learning_triage_agent",
  "action": "launch_mission",
  "resource": "remote_access:high:blocked",
  "timestamp": "2025-01-20T14:25:30Z",
  "data": {
    "mission_id": "mission_b7a1",
    "cluster_key": "remote_access:high:blocked",
    "urgency": 0.75,
    "event_count": 3
  }
}
```

### RAG Context
Knowledge stored with provenance:
```json
{
  "source": "learning_mission_b7a1",
  "topic": "GitHub rate limit handling",
  "content": "Implement exponential backoff...",
  "confidence": 0.92,
  "learned_from": ["GitHub docs", "API best practices"],
  "timestamp": "2025-01-20T14:30:00Z"
}
```

## Configuration

### Triage Agent
```python
# Triage interval (seconds)
TRIAGE_INTERVAL = 30

# Event buffer size
MAX_BUFFER_SIZE = 1000

# Cluster retention
CLUSTER_RETENTION_HOURS = 24
```

### Mission Launcher
```python
# Max concurrent missions
MAX_CONCURRENT_MISSIONS = 3

# Mission timeout (minutes)
MISSION_TIMEOUT = 30

# Learning sources priority
LEARNING_PRIORITY = ['web', 'github', 'rag']
```

## Monitoring

### Real-time Dashboard
```bash
# Open in browser
http://localhost:8000/api/learning-feedback/dashboard
```

### CLI Monitoring
```bash
# Watch triage agent
tail -f logs/grace.log | grep LEARNING-TRIAGE

# Watch mission launcher
tail -f logs/grace.log | grep MISSION-LAUNCHER
```

### Key Metrics
- Events processed per minute
- Active cluster count
- Mission success rate
- Average cluster urgency
- Learning coverage (% of domains)

## Integration Points

### 1. Guardian Integration
```python
# Guardian emits mission events
from backend.learning_systems.event_emitters import guardian_events

await guardian_events.emit_mission_failed(
    mission_id=mission.id,
    error=str(e)
)
```

### 2. HTM Integration
```python
# HTM detector emits anomalies
from backend.learning_systems.event_emitters import htm_events

await htm_events.emit_anomaly_detected(
    detector_id="detector_1",
    metric_name="response_time",
    anomaly_score=0.95,
    value=2500
)
```

### 3. RAG Integration
```python
# RAG emits health/retrieval events
from backend.learning_systems.event_emitters import rag_events

await rag_events.emit_retrieval_failed(
    query="kubernetes patterns",
    error="Timeout after 30s"
)
```

### 4. Agent Integration
```python
# Agents emit task outcomes
from backend.learning_systems.event_emitters import agent_events

await agent_events.emit_task_failed(
    agent="coding_agent",
    task="refactor_module",
    error="Type errors"
)
```

## Best Practices

### Event Emission
✅ **Do**:
- Emit events for all failures/errors
- Include context (IDs, metrics, errors)
- Use appropriate severity levels
- Emit success events for baseline

❌ **Don't**:
- Spam with high-frequency events
- Omit critical context
- Use inconsistent severity
- Emit sensitive data

### Cluster Management
✅ **Do**:
- Review top clusters regularly
- Manually resolve false positives
- Adjust urgency thresholds
- Monitor mission outcomes

❌ **Don't**:
- Ignore high-urgency clusters
- Let clusters grow indefinitely
- Launch duplicate missions
- Skip traceability checks

## Troubleshooting

### High Event Volume
```
Symptom: Events > 1000/min
Cause: Too many subscriptions or noisy events
Fix: Filter low-value events, increase buffer size
```

### Mission Failures
```
Symptom: missions_failed > 50%
Cause: Learning sources unavailable, poor context
Fix: Check network, verify RAG health, review queries
```

### Cluster Explosion
```
Symptom: active_clusters > 50
Cause: Too granular clustering, insufficient resolution
Fix: Adjust clustering dimensions, auto-resolve old clusters
```

## Future Enhancements

- [ ] ML-based clustering (not just rule-based)
- [ ] Predictive mission launching (before errors occur)
- [ ] Cross-cluster pattern analysis
- [ ] Federated learning across Grace instances
- [ ] Auto-tuning of urgency thresholds
- [ ] Mission priority learning from outcomes

---

**Status**: ✅ Active  
**Auto-Start**: Yes (Chunk 6.7)  
**Dependencies**: Message Bus, Immutable Log, RAG, Web Learning, GitHub Miner  
**Maintained By**: Learning Triage Agent (autonomous)
