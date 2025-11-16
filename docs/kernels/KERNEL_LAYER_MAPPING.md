# Kernel-to-Layer Mapping & Console Specifications

**Definitive assignment of kernels to dashboard layers**

---

## Overview

Each dashboard layer displays **only the kernels relevant to its domain**, with dedicated console panels showing logs, actions, and low-code controls.

**Layer Responsibilities**:
- **Layer 1**: Core execution (memory, storage, crypto, ingestion)
- **Layer 2**: Task management (HTM, triggers, scheduling, routing)
- **Layer 3**: Intelligence (learning, intent, policy, trust)
- **Layer 4**: DevOps (secrets, recordings, deployment, monitoring)

---

## Layer 1: Operations Console 🎛️

### Assigned Kernels (7 kernels)

#### 1. Memory Kernel (`memory-kernel-01`)

**Purpose**: Data storage, retrieval, indexing, memory tables

**Console Logs Show**:
- Memory table operations (insert, update, delete)
- Index rebuilds and optimizations
- Fusion operations (merging data)
- Cache hits/misses
- Workspace sync events

**Quick Actions**:
- `flush_cache` - Clear memory cache
- `rebuild_index` - Rebuild search index
- `export_stats` - Export memory statistics
- `run_diagnostics` - Run memory health check

**Low-Code Config**:
```
Max Memory:    [8GB ────●──────]  (2GB - 32GB)
Max Tables:    [100 ────●──────]  (10 - 1000)
Cache Size:    [1GB ────●──────]  (256MB - 8GB)
Auto-optimize: [ON ●───────────]
Log Level:     [INFO ▼]
```

**API Endpoints**:
- Status: `GET /api/kernels/layer1/memory-kernel-01/status`
- Logs: `WS /ws/kernels/memory-kernel-01/logs`
- Actions: `POST /api/kernels/memory-kernel-01/action`
- Config: `GET/PUT /api/kernels/memory-kernel-01/config`

---

#### 2. Librarian Kernel (`librarian-kernel-01`)

**Purpose**: Book processing, document analysis, knowledge extraction

**Console Logs Show**:
- Book uploads and processing
- PDF/EPUB parsing events
- Knowledge extraction results
- Analysis completions
- Queue status (books pending)

**Quick Actions**:
- `pause_processing` - Pause current book
- `view_queue` - Show pending books
- `export_analysis` - Export analysis results
- `clear_completed` - Remove completed books from queue

**Low-Code Config**:
```
Max Concurrent: [3 books ──●──]  (1 - 10)
Auto-analyze:   [ON ●─────────]
Extract Images: [ON ●─────────]
OCR Enabled:    [OFF ──────●──]
Priority Mode:  [First-in ▼]
```

**API Endpoints**:
- Status: `GET /api/kernels/layer1/librarian-kernel-01/status`
- Queue: `GET /api/kernels/librarian-kernel-01/queue`
- Logs: `WS /ws/kernels/librarian-kernel-01/logs`

---

#### 3. Governance Kernel (`governance-kernel-01`)

**Purpose**: Constitutional rules, approvals, parliament voting

**Console Logs Show**:
- Governance sessions created
- Parliament votes cast
- Constitutional rule checks
- Policy enforcement events
- Approval requests and responses

**Quick Actions**:
- `view_pending_approvals` - Show pending votes
- `create_session` - Start new governance session
- `view_constitution` - Show active rules
- `export_audit` - Export governance audit log

**Low-Code Config**:
```
Quorum Required: [3 votes ──●──]  (1 - 10)
Auto-approve:    [OFF ──────●──]
Strict Mode:     [ON ●─────────]
Audit Level:     [Full ▼]
```

---

#### 4. Verification Kernel (`verification-kernel-01`)

**Purpose**: Contract verification, trust validation, integrity checks

**Console Logs Show**:
- Contract verifications (pass/fail)
- Signature validations
- Trust level calculations
- Integrity check results
- Verification failures with reasons

