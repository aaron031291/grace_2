# GRACE Dashboard MVP - Implementation Plan

**Goal**: Get essential dashboard working in 2-3 weeks with existing APIs

---

## MVP Scope

**What's Included**:
- ✅ Layer 1 (Ops): Telemetry + 7 kernel consoles + quick actions
- ✅ Layer 2 (HTM): Queue dashboard + priority controls + HTM console
- ✅ Layer 3 (Learning): Intent list + retrospectives + console
- ✅ Layer 4 (Dev/OS): Secrets vault + recording pipeline basics
- ✅ Co-pilot pane: Chat + notifications (all layers)

**What's Deferred** (post-MVP):
- Visual playbook block editor (use text forms instead)
- Drag-drop queue reordering (use dropdowns)
- Voice input (text only for MVP)
- Screenshot capture (file upload only)
- Advanced charts (tables for MVP)
- Mobile responsive (desktop-first)

---

## Layer 1 (Ops Console) - MVP

### Components

#### 1. Telemetry Cards (Top)
**Data Source**: Existing APIs ✅
- `GET /api/telemetry/kernels/status`
- `GET /api/telemetry/ingestion/throughput`
- `GET /api/telemetry/crypto/health`

**Display**:
```
┌───────┬───────┬───────┬───────┬──────────┐
│Total: │Active:│ Idle: │Errors:│Avg Boot: │
│   7   │   5   │   2   │   0   │ 1250ms   │
└───────┴───────┴───────┴───────┴──────────┘
```

**Implementation**: 5 simple cards with fetch on mount + 5s polling

---

#### 2. Quick Actions Bar
**Actions** (3 buttons):
- **Run Boot Stress**: `POST /api/telemetry/kernels/{id}/control?action=stress`
- **Flush Ingestion Queue**: `POST /api/ingestion/flush` (to be added)
- **Check Crypto Status**: Refresh crypto health card

**UI**:
```
[⚡ Run Boot Stress] [🗑️ Flush Queue] [🔐 Check Crypto]
```

---

#### 3. Kernel Consoles (Accordion)
**Kernels** (7):
1. Memory Kernel
2. Librarian Kernel
3. Governance Kernel
4. Verification Kernel
5. Self-Healing Kernel
6. Ingestion Kernel
7. Crypto Kernel

**Data Source**: New endpoint
- `GET /api/kernels/layer1/status` ✅ Already built

**Each Panel Shows**:
```
[Kernel: Memory] ──────────── [●] Active  [▼]
│ Uptime: 3h 25m | Tasks: 45
│ [▶ Start] [■ Stop] [↻ Restart]

{If expanded:}
│ ┌─ Console Logs ─────────────────┐
│ │ [Simple polling, no WebSocket] │
│ │ 10:30:15 INFO Indexed entries  │
│ │ 10:30:10 INFO Sync completed   │
│ │ [Refresh] [Export]             │
│ └────────────────────────────────┘
```

**Log Source** (MVP - Simple Polling):
- `GET /api/kernels/{id}/logs?lines=50` (poll every 5s when expanded)

**Actions**:
- Start/Stop/Restart: `POST /api/kernels/{id}/action`

**Implementation**:
- Use existing `KernelTerminal` component ✅
- Disable WebSocket for MVP (use polling)
- Remove low-code config for MVP (hardcoded settings)

---

#### 4. Co-Pilot Pane (Right Rail)
**Features for MVP**:
- ✅ Chat interface (text only)
- ✅ Notifications (3-5 mock notifications)
- ✅ Quick actions (context-aware per layer)
- ❌ Voice input (defer)
- ❌ File upload (defer)
- ❌ Screenshot (defer)

**Data Source**:
- `POST /api/copilot/chat/send` ✅ Already built
- `GET /api/copilot/notifications` ✅ Already built

**Implementation**:
- Use existing `CoPilotPane` component ✅
- Disable voice/file/screenshot buttons for MVP
- Use mock Grace responses (basic pattern matching)

---

### Layer 1 MVP Task List

**Backend** (2-3 hours):
- [x] ✅ Kernel status endpoint already built
- [ ] Add simple log polling endpoint (if not exists)
- [ ] Add flush ingestion queue endpoint

