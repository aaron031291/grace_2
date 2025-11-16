# Kernel-Scoped Dashboard Architecture

**Each layer shows only its relevant kernels/services**

---

## Architecture Principle

**Every layer has its own set of kernel terminals** scoped to that layer's responsibilities. This keeps the UI organized and prevents overwhelming users with irrelevant information.

**Structure**:
```
Layer 1: Core Execution Kernels
Layer 2: HTM/Scheduler Kernels
Layer 3: Agentic Brain Kernels
Layer 4: Dev/OS Service Kernels
```

---

## Layer 1: Core Execution Kernels 🎛️

### Kernel List

1. **Memory Kernel** (`memory-kernel-01`)
   - Memory tables, fusion, workspace
   - Responsible for: Data storage, retrieval, indexing

2. **Librarian Kernel** (`librarian-kernel-01`)
   - Book processing, ingestion, analysis
   - Responsible for: Document analysis, knowledge extraction

3. **Governance Kernel** (`governance-kernel-01`)
   - Constitutional rules, approvals, parliament
   - Responsible for: Policy enforcement, decision validation

4. **Verification Kernel** (`verification-kernel-01`)
   - Contract verification, trust checks
   - Responsible for: Data validation, integrity checks

5. **Self-Healing Kernel** (`self-heal-kernel-01`)
   - Anomaly detection, auto-recovery
   - Responsible for: System health, automatic fixes

6. **Ingestion Kernel** (`ingestion-kernel-01`)
   - File processing, data pipeline
   - Responsible for: Raw data intake, preprocessing

7. **Crypto Kernel** (`crypto-kernel-01`)
   - Encryption, signatures, key management
   - Responsible for: Security, authentication

### Kernel Terminal UI (Layer 1)

```
┌─────────────────────────────────────────────────────────┐
│ Core Execution Kernels                            [▼][×]│
├─────────────────────────────────────────────────────────┤
│ [Kernel: Memory] ───────────────────────── [●] Active   │
│ │ Uptime: 3h 25m | Tasks: 45 | Memory: 2.3GB / 8GB     │
│ │ [▶ Start] [■ Stop] [↻ Restart] [⚙ Config] [📋 Logs] │
│ │                                                        │
│ │ ┌─ Console Output (collapsed, click to expand) ─┐    │
│ │ │ [Live Logs OFF] [Filter: All ▼] [Search: ___]  │    │
│ │ │ 10:30:15 INFO  Indexed 1,234 entries            │    │
│ │ │ 10:30:10 INFO  Memory sync completed            │    │
│ │ │ [Export] [Clear] [Jump to Error]                │    │
│ │ └────────────────────────────────────────────────┘    │
│ │                                                        │
│ │ ┌─ Quick Actions ──────────────────────────────┐     │
│ │ │ [Flush Cache] [Rebuild Index] [Export Stats] │     │
│ │ └──────────────────────────────────────────────┘     │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Librarian] ──────────────────── [●] Active     │
│ │ Uptime: 2h 15m | Tasks: 12 | Processing: book_qa.pdf │
│ │ [▶ Start] [■ Stop] [↻ Restart] [⚙ Config] [📋 Logs] │
│ │ [Console collapsed] [Quick Actions collapsed]         │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Governance] ────────────────────── [⏸] Paused  │
│ [Kernel: Verification] ──────────────────── [●] Active  │
│ [Kernel: Self-Healing] ──────────────────── [●] Active  │
│ [Kernel: Ingestion] ─────────────────────── [●] Active  │
│ [Kernel: Crypto] ────────────────────────── [●] Active  │
│                                                          │
│ [+ Spawn New Kernel] [⚙ Kernel Settings] [📊 Overview] │
└─────────────────────────────────────────────────────────┘
```

### Data Contract (Layer 1 Kernels)

**API Endpoint**: `GET /api/kernels/layer1/status`

**Response**:
```json
{
  "kernels": [
    {
      "kernel_id": "memory-kernel-01",
      "name": "Memory Kernel",
      "type": "memory",
      "status": "active",
      "uptime_seconds": 12300,
      "current_tasks": 45,
      "memory_usage_mb": 2300,
      "memory_limit_mb": 8000,
      "last_action": "Indexed 1,234 entries",
      "quick_actions": ["flush_cache", "rebuild_index", "export_stats"]
    },
    {
      "kernel_id": "librarian-kernel-01",
      "name": "Librarian Kernel",
      "type": "librarian",
      "status": "active",
      "current_file": "book_qa.pdf",
      "quick_actions": ["pause_processing", "view_queue", "export_analysis"]
    }
  ]
}
```

