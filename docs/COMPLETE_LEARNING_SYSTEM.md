# Grace Complete Learning System
## Self-Driving, Tiered Execution, and Governance

This document provides a comprehensive overview of Grace's three integrated learning and execution systems.

---

## System Overview

Grace now has a complete autonomous learning and execution pipeline with full governance:

```
┌─────────────────────────────────────────────────────────────────────┐
│                   COMPLETE LEARNING SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  1. SELF-DRIVING LEARNING FEEDBACK LOOP                       │ │
│  │     • Continuous event sensing                                │ │
│  │     • Autonomous diagnosis & clustering                       │ │
│  │     • Auto-launch learning missions                           │ │
│  │     ✅ Chunk 6.7 | 30s triage intervals                       │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                           │                                         │
│                           ▼                                         │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  2. TIERED AGENT EXECUTION                                    │ │
│  │     • research → design → implement → test → deploy           │ │
│  │     • Playbooks as first-class tools                          │ │
│  │     • Guardian pause/resume/override                          │ │
│  │     ✅ Chunk 0.75 | Max 2 concurrent pipelines                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                           │                                         │
│                           ▼                                         │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  3. GOVERNANCE & SAFETY                                       │ │
│  │     • RBAC service accounts                                   │ │
│  │     • Risk-based auto-approval                                │ │
│  │     • Guardian escalation                                     │ │
│  │     ✅ Chunk 6.8 | All logged to immutable log                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Boot Sequence

### Chunk 6.5: Remote Learning Systems
```
[CHUNK 6.5] Remote Learning Systems (Internet & GitHub Access)...
  [OK] Firefox Agent: ENABLED
  [OK] Remote Computer Access: Active
  [OK] Web Scraper: Active (via Firefox)
  [OK] GitHub Knowledge Miner: Active

  🌐 Grace can now learn from:
    • Internet (via Firefox on your PC)
    • GitHub repositories
    • Stack Overflow, arXiv, Kaggle, etc.
```

### Chunk 6.7: Self-Driving Learning Feedback Loop
```
[CHUNK 6.7] Self-Driving Learning Feedback Loop...
  [OK] Learning Mission Launcher: Active
  [OK] Learning Triage Agent: Active
  [OK] Event subscriptions: 30
  [OK] Event Emitters: Active (6 types)

  🔄 Self-Driving Feedback Loop:
    • Continuous event sensing
    • Autonomous diagnosis & clustering
    • Auto-launch learning missions
    • Full traceability
```

### Chunk 0.75: Tiered Agent Orchestrator
```
[CHUNK 0.75] Tiered Agent Orchestrator...
  [OK] Agent Orchestrator: Online
  [OK] Max concurrent pipelines: 2
  [OK] Pipeline phases: research → design → implement → test → deploy
  [OK] Guardian oversight: Active (pause/resume/override)
  [OK] Playbooks: First-class agent tools
```

### Chunk 6.8: Governance & Safety Systems
```
[CHUNK 6.8] Governance & Safety Systems...
  [OK] RBAC System: Active
  [OK] Service accounts: 4
  [OK] Inline Approval Engine: Active
  [OK] Auto-approval threshold: 0.3
  [OK] Escalation threshold: 0.7

  🛡️ Safety & Governance:
    • RBAC: Service account permissions
    • Risk scoring: Auto-approve low risk
    • Guardian escalation: High-risk actions
    • Immutable log: All decisions audited
```

---

## Complete Flow Example

### Scenario: Repeated Deployment Failures

**1. Event Detection** (Self-Driving Learning)
```
[EVENT] deployment_agent.build.failed (3 occurrences in 5 minutes)

Triage Agent:
  → Cluster: agent:high:error
  → Urgency: 0.82 (high)
  → Recurrence: 0.75 (frequent)
  → Decision: Launch learning mission
```

**2. Mission Launch** (With Governance)
```
[MISSION-LAUNCHER] Mission mission_abc123 launched
Task: Learn to resolve error in agent domain

[APPROVAL-ENGINE] Processing approval request
  → Requester: learning_mission_service
  → Resource: staging_model:mission_abc123
  → Action: modify