**Frontend** (1 day):
- [ ] Build Layer 1 page layout
- [ ] Add telemetry cards (reuse existing or create simple cards)
- [ ] Add quick actions bar (3 buttons)
- [ ] Integrate `KernelTerminal` component (7 instances)
- [ ] Configure polling (disable WebSocket for MVP)
- [ ] Add `CoPilotPane` to right rail

**Total**: ~1.5 days

---

## Layer 2 (HTM Console) - MVP

### Components

#### 1. Queue Dashboard Cards
**Data Source**: Existing APIs ✅
- `GET /api/telemetry/htm/queue`
- `GET /api/telemetry/htm/tasks`
- `GET /api/telemetry/htm/workload`

**Display**:
```
┌──────┬────────┬───────┬──────┬──────┐
│Depth:│Pending:│Active:│ SLA: │ P95: │
│  145 │   85   │  60   │  2   │ 120s │
└──────┴────────┴───────┴──────┴──────┘
```

---

#### 2. Priority Controls (Simple Sliders)
**Data Source**: New endpoint
- `POST /api/htm/priorities`

**Payload**:
```json
{
  "critical_weight": 1.0,
  "high_weight": 0.8,
  "normal_weight": 0.5,
  "low_weight": 0.2
}
```

**UI** (MVP - No Drag-Drop):
```
Priority Weights:
Critical: [1.0 ──●──────] (0.5 - 2.0)
High:     [0.8 ──●──────] (0.5 - 2.0)
Normal:   [0.5 ──●──────] (0.5 - 2.0)
Low:      [0.2 ──●──────] (0.5 - 2.0)
[Apply Changes]
```

---

#### 3. HTM Console Panel
**Kernels** (MVP - Single Consolidated Panel):
- HTM Core (shows all HTM activity)

**Display**:
```
[HTM Core Console] ──────── [●] Active  [▼]
│ Queue: 145 | Pending: 85 | Active: 60
│ [⏸ Pause Queue] [🗑️ Flush Completed] [➕ Spawn Agent]

{If expanded:}
│ ┌─ HTM Log Stream ───────────────┐
│ │ 10:30:15 task-abc started      │
│ │ 10:30:14 task-def slow (52s)   │
│ │ [Refresh] [Export]             │
│ └────────────────────────────────┘
```

**Data Source**:
- Logs: `GET /api/telemetry/htm/tasks?status=active&limit=20` (poll every 5s)

**Actions**:
- Pause Queue: `POST /api/htm/pause`
- Flush Completed: `POST /api/htm/flush`
- Spawn Agent: `POST /api/htm/spawn_agent`

---

#### 4. Low-Code Rule Builder (Simple Form)
**Instead of**: Visual trigger builder

**Use** (MVP):
```
HTM Auto-Scaling Rule:
If queue depth > [50 ──●──] (10-200)
Then: [Spawn Agent ▼]
Options: Spawn Agent, Alert Only, Defer Low Priority

[Save Rule] [Test Rule]
```

**Data Source**: New endpoint
- `POST /api/htm/rules`

**Payload**:
```json
{
  "rule_type": "auto_scale",
  "condition": {
    "metric": "queue_depth",
    "operator": "greater_than",
    "threshold": 50
  },
  "action": "spawn_agent"
}
```

---

### Layer 2 MVP Task List

**Backend** (3-4 hours):
- [ ] Add HTM priority weights endpoint: `POST /api/htm/priorities`
- [ ] Add HTM pause/flush/spawn endpoints (simple stubs)
- [ ] Add HTM rules endpoint: `POST /api/htm/rules`

**Frontend** (1 day):
- [ ] Build Layer 2 page layout
- [ ] Add queue metrics cards
- [ ] Add priority sliders (4 sliders + apply button)
- [ ] Add HTM console panel (single expandable)
- [ ] Add simple rule builder form
- [ ] Add `CoPilotPane` to right rail

**Total**: ~1.5 days

---

## Layer 3 (Agentic Brain) - MVP

### Components

#### 1. Intent List (Simple Table)
**Data Source**: Existing APIs ✅
- `GET /api/telemetry/intent/active`

