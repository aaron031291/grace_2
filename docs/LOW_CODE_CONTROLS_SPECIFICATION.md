# Low-Code / No-Code Controls - Dashboard UI

**Declarative controls instead of scripts: drag, click, configure**

---

## Philosophy

Every action that currently requires scripting or terminal commands should have a **visual, declarative control** in the UI. Operators shouldn't need to write Python or bash to accomplish tasks.

**Principles**:
1. **Visual First**: Buttons, sliders, drag-and-drop over text input
2. **Guided Workflows**: Wizards and templates for complex tasks
3. **Instant Feedback**: Show results immediately, no waiting
4. **Undo/Redo**: Every action can be reversed
5. **Progressive Disclosure**: Simple by default, advanced on demand

---

## Layer 1: Operations Console - Low-Code Controls

### 1. Kernel Control Panel

**Instead of**: `python manage_kernels.py restart kern-01`

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Kernel: ingestion-kernel-01                         │
├─────────────────────────────────────────────────────┤
│ Status: ● Active                                    │
│ Uptime: 3h 25m                                      │
│ Tasks: 12 active                                    │
├─────────────────────────────────────────────────────┤
│ Actions:                                            │
│ [▶ Start] [■ Stop] [↻ Restart] [⏸ Pause]          │
│                                                     │
│ Advanced:                                           │
│ ┌─ Auto-restart on failure  [Toggle: ON ]          │
│ ┌─ Max concurrent tasks     [Slider: 50  ]         │
│ ┌─ Memory limit (GB)        [Input: 8    ]         │
│ └─ [Apply Changes]                                  │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Toggle switches** for boolean settings
- **Sliders** for numeric ranges (1-100 tasks, 1-32GB memory)
- **Dropdowns** for enums (log level: debug/info/warn/error)
- **Apply button** to commit changes

---

### 2. Stress Test Builder

**Instead of**: Writing stress test scripts

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Configure Stress Test                               │
├─────────────────────────────────────────────────────┤
│ Test Type:                                          │
│ ● Full System  ○ HTM Queue Only  ○ Kernel Only     │
│                                                     │
│ Duration:                                           │
│ [Slider: 10 minutes] ────●──── (1m - 60m)          │
│                                                     │
│ Intensity:                                          │
│ ○ Low  ● Medium  ○ High  ○ Extreme                 │
│                                                     │
│ Load Pattern:                                       │
│ [Dropdown: Steady ▼]                                │
│ Options: Steady, Ramp Up, Spike, Random             │
│                                                     │
│ Targets:                                            │
│ ☑ Kernels (all 5)                                  │
│ ☑ HTM Queue                                        │
│ ☑ Crypto Service                                   │
│ ☐ Database                                         │
│                                                     │
│ [Preview Load] [Run Test] [Save as Template]       │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Radio buttons** for mutually exclusive options
- **Sliders** for durations and intensities
- **Checkboxes** for multi-select targets
- **Templates** to save/reuse configurations

---

### 3. Log Viewer with Filters

**Instead of**: `tail -f kernel.log | grep ERROR`

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Kernel Logs: ingestion-kernel-01                    │
├─────────────────────────────────────────────────────┤
│ Filters:                                            │
│ Level: [All ▼] Time: [Last Hour ▼] Search: [____]  │
│ ☑ Errors  ☑ Warnings  ☐ Info  ☐ Debug             │
│                                                     │
│ Auto-scroll: [ON] Live: [ON] Lines: [100 ▼]        │
├─────────────────────────────────────────────────────┤
│ 10:30:15 ERROR OutOfMemoryError: heap full          │
│ 10:30:14 WARN  High memory usage: 85%               │
│ 10:30:10 INFO  Processing task task-xyz123          │
│ 10:30:08 INFO  Kernel started successfully          │
│ ...                                                 │
├─────────────────────────────────────────────────────┤
│ [Export to File] [Copy Selected] [Jump to Error]   │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Level filters** (checkboxes for each log level)
- **Time range picker** (dropdown or date picker)
- **Search box** with live filtering
- **Auto-scroll toggle** (enable/disable)
- **Export button** to save logs as file

