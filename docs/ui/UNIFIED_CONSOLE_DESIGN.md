# Unified Grace Console - UI Design Specification

**Date**: November 16, 2025  
**Version**: 1.0

---

## 🎯 Overview

A single-window interface unifying Grace's logs, chat, and task management with dynamic workspace spawning for domain-specific views.

---

## 🏛️ Three Core Pillars

### 1. **Logs Pane** (Left/Bottom)
**Purpose**: Real-time system activity stream

**Features**:
- Color-coded status messages
  - 🟢 Green: Success/OK
  - 🟡 Yellow: Warnings
  - 🔴 Red: Errors/Critical
  - 🔵 Blue: Info/System events
- Filter by domain (Core, Memory, AI, Governance, etc.)
- Filter by log level (INFO, WARN, ERROR)
- Auto-scroll toggle
- Search/grep within logs
- Export logs to file

**Data Source**: Domain event bus + system logs

---

### 2. **Multimodal Chat** (Center)
**Purpose**: Conversational interface with Grace

**Features**:
- Text input/output
- Voice input (speech-to-text)
- Voice output (text-to-speech)
- Image/file upload for multimodal queries
- Code syntax highlighting in responses
- Markdown rendering
- Context-aware suggestions
- Quick actions (run command, open workspace, etc.)

**Backend**: RAG + World Model + Agentic systems

---

### 3. **Task Manager** (Right)
**Purpose**: Mission and follow-up tracking

**Features**:
- Active missions list
  - Status indicators
  - Progress bars
  - Time elapsed
- Proactive missions queue
- Follow-up missions
- Mission details on click
  - Remediation steps
  - Test results
  - KPI deltas
  - Outcome summaries
- Quick filters: by subsystem, by status, by priority

**Data Source**: Mission Control API + Follow-up tracking

---

## 🪟 Dynamic Workspaces (Pop-Out Tabs)

### Concept
**When you ask Grace to "open CRM latency dashboard" or "show mission followup_abc123," Grace spawns a dedicated tab/window with the relevant charts, logs, or code view.**

**Key Design Principle**: Keep tabs lightweight so you can close them without affecting the core console.

### Examples
```
User: "open CRM latency dashboard"
→ Grace spawns tab: CRM Dashboard
  - Real-time latency charts
  - Request traces
  - Performance metrics
  - Recent errors
  - Close tab anytime - console continues

User: "show mission followup_abc123"
→ Grace spawns tab: Mission followup_abc123
  - Mission timeline
  - Remediation steps taken
  - Test results
  - Before/after KPIs
  - Related logs
  - Close when done - no impact on Grace

User: "debug domain memory port 8201"
→ Grace spawns tab: Memory Domain Debug
  - Port status
  - Health checks
  - Recent requests
  - Error logs
  - Quick actions (restart, heal)
  - Independent debugging - close when fixed
```

### Workspace Types
1. **Domain Dashboards** - Health, metrics, logs for specific domain (8200-8209)
2. **Mission Details** - Deep dive into specific mission with full context
3. **Code Views** - File/function being debugged with Monaco editor
4. **Data Explorers** - Database query results, knowledge base search
5. **Chart/Metrics Views** - Time-series, comparisons, trends
6. **Approval Queues** - Pending consents/approvals for review

### Behavior
- **Lightweight** - Minimal overhead, close without affecting main console
- **Independent** - Each tab has own state, doesn't block others
- **Non-blocking** - Closing a workspace doesn't interrupt Grace
- **Linkable** - Tabs can reference each other (click to jump)
- **Persistent** (optional) - Restore open tabs on reload
- **Disposable** - No commitment - open, review, close
- **Multi-instance** - Open multiple of same type (e.g., 3 mission tabs)

### Spawning Methods
1. **Chat Commands**: "open dashboard memory" → spawns workspace
2. **Click Actions**: Click mission card → spawns mission detail
3. **Command Palette**: Cmd+K → "Open Dashboard" → select domain
4. **Quick Links**: Click domain name in logs → spawns domain dashboard
5. **Context Menu**: Right-click on item → "Open in Workspace"

### Workspace Lifecycle
```
1. User triggers spawn (chat, click, palette)
2. Grace creates tab in workspace area
3. Tab fetches data from relevant domain API
4. User interacts with workspace (charts, logs, code)
5. User closes tab when done
6. Main console unaffected - continues running
7. No cleanup needed - just close the tab
```