**Display**:
```
Active Intents:
┌───────────┬─────────────────────┬────────┬──────────┐
│ Intent ID │ Goal                │ Status │ Progress │
├───────────┼─────────────────────┼────────┼──────────┤
│ int-abc   │ Analyze Q4 data     │ Active │ ████ 65% │
│ int-def   │ Learn user patterns │ Pending│ ██░░ 30% │
└───────────┴─────────────────────┴────────┴──────────┘
[+ Create Intent]
```

---

#### 2. Retrospective Feed (Simple List)
**Data Source**: Existing APIs ✅
- `GET /api/telemetry/learning/retrospectives?limit=5`

**Display**:
```
Recent Learning Cycles:
┌────────────────────────────────────────┐
│ Cycle #47 - Nov 14, 9:00 AM            │
│ Insights: Pattern match +12%           │
│ Improvements: Added input sanitization │
│ [View Details]                         │
├────────────────────────────────────────┤
│ Cycle #46 - Nov 13, 9:00 AM            │
│ ...                                    │
└────────────────────────────────────────┘
```

---

#### 3. Agentic Brain Console (Single Panel)
**Kernels** (MVP - Consolidated):
- Learning & Intent Core (shows learning loop + intent engine logs)

**Display**:
```
[Agentic Brain Console] ──── [●] Active  [▼]
│ Active Intents: 3 | Learning Cycle: #47
│ [🎯 Create Intent] [🎓 Generate Retro] [📊 View Stats]

{If expanded:}
│ ┌─ Learning & Intent Logs ───────┐
│ │ 10:30:15 Intent completed      │
│ │ 10:30:10 Learning insight +12% │
│ │ [Refresh] [Export]             │
│ └────────────────────────────────┘
```

---

#### 4. Intent Creation (Simple Form)
**Instead of**: 3-step wizard

**Use** (MVP):
```
Create Intent:
Goal: [Analyze Q4 financial data and generate insights ___]
Data Source: [Uploaded Files ▼]
Priority: ○ Low ● Normal ○ High
[Create] [Cancel]
```

**Data Source**: New endpoint
- `POST /api/intent/create`

**Payload**:
```json
{
  "goal": "Analyze Q4 financial data...",
  "data_source": "uploaded_files",
  "priority": "normal"
}
```

---

### Layer 3 MVP Task List

**Backend** (2-3 hours):
- [ ] Add intent creation endpoint: `POST /api/intent/create`
- [ ] Ensure existing endpoints return proper data

**Frontend** (1 day):
- [ ] Build Layer 3 page layout
- [ ] Add intent table
- [ ] Add retrospective feed (simple list)
- [ ] Add agentic brain console panel
- [ ] Add simple intent creation form
- [ ] Add `CoPilotPane` to right rail

**Total**: ~1.5 days

---

## Layer 4 (Dev/OS) - MVP

### Components

#### 1. System Status Cards
**Data Source**: Existing APIs ✅
- `GET /api/telemetry/secrets/status`
- `GET /api/telemetry/recordings/pending`
- `GET /api/telemetry/deployment/status`

**Display**:
```
┌─────────┬────────────┬────────────┐
│Secrets: │Recordings: │Deployment: │
│15 (✓)   │5 pending   │v4.2.1 (✓)  │
└─────────┴────────────┴────────────┘
```

---

#### 2. Secrets Vault (Simple Form)
**Instead of**: 2-step wizard

**Use** (MVP):
```
Add Secret:
Name:     [OPENAI_API_KEY          ]
Value:    [••••••••••••••] [👁 Show]
Category: [API Key ▼]
☑ I consent to encrypt and store this secret
[Save Secret] [Cancel]
```

**Data Source**: Existing API ✅
- `POST /api/secrets/store`

---

#### 3. Recording Queue (Simple Table + Button)
**Display**:
```
Pending Recordings:
┌──────────┬───────┬────────────────┬───────┬─────────┐
│ ID       │ Type  │ Filename       │ Size  │ Actions │
├──────────┼───────┼────────────────┼───────┼─────────┤
│ rec-abc  │ voice │ meeting.mp3    │ 45MB  │[Ingest] │
│ rec-def  │ screen│ demo.mp4       │ 128MB │[Ingest] │
└──────────┴───────┴────────────────┴───────┴─────────┘
```