---

### 4. Crypto Key Rotation Wizard

**Instead of**: Manual key rotation scripts

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Step 1 of 3: Select Keys to Rotate                  │
├─────────────────────────────────────────────────────┤
│ ☑ Master Encryption Key (last rotated: 30 days ago) │
│ ☑ Signature Key (last rotated: 90 days ago)        │
│ ☐ API Keys (rotated 5 days ago)                    │
│                                                     │
│           [Cancel] [Next: Generate New Keys →]     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 2 of 3: Generate New Keys                      │
├─────────────────────────────────────────────────────┤
│ Key Algorithm:                                      │
│ ● AES-256  ○ RSA-4096  ○ Ed25519                   │
│                                                     │
│ Entropy Source:                                     │
│ ● Hardware RNG  ○ OS Random  ○ Custom Seed         │
│                                                     │
│ Backup Old Keys:                                    │
│ ☑ Create encrypted backup                          │
│ Backup Location: [/secure/backups/ ]               │
│                                                     │
│        [← Back] [Next: Confirm Rotation →]         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 3 of 3: Confirm Rotation                       │
├─────────────────────────────────────────────────────┤
│ You are about to rotate 2 keys:                     │
│ • Master Encryption Key → New AES-256               │
│ • Signature Key → New AES-256                       │
│                                                     │
│ This will:                                          │
│ ✓ Re-encrypt all secrets (456 items)               │
│ ✓ Update all signatures (1234 items)               │
│ ✓ Create backup of old keys                        │
│ ✓ Audit log entry created                          │
│                                                     │
│ Estimated time: 2-3 minutes                         │
│ Downtime: None (hot swap)                           │
│                                                     │
│ ⚠️ This action cannot be undone                     │
│                                                     │
│        [← Back] [Start Rotation]                    │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Multi-step wizard** with progress indicator
- **Selection checkboxes** for keys
- **Radio buttons** for algorithm choice
- **Confirmation screen** with impact summary

---

## Layer 2: HTM Console - Low-Code Controls

### 1. Drag-and-Drop Queue Priority

**Instead of**: Manually editing task priorities

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ HTM Task Queue - Drag to Reorder                    │
├─────────────────────────────────────────────────────┤
│ [Priority: Critical]                                │
│   ┌─ task-abc123 (filesystem, 15MB)  [⋮⋮] ─────┐   │
│   └─ task-def456 (remote, 8MB)       [⋮⋮] ─────┘   │
│                                                     │
│ [Priority: High]                                    │
│   ┌─ task-ghi789 (hunter, 12MB)      [⋮⋮] ─────┐   │
│   └─ task-jkl012 (filesystem, 6MB)   [⋮⋮] ─────┘   │
│                                                     │
│ [Priority: Normal]                                  │
│   └─ task-mno345 (remote, 20MB)      [⋮⋮] ─────┘   │
│                                                     │
│ [Priority: Low]                                     │
│   └─ task-pqr678 (hunter, 3MB)       [⋮⋮] ─────┘   │
│                                                     │
│ Drag tasks between priorities to reorder            │
│ [Save Changes] [Cancel] [Reset to Default]         │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Drag handles** (⋮⋮) for each task
- **Drop zones** for each priority level
- **Visual feedback** while dragging
- **Save/cancel** to commit or discard changes

---

### 2. SLA Slider & Rules Builder

**Instead of**: Editing SLA config files

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Configure SLA Rules                                 │
├─────────────────────────────────────────────────────┤
│ Max Queue Wait Time:                                │
│ [Slider: 60 seconds] ─────●──── (10s - 300s)       │
│                                                     │
│ Max Task Duration:                                  │
│ [Slider: 120 seconds] ────●───── (30s - 600s)      │
│                                                     │
│ Breach Action:                                      │
│ ● Auto-escalate  ○ Notify Only  ○ Ignore           │
│                                                     │
│ Escalation Target:                                  │
│ [Dropdown: Spawn New Agent ▼]                       │
│ Options: Spawn Agent, Alert Admin, Log Only         │
│                                                     │
│ Apply to:                                           │
│ ☑ Filesystem tasks                                 │
│ ☑ Remote tasks                                     │
│ ☐ Hunter tasks (excluded)                          │
│                                                     │
│ [Apply SLA Rules] [Save as Template]               │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Sliders** for time thresholds
- **Radio buttons** for actions
- **Dropdowns** for escalation targets
- **Checkboxes** for task type selection

