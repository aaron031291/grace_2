# Bi-Directional Notifications System ✅

Grace can now proactively push real-time updates to the chat.

---

## Overview

**Grace sends notifications for:**
- ✅ Task completion ("Deployment finished")
- ⚠️ Approval needed ("Action requires approval")
- ❌ Errors detected ("Database connection failed")
- 🔧 Healing triggered ("Auto-healing deployment failure")
- 🧠 Learning complete ("Ingested API_Spec.pdf")
- 🚀 Task started ("Running 5 background tasks")

**All appear in the chat thread** with appropriate badges and styling.

---

## Architecture

```
Backend Systems                      Notification Stream
(Learning, Guardian,                        │
 Self-Heal, Missions)                       │
        │                                   │
        ↓                                   │
   Event Bus ─────────────────────→  /api/notifications/stream
        │                                   │  (WebSocket)
        │                                   │
   Grace detects:                           │
   - Task complete                          ↓
   - Approval needed              ┌──────────────────┐
   - Error occurred               │  notify_user()   │
   - Healing triggered            └────────┬─────────┘
        │                                   │
        └────────────────────────────────→  │
                                            ↓
                                   WebSocket.send()
                                            │
                                            ↓
                                  Frontend Chat UI
                                  (Notification appears
                                   in conversation)
```

---

## How It Works

### 1. Backend Event Detection