**Quick Actions**:
- `verify_all` - Run verification on all contracts
- `rebuild_trust` - Recalculate trust scores
- `export_failures` - Export failed verifications
- `clear_cache` - Clear verification cache

**Low-Code Config**:
```
Trust Threshold: [0.8 ──●──]  (0.0 - 1.0)
Strict Verify:   [ON ●────]
Cache Results:   [ON ●────]
Auto-retry:      [3 attempts ▼]
```

---

#### 5. Self-Healing Kernel (`self-heal-kernel-01`)

**Purpose**: Anomaly detection, auto-recovery, system health

**Console Logs Show**:
- Anomalies detected
- Auto-healing actions taken
- Recovery successes/failures
- Health check results
- Prevention measures applied

**Quick Actions**:
- `run_health_check` - Full system health scan
- `view_anomalies` - Show recent anomalies
- `disable_auto_heal` - Pause auto-healing
- `export_report` - Export healing report

**Low-Code Config**:
```
Auto-heal:       [ON ●─────────]
Sensitivity:     [Medium ▼]
Max Retries:     [3 ──●──]  (1 - 10)
Notify on Fix:   [ON ●─────────]
```

---

#### 6. Ingestion Kernel (`ingestion-kernel-01`)

**Purpose**: File processing, data pipeline, raw data intake

**Console Logs Show**:
- Files ingested
- Processing status (start, progress, complete)
- Errors and retries
- Throughput metrics
- Pipeline stages (validate, parse, index, store)

**Quick Actions**:
- `pause_ingestion` - Pause new ingestions
- `retry_failed` - Retry failed jobs
- `export_stats` - Export throughput stats
- `clear_queue` - Clear completed jobs

**Low-Code Config**:
```
Max Concurrent: [10 jobs ──●──]  (1 - 50)
Auto-retry:     [ON ●─────────]
Retry Attempts: [3 ──●──]  (1 - 10)
Max File Size:  [500MB ──●──]  (1MB - 2GB)
```

---

#### 7. Crypto Kernel (`crypto-kernel-01`)

**Purpose**: Encryption, signatures, key management, authentication

**Console Logs Show**:
- Encryption/decryption operations
- Signature validations (pass/fail)
- Key rotations
- Authentication attempts
- Security alerts

**Quick Actions**:
- `rotate_keys` - Start key rotation wizard
- `backup_keys` - Backup encryption keys
- `validate_all` - Validate all signatures
- `export_audit` - Export security audit log

**Low-Code Config**:
```
Algorithm:       [AES-256 ▼]
Key Rotation:    [90 days ──●──]  (30 - 365)
Auto-rotate:     [ON ●─────────]
Backup Keys:     [ON ●─────────]
```

---

## Layer 2: HTM Console 📊

### Assigned Kernels (5 kernels)

#### 1. HTM Queue Manager (`htm-queue-01`)

**Purpose**: Task queue, priority management, SLA enforcement

**Console Logs Show**:
- Tasks added to queue
- Tasks started/completed
- Priority changes
- SLA breaches
- Queue depth changes

**Quick Actions**:
- `pause_queue` - Pause new task acceptance
- `flush_completed` - Remove completed tasks
- `spawn_agent` - Spawn new processing agent
- `export_queue` - Export queue snapshot

**Low-Code Config**:
```
Max Queue Depth:  [500 ──●──]  (50 - 5000)
SLA Max Wait:     [60s ──●──]  (10s - 300s)
SLA Max Duration: [120s ──●──]  (30s - 600s)
Breach Action:    ● Auto-escalate  ○ Notify
Escalate to:      [Spawn Agent ▼]
```

---

#### 2. Trigger Engine (`trigger-engine-01`)

**Purpose**: Event triggers, automation rules, condition monitoring

**Console Logs Show**:
- Triggers fired
- Condition evaluations (true/false)
- Actions executed
- Trigger creations/deletions
- Execution failures