---

### 3. Task Replay Controller

**Instead of**: Command-line task replay

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Replay Failed Tasks                                 │
├─────────────────────────────────────────────────────┤
│ Failed Tasks (3):                                   │
│ ☑ task-abc123 (filesystem, failed: out of memory)  │
│ ☑ task-def456 (remote, failed: timeout)            │
│ ☐ task-ghi789 (hunter, failed: network error)      │
│                                                     │
│ Replay Options:                                     │
│ Retry Strategy:                                     │
│ ● With increased resources                          │
│ ○ As-is                                             │
│ ○ With modified config                              │
│                                                     │
│ If retry fails:                                     │
│ ○ Retry again  ● Move to quarantine  ○ Delete      │
│                                                     │
│ [Select All] [Replay Selected (2)] [Cancel]        │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Checkboxes** to select tasks
- **Radio buttons** for retry strategy
- **Batch actions** (select all, replay selected)

---

### 4. Agent Spawner

**Instead of**: `python spawn_agent.py --config...`

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Spawn New HTM Agent                                 │
├─────────────────────────────────────────────────────┤
│ Agent Type:                                         │
│ ● General Purpose  ○ Filesystem Only  ○ Remote Only │
│                                                     │
│ Capacity:                                           │
│ Max Concurrent Tasks: [Slider: 10] ──●── (1-50)    │
│                                                     │
│ Lifespan:                                           │
│ ● Temporary (auto-shutdown when idle)               │
│ ○ Permanent (always running)                        │
│ Idle timeout: [30 minutes ▼]                        │
│                                                     │
│ Priority:                                           │
│ ○ High  ● Normal  ○ Low                             │
│                                                     │
│ [Spawn Agent] [Spawn & Monitor]                     │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Radio buttons** for agent type
- **Slider** for capacity
- **Dropdown** for timeout
- **Spawn button** with instant feedback

---

## Layer 3: Learning - Low-Code Controls

### 1. Intent Creation Wizard

**Instead of**: Manually defining intents

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Step 1 of 3: Define Goal                            │
├─────────────────────────────────────────────────────┤
│ What should Grace accomplish?                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Analyze Q4 financial data and generate insights │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Choose template (optional):                         │
│ ○ Data Analysis  ○ Report Generation               │
│ ○ Monitoring     ● Custom                           │
│                                                     │
│           [Cancel] [Next: Select Data Sources →]   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 2 of 3: Select Data Sources                    │
├─────────────────────────────────────────────────────┤
│ Which data should Grace use?                        │
│ ☑ Uploaded files (Q4_financials.xlsx)              │
│ ☑ Database queries (sales_data table)              │
│ ☐ External APIs (Stripe, QuickBooks)               │
│ ☐ Real-time streams (logs, metrics)                │
│                                                     │
│ Ingestion frequency:                                │
│ ● One-time  ○ Daily  ○ Weekly  ○ Real-time         │
│                                                     │
│        [← Back] [Next: Set Completion Criteria →]  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 3 of 3: Set Completion Criteria                │
├─────────────────────────────────────────────────────┤
│ When is the intent complete?                        │
│ ☑ All data processed                               │
│ ☑ Report generated                                 │
│ ☐ Minimum 10 insights found                        │
│ ☐ Approved by user                                 │
│                                                     │
│ Estimated HTM tasks: ~15                            │
│ Estimated time: 2-3 hours                           │
│                                                     │
│ Notifications:                                      │
│ ☑ Notify on completion                             │
│ ☐ Notify on each milestone                         │
│                                                     │
│        [← Back] [Create Intent]                     │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Multi-step wizard** with templates
- **Text area** for goal description
- **Checkboxes** for data sources and criteria
- **Radio buttons** for frequency

---

### 2. Playbook Builder (Block-Based)