**Data Source**: Existing API ✅
- `GET /api/telemetry/recordings/pending`
- `POST /api/recording/ingest/{id}`

---

#### 4. Dev/OS Console (Single Panel)
**Services** (MVP - Consolidated):
- Dev Services (shows secrets, recordings, deployment logs)

**Display**:
```
[Dev/OS Services Console] ── [●] Active  [▼]
│ Secrets: 15 | Recordings: 5 | Deploy: v4.2.1
│ [🔐 Add Secret] [🎙️ Ingest All] [🚀 Deploy]

{If expanded:}
│ ┌─ Dev/OS Logs ──────────────────┐
│ │ 10:30:15 Secret stored         │
│ │ 10:30:10 Recording ingested    │
│ │ [Refresh] [Export]             │
│ └────────────────────────────────┘
```

---

### Layer 4 MVP Task List

**Backend** (2 hours):
- [ ] Add ingestion flush endpoint (if needed)
- [ ] Add deploy action endpoint (if needed)

**Frontend** (1 day):
- [ ] Build Layer 4 page layout
- [ ] Add system status cards
- [ ] Add simple secret form
- [ ] Add recording table with ingest buttons
- [ ] Add dev/OS console panel
- [ ] Add `CoPilotPane` to right rail

**Total**: ~1.5 days

---

## Co-Pilot Pane (All Layers) - MVP

### Features (Simplified)

#### 1. Notifications (Static for MVP)
**Display** (3 mock notifications):
```
Notifications (3)
┌──────────────────────────────┐
│🔴 Kernel crashed             │
│  memory-kernel-01            │
│  [Restart] [View Logs]       │
├──────────────────────────────┤
│🟡 Recording ready            │
│  meeting.mp3                 │
│  [Approve] [Reject]          │
├──────────────────────────────┤
│🔵 Queue running slow         │
│  +30% duration               │
│  [Spawn Agent]               │
└──────────────────────────────┘
```

**Data Source** (MVP):
- Use mock data (hardcoded 3 notifications)
- Post-MVP: Connect to `GET /api/copilot/notifications`

---

#### 2. Chat Interface (Basic Pattern Matching)
**User Input**:
```
You: Show me kernel status
```

**Grace Response** (MVP - Simple Logic):
```
Grace: Here's the current kernel status:
• Total: 7 kernels
• Active: 5
• Idle: 2
• Errors: 0
[View Full Table] [Restart All]
```

**Implementation** (MVP):
- Basic keyword matching (no LLM yet)
- Pattern: "status" → show status
- Pattern: "help" → show help text
- Pattern: "queue" → show HTM status
- Post-MVP: Connect to Grace's LLM

**Data Source**:
- `POST /api/copilot/chat/send` ✅ (enhance with better patterns)

---

#### 3. Quick Actions (Context-Aware)
**Layer 1**:
- [↻ Restart All Kernels]
- [⚡ Run Stress Test]
- [🔐 Check Crypto]

**Layer 2**:
- [➕ Spawn Agent]
- [⏸ Defer Low Priority]
- [🗑️ Clear Completed]

**Layer 3**:
- [🎯 Create Intent]
- [📜 Review Policies]
- [🎓 Generate Retro]

**Layer 4**:
- [🔐 Add Secret]
- [🎙️ Ingest All]
- [⚡ Run Stress Test]

**Implementation**:
- Buttons change based on `currentLayer` prop
- Click → Call `onAction(actionName)`

---

### Co-Pilot MVP Task List

**Backend** (1 hour):
- [x] ✅ Co-pilot endpoints already built
- [ ] Enhance chat logic with better pattern matching

**Frontend** (1 day):
- [x] ✅ CoPilotPane component already built
- [ ] Integrate into all 4 layers
- [ ] Test notification actions
- [ ] Test chat responses
- [ ] Hide voice/file/screenshot buttons for MVP

**Total**: ~1 day

---

## New Backend Endpoints Needed