**Quick Actions**:
- `add_trigger` - Create new trigger
- `disable_all` - Disable all triggers temporarily
- `view_history` - Show trigger execution history
- `export_rules` - Export trigger rules

**Low-Code Config**:
```
Max Active Triggers: [100 ──●──]  (10 - 500)
Eval Interval:       [5s ──●──]  (1s - 60s)
Retry Failed:        [ON ●─────]
Log Executions:      [ON ●─────]
```

**Trigger Builder (Low-Code)**:
```
┌─ Visual Trigger Builder ──────────────────┐
│ When: [File uploaded ▼]                   │
│ And:  [File size > 10MB] [Add condition]  │
│ Then: [Run ingestion] [Add action]        │
│ [Test Trigger] [Save] [Deploy]            │
└───────────────────────────────────────────┘
```

---

#### 3. Scheduler Kernel (`scheduler-kernel-01`)

**Purpose**: Cron jobs, periodic tasks, time-based execution

**Console Logs Show**:
- Scheduled jobs executed
- Missed executions
- Job successes/failures
- Schedule updates
- Next execution times

**Quick Actions**:
- `run_now` - Execute scheduled job immediately
- `pause_all` - Pause all schedules
- `view_upcoming` - Show next 10 scheduled jobs
- `export_schedule` - Export schedule configuration

**Low-Code Config**:
```
Timezone:        [UTC ▼]
Missed Jobs:     ● Run immediately  ○ Skip
Max Concurrent:  [5 ──●──]  (1 - 20)
Retry Failed:    [ON ●─────]
```

**Schedule Builder (Low-Code)**:
```
┌─ Visual Schedule Builder ─────────────────┐
│ Job Name: [Daily backup]                  │
│ Schedule: ● Cron  ○ Interval  ○ One-time  │
│ Cron: [0 2 * * *] (Daily at 2 AM)         │
│ Action: [Run backup script ▼]             │
│ [Test Schedule] [Save] [Enable]           │
└───────────────────────────────────────────┘
```

---

#### 4. Agent Pool Manager (`agent-pool-01`)

**Purpose**: Agent spawning, load balancing, capacity management

**Console Logs Show**:
- Agents spawned/terminated
- Agent health checks
- Task assignments to agents
- Load balancing decisions
- Capacity utilization changes

**Quick Actions**:
- `spawn_agent` - Spawn new agent
- `terminate_idle` - Terminate idle agents
- `balance_load` - Rebalance task distribution
- `export_metrics` - Export agent metrics

**Low-Code Config**:
```
Min Agents:      [2 ──●──]  (1 - 10)
Max Agents:      [10 ──●──]  (2 - 50)
Auto-scale:      [ON ●─────]
Scale Threshold: [80% ──●──]  (50% - 100%)
Idle Timeout:    [30 min ▼]
```

---

#### 5. Task Router (`task-router-01`)

**Purpose**: Task assignment, origin-based routing, distribution logic

**Console Logs Show**:
- Tasks routed to agents
- Routing decisions and reasons
- Origin-based filtering
- Load distribution
- Routing failures

**Quick Actions**:
- `view_routes` - Show current routing rules
- `add_route` - Create new routing rule
- `reset_defaults` - Reset to default routing
- `export_rules` - Export routing configuration

**Low-Code Config**:
```
Routing Strategy: [Load-balanced ▼]
Prefer Local:     [ON ●─────────]
Origin Weights:   Filesys: [1.0 ──●]
                  Remote:  [0.8 ──●]
                  Hunter:  [1.2 ──●]
```

**Route Builder (Low-Code)**:
```
┌─ Visual Route Builder ────────────────────┐
│ If Task Origin: [Filesystem ▼]            │
│ And File Type:  [PDF ▼]                   │
│ Then Route to:  [Librarian Agent ▼]       │
│ Priority:       [High ▼]                  │
│ [Test Route] [Save] [Apply]               │
└───────────────────────────────────────────┘
```

---

## Layer 3: Intent & Learning 🧠