---

## 🎛️ Additional Panels

### Mission & Follow-Up Dashboard
**Location**: Above Task Manager or separate tab

**Features**:
- Card/table view of missions
  - Active missions
  - Proactive missions
  - Follow-up missions
- Columns:
  - Mission ID
  - Subsystem
  - Status (In Progress, Completed, Failed)
  - Latest KPI delta
  - Started/Completed time
  - Actions (View Details, Re-run, Archive)
- Drill-down to:
  - Remediation steps
  - Test results
  - Outcome summaries
  - Grace's narrative

---

### Stakeholder Alerts Panel
**Location**: Top banner or separate tab

**Features**:
- Mirror Slack/email/webhook notifications in-app
- Full audit trail of all alerts sent
- Quick actions:
  - Acknowledge alert
  - Ask Grace for details
  - Spawn related workspace
- Filter by channel (Slack, Email, Webhook)
- Search alerts by content/time

---

### Daily Brief & Trend View
**Location**: Dashboard tab or modal

**Features**:
- Auto-generated daily summary
  - "Today I fixed..."
  - "New patterns discovered..."
  - "Proactive interventions..."
- Trend charts:
  - Mission counts (daily/weekly)
  - MTTR (Mean Time To Repair)
  - Follow-up frequency per subsystem
  - Success rate over time
- Downloadable reports (PDF/JSON)

---

### Command Palette
**Location**: Keyboard shortcut (Cmd+K / Ctrl+K) or top-right button

**Features**:
- Quick actions:
  - ✅ Grant all approvals
  - 🚀 Start mission (with template)
  - 🔍 Query world model
  - 📊 Open dashboard (select domain)
  - 🔧 Trigger healing playbook
  - 📁 Open workspace (by type)
  - 📂 Open knowledge explorer
  - 📝 View recent missions
  - 🧠 Check learning insights
- Fuzzy search
- Keyboard navigation
- Recent commands history

---

### File Explorer UI (New!)
**Location**: Dynamic workspace tab or dedicated panel

**Purpose**: Browse, manage, and ingest knowledge artifacts

**Features**:
- Browse knowledge by category (Documents, Recordings, Code, etc.)
- View metadata (source path, tags, ingestion date, chunk count)
- Actions per file:
  - 👁️ Preview content
  - ✏️ Add notes (appends to artifact)
  - 🔄 Re-ingest (with updated pipeline)
  - 🗑️ Delete (soft delete with archive)
  - 📊 View embeddings
  - ⬇️ Download
- Upload controls:
  - 📤 Drag & drop files → auto-ingest
  - 📝 Paste text directly → chunk & embed
  - 🎤 Record voice note → transcribe & index
  - 🔄 Bulk upload → batch processing
- Search/filter:
  - RAG-powered semantic search
  - Filter by category, date, tags
  - Check for duplicates before upload
- Zero-trust access:
  - Backed by credential vault
  - Every action logged
  - Governance approval required
  - Full audit trail

**Integration**:
- Uses existing ingestion endpoints:
  - `/api/remote-access/rag/ingest-text`
  - `/api/ingestion/upload-document`
  - `/api/speech/upload-voice-note`
- Triggers `vector_integration.embed_all()` on bulk upload
- Stores in `grace_training/` directory structure
- Makes all content RAG-searchable

**See**: [FILE_EXPLORER_DESIGN.md](../ui/FILE_EXPLORER_DESIGN.md) for full specification

---

## 🎨 Layout Mockup