**Log Stream**: `WS /ws/kernels/{kernel_id}/logs`

---

## Layer 2: HTM/Scheduler Kernels 📊

### Kernel List

1. **HTM Queue Manager** (`htm-queue-01`)
   - Task queue, priority management
   - Responsible for: Task scheduling, SLA enforcement

2. **Trigger Engine** (`trigger-engine-01`)
   - Event triggers, automation rules
   - Responsible for: Event detection, rule execution

3. **Scheduler Kernel** (`scheduler-kernel-01`)
   - Cron jobs, periodic tasks
   - Responsible for: Time-based execution, job management

4. **Agent Pool Manager** (`agent-pool-01`)
   - Agent spawning, load balancing
   - Responsible for: Agent lifecycle, capacity management

5. **Task Router** (`task-router-01`)
   - Task assignment, origin-based routing
   - Responsible for: Task distribution, routing logic

### Kernel Terminal UI (Layer 2)

```
┌─────────────────────────────────────────────────────────┐
│ HTM & Scheduler Kernels                           [▼][×]│
├─────────────────────────────────────────────────────────┤
│ [Kernel: HTM Queue Manager] ────────────── [●] Active   │
│ │ Queue Depth: 145 | Pending: 85 | Processing: 60      │
│ │ SLA Breaches: 2 | Avg Wait: 45s | P95: 120s          │
│ │ [▶ Start] [■ Stop] [⚙ SLA Rules] [📋 Queue Logs]    │
│ │                                                        │
│ │ ┌─ HTM Queue Console (expanded) ────────────────┐    │
│ │ │ [Live Updates ON] [Filter: All Origins ▼]      │    │
│ │ │ 10:30:15 INFO  task-abc123 started (filesys)   │    │
│ │ │ 10:30:14 WARN  task-def456 slow (remote, 52s)  │    │
│ │ │ 10:30:10 INFO  task-ghi789 completed (hunter)  │    │
│ │ │ [Export Queue] [Pause Queue] [Flush Completed] │    │
│ │ └────────────────────────────────────────────────┘    │
│ │                                                        │
│ │ ┌─ Low-Code SLA Builder ──────────────────────┐      │
│ │ │ Max Wait: [60s ──●─] Max Duration: [120s]   │      │
│ │ │ Breach Action: ● Auto-escalate ○ Notify     │      │
│ │ │ [Apply Rules] [Save Template]               │      │
│ │ └─────────────────────────────────────────────┘      │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Trigger Engine] ───────────────── [●] Active   │
│ │ Active Triggers: 23 | Fired Today: 156                │
│ │ [Console collapsed] [Rule Builder collapsed]           │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Scheduler] ────────────────────── [●] Active   │
│ [Kernel: Agent Pool Manager] ───────────── [●] Active   │
│ [Kernel: Task Router] ──────────────────── [●] Active   │
│                                                          │
│ [+ Spawn Agent] [⚙ Queue Settings] [📊 HTM Dashboard]  │
└─────────────────────────────────────────────────────────┘
```

### Data Contract (Layer 2 Kernels)

**API Endpoint**: `GET /api/kernels/layer2/status`

**Response**:
```json
{
  "kernels": [
    {
      "kernel_id": "htm-queue-01",
      "name": "HTM Queue Manager",
      "type": "htm_queue",
      "status": "active",
      "queue_depth": 145,
      "pending_tasks": 85,
      "active_tasks": 60,
      "sla_breaches": 2,
      "avg_wait_time_seconds": 45,
      "p95_duration_seconds": 120,
      "quick_actions": ["pause_queue", "flush_completed", "spawn_agent"]
    },
    {
      "kernel_id": "trigger-engine-01",
      "name": "Trigger Engine",
      "type": "trigger",
      "active_triggers": 23,
      "triggers_fired_today": 156,
      "quick_actions": ["add_trigger", "disable_all", "view_history"]
    }
  ]
}
```

**Log Stream**: `WS /ws/kernels/{kernel_id}/logs`

---

## Layer 3: Agentic Brain Kernels 🧠