### Assigned Kernels (6 kernels)

#### 1. Learning Loop (`learning-loop-01`)

**Purpose**: Pattern recognition, retrospectives, improvement suggestions

**Console Logs Show**:
- Learning cycles started/completed
- Insights discovered
- Improvements identified
- Pattern matching results
- Confidence scores

**Quick Actions**:
- `generate_retro` - Generate retrospective now
- `apply_learning` - Apply improvements
- `view_history` - Show learning history
- `export_insights` - Export insights report

**Low-Code Config**:
```
Min Insights:    [5 ──●──]  (1 - 20)
Confidence Min:  [0.8 ──●──]  (0.5 - 1.0)
Auto-apply:      [ON ●─────] (high confidence)
Cycle Frequency: [Daily ▼]
```

---

#### 2. Intent Engine (`intent-engine-01`)

**Purpose**: Goal tracking, intent lifecycle, HTM task generation

**Console Logs Show**:
- Intents created
- Intent status changes (pending→active→complete)
- HTM tasks generated per intent
- Intent completions
- Estimated vs actual completion times

**Quick Actions**:
- `create_intent` - Launch intent wizard
- `view_active` - Show active intents
- `cancel_intent` - Cancel selected intent
- `export_report` - Export intent report

**Low-Code Config**:
```
Max Active Intents: [10 ──●──]  (1 - 50)
Auto-generate HTM:  [ON ●─────]
Priority Boost:     [OFF ──────●]
Notify on Complete: [ON ●─────]
```

**Intent Builder (Low-Code)**:
```
┌─ Intent Creation Wizard ──────────────────┐
│ Step 1/3: Define Goal                     │
│ Goal: [Analyze Q4 financial data...]      │
│ Template: ○ Analysis ● Custom             │
│ [Cancel] [Next: Data Sources →]           │
└───────────────────────────────────────────┘
```

---

#### 3. Policy AI (`policy-ai-01`)

**Purpose**: AI-driven policy suggestions, recommendation engine

**Console Logs Show**:
- Policies generated
- Confidence scores calculated
- Evidence gathered
- User responses (accept/review/reject)
- Policies applied to system

**Quick Actions**:
- `generate_suggestions` - Force policy generation
- `view_pending` - Show pending policies
- `apply_accepted` - Apply accepted policies
- `export_policies` - Export policy history

**Low-Code Config**:
```
Min Confidence:   [0.7 ──●──]  (0.5 - 1.0)
Max Suggestions:  [10 ──●──]  (1 - 50)
Auto-suggest:     [ON ●─────]
Suggestion Freq:  [Daily ▼]
```

---

#### 4. Enrichment Engine (`enrichment-kernel-01`)

**Purpose**: Data enrichment, context building, linking

**Console Logs Show**:
- Enrichment jobs started
- Context added to data
- Links created between entities
- External data fetched
- Enrichment completions

**Quick Actions**:
- `enrich_now` - Trigger enrichment
- `rebuild_links` - Rebuild entity links
- `clear_cache` - Clear enrichment cache
- `export_graph` - Export knowledge graph

**Low-Code Config**:
```
Auto-enrich:      [ON ●─────────]
Max External API: [10 calls/min ▼]
Link Confidence:  [0.8 ──●──]
Cache TTL:        [24h ▼]
```

---

#### 5. Trust Core (`trust-core-01`)

**Purpose**: Trust scoring, reputation management, risk assessment

**Console Logs Show**:
- Trust scores calculated
- Reputation changes
- Risk assessments
- Trust violations detected
- Source validations

**Quick Actions**:
- `recalculate_all` - Recalculate all trust scores
- `view_untrusted` - Show low-trust sources
- `reset_scores` - Reset trust scores (with confirmation)
- `export_report` - Export trust report

**Low-Code Config**:
```
Trust Threshold:  [0.7 ──●──]  (0.0 - 1.0)
Decay Rate:       [1% per day ▼]
Auto-block:       [ON ●─────] (untrusted sources)
Re-validate:      [Weekly ▼]
```