### 1. HTM Management
```python
@router.post("/api/htm/priorities")
async def set_htm_priorities(priorities: dict):
    # Update priority weights
    return {"status": "updated", "priorities": priorities}

@router.post("/api/htm/pause")
async def pause_htm_queue():
    # Pause queue
    return {"status": "paused"}

@router.post("/api/htm/flush")
async def flush_completed_tasks():
    # Remove completed tasks
    return {"status": "flushed", "count": 45}

@router.post("/api/htm/spawn_agent")
async def spawn_htm_agent():
    # Spawn new agent
    return {"status": "spawned", "agent_id": "agent-xyz"}

@router.post("/api/htm/rules")
async def create_htm_rule(rule: dict):
    # Save auto-scale rule
    return {"status": "created", "rule_id": "rule-abc"}
```

### 2. Intent Management
```python
@router.post("/api/intent/create")
async def create_intent(intent: dict):
    # Create new intent
    return {
        "intent_id": "int-xyz",
        "status": "created",
        "estimated_tasks": 15
    }
```

### 3. Ingestion Management
```python
@router.post("/api/ingestion/flush")
async def flush_ingestion_queue():
    # Flush completed ingestion jobs
    return {"status": "flushed", "count": 23}
```

**Total**: 7 new simple endpoints (~2-3 hours to implement)

---

## MVP Implementation Timeline

### Week 1: Foundation
- **Day 1**: Backend - Add 7 new endpoints
- **Day 2**: Backend - Test all endpoints with Postman
- **Day 3**: Frontend - Set up component library (Button, Card, Modal)
- **Day 4**: Frontend - Build shared layout (UnifiedDashboard + NavBar)
- **Day 5**: Frontend - Polish CoPilotPane, test in isolation

### Week 2: Layers
- **Day 1**: Build Layer 1 (Ops Console)
- **Day 2**: Build Layer 2 (HTM Console)
- **Day 3**: Build Layer 3 (Learning)
- **Day 4**: Build Layer 4 (Dev/OS)
- **Day 5**: Integration testing

### Week 3: Polish & Deploy
- **Day 1**: Bug fixes from testing
- **Day 2**: Add loading states, error handling
- **Day 3**: Polish UX (animations, transitions)
- **Day 4**: User testing with operators
- **Day 5**: Deploy to staging

**Total**: 3 weeks to MVP

---

## Simplified Component Hierarchy

```
UnifiedDashboard
├── NavigationBar (simple tabs)
├── Layer1Dashboard
│   ├── TelemetryCards (3 cards)
│   ├── QuickActions (3 buttons)
│   └── KernelTerminalList
│       └── KernelTerminal × 7
├── Layer2Dashboard
│   ├── QueueMetricsCards (5 cards)
│   ├── PrioritySliders (4 sliders)
│   ├── HTMConsolePanel (1 panel)
│   └── SimpleRuleBuilder (1 form)
├── Layer3Dashboard
│   ├── IntentTable (simple table)
│   ├── RetrospectiveList (simple list)
│   ├── AgenticConsolePanel (1 panel)
│   └── SimpleIntentForm (1 form)
├── Layer4Dashboard
│   ├── StatusCards (3 cards)
│   ├── SimpleSecretForm (1 form)
│   ├── RecordingTable (simple table)
│   └── DevOSConsolePanel (1 panel)
└── CoPilotPane (shared, right rail)
    ├── NotificationsList
    ├── ChatMessages
    ├── ChatInput
    └── QuickActions
```

**Estimated Components**: ~30 (vs. 65+ in full spec)

---

## Testing Checklist (MVP)

### End-to-End Flows

**1. View Kernel Status & Restart**
- [ ] Navigate to Layer 1
- [ ] See 7 kernel terminals
- [ ] Expand Memory Kernel
- [ ] See logs (polling)
- [ ] Click [Restart]
- [ ] Verify status updates
- [ ] See toast notification

**2. Manage HTM Queue**
- [ ] Navigate to Layer 2
- [ ] See queue metrics cards
- [ ] Adjust priority sliders
- [ ] Click [Apply Changes]
- [ ] Verify queue updates
- [ ] Expand HTM console
- [ ] See task logs