### Kernel List

1. **Enrichment Engine** (`enrichment-kernel-01`)
   - Data enrichment, context building
   - Responsible for: Adding context, linking data

2. **Trust Core** (`trust-core-01`)
   - Trust scoring, reputation management
   - Responsible for: Trust calculations, risk assessment

3. **Learning Loop** (`learning-loop-01`)
   - Pattern recognition, retrospectives
   - Responsible for: Learning from data, improvement suggestions

4. **Intent Engine** (`intent-engine-01`)
   - Goal tracking, intent completion
   - Responsible for: Intent lifecycle, task generation

5. **Policy AI** (`policy-ai-01`)
   - Policy suggestions, recommendation engine
   - Responsible for: AI-driven policy generation

6. **Playbook Runtime** (`playbook-runtime-01`)
   - Playbook execution, automation
   - Responsible for: Running playbooks, tracking success

### Kernel Terminal UI (Layer 3)

```
┌─────────────────────────────────────────────────────────┐
│ Agentic Brain Kernels                             [▼][×]│
├─────────────────────────────────────────────────────────┤
│ [Kernel: Learning Loop] ────────────────── [●] Active   │
│ │ Cycle #47 | Insights: 12 | Improvements: 5           │
│ │ Success Rate: 94.5% | Last Retro: 2 hours ago        │
│ │ [▶ Start] [■ Stop] [🎓 Generate Retro] [📋 Logs]    │
│ │                                                        │
│ │ ┌─ Learning Console (expanded) ──────────────────┐   │
│ │ │ [Live Learning ON] [Filter: Insights ▼]         │   │
│ │ │ 10:30:15 INSIGHT Pattern match improved +12%    │   │
│ │ │ 10:30:10 IMPROVE Added input sanitization       │   │
│ │ │ 10:30:05 SUCCESS Error rate decreased -8%       │   │
│ │ │ [Export Retro] [Apply Learning] [View History]  │   │
│ │ └─────────────────────────────────────────────────┘   │
│ │                                                        │
│ │ ┌─ Learning Config ────────────────────────────┐     │
│ │ │ Min Insights: [5 ──●─] Confidence: [0.8 ──●]  │     │
│ │ │ Auto-apply: ☑ High confidence improvements    │     │
│ │ │ [Save Config] [Reset Defaults]                │     │
│ │ └───────────────────────────────────────────────┘     │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Intent Engine] ────────────────── [●] Active   │
│ │ Active Intents: 3 | Completed Today: 5                │
│ │ [Console collapsed] [Intent Builder collapsed]         │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Kernel: Policy AI] ─────────────────────── [●] Active  │
│ [Kernel: Enrichment Engine] ─────────────── [●] Active  │
│ [Kernel: Trust Core] ────────────────────── [●] Active  │
│ [Kernel: Playbook Runtime] ──────────────── [●] Active  │
│                                                          │
│ [+ Create Intent] [⚙ Learning Settings] [📊 Analytics] │
└─────────────────────────────────────────────────────────┘
```

### Data Contract (Layer 3 Kernels)

**API Endpoint**: `GET /api/kernels/layer3/status`

**Response**:
```json
{
  "kernels": [
    {
      "kernel_id": "learning-loop-01",
      "name": "Learning Loop",
      "type": "learning",
      "status": "active",
      "current_cycle": 47,
      "insights_count": 12,
      "improvements_count": 5,
      "success_rate_percent": 94.5,
      "last_retrospective": "2025-11-14T08:30:00Z",
      "quick_actions": ["generate_retro", "apply_learning", "view_history"]
    },
    {
      "kernel_id": "intent-engine-01",
      "name": "Intent Engine",
      "type": "intent",
      "active_intents": 3,
      "completed_today": 5,
      "quick_actions": ["create_intent", "view_active", "export_report"]
    }
  ]
}
```

**Log Stream**: `WS /ws/kernels/{kernel_id}/logs`

---

## Layer 4: Dev/OS Service Kernels ⚙️

### Kernel List

1. **Secrets Vault Service** (`secrets-vault-01`)
   - Secret storage, encryption, rotation
   - Responsible for: Secure key management

2. **Recording Pipeline** (`recording-pipeline-01`)
   - Audio/video ingestion, transcription
   - Responsible for: Media processing, indexing

