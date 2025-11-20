# API Integration Guide

Complete documentation for Grace's backend→frontend wiring.

## Table of Contents

1. [Chat Integration](#chat-integration)
2. [Memory & File Management](#memory--file-management)
3. [Remote Monitoring](#remote-monitoring)
4. [Real-time Notifications](#real-time-notifications)
5. [Learning Loop Integration](#learning-loop-integration)

---

## Chat Integration

### Endpoint: `/api/unified/chat`

**Method:** POST

**Request:**
```json
{
  "message": "User message text",
  "session_id": "optional-session-id",
  "user_id": "user",
  "attachments": [],
  "vision_context": null,
  "voice_enabled": false,
  "include_logs": false,
  "include_telemetry": true
}
```

**Response:**
```json
{
  "reply": "Grace's response",
  "trace_id": "chat_abc123def456",
  "session_id": "session_xyz789",
  "timestamp": "2025-11-19T00:14:23.456Z",
  "confidence": 0.92,
  "voice_url": null,
  "actions": [
    {
      "trace_id": "action_123",
      "action_type": "database_write",
      "tier": 2,
      "justification": "User requested data update",
      "params": {},
      "timestamp": "2025-11-19T00:14:23.456Z",
      "requires_approval": true
    }
  ],
  "requires_approval": false,
  "pending_approvals": [],
  "telemetry": {
    "health": "healthy",
    "trust_score": 0.87,
    "confidence": 0.92,
    "pending_approvals": 0,
    "active_tasks": 3,
    "active_missions": 1,
    "learning_jobs": 2,
    "incidents": 0,
    "timestamp": "2025-11-19T00:14:23.456Z"
  },
  "logs": [],
  "citations": ["source1", "source2"],
  "error": null,
  "healing_options": []
}
```

### Frontend Usage:

```typescript
async function sendMessage(message: string, sessionId?: string) {
  const response = await fetch('/api/unified/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: 'user',
      include_telemetry: true
    })
  });
  
  const data = await response.json();
  return data;
}
```

---

## Memory & File Management

### List Memory Assets: `/api/memory/assets`

**Method:** GET

**Query Parameters:**
- `asset_type`: Filter by type (pdf, video_transcript, etc.)
- `status`: Filter by status (raw, processed, indexed)
- `min_trust`: Minimum trust score (0.0-1.0)
- `limit`: Max results (default: 100)

**Response:**
```json
[
  {
    "asset_id": "uuid-1234",
    "asset_type": "pdf",
    "path": "storage/memory/raw/pdf/uuid-1234.pdf",
    "status": "indexed",
    "source": "upload",
    "trust_score": 0.85,
    "ingestion_date": "2025-11-19T00:00:00Z",
    "size_bytes": 1024000,
    "metadata": {
      "original_filename": "document.pdf"
    },
    "tags": ["finance", "2024"]
  }
]
```

### Upload File: `/api/memory/upload`

**Method:** POST (multipart/form-data)

**Form Data:**
- `file`: File to upload
- `asset_type`: Asset type (default: "upload")
- `trust_score`: Initial trust (default: 0.5)

**Response:**
```json
{
  "status": "success",
  "asset_id": "uuid-5678",
  "path": "storage/memory/raw/upload/uuid-5678.ext"
}
```

### Frontend Usage:

```typescript
async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('asset_type', 'upload');
  formData.append('trust_score', '0.5');
  
  const response = await fetch('/api/memory/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

### Browse Files: `/api/memory/browse`

**Method:** GET

**Query Parameters:**
- `path`: Directory path (default: "storage/memory")

**Response:**
```json
{
  "type": "directory",
  "path": "storage/memory",
  "entries": [
    {
      "name": "raw",
      "path": "storage/memory/raw",
      "type": "directory"
    },
    {
      "name": "processed",
      "path": "storage/memory/processed",
      "type": "directory"
    }
  ]
}
```

---

## Remote Monitoring

### System Status: `/api/remote/status`

**Method:** GET

**Response:**
```json
{
  "timestamp": "2025-11-19T00:14:23.456Z",
  "health": "healthy",
  "trust_score": 0.87,
  "confidence": 0.92,
  "active_tasks": 3,
  "active_missions": 1,
  "pending_approvals": 0,
  "learning_jobs": 2,
  "incidents": 0,
  "memory_usage_mb": 245.3,
  "uptime_seconds": 86400
}
```

### Active Tasks: `/api/remote/tasks`

**Method:** GET

**Response:**
```json
[
  {
    "task_id": "task_abc123",
    "status": "running",
    "progress": 0.65,
    "started_at": "2025-11-19T00:00:00Z",
    "updated_at": "2025-11-19T00:14:00Z",
    "description": "Processing uploaded PDF",
    "metadata": {}
  }
]
```

### Approve Action: `/api/remote/approve/{approval_id}`

**Method:** POST

**Response:**
```json
{
  "status": "approved",
  "result": {}
}
```

---

## Real-time Notifications

### SSE Stream: `/api/notifications/stream`

**Method:** GET

**Returns:** Server-Sent Events stream

**Event Format:**
```json
{
  "type": "approval_request|task_update|healing_action|...",
  "timestamp": "2025-11-19T00:14:23.456Z",
  "source": "system_component",
  "data": {}
}
```

### Frontend Usage:

```typescript
const eventSource = new EventSource('/api/notifications/stream');

eventSource.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  
  switch (notification.type) {
    case 'approval_request':
      handleApprovalRequest(notification.data);
      break;
    case 'task_update':
      updateTaskStatus(notification.data);
      break;
    case 'healing_action':
      showHealingNotification(notification.data);
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);
  // Implement reconnection logic
};
```

---

## Learning Loop Integration

### Automatic Ingestion Flow

**File Upload:**
1. User uploads file via `/api/memory/upload`
2. File saved to `storage/memory/raw/{type}/`
3. Asset registered in catalog
4. Event published: `MEMORY_UPDATE` with `action: file_uploaded`
5. `MemoryIngestionHook` triggers processing
6. Text extracted, embeddings generated
7. Asset marked as `processed` → `indexed`
8. World model updated with new knowledge

**Screen Share:**
1. Screen capture saved to `storage/memory/raw/screen_share/`
2. Asset registered with `source: screen_share`
3. OCR/vision processing triggered
4. Extracted text indexed
5. Available for RAG queries

**Web Learning:**
1. Web content fetched and saved
2. Asset registered with `source: web_learning`
3. Content parsed and indexed
4. Citations stored in metadata

### Event Bus Integration

All ingestion events flow through the event bus:

```python
from backend.event_bus import event_bus, Event, EventType

# Publish upload event
await event_bus.publish(Event(
    event_type=EventType.MEMORY_UPDATE,
    source="upload_handler",
    data={
        "action": "file_uploaded",
        "file_path": "/path/to/file",
        "metadata": {}
    }
))
```

The `MemoryIngestionHook` subscribes to these events and automatically:
- Ingests into catalog
- Assigns trust score
- Queues for processing
- Syncs to world model

---

## Frontend Components Wiring

### Chat Component

```typescript
// GraceConsole.tsx or GraceChat.tsx

const [messages, setMessages] = useState([]);
const [sessionId, setSessionId] = useState(null);

async function handleSendMessage(text: string) {
  const response = await fetch('/api/unified/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: text,
      session_id: sessionId,
      user_id: 'user',
      include_telemetry: true
    })
  });
  
  const data = await response.json();
  
  setSessionId(data.session_id);
  setMessages(prev => [...prev, 
    { role: 'user', content: text },
    { role: 'assistant', content: data.reply }
  ]);
  
  if (data.telemetry) {
    updateMetricsPanels(data.telemetry);
  }
  
  if (data.requires_approval) {
    showApprovalDialog(data.actions);
  }
}
```

### File Explorer Component

```typescript
const [files, setFiles] = useState([]);

async function loadFiles(path = 'storage/memory') {
  const response = await fetch(`/api/memory/browse?path=${path}`);
  const data = await response.json();
  setFiles(data.entries);
}

async function handleFileUpload(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/memory/upload', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  if (result.status === 'success') {
    loadFiles(); // Refresh file list
  }
}
```

### Metrics Panel Component

```typescript
const [metrics, setMetrics] = useState(null);