---

#### 6. Playbook Runtime (`playbook-runtime-01`)

**Purpose**: Playbook execution, automation, success tracking

**Console Logs Show**:
- Playbooks executed
- Step-by-step execution logs
- Success/failure per playbook
- Execution times
- Error details

**Quick Actions**:
- `run_playbook` - Execute playbook manually
- `view_active` - Show running playbooks
- `pause_execution` - Pause current playbook
- `export_stats` - Export playbook statistics

**Low-Code Config**:
```
Max Concurrent:   [5 ──●──]  (1 - 20)
Auto-retry:       [ON ●─────]
Retry Attempts:   [3 ──●──]  (1 - 10)
Timeout:          [10 min ▼]
```

**Playbook Builder** (covered in main wireframes)

---

## Layer 4: Dev/OS View ⚙️

### Assigned Services (6 services)

#### 1. Secrets Vault Service (`secrets-vault-01`)

**Purpose**: Secret storage, encryption, key rotation

**Console Logs Show**:
- Secrets stored/retrieved
- Encryption operations
- Key rotations
- Access attempts (with user)
- Audit events

**Quick Actions**:
- `add_secret` - Launch secret wizard
- `rotate_keys` - Start key rotation
- `backup_vault` - Backup all secrets
- `view_audit` - Show audit log

**Low-Code Config**:
```
Encryption:       [AES-256 ▼]
Auto-rotate:      [ON ●─────────]
Rotation Period:  [90 days ▼]
Backup Schedule:  [Daily 2AM ▼]
Access Logging:   [Full ▼]
```

**Secret Wizard** (covered in main wireframes)

---

#### 2. Recording Pipeline (`recording-pipeline-01`)

**Purpose**: Audio/video ingestion, transcription, indexing

**Console Logs Show**:
- Recordings uploaded
- Transcription progress
- Indexing completions
- Errors (transcription failed, etc.)
- Summary generation

**Quick Actions**:
- `ingest_all` - Ingest all pending recordings
- `view_queue` - Show processing queue
- `export_transcripts` - Export all transcripts
- `clear_processed` - Remove processed recordings

**Low-Code Config**:
```
Auto-transcribe:  [ON ●─────────]
Generate Summary: [ON ●─────────]
Extract Keywords: [ON ●─────────]
Speaker ID:       [OFF ──────●──]
Max Concurrent:   [3 ──●──]  (1 - 10)
```

**Ingestion Pipeline** (covered in main wireframes)

---

#### 3. Remote Access Agent (`remote-access-01`)

**Purpose**: SSH/RDP sessions, remote control, session logging

**Console Logs Show**:
- Sessions started/ended
- Commands executed remotely
- File transfers
- Connection errors
- Security alerts

**Quick Actions**:
- `view_active_sessions` - Show active sessions
- `terminate_session` - End specific session
- `export_session_log` - Export session logs
- `review_commands` - Show executed commands

**Low-Code Config**:
```
Max Sessions:     [5 ──●──]  (1 - 20)
Session Timeout:  [30 min ▼]
Audit Commands:   [ON ●─────────]
Allow File Transfer: [ON ●──────]
```

---

#### 4. Deployment Service (`deployment-service-01`)

**Purpose**: CI/CD pipeline, build, test, deploy

**Console Logs Show**:
- Build started/completed
- Test results
- Deployment events
- Environment changes
- Rollbacks

**Quick Actions**:
- `deploy_staging` - Deploy to staging
- `promote_production` - Promote to production
- `rollback` - Rollback last deployment
- `view_pipeline` - Show full pipeline status

**Low-Code Config**:
```
Auto-deploy:      [Staging ▼]
Test Required:    [ON ●─────────]
Min Test Coverage: [80% ──●──]
Auto-rollback:    [ON ●─────] (on error)
```

**Deployment Pipeline** (covered in main wireframes)

---

