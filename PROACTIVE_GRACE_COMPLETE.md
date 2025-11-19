# Proactive Grace - Reminders & Background Tasks ✅

Complete implementation of reminders, background task monitoring, and proactive notifications.

---

## Overview

Grace can now:
- ✅ Create reminders from natural language
- ✅ Track and display background tasks/jobs
- ✅ Proactively notify when tasks complete or need input
- ✅ Keep everything in the conversation thread

---

## Feature 1: Natural Language Reminders

### Creating Reminders

**In Chat:**
```
User: Remind me tomorrow to review the CRM deploy
Grace: ✅ Reminder set! I'll notify you when it's time.
```

**Behind the scenes:**
```python
# Parses:
# - "tomorrow" → trigger_time = tomorrow at 9 AM
# - "to review the CRM deploy" → message

reminder_id = await reminder_service.parse_natural_language(
    user_id="user",
    text="Remind me tomorrow to review the CRM deploy"
)
```

### Supported Patterns

| Pattern | Example | Trigger |
|---------|---------|---------|
| **Tomorrow** | "Remind me tomorrow to review metrics" | Next day at 9 AM |
| **In X hours** | "Remind me in 2 hours to check logs" | 2 hours from now |
| **In X minutes** | "Remind me in 30 minutes" | 30 minutes from now |
| **Recurring** | "Remind me every Monday to review KPIs" | Weekly on Mondays |
| **Event-based** | "Remind me when the import finishes" | On event trigger |

### When Reminder Triggers

```
[Notification appears]
⏰ Reminder: Review the CRM deploy

[Also appears in chat]
Grace: ⏰ Reminder: You asked me to remind you to review the CRM deploy
```

**Notification payload:**
```json
{
  "type": "reminder",
  "user_id": "user",
  "message": "⏰ Reminder: Review the CRM deploy",
  "badge": "⏰",
  "data": {
    "reminder_id": "reminder_abc123"
  },
  "timestamp": "2025-11-20T09:00:00.000Z"
}
```

---

## Feature 2: Background Tasks Drawer

### View Running Tasks

**GET** `/api/background-tasks/active`

```json
{
  "tasks": [
    {
      "task_id": "task_xyz789",
      "task_type": "data_import",
      "description": "Importing customer data from CSV",
      "status": "running",
      "progress": 0.65,
      "started_at": "2025-11-19T14:00:00.000Z",
      "logs": [
        "2025-11-19T14:00:05: Started import",
        "2025-11-19T14:02:30: Processed 10,000 records",
        "2025-11-19T14:05:15: Processed 20,000 records"
      ]
    },
    {
      "task_id": "task_abc456",
      "task_type": "model_training",
      "description": "Training sentiment analysis model",
      "status": "needs_input",
      "progress": 0.50,
      "started_at": "2025-11-19T14:10:00.000Z",
      "metadata": {
        "input_prompt": "Which validation dataset should I use?",
        "input_options": ["validation_2024.csv", "validation_latest.csv"]
      },
      "logs": [
        "2025-11-19T14:10:00: Training started",
        "2025-11-19T14:15:00: Epoch 1/10 complete"
      ]
    }
  ],
  "total": 2,
  "by_status": {
    "running": 1,
    "paused": 0,
    "needs_input": 1
  }
}
```

### Frontend Drawer Component

```typescript
function BackgroundTasksDrawer({ isOpen, onClose }) {
  const [tasks, setTasks] = useState([]);
  
  useEffect(() => {
    async function loadTasks() {
      const response = await fetch('/api/background-tasks/active');
      const data = await response.json();
      setTasks(data.tasks);
    }
    
    loadTasks();
    const interval = setInterval(loadTasks, 3000); // Refresh every 3s
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="Background Tasks">
      {tasks.map(task => (
        <TaskCard key={task.task_id} task={task} />
      ))}
    </Drawer>
  );
}

function TaskCard({ task }) {
  return (
    <div className="task-card">
      <div className="task-header">
        <span className="task-type">{task.task_type}</span>
        <span className={`status status-${task.status}`}>
          {task.status}
        </span>
      </div>
      
      <div className="task-description">{task.description}</div>
      
      <div className="task-progress">
        <ProgressBar value={task.progress} />
        <span>{Math.round(task.progress * 100)}%</span>
      </div>
      
      {task.logs && task.logs.length > 0 && (
        <div className="task-logs">
          {task.logs.map((log, i) => (
            <div key={i} className="log-entry">{log}</div>
          ))}
        </div>
      )}
      
      {task.status === 'needs_input' && (
        <InputPrompt task={task} />
      )}
      
      <div className="task-actions">
        <button onClick={() => pauseTask(task.task_id)}>Pause</button>
        <button onClick={() => cancelTask(task.task_id)}>Cancel</button>
      </div>
    </div>
  );
}
```