useEffect(() => {
  const fetchMetrics = async () => {
    const response = await fetch('/api/remote/status');
    const data = await response.json();
    setMetrics(data);
  };
  
  fetchMetrics();
  const interval = setInterval(fetchMetrics, 5000); // Poll every 5s
  
  return () => clearInterval(interval);
}, []);
```

### Notification Listener

```typescript
useEffect(() => {
  const eventSource = new EventSource('/api/notifications/stream');
  
  eventSource.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    handleNotification(notification);
  };
  
  return () => eventSource.close();
}, []);
```

---

## Testing

Run smoke tests:

```bash
pytest tests/test_chat_approval_flow.py -v
```

Test individual endpoints:

```bash
# Chat
curl -X POST http://localhost:8420/api/unified/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Grace", "user_id": "test"}'

# Memory stats
curl http://localhost:8420/api/memory/stats

# Remote status
curl http://localhost:8420/api/remote/status

# Notifications stream
curl -N http://localhost:8420/api/notifications/stream
```

---

## Summary

All major systems now connected:
- ✅ Chat → OpenAI reasoner → Governance
- ✅ File uploads → Memory catalog → RAG
- ✅ Screen shares → Memory catalog → World model
- ✅ Real-time notifications via SSE
- ✅ Remote monitoring and metrics
- ✅ Approval workflow integration