**Instead of**: Writing playbook Python code

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Playbook Builder: data-ingestion-standard           │
├─────────────────────────────────────────────────────┤
│ Drag blocks from left palette to canvas:            │
│                                                     │
│ [Palette]          [Canvas]                         │
│                                                     │
│ Triggers:          ┌─ When: [File Uploaded]         │
│ [File Upload]      │                                │
│ [Schedule]         ├─ Then: [Validate Format]       │
│ [Manual]           │                                │
│                    ├─ If Valid:                     │
│ Actions:           │  ├─ [Ingest to Database]       │
│ [Ingest Data]      │  └─ [Generate Summary]         │
│ [Transform]        │                                │
│ [Notify]           ├─ Else:                         │
│                    │  └─ [Send Error Alert]         │
│ Conditions:        │                                │
│ [If/Else]          └─ Finally: [Log Completion]     │
│ [Loop]                                              │
│ [Wait]             [Test Playbook] [Save & Deploy]  │
│                                                     │
│ Execution Count: 145 | Success Rate: 94.5%         │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Block palette** with drag-and-drop
- **Visual flow** editor (like Scratch or Node-RED)
- **Connectors** between blocks
- **Test button** to validate playbook
- **Stats display** (executions, success rate)

---

### 3. Policy Review Dashboard

**Instead of**: Reviewing policies one-by-one in code

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Pending Policy Suggestions (5)                      │
├─────────────────────────────────────────────────────┤
│ Sort: [Confidence ▼] Filter: [All Areas ▼]         │
│                                                     │
│ ☑ Security: Implement rate limiting (87%)          │
│   Evidence: 15 abuse patterns, 45% reduction        │
│   [Accept] [Review] [Reject]                        │
│                                                     │
│ ☑ Performance: Cache API responses (82%)           │
│   Evidence: 200ms avg latency, 50% cache hits       │
│   [Accept] [Review] [Reject]                        │
│                                                     │
│ ☐ Cost: Scale down idle kernels (75%)              │
│   Evidence: 3 kernels idle >2h, save $50/month      │
│   [Accept] [Review] [Reject]                        │
│                                                     │
│ [Select All] [Bulk Accept (2)] [Defer Selected]    │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Checkboxes** for bulk selection
- **Sort/filter** dropdowns
- **Quick action buttons** per policy
- **Bulk actions** for selected items

---

## Layer 4: Dev/OS - Low-Code Controls

### 1. Secret Addition Wizard

**Instead of**: Manual secret storage

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Step 1 of 2: Enter Secret                           │
├─────────────────────────────────────────────────────┤
│ Secret Name:                                        │
│ [OPENAI_API_KEY                    ]                │
│                                                     │
│ Secret Value:                                       │
│ [••••••••••••••••••••••••••••••••] [👁 Show]       │
│                                                     │
│ Category:                                           │
│ [Dropdown: API Key ▼]                               │
│ Options: API Key, Password, Token, Certificate      │
│                                                     │
│ Expiration (optional):                              │
│ [Date Picker: 2026-11-14] or [Never Expires ☐]     │
│                                                     │
│ Tags (comma-separated):                             │
│ [openai, production, critical     ]                 │
│                                                     │
│           [Cancel] [Next: Confirm & Encrypt →]     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 2 of 2: Consent & Encryption                   │
├─────────────────────────────────────────────────────┤
│ You are storing: OPENAI_API_KEY                     │
│ Category: API Key                                   │
│                                                     │
│ This secret will be:                                │
│ ✓ Encrypted using AES-256                           │
│ ✓ Stored in secure vault                            │
│ ✓ Accessible only to authorized agents              │
│ ✓ Audited and logged                                │
│ ✓ Rotated automatically (if expiration set)         │
│                                                     │
│ ☑ I consent to storing this secret                 │
│                                                     │
│        [← Back] [Store Secret]                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Password field** with show/hide toggle
- **Dropdown** for categories
- **Date picker** for expiration
- **Tags input** with autocomplete
- **Consent checkbox** before storing

---

### 2. Recording Ingestion Pipeline

