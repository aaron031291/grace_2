# Grace Chat API Contract

Complete reference for developers extending Grace's chat interface.

## Table of Contents

- [Chat API](#chat-api)
- [Governance API](#governance-api)
- [Voice API](#voice-api)
- [Metrics API](#metrics-api)
- [Notifications WebSocket](#notifications-websocket)
- [Background Tasks API](#background-tasks-api)

---

## Chat API

### POST `/api/chat`

Send a message to Grace and receive a response.

**Request:**
```json
{
  "message": "string",           // Required: User's message
  "session_id": "string",         // Optional: Session ID from previous response
  "user_id": "string",           // Optional: User identifier (default: "user")
  "attachments": ["string"]      // Optional: Array of attachment paths/names
}
```

**Response:**
```json
{
  "reply": "string",                    // Grace's response text
  "trace_id": "string",                 // Unique trace ID for this interaction
  "session_id": "string",               // Session ID (reuse in next request)
  "actions": [                          // Proposed actions
    {
      "trace_id": "string",
      "action_type": "string",
      "agent": "string",
      "params": {},
      "governance_tier": "string",
      "timestamp": "ISO8601",
      "approved": boolean,
      "reason": "string"
    }
  ],
  "citations": ["string"],              // Source references
  "confidence": 0.95,                   // Confidence score (0-1)
  "requires_approval": boolean,         // Whether approval needed
  "pending_approvals": [                // Approvals waiting for user
    {
      "trace_id": "string",
      "action_type": "string",
      "agent": "string",
      "governance_tier": "supervised" | "approval_required",
      "params": {},
      "reason": "string",
      "timestamp": "ISO8601"
    }
  ],
  "timestamp": "ISO8601"
}
```

**Example:**
```javascript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is my current trust score?',
    session_id: 'sess_abc123',
    user_id: 'user'
  })
});

const data = await response.json();
console.log(data.reply); // "Your trust score is 87%"
console.log(data.session_id); // "sess_abc123"
```

---

## Governance API

### GET `/api/governance/pending`

Get all pending approval requests.

**Query Parameters:**
- `limit` (number, default: 20) - Maximum number of results

**Response:**
```json
{
  "pending_approvals": [
    {
      "trace_id": "string",
      "action_type": "string",
      "agent": "string",
      "governance_tier": "supervised" | "approval_required",
      "params": {},
      "reason": "string",
      "timestamp": "ISO8601"
    }
  ],
  "total_pending": 5,
  "limit": 20,
  "timestamp": "ISO8601"
}
```

### POST `/api/governance/approve`

Approve a pending action.

**Request:**
```json
{
  "trace_id": "string",        // Required: Trace ID from pending approval
  "approved": true,             // Required: Must be true
  "reason": "string",           // Optional: Reason for approval
  "user_id": "string"          // Optional: User performing approval
}
```

**Response:**
```json
{
  "success": true,
  "action": "approved",
  "trace_id": "string",
  "approved_by": "user",
  "timestamp": "ISO8601",
  "details": {
    "action_type": "string",
    // ... action details
  }
}
```

### POST `/api/governance/reject`

Reject a pending action.

**Request:**
```json
{
  "trace_id": "string",        // Required: Trace ID from pending approval
  "approved": false,            // Required: Must be false
  "reason": "string",           // Optional: Reason for rejection
  "user_id": "string"          // Optional: User performing rejection
}
```

**Response:**
```json
{
  "success": true,
  "action": "rejected",
  "trace_id": "string",
  "rejected_by": "user",
  "timestamp": "ISO8601",
  "reason": "string"
}
```

**Example:**
```javascript
// Approve an action
await fetch('/api/governance/approve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    trace_id: 'trace_xyz789',
    approved: true,
    user_id: 'user'
  })
});
```

---

## Voice API

### POST `/api/voice/start`

Start a persistent voice session.

**Request:**
```json
{
  "user_id": "string",         // Optional: User ID (default: "user")
  "language": "string",        // Optional: Language code (default: "en-US")
  "continuous": boolean        // Optional: Continuous mode (default: true)
}
```

**Response:**
```json
{
  "success": true,
  "message": "Voice session started",
  "session": {
    "session_id": "voice_abc123",
    "user_id": "user",
    "status": "active",
    "language": "en-US",
    "continuous": true,
    "started_at": "ISO8601",
    "stopped_at": null,
    "message_count": 0
  }
}
```

### POST `/api/voice/stop`

Stop an active voice session.

**Query Parameters:**
- `session_id` (string, optional) - Specific session to stop
- `user_id` (string, optional) - Stop all sessions for user

**Response:**
```json
{
  "success": true,
  "message": "Voice session stopped",
  "stopped_sessions": ["voice_abc123"]
}
```

### GET `/api/voice/status`

Get status of voice sessions.

**Query Parameters:**
- `user_id` (string, optional) - Filter by user

**Response:**
```json
{
  "active_sessions": [
    {
      "session_id": "voice_abc123",
      "user_id": "user",
      "status": "active",
      "language": "en-US",
      "continuous": true,
      "started_at": "ISO8601",
      "message_count": 5
    }
  ],
  "total_sessions": 1,
  "total_messages": 5
}
```

**Example:**
```javascript
// Start voice session
const voiceResponse = await fetch('/api/voice/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user',
    language: 'en-US',
    continuous: true
  })
});

const voiceData = await voiceResponse.json();
const sessionId = voiceData.session.session_id;

// Later, stop the session
await fetch(`/api/voice/stop?session_id=${sessionId}`, {
  method: 'POST'
});
```

---

## Metrics API

### GET `/api/metrics/summary`

Get system health and trust metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "health": "healthy" | "degraded" | "offline",
    "trust": 0.87,                    // Trust score (0-1)
    "confidence": 0.87,               // Confidence score (0-1)
    "trust_score": 0.87,              // Same as trust
    "pending_approvals": 2,           // Count of pending approvals
    "active_tasks": 15,               // Count of active tasks
    "system_status": "healthy",       // System status
    "timestamp": "ISO8601"
  }
}
```

**Example:**
```javascript
const metrics = await fetch('/api/metrics/summary').then(r => r.json());
console.log(`Trust: ${(metrics.data.trust * 100).toFixed(0)}%`);
console.log(`Status: ${metrics.data.system_status}`);
```

---

## Notifications WebSocket

Real-time event stream for notifications.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/notifications/ws/user');

ws.onopen = () => {
  console.log('Connected to notifications');
};

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('Notification:', notification);
};
```

### Message Format

```json
{
  "message": "string",           // Notification text
  "timestamp": "ISO8601",        // When it occurred
  "badge": "🔔",                // Optional: Emoji badge
  "level": "info" | "warning" | "error",
  "source": "string",            // Which component sent it
  "data": {}                     // Optional: Additional data
}
```

### Example Messages

```json
// Learning notification
{
  "message": "Completed training on 150 new examples",
  "timestamp": "2024-01-15T10:30:00Z",
  "badge": "📚",
  "level": "info",
  "source": "learning_pipeline"
}

// Approval required
{
  "message": "Action requires approval: execute_command",
  "timestamp": "2024-01-15T10:31:00Z",
  "badge": "⚠️",
  "level": "warning",
  "source": "governance",
  "data": {
    "trace_id": "trace_xyz789",
    "action_type": "execute_command"
  }
}
```

---

## Background Tasks API

### GET `/api/control/tasks`

Get pending background tasks.

**Response:**
```json
{
  "pending_tasks": [
    {
      "task_id": "task_abc123",
      "name": "Process uploaded document",
      "description": "Ingesting file.pdf into knowledge base",
      "status": "pending" | "running" | "completed" | "failed",
      "priority": 5,
      "created_at": "ISO8601",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "progress": 45,              // 0-100
      "result": {},                // Result data when completed
      "error": "string"            // Error message if failed
    }
  ],
  "total_tasks": 3
}
```

### GET `/api/world-model/background-tasks/:task_id`

Get status of a specific task.

**Response:**
```json
{
  "task_id": "task_abc123",
  "name": "string",
  "status": "running",
  "progress": 75,
  "created_at": "ISO8601",
  "started_at": "ISO8601"
}
```

### POST `/api/control/tasks/:task_id/cancel`

Cancel a pending or running task.

**Response:**
```json
{
  "success": true,
  "task_id": "task_abc123",
  "status": "cancelled"
}
```

---

## Remote Access API

### POST `/api/remote-cockpit/remote/start`

Start a remote access session.

**Request:**
```json
{
  "user_id": "string",
  "safety_mode": "supervised" | "autonomous"
}
```

### POST `/api/world-model/multimodal/screen-share/start`

Start screen sharing.

**Request:**
```json
{
  "user_id": "string",
  "quality": "low" | "medium" | "high"
}
```

---

## Error Handling

All APIs follow consistent error format:

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found (resource doesn't exist)
- `500` - Internal server error

**Example:**
```javascript
try {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'test' })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('API Error:', error.message);
}
```

---

## TypeScript Types

```typescript
// Chat
interface ChatMessage {
  message: string;
  session_id?: string;
  user_id?: string;
  attachments?: string[];
}

interface ChatResponse {
  reply: string;
  trace_id: string;
  session_id: string;
  actions: ActionProposal[];
  citations: string[];
  confidence: number;
  requires_approval: boolean;
  pending_approvals: PendingApproval[];
  timestamp: string;
}

interface PendingApproval {
  trace_id: string;
  action_type: string;
  agent: string;
  governance_tier: 'supervised' | 'approval_required';
  params: Record<string, any>;
  reason: string;
  timestamp: string;
}

// Voice
interface VoiceSession {
  session_id: string;
  user_id: string;
  status: string;
  language: string;
  continuous: boolean;
  started_at: string;
  stopped_at?: string;
  message_count: number;
}

// Notifications
interface Notification {
  message: string;
  timestamp: string;
  badge?: string;
  level: 'info' | 'warning' | 'error';
  source: string;
  data?: any;
}

// Tasks
interface BackgroundTask {
  task_id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress?: number;
  result?: any;
  error?: string;
}
```

---

## Quick Start Example

```typescript
import { ChatAPI } from './api/chat';
import { VoiceAPI } from './api/voice';
import { useNotifications } from './hooks/useNotifications';

function MyChatComponent() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState('');
  const { notifications } = useNotifications('user');
  
  const sendMessage = async (text: string) => {
    const response = await ChatAPI.sendMessage({
      message: text,
      session_id: sessionId,
      user_id: 'user'
    });
    
    setSessionId(response.session_id);
    setMessages(prev => [...prev, {
      role: 'user',
      content: text
    }, {
      role: 'assistant',
      content: response.reply
    }]);
    
    // Handle approvals
    if (response.pending_approvals.length > 0) {
      // Show approval UI
    }
  };
  
  return (
    <div>
      {/* Your chat UI */}
    </div>
  );
}
```

---

## Testing

See [tests/chat.spec.ts](./tests/chat.spec.ts) for Playwright smoke tests.

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run smoke tests only
npm run test:smoke
```