#### 5. Stress Test Runner (`stress-runner-01`)

**Purpose**: Load testing, performance monitoring, bottleneck detection

**Console Logs Show**:
- Stress tests started
- Load injection events
- Performance metrics during test
- Bottlenecks detected
- Test completions with results

**Quick Actions**:
- `run_test` - Launch stress test wizard
- `stop_test` - Terminate running test
- `view_results` - Show last test results
- `export_report` - Export performance report

**Low-Code Config**:
```
Default Duration:  [10 min ▼]
Default Intensity: [Medium ▼]
Auto-analyze:      [ON ●─────────]
Alert on Bottleneck: [ON ●───────]
```

**Stress Test Template Library** (covered in main wireframes)

---

#### 6. Monitoring Service (`monitoring-service-01`)

**Purpose**: System metrics, alerting, health checks

**Console Logs Show**:
- Metrics collected
- Alerts triggered
- Health check results
- Threshold breaches
- Recovery actions

**Quick Actions**:
- `run_health_check` - Full system health scan
- `view_alerts` - Show active alerts
- `configure_alerts` - Alert threshold settings
- `export_metrics` - Export metrics data

**Low-Code Config**:
```
Metric Interval:  [30s ▼]
Alert Threshold:  CPU: [80% ──●──]
                  Mem: [85% ──●──]
                  Disk: [90% ──●──]
Enable Alerts:    [ON ●─────────]
```

---

## Wireframe Component Specifications

### Kernel Terminal Component

**File**: `frontend/src/components/KernelTerminal.tsx`

```typescript
<KernelTerminal
  kernel={kernel}
  defaultExpanded={false}
  showQuickActions={true}
  showConfig={true}
  onAction={(action, params) => handleKernelAction(action, params)}
  onConfigChange={(config) => handleConfigChange(config)}
/>
```