[RBAC-SYSTEM] Permission check
  → Service account: learning_mission_service
  → Role: learning_mission
  → Permissions: read, write ✓
  → Scope: staging_model:* ✓
  → Result: ALLOWED

[APPROVAL-ENGINE] Risk calculation
  → Resource risk: 0.3 (staging)
  → Action risk: 0.6 (modify)
  → Combined: 0.42
  → Decision: PENDING (medium risk)

[APPROVAL-ENGINE] Manual approval required
  → Request ID: approval_20250120_143000
  → Waiting for human approval...
```

**3. Manual Approval**
```
POST /api/governance/approve
{
  "request_id": "approval_20250120_143000",
  "approved": true,
  "approved_by": "admin",
}

[APPROVAL-ENGINE] ✅ Manually approved
[IMMUTABLE-LOG] Decision logged

[MISSION-LAUNCHER] Approval granted, proceeding...
```

**4. Tiered Execution** (Agent Pipeline)
```
[AGENT-ORCHESTRATOR] Pipeline started: pipeline_def456
Phases: research → design → implement → test

PHASE 1: Research
  → Web: "deployment failure patterns kubernetes"
  → GitHub: kubernetes/deployment repo
  → Artifact: research_doc

PHASE 2: Design
  → Input: research artifacts
  → Playbook: create_design_spec
  → Artifact: design_spec (retry logic + health checks)

PHASE 3: Implement
  → Playbook: implement_code
  → Output: deployment_agent_v2.py
  → Artifact: code

PHASE 4: Test
  → Playbook: run_tests
  → Result: 35/35 passed ✓
  → Artifact: test_results
```

**5. Guardian Oversight**
```
[GUARDIAN] Monitoring pipeline: pipeline_def456
  → Current phase: implement
  → Risk level: acceptable
  → No intervention needed

[ARTIFACT-FEEDBACK] Feeding to learning loop
  → Event: agent.artifact.created
  → Artifacts: 4 (research, design, code, tests)
  → Playbooks used: 3
```

**6. Knowledge Application**
```
[MISSION-LAUNCHER] Mission completed
  → Knowledge acquired: Deployment retry patterns
  → Artifacts: 4
  → Duration: 18.5s

[LEARNING-TRIAGE] Cluster resolved
  → Mission: mission_abc123
  → Knowledge stored in RAG with provenance
  → Next deployment failure will use learned fix
```

---

## Safety Guarantees

### 1. Permission Checks (RBAC)
```python
# Every action checks permissions
allowed = await rbac_system.check_permission(
    principal='learning_mission_service',
    resource_type='production_db',
    resource_id='customers',
    action='write'
)

if not allowed:
    # Denied & logged
    # Guardian notified
    # Mission blocked
```

### 2. Risk-Based Approval
```python
risk_score = calculate_risk(
    resource='production_model',  # 0.8 weight
    action='deploy',               # 0.8 weight
    context={'previous_failures': 0}
)
# risk_score = 0.8 (high)

if risk_score > 0.7:
    # Escalate to Guardian
    # Human approval required
    # Cannot proceed without approval
```

### 3. Immutable Audit Trail
```json
{
  "category": "governance",
  "subcategory": "approval_decision",
  "timestamp": "2025-01-20T14:30:00Z",
  "actor": "learning_mission_service",
  "action": "request_approval",
  "resource": "production_model:gpt-4",
  "decision": "escalated",
  "risk_score": 0.85,
  "escalated_to": "guardian"
}
```

### 4. Guardian Control
```python
# Guardian can pause any pipeline
await message_bus.publish('guardian.pause_pipeline', {
    'pipeline_id': 'pipeline_abc'
})