3. **Remote Access Agent** (`remote-access-01`)
   - SSH/RDP sessions, remote control
   - Responsible for: Remote connections, session logs

4. **Deployment Service** (`deployment-service-01`)
   - CI/CD pipeline, deployments
   - Responsible for: Build, test, deploy

5. **Stress Test Runner** (`stress-runner-01`)
   - Load testing, performance monitoring
   - Responsible for: Stress tests, bottleneck detection

6. **Monitoring Service** (`monitoring-service-01`)
   - System metrics, alerting
   - Responsible for: Health checks, alerts

### Kernel Terminal UI (Layer 4)

```
┌─────────────────────────────────────────────────────────┐
│ Dev/OS Service Kernels                            [▼][×]│
├─────────────────────────────────────────────────────────┤
│ [Service: Secrets Vault] ───────────────── [●] Active   │
│ │ Total Secrets: 15 | Encrypted: 15 | Health: Healthy  │
│ │ Next Rotation: 5 days | Last Audit: 2 hours ago      │
│ │ [▶ Start] [■ Stop] [🔐 Add Secret] [📋 Audit Log]   │
│ │                                                        │
│ │ ┌─ Vault Console (expanded) ──────────────────────┐  │
│ │ │ [Live Audit ON] [Filter: All Actions ▼]          │  │
│ │ │ 10:30:15 INFO  Secret stored: OPENAI_API_KEY     │  │
│ │ │ 10:30:10 INFO  Secret accessed: DB_PASSWORD      │  │
│ │ │ 10:30:05 WARN  Rotation due: STRIPE_KEY (5 days) │  │
│ │ │ [Export Audit] [Rotate Keys] [Backup Vault]      │  │
│ │ └──────────────────────────────────────────────────┘  │
│ │                                                        │
│ │ ┌─ Secret Wizard ────────────────────────────────┐   │
│ │ │ [+ Add Secret] [🔄 Rotate All] [🗑️ Clean Dupes] │   │
│ │ └────────────────────────────────────────────────┘   │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Service: Recording Pipeline] ──────────── [●] Active   │
│ │ Pending: 5 recordings | Processing: 2 (45% complete) │
│ │ [Console collapsed] [Ingestion Queue collapsed]       │
│ └────────────────────────────────────────────────────── │
│                                                          │
│ [Service: Remote Access Agent] ─────────── [●] Active   │
│ [Service: Deployment Service] ──────────── [●] Active   │
│ [Service: Stress Test Runner] ──────────── [○] Idle     │
│ [Service: Monitoring Service] ──────────── [●] Active   │
│                                                          │
│ [+ Run Stress Test] [⚙ Service Settings] [📊 Dashboard]│
└─────────────────────────────────────────────────────────┘
```

### Data Contract (Layer 4 Kernels)

**API Endpoint**: `GET /api/kernels/layer4/status`

**Response**:
```json
{
  "services": [
    {
      "service_id": "secrets-vault-01",
      "name": "Secrets Vault Service",
      "type": "secrets",
      "status": "active",
      "total_secrets": 15,
      "encrypted_secrets": 15,
      "health": "healthy",
      "next_rotation_days": 5,
      "last_audit": "2025-11-14T08:30:00Z",
      "quick_actions": ["add_secret", "rotate_keys", "backup_vault"]
    },
    {
      "service_id": "recording-pipeline-01",
      "name": "Recording Pipeline",
      "type": "recording",
      "pending_recordings": 5,
      "processing_count": 2,
      "processing_progress_percent": 45,
      "quick_actions": ["ingest_all", "view_queue", "export_transcripts"]
    }
  ]
}
```

**Log Stream**: `WS /ws/kernels/{service_id}/logs`

---

## Kernel Terminal Component Specification

### Collapsed State (Default)

```
[Kernel: Memory] ──────────────────────── [●] Active
│ Uptime: 3h 25m | Tasks: 45 | Memory: 2.3GB / 8GB
│ [▶ Start] [■ Stop] [↻ Restart] [⚙ Config] [📋 Logs]
```

### Expanded State (Click to toggle)