**Visual Structure**:
```
┌─────────────────────────────────────────────────────────┐
│ [Kernel: {name}] ──────────────────── [Status] [Toggle]│
│ │ {subtitle} (uptime, current task, etc.)              │
│ │ [Action Buttons Row]                                 │
│ │                                                       │
│ │ {if expanded:}                                        │
│ │ ┌─ Console Output ─────────────────────────────────┐ │
│ │ │ [Controls: Live, Filter, Search]                  │ │
│ │ │ [Log stream area - scrollable]                    │ │
│ │ │ [Footer actions: Export, Clear, Jump]             │ │
│ │ └───────────────────────────────────────────────────┘ │
│ │                                                       │
│ │ ┌─ Quick Actions ──────────────────────────────────┐ │
│ │ │ [Action 1] [Action 2] [Action 3]                  │ │
│ │ └───────────────────────────────────────────────────┘ │
│ │                                                       │
│ │ ┌─ Low-Code Config (if applicable) ────────────────┐ │
│ │ │ [Sliders, Toggles, Dropdowns]                     │ │
│ │ │ [Apply] [Save Template] [Reset]                   │ │
│ │ └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Kernel Inventory

### Summary Table

| Layer | Kernel/Service | Type | Key Responsibility |
|-------|----------------|------|--------------------|
| **Layer 1** | Memory Kernel | Kernel | Data storage & indexing |
| **Layer 1** | Librarian Kernel | Kernel | Document processing |
| **Layer 1** | Governance Kernel | Kernel | Policy enforcement |
| **Layer 1** | Verification Kernel | Kernel | Data validation |
| **Layer 1** | Self-Healing Kernel | Kernel | Auto-recovery |
| **Layer 1** | Ingestion Kernel | Kernel | Data pipeline |
| **Layer 1** | Crypto Kernel | Kernel | Security & encryption |
| **Layer 2** | HTM Queue Manager | Kernel | Task scheduling |
| **Layer 2** | Trigger Engine | Kernel | Event automation |
| **Layer 2** | Scheduler Kernel | Kernel | Cron jobs |
| **Layer 2** | Agent Pool Manager | Kernel | Agent lifecycle |
| **Layer 2** | Task Router | Kernel | Task distribution |
| **Layer 3** | Learning Loop | Kernel | Pattern learning |
| **Layer 3** | Intent Engine | Kernel | Goal management |
| **Layer 3** | Policy AI | Kernel | Policy generation |
| **Layer 3** | Enrichment Engine | Kernel | Data enrichment |
| **Layer 3** | Trust Core | Kernel | Trust scoring |
| **Layer 3** | Playbook Runtime | Kernel | Automation execution |
| **Layer 4** | Secrets Vault | Service | Secret management |
| **Layer 4** | Recording Pipeline | Service | Media processing |
| **Layer 4** | Remote Access | Service | Remote sessions |
| **Layer 4** | Deployment Service | Service | CI/CD |
| **Layer 4** | Stress Test Runner | Service | Load testing |
| **Layer 4** | Monitoring Service | Service | System metrics |

**Total**: 24 kernels/services (7 + 5 + 6 + 6)

---

## API Endpoint Summary

### Kernel Status Endpoints (4)

```
GET /api/kernels/layer1/status   → All Layer 1 kernels
GET /api/kernels/layer2/status   → All Layer 2 kernels
GET /api/kernels/layer3/status   → All Layer 3 kernels
GET /api/kernels/layer4/status   → All Layer 4 services
```

**Response Format** (universal):
```json
{
  "kernels": [
    {
      "kernel_id": "memory-kernel-01",
      "name": "Memory Kernel",
      "type": "memory",
      "status": "active" | "idle" | "paused" | "error",
      "uptime_seconds": 12300,
      "current_tasks": 45,
      "health": "healthy" | "degraded" | "unhealthy",
      "metrics": {
        "memory_usage_mb": 2300,
        "memory_limit_mb": 8000,
        "cpu_percent": 35
      },
      "last_action": "Indexed 1,234 entries",
      "quick_actions": ["flush_cache", "rebuild_index", "export_stats"],
      "config_options": [
        {
          "name": "max_memory_gb",
          "type": "slider",
          "value": 8,
          "min": 2,
          "max": 32
        }
      ]
    }
  ]
}
```

### Kernel Action Endpoint (1)

```
POST /api/kernels/{kernel_id}/action

Body: {
  "action": "start" | "stop" | "restart" | "pause" | "resume" | "{quick_action}",
  "params": { /* optional parameters */ }
}

Response: {
  "kernel_id": "memory-kernel-01",
  "action": "restart",
  "status": "success" | "error",
  "message": "Kernel restarted successfully"
}
```

### Kernel Config Endpoints (2)

```
GET /api/kernels/{kernel_id}/config

Response: {
  "kernel_id": "memory-kernel-01",
  "config": {
    "max_memory_gb": 8,
    "max_tables": 100,
    "cache_size_gb": 1,
    "auto_optimize": true,
    "log_level": "INFO"
  }
}
```

```
PUT /api/kernels/{kernel_id}/config

Body: {
  "config": {
    "max_memory_gb": 16,
    "max_tables": 200
  }
}

Response: {
  "kernel_id": "memory-kernel-01",
  "status": "updated",
  "config": { /* updated config */ }
}
```

### WebSocket Log Streaming (1)

```
WS /ws/kernels/{kernel_id}/logs

