# Grace - Complete Architecture

## 🏛️ System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  Chat | Dashboard | IDE | Memory Browser | Audit Viewer     │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI)                      │
│     Authentication | CORS | Rate Limiting                   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     TRIGGER MESH                             │
│        Event Bus connecting all subsystems                   │
│    Subscribers: Governance, Hunter, MLDL, AVN, Healing      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────┬──────────────────┬─────────────────────┐
│   MEMORY         │  IMMUTABLE LOG   │   SUBSYSTEMS        │
│   (Workspace)    │  (Ground Truth)  │                     │
├──────────────────┼──────────────────┼─────────────────────┤
│ • Artifacts      │ • Hash Chain     │ • Governance        │
│ • Knowledge      │ • Audit Trail    │ • Hunter            │
│ • Tasks/Goals    │ • Tamper-Proof   │ • Self-Healing      │
│ • Reflections    │ • Forensics      │ • MLDL              │
│ • Chat History   │ • Compliance     │ • AVN/AVM           │
│ • Sandbox Files  │                  │ • Remedy Engine     │
└──────────────────┴──────────────────┴─────────────────────┘
```

## 📚 Memory vs Immutable Log

### Memory (Structured Workspace)
**Purpose:** Active data Grace works with  
**Operations:** Create, Read, Update, Delete (governed)  
**Storage:** memory_artifacts table  
**Organized by:** domain/category/path (file-explorer style)

**What's stored:**
- Knowledge artifacts (`security/protocols.md`)
- Chat history (`chat/admin/2025-11-02.json`)
- Reflections (`insights/daily/2025-11-02.json`)
- Tasks & Goals
- Sandbox code files
- ML models & training data
- Health check summaries

### Immutable Log (Append-Only Forensics)
**Purpose:** Tamper-proof audit trail  
**Operations:** Append only, never edit  
**Storage:** immutable_log table  
**Hash Chain:** Each entry cryptographically linked

**What's logged:**
- Every action: who, what, when, where, why
- Governance decisions
- Hunter alerts
- Self-healing actions
- Memory operations
- Sandbox executions
- ML deployments
- AVN verifications

## 🔄 Trigger Mesh Event Flow

```
Action occurs → Immutable Log Entry → Trigger Mesh Event → Subscribers React

Example 1: Sandbox Run
  User runs code
    → Logged to immutable_log
    → Event: "sandbox.execution"
    → Hunter subscribes → Scans for threats
    → Governance subscribes → Checks policies
    → Remedy subscribes → Logs issues on failure
    → All reactions also logged immutably

Example 2: Memory Edit
  User updates knowledge artifact
    → Logged to immutable_log with hash
    → Event: "memory.item.updated"
    → Hunter subscribes → Scans content
    → Governance subscribes → Policy check
    → Memory audit trail updated
    → Hash chain verified

Example 3: ML Deployment
  Grace deploys model
    → Logged to immutable_log
    → Event: "mldl.model_deployed"
    → Governance subscribes → Check accuracy threshold
    → AVN subscribes → Verify model integrity
    → If blocked → Task created for review
```

## 🎯 Subsystem Integration

### 1. Governance Engine
- **Subscribes to:** `*` (all events)
- **Checks:** Policies before critical actions
- **Logs:** Every decision to immutable log
- **Creates:** Approval requests when needed
- **Memory:** Stores policies, links to audit entries

### 2. Hunter Protocol
- **Subscribes to:** `memory.*, sandbox.*, governance.*`
- **Scans:** Content for threats/suspicious patterns
- **Logs:** Security events immutably
- **Creates:** Security alerts in memory
- **Escalates:** To governance for blocking

### 3. Self-Healing
- **Subscribes to:** `health.*, avn.anomaly_detected`
- **Monitors:** Component health every 60s
- **Logs:** Health checks + healing attempts
- **Memory:** Current status for dashboard
- **Triggers:** Restart procedures

### 4. MLDL (Meta-Learning)
- **Subscribes to:** `task.completed, reflection.generated`
- **Tracks:** Model training, validation, deployment
- **Logs:** ML lifecycle events
- **Memory:** Model metadata, metrics
- **Governance:** Requires approval for low-accuracy deployments

### 5. AVN/AVM (Verification Network)
- **Subscribes to:** `*.critical, mldl.*, sandbox.*`
- **Verifies:** Component integrity, anomaly detection
- **Logs:** Verification results
- **Memory:** Anomaly scores, confidence levels
- **Triggers:** Self-healing on failures

### 6. Remedy Engine
- **Subscribes to:** `sandbox.error, issue.*`
- **Analyzes:** Errors (NameError, ModuleNotFound, etc.)
- **Logs:** Issue detection + fix attempts
- **Memory:** Suggested fixes, one-click actions
- **Creates:** Tasks for unresolved issues

## 🗂️ Memory Organization

```
memory_artifacts/
├── chat/
│   ├── general/
│   │   └── 2025-11-02.json
│   └── admin/
│       └── conversations.json
├── knowledge/
│   ├── security/
│   │   ├── protocols.md
│   │   └── policies.json
│   ├── technical/
│   │   └── api-docs.md
│   └── research/
│       └── quantum-computing.md
├── tasks/
│   └── autonomous/
│       └── generated-tasks.json
├── ml/
│   ├── models/
│   │   └── grace-v1.metadata
│   └── training/
│       └── datasets.json
└── sandbox/
    ├── code/
    │   └── test.py
    └── results/
        └── output.txt
