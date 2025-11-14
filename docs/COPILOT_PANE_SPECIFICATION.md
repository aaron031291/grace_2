# Grace Co-Pilot Pane - Interactive AI Assistant UI

**Grace's persistent presence: Always-on, bi-directional, multi-modal**

---

## Overview

The Co-Pilot Pane is a **fixed right-rail panel** that remains visible across all dashboard layers. It serves as Grace's interactive interface, enabling bi-directional communication, proactive notifications, contextual actions, and multi-modal interaction.

**Think of it as**: Grace's "face" in the UI - where she talks to you, listens to you, and takes action.

---

## Layout & Positioning

### Desktop (> 1200px)
```
┌────────────────────────────────────────────────────────┐
│ [Nav: Layer 1 | Layer 2 | Layer 3 | Layer 4]           │
├────────────────────────────────────┬───────────────────┤
│                                    │                   │
│                                    │  ╔═══════════════╗│
│         Dashboard Content          │  ║   Co-Pilot    ║│
│         (Layer 1-4 Views)          │  ║     Pane      ║│
│                                    │  ║               ║│
│                                    │  ║ • Notifications│
│                                    │  ║ • Chat        ║│
│                                    │  ║ • Actions     ║│
│                                    │  ║ • Context     ║│
│                                    │  ╚═══════════════╝│
│                                    │   (Fixed 380px)   │
└────────────────────────────────────┴───────────────────┘
```

**Width**: 380px fixed  
**Position**: Sticky right rail  
**Visibility**: Always visible, cannot be closed (can be collapsed to 60px icon bar)

### Tablet (768-1200px)
- **Collapsed by default** to icon bar (60px)
- **Expands on click** to 320px overlay
- **Auto-collapses** after inactivity (30s)

### Mobile (< 768px)
- **Hidden by default**
- **Floating action button** (bottom-right corner)
- **Slides up as bottom sheet** on click (full width, 70% height)

---

## Component Structure

```
Co-Pilot Pane
├─ Header
│  ├─ Grace Avatar (animated when speaking/listening)
│  ├─ Status Indicator (idle/listening/thinking/speaking)
│  └─ Collapse Button
│
├─ Notifications Panel (expandable)
│  ├─ Active Alerts (red badges)
│  ├─ Pending Actions (yellow badges)
│  └─ Info Messages (blue badges)
│
├─ Chat Interface (scrollable, main area)
│  ├─ Message History
│  │  ├─ Grace Messages (left-aligned)
│  │  └─ User Messages (right-aligned)
│  ├─ Rich Content Support
│  │  ├─ Code snippets (syntax highlighted)
│  │  ├─ Tables/charts (inline)
│  │  ├─ Images/screenshots
│  │  ├─ Audio players (for recordings)
│  │  └─ Action buttons (contextual)
│  └─ Typing Indicator
│
├─ Input Area (bottom)
│  ├─ Multi-Modal Input Selector
│  │  ├─ Text input (default)
│  │  ├─ Voice input (🎤 button)
│  │  ├─ File upload (📎 button)
│  │  └─ Screen capture (📸 button)
│  ├─ Text Input Field (expandable)
│  ├─ Send Button
│  └─ Voice Input Button
│
└─ Quick Actions Bar (collapsible)
   ├─ Common Tasks (context-aware)
   ├─ Recent Commands
   └─ Suggested Actions
```

---

## Sections Detailed

### 1. Header

**Components**:
- **Grace Avatar**: Animated circle (pulsing when active)
- **Status Badge**: 
  - 🟢 Idle - "Grace is ready"
  - 🟡 Listening - "Listening..."
  - 🔵 Thinking - "Processing..."
  - 🟣 Speaking - "Grace is responding..."
- **Collapse Button**: Minimize to icon bar

**Visual**:
```
┌─────────────────────────────────────┐
│  [●] Grace                    [─]   │
│   🟢 Ready                          │
└─────────────────────────────────────┘
```

---

### 2. Notifications Panel

**Purpose**: Proactive alerts from Grace that demand attention

**Types**:
1. **Critical Alerts** (red) - Require immediate action
2. **Pending Actions** (yellow) - Awaiting user approval
3. **Info Updates** (blue) - FYI notifications