```
┌──────────────────────────────────────────────────────────────────┐
│  🎛️ Command Palette (Cmd+K)          🔔 Alerts (3)    👤 User   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┬───────────────────────────┬──────────────────┐ │
│  │             │                           │                  │ │
│  │    LOGS     │      MULTIMODAL CHAT      │   TASK MANAGER   │ │
│  │   (Left)    │        (Center)           │     (Right)      │ │
│  │             │                           │                  │ │
│  │ 🟢 [OK]     │  User: Fix memory leak    │ ✅ Mission #123  │ │
│  │ 🟡 [WARN]   │                           │    Status: Done  │ │
│  │ 🔴 [ERROR]  │  Grace: I found the issue │                  │ │
│  │ 🔵 [INFO]   │  in memory_api.py...      │ 🔄 Mission #124  │ │
│  │             │                           │    In Progress   │ │
│  │ Filter:     │  [Attach] [Voice] [Send]  │                  │ │
│  │ ▼ All       │                           │ 📋 Follow-ups:2  │ │
│  │             │                           │                  │ │
│  └─────────────┴───────────────────────────┴──────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  📊 DYNAMIC WORKSPACES (Pop-out Tabs)                       │ │
│  │                                                              │ │
│  │  [CRM Dashboard] [Mission #123] [Memory Domain Debug]      │ │
│  │                                                              │ │
│  │  (Current: CRM Dashboard)                                   │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │  CRM Latency: 45ms (↓ 20%)                            │ │ │
│  │  │  [Chart: Last 24h]                                     │ │ │
│  │  │  Recent Errors: 0                                      │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Backend Integration

### Domain-Grouped Architecture Mapping

**Logs Pane**:
- Subscribes to Domain Event Bus
- Receives events from all domains (8200-8209)
- Color-codes by event type/severity
- Filters by domain

**Chat Interface**:
- Routes through AI Domain (8202)
- Uses RAG + World Model
- Spawns autonomous agents for complex queries
- Records conversations in Memory Domain (8201)

**Task Manager**:
- Queries Mission Control API (Execution Domain 8204)
- Displays missions from mission tracking system
- Updates via WebSocket for real-time status

**Dynamic Workspaces**:
- Domain Dashboards: Query specific domain (8200-8209)
- Mission Details: Query Mission Control + Telemetry (8205)
- Code Views: Query Coding Agent (8202) + File System
- Data Explorers: Query Memory Domain (8201)

---

## 📡 Real-Time Updates

**WebSocket Connections**:
```
/ws/logs        - Stream logs to Logs Pane
/ws/missions    - Stream mission updates to Task Manager
/ws/telemetry   - Stream metrics to dashboards
/ws/events      - Stream domain events
```

**Polling** (fallback):
- Logs: Poll `/api/logs/recent` every 2s
- Missions: Poll `/api/missions/active` every 5s
- Alerts: Poll `/api/alerts/unread` every 10s

---

## 🎯 Implementation Tasks

### Phase 1: Core Layout (Week 1)
- [ ] Create shared layout component (3-pane split)
- [ ] Implement resizable panels
- [ ] Add Logs Pane with color-coding
- [ ] Add Chat Pane with text input/output
- [ ] Add Task Manager Pane with mission cards
- [ ] Wire WebSocket connections

### Phase 2: Dynamic Workspaces (Week 2)
- [ ] Implement tab/window spawning system
- [ ] Create workspace types (dashboard, mission, code, data)
- [ ] Add workspace routing from chat commands
- [ ] Implement tab close/minimize
- [ ] Add workspace state persistence

### Phase 3: Additional Panels (Week 3)
- [ ] Build Mission & Follow-Up Dashboard
- [ ] Create Stakeholder Alerts Panel
- [ ] Implement Daily Brief & Trend View
- [ ] Add Command Palette (Cmd+K)

### Phase 4: Polish & Integration (Week 4)
- [ ] Add keyboard shortcuts
- [ ] Implement theme support (dark/light)
- [ ] Add export/download features
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] User preferences/settings

---

## 🚀 Command Palette Actions

### Workspace Actions
```
"open dashboard memory"       → Spawn Memory Domain Dashboard
"open mission abc123"         → Spawn Mission Detail View
"show alerts"                 → Open Stakeholder Alerts Panel
"daily brief"                 → Show Daily Brief & Trends
```

### Approval Actions
```
"approve all"                 → Grant single approval for all operations
"show pending approvals"      → List pending consent requests
"revoke approval xyz"         → Revoke specific approval
```

### Mission Actions
```
"new mission"                 → Start new mission with template
"view missions"               → Open Mission Dashboard
"mission status abc"          → Show specific mission status
```

### System Actions
```
"restart domain memory"       → Restart Memory Domain (8201)
"heal network"                → Trigger network healing
"system health"               → Show health dashboard
"query world model"           → Open world model query interface
```

---

## 🎨 UI Framework Recommendations

### Frontend Stack
- **React** or **Svelte** - Component framework
- **TailwindCSS** - Styling
- **Monaco Editor** - Code views
- **Recharts** or **Chart.js** - Data visualization
- **React Query** or **SWR** - Data fetching
- **Socket.io** or native WebSocket - Real-time updates

### Component Structure
```
src/
├── components/
│   ├── Console/
│   │   ├── LogsPane.tsx
│   │   ├── ChatPane.tsx
│   │   └── TaskManagerPane.tsx
│   │
│   ├── Workspaces/
│   │   ├── WorkspaceContainer.tsx
│   │   ├── DomainDashboard.tsx
│   │   ├── MissionDetail.tsx
│   │   ├── CodeView.tsx
│   │   └── DataExplorer.tsx
│   │
│   ├── Panels/
│   │   ├── MissionDashboard.tsx
│   │   ├── AlertsPanel.tsx
│   │   ├── DailyBrief.tsx
│   │   └── CommandPalette.tsx
│   │
│   └── Shared/
│       ├── ResizablePanel.tsx
│       ├── StatusIndicator.tsx
│       └── Chart.tsx
│
├── hooks/
│   ├── useWebSocket.ts
│   ├── useMissions.ts
│   └── useDomainEvents.ts
│
└── api/
    ├── missions.ts
    ├── logs.ts
    └── domains.ts