```
[Kernel: Memory] ──────────────────────── [●] Active  [▲]
│ Uptime: 3h 25m | Tasks: 45 | Memory: 2.3GB / 8GB
│ [▶ Start] [■ Stop] [↻ Restart] [⚙ Config] [📋 Logs]
│
│ ┌─ Console Output ─────────────────────────────────────┐
│ │ [Live Logs ON] [Filter: All ▼] [Search: _______]    │
│ │ [Auto-scroll ●] [Wrap Text ○] [Lines: 100 ▼]        │
│ │ ┌──────────────────────────────────────────────────┐ │
│ │ │ 10:30:15 INFO  Indexed 1,234 entries             │ │
│ │ │ 10:30:14 WARN  High memory usage: 85%            │ │
│ │ │ 10:30:10 INFO  Memory sync completed             │ │
│ │ │ 10:30:08 INFO  Processing batch 47/120           │ │
│ │ │ ...                                              │ │
│ │ └──────────────────────────────────────────────────┘ │
│ │ [Export Logs] [Clear Console] [Jump to Error]        │
│ └──────────────────────────────────────────────────────┘
│
│ ┌─ Quick Actions ──────────────────────────────────────┐
│ │ [Flush Cache] [Rebuild Index] [Export Stats]        │
│ │ [Run Diagnostics] [View Config]                     │
│ └──────────────────────────────────────────────────────┘
│
│ ┌─ Low-Code Config (if applicable) ────────────────────┐
│ │ Max Memory: [8GB ────●──] (2GB - 32GB)               │
│ │ Max Tasks: [50 ──●────] (10 - 100)                   │
│ │ Auto-restart: [ON ●─────] Log Level: [INFO ▼]        │
│ │ [Apply Changes] [Save as Template] [Reset]           │
│ └──────────────────────────────────────────────────────┘
```

### Component Props (React/TypeScript)

```typescript
interface KernelTerminalProps {
  kernel: {
    kernel_id: string
    name: string
    type: string
    status: "active" | "idle" | "error" | "paused"
    uptime_seconds: number
    current_tasks?: number
    memory_usage_mb?: number
    memory_limit_mb?: number
    quick_actions: string[]
    config_options?: ConfigOption[]
  }
  onAction: (kernelId: string, action: string) => void
  onConfigChange: (kernelId: string, config: Record<string, any>) => void
  defaultExpanded?: boolean
}

interface ConfigOption {
  name: string
  type: "slider" | "toggle" | "dropdown" | "input"
  value: any
  min?: number
  max?: number
  options?: string[]
}
```

---

## Kernel Actions & Interactions

### Universal Kernel Actions

Every kernel supports these base actions:

1. **Start** - Boot the kernel
2. **Stop** - Graceful shutdown
3. **Restart** - Stop + Start
4. **Pause** - Suspend (if supported)
5. **Resume** - Resume from pause
6. **View Logs** - Expand console
7. **Configure** - Open config panel

### Layer-Specific Quick Actions

**Layer 1 (Memory Kernel)**:
- Flush Cache
- Rebuild Index
- Export Stats
- Run Diagnostics

**Layer 2 (HTM Queue)**:
- Pause Queue
- Flush Completed
- Spawn Agent
- Export Queue Snapshot

**Layer 3 (Learning Loop)**:
- Generate Retrospective
- Apply Learning
- View History
- Export Insights

**Layer 4 (Secrets Vault)**:
- Add Secret
- Rotate Keys
- Backup Vault
- View Audit Log

---

## API Endpoints Summary

### Kernel Management

```
GET  /api/kernels/layer1/status      → Layer 1 kernels
GET  /api/kernels/layer2/status      → Layer 2 kernels
GET  /api/kernels/layer3/status      → Layer 3 kernels
GET  /api/kernels/layer4/status      → Layer 4 services
POST /api/kernels/{id}/action        → Execute action
GET  /api/kernels/{id}/config        → Get config
PUT  /api/kernels/{id}/config        → Update config
WS   /ws/kernels/{id}/logs           → Log stream
```

### Quick Action Execution

```
POST /api/kernels/{id}/quick-action
Body: {
  "action": "flush_cache" | "rebuild_index" | etc.
  "params": { /* optional */ }
}
```

---

## Next: Wireframes & Mockups

Now that kernels are scoped per layer, I'll create detailed wireframes showing:
1. Full layer layouts with kernel terminals
2. Co-pilot pane integration
3. Interaction states (collapsed/expanded)
4. Low-code control positioning
5. Responsive layouts

Would you like me to create the wireframe specifications next?