```

## 🔐 Security Architecture

### Defense Layers
1. **Authentication** - JWT tokens
2. **Governance** - Policy enforcement
3. **Hunter** - Threat detection
4. **AVN** - Integrity verification
5. **Audit** - Immutable logging
6. **Approval** - Human-in-loop for critical actions

### Threat Detection Pipeline
```
Action → Hunter Scan → Governance Check → AVN Verify → Execute/Block
                ↓              ↓              ↓
         Security Alert  Audit Log    Anomaly Score
                ↓              ↓              ↓
            Memory       Immutable      Self-Healing
```

## 📊 Complete Table Schema

### Core
- users, chat_messages, tasks, goals

### Intelligence
- reflections, causal_events, issue_reports

### Execution
- execution_tasks, sandbox_runs, sandbox_files

### Memory System
- **memory_artifacts** - File-explorer workspace
- **memory_operations** - Hash-chained edit history
- **memory_events** - Trigger mesh events

### Immutable Layer
- **immutable_log** - Tamper-proof audit trail

### Governance
- governance_policies, audit_log, approval_requests

### Security
- security_events, security_rules

### Health
- health_checks, healing_actions, verification_events

### ML/DL
- ml_events (training, deployment, validation)

## 🚀 API Endpoints by Subsystem

### Memory System
- `GET /api/memory/tree` - File-explorer view
- `GET /api/memory/item/{path}` - Artifact + audit trail
- `POST /api/memory/items` - Create (governed)
- `PATCH /api/memory/items/{id}` - Edit (governed)
- `POST /api/memory/export` - Training data bundle
- `GET /api/memory/domains` - List all domains

### Immutable Log
- `GET /api/log/entries` - Query audit trail
- `GET /api/log/verify` - Hash chain verification

### Trigger Mesh
- Events auto-published
- Subsystems subscribe programmatically

### Governance
- `GET /api/governance/policies`
- `POST /api/governance/policies`
- `GET /api/governance/audit`
- `GET /api/governance/approvals`
- `POST /api/governance/approvals/{id}/decision`

### Hunter
- `GET /api/hunter/alerts`
- `POST /api/hunter/alerts/{id}/resolve`
- `GET /api/hunter/rules`

### Self-Healing
- `GET /api/health/status`

### Issues & Remediation
- `GET /api/issues/`
- `POST /api/issues/{id}/resolve` - Apply auto-fix

### Execution
- `POST /api/executor/submit` - Background task
- `GET /api/executor/status/{id}` - Progress tracking

## 🎯 Use Cases

### 1. Auditable Knowledge Management
```
User creates: security/new-policy.md
  → Immutable log: "admin created security/new-policy.md"
  → Hunter scans: Checks for secrets
  → Governance: Validates path
  → Memory artifact created with hash
  → Audit trail: Create operation logged
  → Trigger Mesh: "memory.item.created" published
```

### 2. Auto-Fix Error
```
Sandbox error: NameError
  → Immutable log: "sandbox failed with NameError"
  → Remedy analyzes: Suggests fix
  → Issue created in memory
  → User clicks "Apply Fix"
  → Governance checks: Policy allows
  → Fix applied
  → Immutable log: "remedy applied fix"
  → Memory updated: Issue marked resolved
```

### 3. Security Threat
```
User runs: "rm -rf /"
  → Hunter scans: Detects dangerous pattern
  → Security alert in memory
  → Immutable log: "hunter blocked dangerous command"
  → Governance: Blocks execution
  → Task created: "Review security incident"
  → Dashboard shows alert
```

## 🔮 Transcendence IDE Integration

The IDE will:
- Browse memory artifacts like files
- Show audit trail inline
- Execute governed sandbox operations
- Display Hunter alerts
- Apply one-click fixes
- Export training data
- All operations flow through Trigger Mesh!

Grace is now a fully unified, auditable, self-governing AI platform! 🚀🛡️📁🔒