**Example Notifications**:
```
┌─────────────────────────────────────┐
│ Notifications (3)            [▼][×] │
├─────────────────────────────────────┤
│ 🔴 Kernel Error Detected            │
│    ingestion-kernel-01 crashed      │
│    [View Logs] [Restart]     2m ago │
├─────────────────────────────────────┤
│ 🟡 Recording Ready for Ingestion    │
│    meeting_2025-11-14.mp3           │
│    [Approve] [Reject]       5m ago  │
├─────────────────────────────────────┤
│ 🔵 HTM Queue Running Long           │
│    Queue depth: 145 (+30%)          │
│    [Spawn Agent] [Defer]    8m ago  │
└─────────────────────────────────────┘
```

**Interaction**:
- **Click notification** → Jump to relevant layer with context highlighted
- **Action buttons** → Execute action directly from notification
- **Dismiss (×)** → Remove notification
- **Collapse (▼)** → Hide panel, show badge count on header

**API Integration**:
- **GET /api/copilot/notifications** → Fetch active notifications
- **POST /api/copilot/notifications/{id}/action** → Execute action
- **DELETE /api/copilot/notifications/{id}** → Dismiss notification

---

### 3. Chat Interface

**Purpose**: Bi-directional conversation with Grace

**Message Types**:

#### Grace Messages (System)
```
┌─────────────────────────────────────┐
│ Grace                        10:30a │
│ ┌─────────────────────────────────┐ │
│ │ I've detected 3 kernels are     │ │
│ │ idle. Would you like me to      │ │
│ │ reallocate them?                │ │
│ │                                 │ │
│ │ [Yes, Reallocate] [No, Keep]   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### User Messages
```
┌─────────────────────────────────────┐
│                         You  10:31a │
│ ┌─────────────────────────────────┐ │
│ │ Show me the HTM queue status    │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### Rich Content Messages