**Instead of**: Manual ingestion triggers

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Batch Recording Ingestion                           │
├─────────────────────────────────────────────────────┤
│ Pending Recordings (5):                             │
│ ☑ meeting_2025-11-14.mp3 (voice, 45MB)             │
│ ☑ demo_capture.mp4 (screen, 128MB)                 │
│ ☐ standup_2025-11-13.mp3 (voice, 12MB)             │
│ ☐ interview_recording.mp3 (voice, 67MB)            │
│ ☐ system_walkthrough.mp4 (screen, 234MB)           │
│                                                     │
│ Ingestion Settings:                                 │
│ ☑ Transcribe audio/video                           │
│ ☑ Generate summary                                 │
│ ☑ Extract keywords/tags                            │
│ ☐ Speaker identification                           │
│                                                     │
│ Processing:                                         │
│ ● Sequential (one at a time)                        │
│ ○ Parallel (up to 3 concurrent)                     │
│                                                     │
│ [Select All] [Ingest Selected (2)] [Schedule]      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Checkboxes** for batch selection
- **Options** for ingestion features
- **Radio buttons** for processing mode
- **Bulk actions** (select all, ingest selected)

---

### 3. Deployment Status Board

**Instead of**: CI/CD dashboard in separate tool

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Deployment Pipeline                                 │
├─────────────────────────────────────────────────────┤
│ [Build] → [Test] → [Stage] → [Deploy]              │
│   ✓        ⏳       ○         ○                     │
│                                                     │
│ Current Stage: Running Tests                        │
│ Progress: ████████████░░░░░░ 65%                    │
│                                                     │
│ Recent Deployments:                                 │
│ ┌─ v4.2.1 (Production)  ✓ 2 days ago               │
│ │  [Rollback] [View Logs]                          │
│ ├─ v4.2.0 (Staging)     ✓ 5 days ago               │
│ └─ v4.1.9 (Production)  ✓ 7 days ago               │
│                                                     │
│ Quick Actions:                                      │
│ [Deploy to Staging] [Promote to Production]        │
│ [Rollback Last Deploy] [View Full Pipeline]        │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Visual pipeline** with status indicators
- **Progress bar** for current stage
- **Rollback button** per deployment
- **Quick actions** for common tasks

---

### 4. Stress Test Template Library

**Instead of**: Writing test scripts from scratch

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ Stress Test Templates                               │
├─────────────────────────────────────────────────────┤
│ My Templates:                                       │
│ ┌─ "Morning Health Check" (daily)                  │
│ │  Type: Kernel Only, Duration: 5m, Intensity: Low  │
│ │  [Run Now] [Edit] [Clone] [Delete]               │
│ │                                                   │
│ ├─ "Weekly Full Stress" (weekly)                   │
│ │  Type: Full System, Duration: 30m, Intensity: High│
│ │  [Run Now] [Edit] [Clone] [Delete]               │
│ │                                                   │
│ └─ "Pre-Deployment Validation"                     │
│    Type: Full System, Duration: 10m, Intensity: Med │
│    [Run Now] [Edit] [Clone] [Delete]               │
│                                                     │
│ Public Templates:                                   │
│ ┌─ "Standard Kernel Stress" (recommended)          │
│ │  Used 1,234 times | 4.5★ rating                  │
│ │  [Use This Template] [Preview]                   │
│ │                                                   │
│ └─ "HTM Queue Endurance Test"                      │
│    Used 567 times | 4.2★ rating                    │
│    [Use This Template] [Preview]                   │
│                                                     │
│ [+ Create New Template]                             │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Template cards** with metadata
- **Action buttons** per template (run, edit, clone)
- **Public library** with ratings
- **Create new** from scratch or from template

---

## Unified Telemetry & Log Viewers

### Embedded Log Viewer (All Layers)