---

## Feature 3: Proactive Notifications

### Task Started

```json
{
  "type": "task_started",
  "message": "🚀 Started: Importing customer data from CSV",
  "badge": "🚀",
  "data": {
    "task_id": "task_xyz789"
  }
}
```

### Progress Milestones

At 25%, 50%, 75%, 100%:

```json
{
  "type": "task_progress",
  "message": "📊 Importing customer data: 50% complete",
  "badge": "📊",
  "data": {
    "task_id": "task_xyz789",
    "progress": 0.5
  }
}
```

### Task Completed

```json
{
  "type": "task_completed",
  "message": "✅ Completed: Importing customer data from CSV",
  "badge": "✅",
  "data": {
    "task_id": "task_xyz789",
    "result": {
      "records_imported": 30000,
      "duration_seconds": 320
    }
  }
}
```

**Also appears in chat:**
```
Grace: ✅ Your data import has finished! Imported 30,000 records in 5 minutes.
```

### Task Needs Input

```json
{
  "type": "task_needs_input",
  "message": "❓ Training sentiment model: Which validation dataset should I use?",
  "badge": "❓",
  "data": {
    "task_id": "task_abc456",
    "prompt": "Which validation dataset should I use?",
    "options": ["validation_2024.csv", "validation_latest.csv"]
  }
}
```

**In chat:**
```
Grace: ❓ I need your input on the model training:
Which validation dataset should I use?

[validation_2024.csv]  [validation_latest.csv]
```

**User clicks option:**
```typescript
async function provideInput(taskId: string, value: string) {
  await fetch(`/api/background-tasks/${taskId}/input`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_value: value })
  });
  
  // Task resumes automatically
}
```

---

## Feature 4: Chat Integration

### Reminder in Conversation

```
User: Remind me tomorrow to review the CRM deploy

Grace: ✅ Reminder set! I'll notify you when it's time.
      🛡️ Trust: 90% | ✓ Confidence: 100%

[Tomorrow at 9 AM]
Grace: ⏰ Reminder: You asked me to remind you to review the CRM deploy
```

### Background Task Updates in Chat

```
User: Start importing the customer data

Grace: 🚀 I've started importing the customer data. This will run in the background.
      You can monitor progress in the Background Tasks drawer.
      🛡️ Trust: 87% | ✓ Confidence: 92%

[5 minutes later - proactive notification]
Grace: ✅ Your data import has finished! Imported 30,000 records in 5 minutes.
      📊 Success rate: 99.8% (60 records skipped due to validation errors)
      
      Would you like me to analyze the imported data?
```

### Task Needs Input - Inline Dialog

```
Grace: ❓ I need your input on the model training:
      Which validation dataset should I use?
      
      [validation_2024.csv]  [validation_latest.csv]

User: *clicks validation_latest.csv*

Grace: Thanks! Resuming training with validation_latest.csv...
      I'll notify you when it's complete.
```

---

## API Endpoints

### Reminders

```bash
# Create reminder from natural language
POST /api/reminders/create
{
  "text": "Remind me tomorrow to review metrics",
  "user_id": "user"
}

# Get pending reminders
GET /api/reminders/pending?user_id=user

# Complete reminder
POST /api/reminders/{reminder_id}/complete

# Cancel reminder
DELETE /api/reminders/{reminder_id}
```

### Background Tasks

```bash
# Get active tasks
GET /api/background-tasks/active?user_id=user

# Get task details
GET /api/background-tasks/{task_id}

# Provide input for task
POST /api/background-tasks/{task_id}/input
{
  "input_value": "validation_latest.csv"
}

# Pause task
POST /api/background-tasks/{task_id}/pause

# Resume task
POST /api/background-tasks/{task_id}/resume

# Cancel task
POST /api/background-tasks/{task_id}/cancel

# Get stats
GET /api/background-tasks/stats
```