```

---

## 🔗 API Integration

### Required Backend Endpoints

**Logs**:
- `GET /api/logs/recent` - Recent log entries
- `GET /api/logs/stream` (WebSocket) - Real-time logs
- `GET /api/logs/filter` - Filtered logs

**Missions**:
- `GET /api/missions/active` - Active missions
- `GET /api/missions/{id}` - Mission details
- `POST /api/missions/create` - Create new mission
- `GET /api/missions/followups` - Follow-up missions
- `WS /ws/missions` - Real-time mission updates

**Domains**:
- `GET /api/domains/health` - All domain health
- `GET /api/domains/{id}/metrics` - Domain-specific metrics
- `GET /api/domains/{id}/dashboard` - Dashboard data

**Alerts**:
- `GET /api/alerts/recent` - Recent alerts
- `POST /api/alerts/acknowledge` - Acknowledge alert
- `WS /ws/alerts` - Real-time alerts

**Approvals**:
- `GET /api/secrets/consent/pending` - Pending approvals
- `POST /api/secrets/consent/respond` - Grant approval
- `POST /api/approvals/grant-all` - Single approval endpoint

**Daily Brief**:
- `GET /api/reports/daily-brief` - Today's summary
- `GET /api/reports/trends` - Trend data

---

## 🎭 User Flows

### Flow 1: Grant Single Approval
```
1. User opens Grace Console
2. Command Palette shows: "6 approvals pending"
3. User hits Cmd+K → types "approve"
4. Selects "Approve All (Single Point)"
5. Grace calls: POST /api/approvals/grant-all
6. All 6 items approved at once
7. Console shows: "✅ All operations authorized"
```

### Flow 2: Investigate Mission
```
1. Task Manager shows: Mission #124 (Memory leak in Memory Domain)
2. User clicks Mission #124
3. Dynamic workspace opens: Mission Detail tab
4. Tab shows:
   - Problem: Memory usage 95% → 40%
   - Actions taken: Restarted worker, cleared cache
   - Tests passed: 5/5
   - KPI: -55% memory usage
5. User asks in Chat: "Why did this happen?"
6. Grace explains in Chat pane
7. Grace suggests: "Want to see the code?"
8. User: "yes"
9. Grace spawns: Code View workspace with memory_api.py
```

### Flow 3: Monitor Domain Health
```
1. User types in Chat: "How is the AI domain doing?"
2. Grace responds: "AI Domain healthy, latency 120ms"
3. Grace auto-spawns: AI Domain Dashboard workspace
4. Dashboard shows:
   - Health: 🟢 Healthy
   - Latency: 120ms (avg)
   - Requests/sec: 45
   - Recent activity graph