# Guardian can override decisions
await message_bus.publish('guardian.override_pipeline', {
    'pipeline_id': 'pipeline_abc',
    'override': {'skip_deploy': True}
})
```

---

## Service Accounts

### Default Accounts Created at Boot

**1. learning_mission_service**
- **Role**: learning_mission
- **Permissions**: read, write
- **Scope**: vector_store:*, staging_model:*, /grace_training/*
- **Purpose**: Learning missions

**2. agent_pipeline_service**
- **Role**: agent_pipeline
- **Permissions**: read, write, execute
- **Scope**: /backend/*, /frontend/*, test_environment:*
- **Purpose**: Agent pipelines

**3. self_healing_service**
- **Role**: self_healing
- **Permissions**: read, write, modify
- **Scope**: staging_db:*, /config/*, /logs/*
- **Purpose**: Self-healing operations

**4. guardian_service**
- **Role**: guardian
- **Permissions**: read, write, modify, execute, deploy
- **Scope**: *:* (all resources)
- **Purpose**: Guardian oversight

---

## API Endpoints

### Learning Feedback Loop
```bash
GET /api/learning-feedback/dashboard
GET /api/learning-feedback/clusters
GET /api/learning-feedback/missions/{mission_id}
```

### Agent Pipelines
```bash
POST /api/agent-pipeline/execute
GET /api/agent-pipeline/pipelines/{pipeline_id}
POST /api/agent-pipeline/guardian/control
```

### Governance
```bash
GET /api/governance/dashboard
GET /api/governance/pending-approvals
POST /api/governance/approve
GET /api/governance/service-accounts
```

---

## Configuration

### Approval Thresholds
```python
# Auto-approve if risk < 0.3
auto_approval_threshold = 0.3

# Escalate to Guardian if risk > 0.7
escalation_threshold = 0.7
```

### Risk Weights
```python
# Resource types
resource_risk_weights = {
    'production_db': 0.9,      # Very high risk
    'production_model': 0.8,   # High risk
    'staging_db': 0.4,         # Medium risk
    'test_environment': 0.1    # Low risk
}

# Actions
action_risk_weights = {
    'read': 0.1,     # Very low risk
    'write': 0.5,    # Medium risk
    'delete': 0.9,   # Very high risk
    'deploy': 0.8    # High risk
}
```

### Pipeline Settings
```python
# Max concurrent pipelines
max_concurrent_pipelines = 2

# Auto-recovery on failure
auto_recover_on_failure = True
```

---

## Monitoring

### Real-Time Dashboards

**Learning Feedback**:
- http://localhost:8000/api/learning-feedback/dashboard
- Shows: active clusters, missions, event stats

**Agent Pipelines**:
- http://localhost:8000/api/agent-pipeline/dashboard
- Shows: running pipelines, artifacts, success rate

**Governance**:
- http://localhost:8000/api/governance/dashboard
- Shows: pending approvals, permission stats, risk distribution

### CLI Monitoring
```bash
# Watch learning triage
tail -f logs/grace.log | grep LEARNING-TRIAGE

# Watch approvals
tail -f logs/grace.log | grep APPROVAL-ENGINE

# Watch RBAC denials
tail -f logs/grace.log | grep "Permission denied"
```

---

## Key Metrics

### Learning System
- Events processed per minute
- Mission launch rate
- Cluster urgency scores
- Learning success rate

### Execution System
- Pipeline success rate
- Average execution time
- Artifacts produced
- Playbook usage

### Governance System
- Auto-approval rate
- Escalation rate
- Permission grant rate
- Manual approval time

---

## Safety Features

✅ **RBAC**: Every operation checked against service account permissions  
✅ **Risk Scoring**: Automatic risk calculation for all actions  
✅ **Auto-Approval**: Low-risk actions proceed immediately  
✅ **Guardian Escalation**: High-risk actions require Guardian approval  
✅ **Immutable Log**: All decisions permanently recorded  
✅ **Scope Limiting**: Service accounts can only access permitted resources  
✅ **Fail-Safe**: Denies on error or uncertainty  
✅ **Audit Trail**: Complete provenance for compliance  

---

## Documentation Links

- **Remote Learning**: [REMOTE_LEARNING.md](./REMOTE_LEARNING.md)
- **Self-Driving Learning**: [SELF_DRIVING_LEARNING.md](./SELF_DRIVING_LEARNING.md)
- **Tiered Agents**: [TIERED_AGENT_EXECUTION.md](./TIERED_AGENT_EXECUTION.md)

---

**Status**: ✅ All Systems Active  
**Auto-Start**: Yes (Chunks 6.5, 6.7, 0.75, 6.8)  
**Guardian Integration**: Full oversight and control  
**Governance**: RBAC + Risk-based + Immutable audit  
**Learning**: Continuous, autonomous, and safe