**Code Snippet**:
```
┌─────────────────────────────────────┐
│ Grace                        10:32a │
│ ┌─────────────────────────────────┐ │
│ │ Here's the kernel config:       │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ {                           │ │ │
│ │ │   "kernel_id": "kern-123",  │ │ │
│ │ │   "max_tasks": 50           │ │ │
│ │ │ }                           │ │ │
│ │ └─────────────────────────────┘ │ │
│ │ [Copy] [Apply Changes]          │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Table/Chart**:
```
┌─────────────────────────────────────┐
│ Grace                        10:33a │
│ ┌─────────────────────────────────┐ │
│ │ HTM Task Breakdown:             │ │
│ │ ┌──────────┬───────┬─────────┐ │ │
│ │ │ Origin   │ Count │ Avg Time││ │
│ │ ├──────────┼───────┼─────────┤ │ │
│ │ │ Filesys  │   45  │  12.5s  ││ │
│ │ │ Remote   │   30  │  18.2s  ││ │
│ │ │ Hunter   │   25  │   9.1s  ││ │
│ │ └──────────┴───────┴─────────┘ │ │
│ │ [Export CSV] [View Details]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Image/Screenshot**:
```
┌─────────────────────────────────────┐
│ Grace                        10:34a │
│ ┌─────────────────────────────────┐ │
│ │ I captured the error screen:    │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ [Screenshot Preview]        │ │ │
│ │ │                             │ │ │
│ │ └─────────────────────────────┘ │ │
│ │ [View Full Size] [Download]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Audio Player** (for voice recordings):
```
┌─────────────────────────────────────┐
│ Grace                        10:35a │
│ ┌─────────────────────────────────┐ │
│ │ Transcript from recording:      │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ [▶] meeting_2025-11-14.mp3  │ │ │
│ │ │ ████████░░░░░░░  0:45 / 2:30│ │ │
│ │ └─────────────────────────────┘ │ │
│ │ "Meeting discussed Q4 goals..." │ │
│ │ [Read Full Transcript]          │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Action Buttons** (contextual):
```
┌─────────────────────────────────────┐
│ Grace                        10:36a │
│ ┌─────────────────────────────────┐ │
│ │ Recording is ready. What would  │ │
│ │ you like to do?                 │ │
│ │                                 │ │
│ │ [✓ Approve for Learning]        │ │
│ │ [👁 Review First]               │ │
│ │ [✕ Delete Recording]            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

### 4. Input Area

**Text Input** (default):
```
┌─────────────────────────────────────┐
│ [📎] [🎤] [📸]                      │
│ ┌─────────────────────────────────┐ │
│ │ Ask Grace anything...          │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
│                              [Send] │
└─────────────────────────────────────┘
```

**Voice Input** (active):
```
┌─────────────────────────────────────┐
│ 🎤 Listening...                     │
│ ┌─────────────────────────────────┐ │
│ │ ●●●●●●●●●●●●●●●●●●●●●●●       │ │
│ │ "Show me kernel status"         │ │
│ └─────────────────────────────────┘ │
│                          [Stop] [×] │
└─────────────────────────────────────┘
```

**File Upload**:
```
┌─────────────────────────────────────┐
│ Attach File                         │
│ ┌─────────────────────────────────┐ │
│ │ Drag & drop or click to upload  │ │
│ │                                 │ │
│ │ Supported: logs, configs, code, │ │
│ │ images, audio, video            │ │
│ └─────────────────────────────────┘ │
│                        [Cancel] [×] │
└─────────────────────────────────────┘
```

**Screen Capture**:
```
┌─────────────────────────────────────┐
│ Capture Screen                      │
│ ┌─────────────────────────────────┐ │
│ │ Select area to capture:         │ │
│ │                                 │ │
│ │ [Full Screen]                   │ │
│ │ [Current Layer]                 │ │
│ │ [Custom Selection]              │ │
│ └─────────────────────────────────┘ │
│                        [Cancel] [×] │
└─────────────────────────────────────┘
```

---

### 5. Quick Actions Bar

**Purpose**: Context-aware shortcuts based on current layer

**Layer 1 (Ops Console)**:
```
┌─────────────────────────────────────┐
│ Quick Actions                  [▲]  │
├─────────────────────────────────────┤
│ [Restart All Kernels]               │
│ [Run Full Stress Test]              │
│ [Check Crypto Health]               │
│ [View Ingestion Logs]               │
└─────────────────────────────────────┘
```

**Layer 2 (HTM Console)**:
```
┌─────────────────────────────────────┐
│ Quick Actions                  [▲]  │
├─────────────────────────────────────┤
│ [Spawn Extra Agent]                 │
│ [Defer Low Priority Tasks]          │
│ [Clear Completed Tasks]             │
│ [Export Queue Snapshot]             │
└─────────────────────────────────────┘
```

**Layer 3 (Learning)**:
```
┌─────────────────────────────────────┐
│ Quick Actions                  [▲]  │
├─────────────────────────────────────┤
│ [Create New Intent]                 │
│ [Review Pending Policies]           │
│ [Generate Retrospective]            │
│ [Export Learning Report]            │
└─────────────────────────────────────┘
```

**Layer 4 (Dev/OS)**:
```
┌─────────────────────────────────────┐
│ Quick Actions                  [▲]  │
├─────────────────────────────────────┤
│ [Add New Secret]                    │
│ [Ingest All Recordings]             │
│ [Run System Stress Test]            │
│ [View Deployment Status]            │
└─────────────────────────────────────┘
```

---

## Proactive Messaging Examples

### 1. Alert & Suggest Action
```
Grace (System)                   10:40a
┌──────────────────────────────────┐
│ 🔴 Alert: Kernel crashed         │
│                                  │
│ ingestion-kernel-01 encountered  │
│ an error and stopped. Last log:  │
│                                  │
│ "OutOfMemoryError: heap full"    │
│                                  │
│ I can:                           │
│ • [Restart with more memory]     │
│ • [View full crash dump]         │
│ • [Disable this kernel]          │
│                                  │
│ What would you like me to do?    │
└──────────────────────────────────┘
```

### 2. Request Approval
```
Grace (System)                   10:42a
┌──────────────────────────────────┐
│ 🟡 Approval Needed               │
│                                  │
│ A new recording is ready:        │
│ • meeting_2025-11-14.mp3         │
│ • Duration: 2h 15m               │
│ • Size: 128 MB                   │
│                                  │
│ Approve for learning ingestion?  │
│                                  │
│ [✓ Yes, Ingest] [👁 Review]     │
│ [✕ Delete]                       │
└──────────────────────────────────┘
```

### 3. Provide Context & Insight
```
Grace (System)                   10:45a
┌──────────────────────────────────┐
│ 💡 Insight: HTM queue slowdown   │
│                                  │
│ I noticed tasks are taking 30%   │
│ longer than usual. Analysis:     │
│                                  │
│ • Remote tasks: +45% duration    │
│ • Network latency: 250ms avg     │
│ • Likely cause: API rate limits  │
│                                  │
│ Recommendation:                  │
│ • [Spawn local agent]            │
│ • [Defer remote tasks]           │
│ • [View detailed metrics]        │
└──────────────────────────────────┘
```

### 4. Completion Notification
```
Grace (System)                   10:50a
┌──────────────────────────────────┐
│ ✅ Task Complete                 │
│                                  │
│ Stress test finished:            │
│ • Duration: 10 minutes           │
│ • Max queue depth: 145           │
│ • Error rate: 0.5%               │
│ • Bottlenecks: DB connections    │
│                                  │
│ [View Full Report]               │
│ [Export Results]                 │
└──────────────────────────────────┘
```

### 5. Ask for Guidance
```
Grace (System)                   10:55a
┌──────────────────────────────────┐
│ ❓ Need your input               │
│                                  │
│ I found 3 duplicate secrets in   │
│ the vault:                       │
│ • OPENAI_KEY (created Nov 10)    │
│ • OPENAI_KEY (created Nov 12)    │
│ • OPENAI_KEY (created Nov 14)    │
│                                  │
│ Which should I keep?             │
│                                  │
│ [Keep Latest] [Keep Oldest]      │
│ [Review Manually]                │
└──────────────────────────────────┘
```

---

## Chat Commands

Users can type structured commands for quick actions:

### Status Commands
```
/status kernels        → Show kernel status
/status htm            → Show HTM queue status
/status crypto         → Show crypto health
/status all            → Show full system status
```

### Action Commands
```
/restart kernel-01     → Restart specific kernel
/stress run full       → Run full stress test
/ingest rec-abc123     → Ingest specific recording
/spawn agent           → Spawn new HTM agent
```

### Query Commands
```
/logs kernel-01        → Show kernel logs
/tasks origin=remote   → Filter HTM tasks
/intents active        → Show active intents
/secrets status        → Show vault status
```

### Navigation Commands
```
/goto layer1           → Switch to Layer 1
/goto layer2           → Switch to Layer 2
/goto layer3           → Switch to Layer 3
/goto layer4           → Switch to Layer 4
```

### Help Commands
```
/help                  → Show all commands
/help kernels          → Show kernel-related commands
/help htm              → Show HTM-related commands
```

**Command Autocomplete**: Type `/` to see suggestions

---

## Multi-Modal Input/Output

### Input Modes

**1. Text** (default)
- Typed commands and queries
- Natural language questions
- Slash commands

**2. Voice** (🎤 button)
- Voice-to-text transcription
- Natural language processing
- Hands-free operation
- **API**: `POST /api/copilot/voice/transcribe`

**3. File Upload** (📎 button)
- Log files → Auto-analysis
- Config files → Validation
- Code snippets → Review
- Images → OCR and analysis
- **API**: `POST /api/copilot/upload`

**4. Screen Capture** (📸 button)
- Full screen or selection
- Annotate before sending
- OCR for text extraction
- **API**: `POST /api/copilot/screenshot`

### Output Modes

**1. Text** (default)
- Formatted markdown
- Code blocks with syntax highlighting
- Links and references

**2. Rich Content**
- Tables and charts
- Images and screenshots
- Audio/video players
- Interactive buttons

**3. Voice** (optional, future)
- Text-to-speech responses
- Audio playback of summaries
- **API**: `GET /api/copilot/voice/synthesize`

**4. Notifications**
- Toast alerts
- Browser notifications
- Email/SMS (external)

---

## Backend API Endpoints

### Chat & Messaging

```
POST /api/copilot/chat/send
Request: {
  "message": "Show me kernel status",
  "context": {
    "current_layer": "layer1",
    "selected_kernel": "kern-123"
  }
}
Response: {
  "message_id": "msg-xyz789",
  "grace_response": {
    "text": "Here's the current kernel status...",
    "rich_content": { /* table/chart data */ },
    "actions": [
      {"label": "Restart Kernel", "action": "restart_kernel", "params": {"kernel_id": "kern-123"}}
    ]
  }
}
```

### Notifications

```
GET /api/copilot/notifications
Response: {
  "notifications": [
    {
      "id": "notif-123",
      "type": "alert",
      "severity": "critical",
      "title": "Kernel Error Detected",
      "message": "ingestion-kernel-01 crashed",
      "actions": [
        {"label": "View Logs", "action": "view_logs", "params": {"kernel_id": "kern-01"}},
        {"label": "Restart", "action": "restart_kernel", "params": {"kernel_id": "kern-01"}}
      ],
      "created_at": "2025-11-14T10:40:00Z"
    }
  ]
}
```

### Voice Input

```
POST /api/copilot/voice/transcribe
Body: FormData with audio file
Response: {
  "transcription": "Show me kernel status",
  "confidence": 0.95
}
```

### File Upload

```
POST /api/copilot/upload
Body: FormData with file
Response: {
  "file_id": "file-abc123",
  "analysis": {
    "type": "log_file",
    "errors_found": 5,
    "summary": "Found 5 errors in kernel logs"
  },
  "suggested_actions": [
    {"label": "View Errors", "action": "show_errors"}
  ]
}
```

### Actions

```
POST /api/copilot/actions/execute
Request: {
  "action": "restart_kernel",
  "params": {"kernel_id": "kern-123"}
}
Response: {
  "status": "success",
  "result": "Kernel restarted successfully"
}
```

---

## State Management

### Grace's "Memory" (Context)

Grace maintains context across conversations:

```typescript
interface GraceContext {
  current_layer: "layer1" | "layer2" | "layer3" | "layer4"
  recent_actions: Action[]
  pending_approvals: Notification[]
  conversation_history: Message[]
  user_preferences: {
    auto_approve_recordings: boolean
    notification_threshold: "all" | "important" | "critical"
    voice_enabled: boolean
  }
}
```

**Stored**: Local storage + backend sync  
**Cleared**: On logout or explicit "Clear Context"

---

## Integration with Layers

### Layer 1 (Ops Console)

**Grace Can**:
- Alert on kernel crashes → Suggest restart
- Notice high stress scores → Recommend load balancing
- Detect crypto issues → Explain impact and solution

**User Can Ask**:
- "What's wrong with kernel-01?"
- "Run a stress test on all kernels"
- "Show me ingestion logs from last hour"

---

### Layer 2 (HTM Console)

**Grace Can**:
- Alert on queue depth increase → Suggest spawn agent
- Identify slow tasks → Recommend priority changes
- Detect SLA breaches → Auto-escalate or ask approval

**User Can Ask**:
- "Why is the queue slow?"
- "Filter tasks by filesystem origin"
- "Override priority for task-xyz to critical"

---

### Layer 3 (Learning)

**Grace Can**:
- Suggest policies based on patterns
- Summarize retrospectives
- Alert on intent completion
- Recommend playbook improvements

**User Can Ask**:
- "What did we learn today?"
- "Show me active intents"
- "Accept all pending policies"

---

### Layer 4 (Dev/OS)

**Grace Can**:
- Prompt for secret consent
- Ask approval for recording ingestion
- Report deployment status
- Suggest stress test parameters

**User Can Ask**:
- "Add a new API key"
- "Ingest all pending recordings"
- "Run a 10-minute stress test"
- "Show remote access sessions"

---

## Accessibility

- **Keyboard Navigation**: Tab through notifications, focus chat input with `/`
- **Screen Reader**: ARIA labels on all interactive elements
- **High Contrast**: Respect system theme
- **Voice Control**: Full voice input/output support
- **Shortcuts**: 
  - `Ctrl+/` → Focus chat
  - `Ctrl+K` → Open command palette
  - `Esc` → Dismiss notifications

---

## Next Steps for Implementation

1. **Design Co-Pilot Pane** component structure
2. **Implement Chat API** endpoints
3. **Add Notification System** with WebSocket push
4. **Build Multi-Modal Input** handlers
5. **Create Action Execution** framework
6. **Test Bi-Directional** conversation flow

---

**Grace Co-Pilot Pane: Your always-on AI assistant** 🤖