5. User can monitor in real-time
6. Close tab when done
```

---

## 🎨 Visual Design Principles

### Colors (Dark Theme)
- **Background**: #1a1a1a (dark gray)
- **Panels**: #2a2a2a (lighter gray)
- **Text**: #e0e0e0 (light gray)
- **Success**: #4ade80 (green)
- **Warning**: #fbbf24 (yellow)
- **Error**: #ef4444 (red)
- **Info**: #60a5fa (blue)
- **Accent**: #8b5cf6 (purple)

### Typography
- **Headings**: Inter or System UI
- **Body**: Inter or System UI
- **Code**: JetBrains Mono or Fira Code

### Spacing
- **Panel padding**: 16px
- **Card padding**: 12px
- **Gap between elements**: 8px
- **Border radius**: 8px

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GRACE CONSOLE UI                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Logs Pane ←─── WebSocket ←─── Domain Event Bus (8000)     │
│                                                              │
│  Chat Pane ←─── REST API ←───── AI Domain (8202)           │
│                └─── WebSocket                               │
│                                                              │
│  Task Mgr  ←─── REST API ←───── Execution Domain (8204)    │
│                └─── WebSocket   (Mission Control)           │
│                                                              │
│  Workspaces ←── REST API ←───── Specific Domains            │
│                └─── Domain Query APIs (8200-8209)           │
│                                                              │
│  Alerts    ←─── WebSocket ←──── Monitoring Domain (8205)    │
│                                                              │
│  Approvals ←─── REST API ←───── Core Domain (8200)          │
│                                  (Secrets Consent API)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Single Approval Integration

### Command Palette Action
```typescript
// When user triggers "Approve All"
async function grantSingleApproval() {
  const response = await fetch('/api/approvals/grant-all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: 'admin',
      approval_method: 'command_palette',
      approved: true
    })
  });
  
  if (response.ok) {
    showNotification('✅ All operations authorized', 'success');
  }
}
```

### Backend Endpoint (NEW)
```python
# backend/routes/approval_api.py

@router.post("/api/approvals/grant-all")
async def grant_all_approvals(user_id: str, approval_method: str = "ui"):
    """
    Single approval point - grant all pending approvals at once
    """
    from backend.security.single_approval import single_approval
    
    # Grant the single approval
    single_approval.grant_approval(method=approval_method)
    
    # Also approve all pending consents
    from backend.security.secrets_consent_flow import secrets_consent_flow
    pending = await secrets_consent_flow.get_consent_history(user_id=user_id, limit=100)
    
    approved_count = 0
    for consent in pending:
        if consent.get("consent_status") == "pending":
            await secrets_consent_flow.approve_consent(
                consent_id=consent["consent_id"],
                user_id=user_id,
                method=approval_method
            )
            approved_count += 1
    
    return {
        "success": True,
        "approved_count": approved_count,
        "single_approval": True,
        "message": "All operations authorized"
    }
```

---

## 🚀 Implementation Roadmap

### Immediate (This Week)
1. ✅ Fix syntax errors in backend
2. ✅ Create single approval system
3. ✅ Document UI spec (this file)
4. Create `/api/approvals/grant-all` endpoint
5. Test backend with domain architecture

### Short-term (Next 2 Weeks)
1. Build 3-pane layout
2. Implement Logs Pane with WebSocket
3. Implement Chat Pane with API
4. Implement Task Manager with missions
5. Add Command Palette with single approval

### Medium-term (Next Month)
1. Implement Dynamic Workspaces
2. Add Mission & Follow-Up Dashboard
3. Add Stakeholder Alerts Panel
4. Add Daily Brief & Trend View
5. Polish and optimize

---

## 📋 Technical Requirements

### Performance
- Initial load: < 2s
- Log streaming: < 100ms latency
- Chat response: < 500ms (excluding LLM)
- Workspace spawn: < 300ms

### Scalability
- Support 1000+ log entries in view
- Handle 100+ missions
- 10+ concurrent dynamic workspaces
- 50+ alerts in panel

### Browser Support
- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+

---

## ✅ Success Criteria

1. **Single approval** grants all 6 permissions at once
2. **Logs** stream in real-time, color-coded, filterable
3. **Chat** accepts text/voice, spawns workspaces on command
4. **Task Manager** shows missions with live updates
5. **Workspaces** pop out/close without affecting console
6. **Command Palette** provides quick access to all actions
7. **No hunting logs** - everything visible in one view

---

**Status**: Spec complete! Ready for frontend implementation.