Connect and receive:
{
  "timestamp": "2025-11-14T10:30:15Z",
  "level": "INFO" | "WARN" | "ERROR" | "DEBUG",
  "message": "Indexed 1,234 entries",
  "kernel_id": "memory-kernel-01"
}
```

**Total New Endpoints**: 8 kernel-specific endpoints

---

## Wireframe Assignments for Designers

### Layer 1 Wireframe Checklist

- [ ] Page header with "Layer 1: Operations Console" title
- [ ] Metrics grid (5-7 cards) showing kernel overview
- [ ] Kernel terminal list (7 kernels):
  - [ ] Memory Kernel terminal
  - [ ] Librarian Kernel terminal
  - [ ] Governance Kernel terminal
  - [ ] Verification Kernel terminal
  - [ ] Self-Healing Kernel terminal
  - [ ] Ingestion Kernel terminal
  - [ ] Crypto Kernel terminal
- [ ] Each terminal shows:
  - [ ] Collapsed state (1 row with actions)
  - [ ] Expanded state (console + quick actions + config)
- [ ] Embedded system log viewer (bottom section)
- [ ] Stress test builder (low-code widget)
- [ ] Co-pilot pane (right rail, 380px)

---

### Layer 2 Wireframe Checklist

- [ ] Page header with "Layer 2: HTM Console" title
- [ ] Queue metrics grid (9 cards)
- [ ] Kernel terminal list (5 kernels):
  - [ ] HTM Queue Manager terminal
  - [ ] Trigger Engine terminal
  - [ ] Scheduler Kernel terminal
  - [ ] Agent Pool Manager terminal
  - [ ] Task Router terminal
- [ ] Drag-drop priority queue (low-code widget)
- [ ] SLA rules builder (low-code widget)
- [ ] Agent spawner (low-code widget)
- [ ] Embedded HTM log viewer
- [ ] Co-pilot pane (right rail, 380px)

---

### Layer 3 Wireframe Checklist

- [ ] Page header with "Layer 3: Intent & Learning" title
- [ ] Active intents grid (card layout)
- [ ] Kernel terminal list (6 kernels):
  - [ ] Learning Loop terminal
  - [ ] Intent Engine terminal
  - [ ] Policy AI terminal
  - [ ] Enrichment Engine terminal
  - [ ] Trust Core terminal
  - [ ] Playbook Runtime terminal
- [ ] Intent creation wizard (3-step, low-code)
- [ ] Visual playbook builder (block editor)
- [ ] Policy review dashboard (bulk actions)
- [ ] Retrospectives list
- [ ] Co-pilot pane (right rail, 380px)

---

### Layer 4 Wireframe Checklist

- [ ] Page header with "Layer 4: Dev/OS View" title
- [ ] System status grid (3-5 cards)
- [ ] Service terminal list (6 services):
  - [ ] Secrets Vault terminal
  - [ ] Recording Pipeline terminal
  - [ ] Remote Access terminal
  - [ ] Deployment Service terminal
  - [ ] Stress Test Runner terminal
  - [ ] Monitoring Service terminal
- [ ] Secret wizard (2-step with consent)
- [ ] Recording pipeline (batch ingestion)
- [ ] Visual deployment pipeline
- [ ] Stress test template library
- [ ] Co-pilot pane (right rail, 380px)

---

### Co-Pilot Pane (All Layers)

- [ ] Header with Grace avatar and status
- [ ] Notifications panel (expandable)
  - [ ] Notification cards with action buttons
  - [ ] Badge count indicator
- [ ] Chat interface (scrollable)
  - [ ] Message history (Grace + User)
  - [ ] Rich content support (code, tables, images)
  - [ ] Action buttons in messages
- [ ] Input area (bottom)
  - [ ] Text input field
  - [ ] Multi-modal buttons (📎🎤📸)
  - [ ] Send button
- [ ] Quick actions bar (context-aware per layer)
  - [ ] Layer 1 actions (restart all, stress test, etc.)
  - [ ] Layer 2 actions (spawn agent, defer, etc.)
  - [ ] Layer 3 actions (create intent, review policies, etc.)
  - [ ] Layer 4 actions (add secret, ingest all, etc.)

---

## Next Steps

1. **Finalize wireframes** using this kernel mapping
2. **Build backend** kernel status endpoints (8 new endpoints)
3. **Build frontend** KernelTerminal component
4. **Build frontend** CoPilotPane component
5. **Integrate** Grace's LLM for chat
6. **Test** each layer independently
7. **Deploy** and iterate

**All kernels are now scoped to their layers. Ready to build!** 🚀