---

## Backend Implementation

### Reminder Service

**File:** `backend/reminders/reminder_service.py`

- SQLite storage for reminders
- Background checker runs every 30 seconds
- Parses natural language patterns
- Triggers notifications when due
- Supports recurring reminders

**Database Schema:**
```sql
CREATE TABLE reminders (
    reminder_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL,
    reminder_type TEXT NOT NULL,  -- time_based, event_based, recurring
    trigger_time TEXT,
    trigger_event TEXT,
    recurrence_pattern TEXT,
    status TEXT NOT NULL,  -- pending, triggered, completed, cancelled
    created_at TEXT NOT NULL
);
```

### Background Task Manager

**File:** `backend/background_tasks/task_manager.py`

- In-memory task tracking
- Progress monitoring
- Proactive notifications at milestones
- Input request/response handling

**Task Lifecycle:**
```
QUEUED
  ↓
RUNNING (progress 0% → 100%)
  ↓ (may pause/resume)
  ↓ (may request input → NEEDS_INPUT)
COMPLETED / FAILED
```

---

## Testing

### Test Reminders

```bash
# Create reminder
curl -X POST http://localhost:8420/api/reminders/create \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Remind me in 2 minutes to test reminders",
    "user_id": "test_user"
  }'

# List pending
curl http://localhost:8420/api/reminders/pending?user_id=test_user

# Wait 2 minutes, notification will trigger
```

### Test Background Tasks

```bash
# Create a mock task
curl -X POST http://localhost:8420/api/background-tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "data_import",
    "description": "Test import",
    "user_id": "test_user"
  }'

# Get active tasks
curl http://localhost:8420/api/background-tasks/active

# Simulate progress
curl -X POST http://localhost:8420/api/background-tasks/{task_id}/progress \
  -H "Content-Type: application/json" \
  -d '{"progress": 0.5}'
```

---

## Frontend Integration Examples

### Reminder Button in Chat

```typescript
<button onClick={() => setShowReminderDialog(true)}>
  ⏰ Set Reminder
</button>

<ReminderDialog
  isOpen={showReminderDialog}
  onClose={() => setShowReminderDialog(false)}
  onSubmit={async (text) => {
    await fetch('/api/reminders/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, user_id: 'user' })
    });
  }}
/>
```

### Background Tasks Badge

```typescript
function TasksBadge() {
  const [taskCount, setTaskCount] = useState(0);
  
  useEffect(() => {
    async function loadCount() {
      const response = await fetch('/api/background-tasks/stats');
      const data = await response.json();
      setTaskCount(data.total_active);
    }
    
    loadCount();
    const interval = setInterval(loadCount, 5000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <button onClick={() => setDrawerOpen(true)}>
      Background Tasks
      {taskCount > 0 && (
        <span className="badge">{taskCount}</span>
      )}
    </button>
  );
}
```

### Notification Listener

```typescript
useEffect(() => {
  const eventSource = new EventSource('/api/notifications/stream');
  
  eventSource.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    
    // Show toast
    showToast(notification.message, notification.badge);
    
    // If task-related, refresh tasks
    if (notification.type.startsWith('task_')) {
      refreshBackgroundTasks();
    }
    
    // If reminder, add to chat
    if (notification.type === 'reminder') {
      addMessageToChat({
        role: 'assistant',
        content: notification.message
      });
    }
  };
  
  return () => eventSource.close();
}, []);
```

---

## Summary

✅ **Natural Language Reminders**
- Parse "remind me tomorrow/in 2 hours/every Monday"
- SQLite storage with background checker
- Proactive notifications when due
- Integrated into chat flow

✅ **Background Tasks**
- Track running jobs/missions
- Show progress and logs
- Pause/resume/cancel controls
- Drawer UI linked to chat

✅ **Proactive Notifications**
- Task started/progress/completed
- Reminder triggers
- Input requests
- All delivered via SSE + chat

✅ **Conversational Context**
- Everything stays in chat thread
- Grace pings proactively
- User can respond inline
- Background work visible but not intrusive

Grace is now proactive! 🚀