**File:** [notifications_api.py](file:///c:/Users/aaron/grace_2/backend/routes/notifications_api.py)

**Event bus subscription:**
```python
def handle_governance_event(event: Event):
    if event.data.get("action") == "approval_needed":
        notify_user(
            user_id=event.data.get("user_id"),
            notification_type="approval_needed",
            message=f"Approval needed: {event.data.get('action_type')}",
            badge="⚠️"
        )

event_bus.subscribe(EventType.GOVERNANCE_CHECK, handle_governance_event)
```

### 2. Notification Delivery

**Push to connected clients:**
```python
async def notify_user(user_id, notification_type, message, badge="🤖"):
    notification = {
        "type": notification_type,
        "message": message,
        "badge": badge,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all active WebSocket connections for this user
    for ws in active_connections.get(user_id, []):
        await ws.send_json(notification)
```

### 3. Frontend Receipt

**React hook:** [useNotifications.ts](file:///c:/Users/aaron/grace_2/frontend/src/hooks/useNotifications.ts)

```typescript
websocket.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  setNotifications((prev) => [...prev, notification]);
};
```

### 4. Display in Chat

**ChatPanel integration:**
```typescript
useEffect(() => {
  notifications.forEach((notif) => {
    setMessages((prev) => [...prev, {
      role: 'notification',
      content: notif.message,
      badge: notif.badge,
      timestamp: notif.timestamp
    }]);
  });
}, [notifications]);
```

---

## Notification Types

| Type | Badge | When | Example |
|------|-------|------|---------|
| `task_started` | 🚀 | Background task begins | "Deployment task started: task_123" |
| `task_completed` | ✅ | Background task finishes | "Deployment completed successfully" |
| `task_failed` | ❌ | Background task fails | "Deployment failed: Connection timeout" |
| `approval_needed` | ⚠️ | Action requires approval | "Approval needed: deploy_service" |
| `error_detected` | ❌ | System error occurs | "Database connection failed" |
| `healing_triggered` | 🔧 | Self-healing activates | "Auto-healing deployment failure" |
| `learning_complete` | 🧠 | Document ingested | "Ingested CRM_API_Spec.pdf, trust 0.92" |

---

## Example Flows

### Task Completion Notification

**User (chat):**
```
"Run deployment in the background"
```

**Grace (chat):**
```
Starting deployment as background task #5.
I'll notify you when it's complete.
```

**Background:**
```python
task_id = await start_background_task(
    task_id="task_deploy_123",
    task_type="deployment",
    task_fn=deploy_backend,
    user_id="user"
)
# → Notification sent: "🚀 Deployment task started: task_deploy_123"
```

**Chat shows notification:**
```
┌──────────────────────────────────────┐
│ 🚀 Grace Notification                │
│ Deployment task started: task_123    │
│ 10:30 AM                             │
└──────────────────────────────────────┘
```

**5 minutes later, deployment completes:**

**Notification pushed:**
```
┌──────────────────────────────────────┐
│ ✅ Grace Notification                │
│ Deployment completed successfully    │
│ 10:35 AM                             │
└──────────────────────────────────────┘
```

**User sees it in real-time** without refreshing!

---

### Approval Request Notification

**Background:**
Grace's autonomous learning tries to modify a file.

**Governance check:**
```python
governance_result = await action_gateway.request_action(
    action_type="modify_file",
    agent="learning_supervisor",
    params={"file_path": "config.yaml"},
    trace_id="auto_learn_123"
)

if not governance_result.get("approved"):
    # Notify user
    await notify_user(
        user_id="user",
        notification_type="approval_needed",
        message="Learning supervisor wants to modify config.yaml",
        data={"trace_id": "auto_learn_123"},
        badge="⚠️"
    )
```

**Chat shows:**
```
┌──────────────────────────────────────┐
│ ⚠️ Grace Notification                │
│ Learning supervisor wants to modify  │
│ config.yaml                          │
│                                      │
│ [View Details] [Approve] [Reject]   │
└──────────────────────────────────────┘
```

---

### Error + Healing Notification

**Background:**
Deployment fails, self-healing triggers.

**Error detected:**
```python
await notify_user(
    user_id="user",
    notification_type="error_detected",
    message="Deployment failed: Connection timeout",
    data={"error": "...", "trace_id": "deploy_456"},
    badge="❌"
)
```

**Self-healing starts:**
```python
await notify_user(
    user_id="user",
    notification_type="healing_triggered",
    message="Auto-healing deployment failure (rollback strategy)",
    data={"playbook": "rollback_deployment"},
    badge="🔧"
)
```

**Chat shows:**
```
┌──────────────────────────────────────┐
│ ❌ Grace Notification                │
│ Deployment failed: Connection timeout│
│ 10:40 AM                             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 🔧 Grace Notification                │
│ Auto-healing deployment failure      │
│ (rollback strategy)                  │
│ 10:40 AM                             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ ✅ Grace Notification                │
│ Healing complete: Rolled back to    │
│ version v2.0.5                       │
│ 10:41 AM                             │
└──────────────────────────────────────┘
```

---

## Commands from Chat

Users can manage background work from the chat:

### List Active Tasks

**User:**
```
"Show background tasks"
```

**Frontend sends:**
```typescript
ws.send(JSON.stringify({ type: 'list_tasks' }));
```

**Grace responds:**
```
┌──────────────────────────────────────┐
│ Background Tasks (3 active):         │
│                                      │
│ ✅ task_deploy_123 - Deployment      │
│    Status: Running (5m 23s)          │
│                                      │
│ 🔄 task_learn_456 - Learning         │
│    Status: Running (2m 10s)          │
│                                      │
│ ⏸️ task_backup_789 - Backup          │
│    Status: Paused                    │
└──────────────────────────────────────┘
```

### Cancel Task

**User:**
```
"Cancel task task_backup_789"
```

**Frontend:**
```typescript
ws.send(JSON.stringify({
  type: 'cancel_task',
  task_id: 'task_backup_789'
}));
```

**Notification:**
```
┌──────────────────────────────────────┐
│ ⚠️ Grace Notification                │
│ Task task_backup_789 has been        │
│ cancelled                            │
└──────────────────────────────────────┘
```

### Pause/Resume Learning

**User:**
```
"Pause learning for now"
```

**Frontend:**
```typescript
ws.send(JSON.stringify({ type: 'pause_learning' }));
```

**Notification:**
```
┌──────────────────────────────────────┐
│ ⏸️ Grace Notification                │
│ Learning jobs paused. Grace will not │
│ start new learning tasks.            │
└──────────────────────────────────────┘
```

---

## Integration with Background Systems

### HTM/Learning Loop

**When learning completes:**
```python
# In learning supervisor
await event_bus.publish(Event(
    event_type=EventType.LEARNING_OUTCOME,
    source="learning_supervisor",
    data={
        "action": "learning_complete",
        "source": "kubernetes_docs",
        "user_id": "user"
    }
))

# notifications_api.py receives event → pushes notification
→ User sees: "🧠 Learned from kubernetes_docs"
```

### Guardian System

**When guardian detects issue:**
```python
await event_bus.publish(Event(
    event_type=EventType.AGENT_ACTION,
    source="guardian",
    data={
        "action": "error_detected",
        "message": "High memory usage detected",
        "user_id": "user"
    }
))

→ User sees: "⚠️ High memory usage detected"
```

### Self-Healing

**When healing triggers:**
```python
await event_bus.publish(Event(
    event_type=EventType.AGENT_ACTION,
    source="self_heal",
    data={
        "action": "self_healing_triggered",
        "playbook": "restart_service",
        "user_id": "user"
    }
))

→ User sees: "🔧 Auto-healing: Restarting service"
```

### Mission Control

**When mission completes:**
```python
await event_bus.publish(Event(
    event_type=EventType.AGENT_ACTION,
    source="mission_control",
    data={
        "action": "mission_completed",
        "mission_id": "mission_123",
        "user_id": "user"
    }
))

→ User sees: "✅ Mission mission_123 completed"
```

---

## Chat Commands

Users can query background systems through chat:

| User Says | Grace Responds With |
|-----------|---------------------|
| "Show background tasks" | List of active tasks via notification |
| "Cancel task X" | Cancels task, sends confirmation notification |
| "Pause learning" | Pauses learning jobs, notifies |
| "Resume learning" | Resumes learning, notifies |
| "What's Grace doing?" | Status of all background systems |
| "Show healing attempts" | Recent self-healing logs |
| "List active missions" | Current mission status |

**Grace talks from her brain** - she pulls from:
- World Model (canonical knowledge)
- RAG (semantic search)
- Event Bus (recent events)
- Action Gateway (pending approvals)
- Learning Supervisor (current learning jobs)
- Guardian (detected issues)
- Self-Heal (healing attempts)

**All through `/api/unified/chat`** - No separate dashboards needed!

---

## WebSocket Protocol

### Client → Server (Commands)

```json
{"type": "list_tasks"}
{"type": "cancel_task", "task_id": "task_123"}
{"type": "pause_learning"}
{"type": "resume_learning"}
{"type": "ping"}
```

### Server → Client (Notifications)

```json
{
  "type": "task_completed",
  "message": "Deployment completed successfully",
  "badge": "✅",
  "timestamp": "2024-01-15T10:35:00",
  "data": {
    "task_id": "task_deploy_123",
    "result": {"status": "success"}
  }
}
```

---

## Implementation

### Backend

**File:** [notifications_api.py](file:///c:/Users/aaron/grace_2/backend/routes/notifications_api.py)

**Key functions:**
- `notification_stream()` - WebSocket endpoint
- `notify_user()` - Push notification to user
- `subscribe_to_events()` - Connect to event bus
- `start_background_task()` - Run task with notifications
- Command handlers (list/cancel/pause/resume)

### Frontend

**File:** [useNotifications.ts](file:///c:/Users/aaron/grace_2/frontend/src/hooks/useNotifications.ts)

**Hook:**
```typescript
const { notifications, connected, listTasks, pauseLearning } = useNotifications('user');
```

**Integration in ChatPanel:**
```typescript
useEffect(() => {
  notifications.forEach((notif) => {
    setMessages((prev) => [...prev, {
      role: 'notification',
      content: notif.message,
      badge: notif.badge
    }]);
  });
}, [notifications]);
```

---

## Example: Background Deployment

```
1. User: "Deploy backend in the background"

2. Grace starts background task:
   await start_background_task(
     task_id="deploy_123",
     task_type="deployment",
     task_fn=deploy_backend,
     user_id="user"
   )

3. Notification pushed:
   🚀 "Deployment task started: deploy_123"

4. User sees in chat immediately (no polling!)

5. User continues chatting while deployment runs

6. 5 minutes later, deployment completes

7. Notification pushed:
   ✅ "Deployment completed successfully"

8. User sees notification appear in chat

9. User: "Show deployment logs"

10. Grace includes logs in response
```

---

## Files Created/Modified

### Backend
1. [backend/routes/notifications_api.py](file:///c:/Users/aaron/grace_2/backend/routes/notifications_api.py) - WebSocket endpoint ⭐
2. [backend/main.py](file:///c:/Users/aaron/grace_2/backend/main.py) - Register notifications API

### Frontend
3. [frontend/src/hooks/useNotifications.ts](file:///c:/Users/aaron/grace_2/frontend/src/hooks/useNotifications.ts) - Notification hook ⭐
4. [frontend/src/components/ChatPanel.tsx](file:///c:/Users/aaron/grace_2/frontend/src/components/ChatPanel.tsx) - Notification display
5. [frontend/src/components/ChatPanel.css](file:///c:/Users/aaron/grace_2/frontend/src/components/ChatPanel.css) - Notification styles

---

## Testing

### Connect to Notification Stream

```javascript
const ws = new WebSocket('ws://localhost:8000/api/notifications/stream?user_id=user');

ws.onopen = () => {
  console.log('Connected to notifications');
};

ws.onmessage = (event) => {
  const notif = JSON.parse(event.data);
  console.log('Notification:', notif);
};

// Send command
ws.send(JSON.stringify({ type: 'list_tasks' }));
```

### Trigger Test Notification

```python
# In backend
from backend.routes.notifications_api import notify_user

await notify_user(
    user_id="user",
    notification_type="test",
    message="This is a test notification",
    badge="🧪"
)
```

### Chat Command

```
User: "List active tasks"
→ Frontend sends: {type: 'list_tasks'}
→ Backend responds with task list
→ Grace shows tasks in chat
```

---

## Background System Integration

### All background systems now notify through chat:

**Learning Supervisor:**
- Document ingestion complete
- Learning job finished
- Trust score calculated

**Guardian:**
- Issue detected
- Health check failed
- Threshold exceeded

**Self-Heal:**
- Healing triggered
- Playbook executed
- Healing complete/failed

**Mission Control:**
- Mission started
- Mission completed
- Mission failed

**Action Gateway:**
- Approval needed
- Action approved
- Action executed

**All appear in chat conversation!** No separate dashboards needed.

---

## Benefits

✅ **Real-time updates** - No polling required  
✅ **In-context** - Notifications appear in conversation  
✅ **Actionable** - Can approve/view details inline  
✅ **Unified interface** - Chat is the only UI needed  
✅ **Background-aware** - Grace reports her own state  
✅ **Bi-directional** - User can query and control  

---

**Status: ✅ COMPLETE**

Grace can now proactively communicate while background systems run. The chat becomes a living conversation where Grace narrates what she's doing!