**3. Create Intent**
- [ ] Navigate to Layer 3
- [ ] See intent table
- [ ] Click [+ Create Intent]
- [ ] Fill form
- [ ] Submit
- [ ] See new intent in table

**4. Store Secret**
- [ ] Navigate to Layer 4
- [ ] Fill secret form
- [ ] Check consent checkbox
- [ ] Click [Save Secret]
- [ ] Verify vault status updates
- [ ] See success toast

**5. Chat with Grace**
- [ ] Type "show kernel status" in co-pilot
- [ ] See Grace response
- [ ] Click action button in response
- [ ] Verify action executes

**6. Handle Notification**
- [ ] See notification in co-pilot
- [ ] Click action button
- [ ] Verify action executes
- [ ] Notification dismissed

---

## MVP vs. Full Feature Comparison

| Feature | MVP | Full Spec |
|---------|-----|-----------|
| **Kernels per Layer** | Simplified (1-2 panels) | All 24 kernels separate |
| **Log Streaming** | HTTP polling (5s) | WebSocket real-time |
| **Co-pilot Input** | Text only | Text + Voice + File + Screenshot |
| **Grace Intelligence** | Pattern matching | Full LLM integration |
| **Low-Code Widgets** | Simple forms/sliders | Visual editors, drag-drop |
| **Charts** | Tables only | Charts + graphs |
| **Playbook Builder** | Text forms | Visual block editor |
| **Priority Queue** | Sliders | Drag-and-drop |
| **Responsive** | Desktop only | Mobile + Tablet + Desktop |
| **Themes** | Dark only | Dark + Light |

---

## Quick Start Guide

### 1. Start Backend
```bash
cd backend
# Add new routes to serve.py first
python serve.py
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Test
```bash
# Visit frontend
open http://localhost:5173

# Test Layer 1
- Click "Layer 1" nav
- Expand Memory Kernel
- Click [Restart]

# Test Co-pilot
- Type "help" in chat
- See Grace respond
- Click quick action
```

---

## File Checklist

### Backend Files
- [x] ✅ `backend/routes/telemetry_api.py` (26 endpoints)
- [x] ✅ `backend/routes/telemetry_ws.py` (WebSocket)
- [x] ✅ `backend/routes/kernels_api.py` (8 endpoints)
- [x] ✅ `backend/routes/copilot_api.py` (7 endpoints)
- [ ] `backend/routes/htm_management.py` (7 new endpoints) ← TO BUILD
- [ ] `backend/routes/intent_management.py` (1 new endpoint) ← TO BUILD

### Frontend Files
- [x] ✅ `frontend/src/components/KernelTerminal.tsx`
- [x] ✅ `frontend/src/components/KernelTerminal.css`
- [x] ✅ `frontend/src/components/CoPilotPane.tsx`
- [x] ✅ `frontend/src/components/CoPilotPane.css`
- [ ] `frontend/src/pages/Layer1DashboardMVP.tsx` ← TO BUILD
- [ ] `frontend/src/pages/Layer2DashboardMVP.tsx` ← TO BUILD
- [ ] `frontend/src/pages/Layer3DashboardMVP.tsx` ← TO BUILD
- [ ] `frontend/src/pages/Layer4DashboardMVP.tsx` ← TO BUILD
- [ ] `frontend/src/components/UnifiedDashboardMVP.tsx` ← TO BUILD

---

## Success Criteria (MVP)

- [ ] All 4 layers load and display data
- [ ] Kernel terminals expand/collapse
- [ ] Logs display (polling, not WebSocket)
- [ ] Basic actions work (restart kernel, create intent, save secret)
- [ ] Co-pilot chat responds to simple queries
- [ ] Notifications display
- [ ] Quick actions execute
- [ ] System runs stable for 1 hour without errors

**Once MVP works, iterate toward full spec (drag-drop, visual builders, LLM, etc.)**

---

## Next Action

**Build the 7 HTM management endpoints, then create Layer1DashboardMVP.tsx to prove the pattern works.**

Would you like me to:
1. Build the HTM management endpoints now?
2. Create Layer1DashboardMVP.tsx as a working example?
3. Or both in parallel?