**Instead of**: Dropping to terminal for logs

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ System Logs                                    [×]  │
├─────────────────────────────────────────────────────┤
│ Source: [All Systems ▼] Level: [All ▼] Time: [1h]  │
│ Search: [____________________________________]  [🔍] │
│                                                     │
│ Filters:                                            │
│ ☑ Kernels  ☑ HTM  ☑ Ingestion  ☐ Remote Access     │
│ ☑ ERROR  ☑ WARN  ☐ INFO  ☐ DEBUG                   │
│                                                     │
│ Live: [ON]  Auto-scroll: [ON]  Wrap: [OFF]         │
├─────────────────────────────────────────────────────┤
│ 10:30:15 [KERNEL-01] ERROR OutOfMemoryError         │
│ 10:30:14 [HTM-QUEUE] WARN  Queue depth: 145 (+30%)  │
│ 10:30:10 [INGESTION] INFO  Processing file.txt      │
│ 10:30:08 [KERNEL-02] INFO  Task completed           │
│ ...                                                 │
├─────────────────────────────────────────────────────┤
│ [Export] [Copy] [Clear] [Jump to First Error]      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Multi-source dropdown** (all systems or specific)
- **Level checkboxes** (filter by severity)
- **Time range selector** (last hour, day, week, custom)
- **Live mode** with auto-scroll
- **Jump to error** button for quick navigation

---

### Embedded Metrics Dashboard

**Instead of**: External monitoring tool

**Use**:
```
┌─────────────────────────────────────────────────────┐
│ System Metrics                                      │
├─────────────────────────────────────────────────────┤
│ Time Range: [Last 24 Hours ▼]  Refresh: [30s ▼]    │
│                                                     │
│ CPU Usage:                                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ╱╲    ╱╲                                        │ │
│ │╱  ╲  ╱  ╲╱╲  ╱                                  │ │
│ │      ╲╱    ╲╱                                   │ │
│ └─────────────────────────────────────────────────┘ │
│ Current: 45% | Avg: 38% | Peak: 67%                │
│                                                     │
│ Memory Usage:                                       │
│ ████████████░░░░░░░░ 60% (4.8GB / 8GB)             │
│                                                     │
│ Queue Depth:                                        │
│ [Bar Chart: Filesystem=45, Remote=30, Hunter=25]    │
│                                                     │
│ [Export Data] [Configure Alerts] [Full Dashboard]  │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Line charts** for time-series (CPU, memory)
- **Progress bars** for current state
- **Bar charts** for distributions
- **Configurable** time range and refresh

---

## Context-Aware Jump Actions

From co-pilot notifications, jump directly to relevant logs/data:

**Example**:
```
Grace: "HTM queue running 30% long"
       [Jump to HTM Queue →] [View Queue Logs →]

Click "View Queue Logs" →
┌─────────────────────────────────────────────────────┐
│ HTM Queue Logs (filtered: slow tasks)               │
├─────────────────────────────────────────────────────┤
│ 10:30:15 WARN  task-xyz123 duration: 45s (expected) │
│ 10:30:10 WARN  task-abc456 duration: 52s (slow)     │
│ 10:30:05 WARN  task-def789 duration: 61s (slow)     │
│ ...                                                 │
│                                                     │
│ Root Cause Analysis:                                │
│ • Network latency: 250ms avg (normal: 50ms)        │
│ • Remote API rate limiting detected                 │
│ • Recommendation: Spawn local agent                 │
│                                                     │
│ [Spawn Agent] [Defer Remote Tasks] [Export Report] │
└─────────────────────────────────────────────────────┘
```

**Features**:
- **Contextual filtering** (pre-filtered to relevant logs)
- **Root cause analysis** (Grace's insights)
- **Actionable buttons** based on context

---

## Summary: Low-Code Principles

| Instead of... | Use... |
|---------------|--------|
| Writing scripts | Visual wizards |
| Editing config files | Sliders, dropdowns, toggles |
| Command-line args | Form fields with validation |
| Manual log grep | Embedded viewers with filters |
| External tools | Unified dashboard |
| Text-based playbooks | Block-based visual editor |
| Batch scripts | Drag-and-drop workflows |
| SSH commands | Click-and-confirm actions |

**Every complex task should have**:
1. A **wizard** or **multi-step form**
2. **Visual preview** before execution
3. **Undo/rollback** capability
4. **Templates** for common patterns
5. **Contextual help** and examples

---

**Next**: Integrate these controls into each layer's wireframes! 🎨
