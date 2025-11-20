# Unified Chat API - Complete Integration 🎯

Single endpoint that handles everything: text, voice, vision, logs, errors, telemetry, and governance.

## Overview

The **Unified Chat API** (`/api/unified/chat`) is the single source of truth for all Grace interactions. Every input type funnels through here, and every response includes everything the UI needs.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    ANY INPUT TYPE                            │
│   💬 Text | 🎙️ Voice Transcript | 📹 Vision Context        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│         POST /api/unified/chat (SINGLE ENDPOINT)             │
│                                                              │
│  Automatically Detects:                                      │
│  - Log requests ("show API errors")                          │
│  - Telemetry requests ("system health")                      │
│  - Action commands ("deploy backend")                        │
│  - General questions ("what is Grace?")                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  CONTEXT ASSEMBLY                            │
│                                                              │
│  1. RAG retrieval (semantic context)                         │
│  2. World model facts (canonical knowledge)                  │
│  3. Logs (if requested or errors present)                    │
│  4. Vision context (if provided)                             │
│  5. Conversation history                                     │
│  6. Trust scores + pending approvals                         │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  OPENAI REASONER                             │
│  - Grace's personality                                       │
│  - Full context (RAG + WM + logs + vision)                   │
│  - Proposes actions with justifications                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│              COMPREHENSIVE RESPONSE                          │
│                                                              │
│  ✅ reply (text to display/speak)                            │
│  ✅ voice_url (audio stream if voice enabled)                │
│  ✅ actions (approval cards with tier + justification)       │
│  ✅ telemetry (health, trust, missions, incidents)           │
│  ✅ logs (recent errors, executions, healing)                │
│  ✅ citations (knowledge sources used)                       │
│  ✅ healing_options (if errors occurred)                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Request Format

### UnifiedChatMessage

```json
{
  "message": "Deploy the backend to production",
  "session_id": "session_abc123",
  "user_id": "user",
  
  // Optional
  "attachments": ["file1.txt", "file2.pdf"],
  "vision_context": {
    "screen_text": "Deployment logs showing errors...",
    "objects": ["terminal", "error_message"]
  },
  "voice_enabled": true,
  
  // Flags
  "include_logs": false,
  "include_telemetry": true
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ Yes | User message, voice transcript, or command |
| `session_id` | string | No | Session ID for conversation continuity |
| `user_id` | string | No | User identifier (default: "user") |
| `attachments` | array | No | File paths or URLs |
| `vision_context` | object | No | Screen/camera context from vision stream |
| `voice_enabled` | bool | No | True if persistent voice session active |
| `include_logs` | bool | No | Force include recent logs (default: false) |
| `include_telemetry` | bool | No | Include system telemetry (default: true) |

---

## Response Format

### UnifiedChatResponse

```json
{
  // Core response
  "reply": "I'll deploy the backend to production...",
  "trace_id": "chat_abc123",
  "session_id": "session_abc123",
  "timestamp": "2024-01-15T10:30:00",
  "confidence": 0.92,
  
  // Voice (if enabled)
  "voice_url": "/api/voice/stream/session_abc123/response.mp3",
  "voice_transcript": "I'll deploy the backend to production...",
  
  // Actions & governance
  "actions": [
    {
      "trace_id": "chat_abc123",
      "action_type": "deploy_service",
      "tier": "approval_required",
      "justification": "Production deployment requires explicit approval",
      "params": {
        "service_name": "backend",
        "environment": "production"
      },
      "timestamp": "2024-01-15T10:30:00",
      "approved": false,
      "requires_approval": true
    }
  ],
  "requires_approval": true,
  "pending_approvals": [...],
  
  // Telemetry
  "telemetry": {
    "health": "healthy",
    "trust_score": 0.87,
    "confidence": 0.89,
    "pending_approvals": 2,
    "active_tasks": 15,
    "active_missions": 3,
    "learning_jobs": 5,
    "incidents": 0,
    "timestamp": "2024-01-15T10:30:00"
  },
  
  // Logs (if requested or errors present)
  "logs": [
    {
      "log_type": "error",
      "timestamp": "2024-01-15T10:25:00",
      "message": "API request failed: Connection timeout",
      "source": "error.log",
      "severity": "ERROR"
    }
  ],
  
  // Citations
  "citations": [
    "backend/world_model/deployment_guide.md",
    "RAG: Production deployment best practices"
  ],
  
  // Error handling (if applicable)
  "error": null,
  "healing_options": []
}
```

---

## Usage Examples

### 1. Simple Text Chat

```bash
curl -X POST http://localhost:8000/api/unified/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Grace?",
    "user_id": "user"
  }'
```

**Response:**
```json
{
  "reply": "I am Grace, an AI assistant with governance...",
  "trace_id": "chat_xyz",
  "session_id": "session_abc",
  "confidence": 0.95,
  "citations": ["world_model/self_knowledge"],
  "telemetry": {...},
  "actions": [],
  "logs": []
}
```

### 2. Request Logs

```bash
curl -X POST http://localhost:8000/api/unified/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me the latest API errors",
    "user_id": "user"
  }'
```

**Response:**
```json
{
  "reply": "Here are the recent API errors...",
  "logs": [
    {
      "log_type": "api_errors",
      "timestamp": "2024-01-15T10:25:00",
      "message": "GET /api/chat returned 500",
      "source": "access.log",
      "severity": "ERROR"
    }
  ],
  "citations": ["logs/access.log"],
  "actions": []
}
```

### 3. Voice-Enabled Chat

```bash
curl -X POST http://localhost:8000/api/unified/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Deploy the backend",
    "user_id": "user",
    "voice_enabled": true,
    "session_id": "session_voice_123"
  }'
```

**Response:**
```json
{
  "reply": "I'll deploy the backend for you.",
  "voice_url": "/api/voice/stream/session_voice_123/response.mp3",
  "voice_transcript": "I'll deploy the backend for you.",
  "actions": [
    {
      "action_type": "deploy_service",
      "tier": "approval_required",
      "requires_approval": true
    }
  ]
}
```

**Client plays audio AND displays text simultaneously!**

### 4. Vision Context Integration

```bash
curl -X POST http://localhost:8000/api/unified/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you see on my screen?",
    "user_id": "user",
    "vision_context": {
      "screen_text": "Error: Connection timeout",
      "objects": ["terminal", "error_message", "logs"]
    }
  }'
```

**Response:**
```json
{
  "reply": "I see a connection timeout error in your terminal...",
  "logs": [],
  "citations": ["vision_context"],
  "healing_options": [
    {
      "healing_id": "heal_retry",
      "title": "Retry Connection",
      "description": "Retry with exponential backoff",
      "playbook": "retry_with_backoff",
      "confidence": 0.85
    }
  ]
}
```

### 5. Error Surfacing with Healing

```bash
# Grace responds to failed action
{
  "reply": "The deployment failed due to a network timeout.",
  "error": "Deployment failed: Connection timeout after 30s",
  "logs": [
    {
      "log_type": "execution",
      "message": "Deployment to production failed",
      "source": "execution.log"
    }
  ],
  "healing_options": [
    {
      "healing_id": "heal_rollback",
      "title": "Rollback Deployment",
      "description": "Rollback to previous stable version",
      "playbook": "rollback_deployment",
      "confidence": 0.9
    },
    {
      "healing_id": "heal_retry",
      "title": "Retry Deployment",
      "description": "Retry with increased timeout",
      "playbook": "retry_with_backoff",
      "confidence": 0.75
    }
  ]
}
```

**User can:**
- See the error inline
- View relevant log snippet
- Click healing option to run playbook

---

## Features

### ✅ 1. Unified Input Handling

**All input types flow through one endpoint:**
- Text messages
- Voice transcripts (from WebSocket)
- Vision context (from screen/camera)
- Attachments

**No need for separate endpoints per input type!**

### ✅ 2. Automatic Log Detection

**Grace detects when you're asking for logs:**

| User says | Grace returns |
|-----------|---------------|
| "Show API errors" | Recent API errors from access.log |
| "Latest logs" | Recent application logs |
| "What went wrong?" | Recent errors + healing logs |
| "Deployment issues" | Execution logs + error logs |

### ✅ 3. Inline Governance Approvals

**Every response includes pending approval cards:**

```json
"pending_approvals": [
  {
    "trace_id": "chat_abc",
    "action_type": "deploy_service",
    "tier": "approval_required",
    "justification": "Production deployment requires approval",
    "requires_approval": true
  }
]
```

**UI renders inline cards:**
```
┌─────────────────────────────────────┐
│ ⚠️ Pending Approval                 │
│                                     │
│ Action: deploy_service              │
│ Tier: APPROVAL_REQUIRED             │
│                                     │
│ Production deployment requires      │
│ explicit approval                   │
│                                     │
│  [✅ Approve]  [❌ Reject]           │
└─────────────────────────────────────┘
```

### ✅ 4. Voice + Text Simultaneously

**When voice_enabled=true:**
- `voice_url`: Audio stream URL
- `voice_transcript`: Text version of reply
- **User hears AND sees the response!**

**Persistent voice session:**
- Session stays active
- Every reply includes audio
- No need to re-enable voice each turn

### ✅ 5. Error Surfacing with Healing

**When actions fail:**
```json
{
  "error": "Deployment failed: Connection timeout",
  "logs": [
    {
      "log_type": "execution",
      "message": "Failed to deploy backend",
      "source": "execution.log"
    }
  ],
  "healing_options": [
    {
      "healing_id": "heal_rollback",
      "title": "Rollback Deployment",
      "playbook": "rollback_deployment",
      "confidence": 0.9
    }
  ]
}
```

**UI shows:**
- ❌ Error message
- 📋 Log snippet
- 🔧 Healing options with confidence scores

### ✅ 6. Telemetry Panels

**Every response includes system status:**
```json
"telemetry": {
  "health": "healthy",
  "trust_score": 0.87,
  "pending_approvals": 2,
  "active_tasks": 15,
  "active_missions": 3,
  "learning_jobs": 5,
  "incidents": 0
}
```

**UI renders real-time panels:**
- Health indicator
- Trust meter
- Active missions counter
- Pending approvals badge

---

## Integration with Existing Systems

### Chat API (Legacy)

**Old:** `POST /api/chat`
**New:** `POST /api/unified/chat`

**Migration path:**
1. Both endpoints work
2. Unified endpoint has more features
3. Frontend can use unified for enhanced UX
4. Legacy endpoint stays for backward compatibility

### Voice Stream

**Voice WebSocket forwards to unified chat:**
```python
# In voice_stream_api.py
transcript = transcribe_audio(audio_buffer)
response = await unified_chat(UnifiedChatMessage(
    message=transcript,
    voice_enabled=True,
    session_id=session_token
))
# Return voice_url to client
```

### Vision Stream

**Vision analysis forwarded as context:**
```python
# In vision_api.py
vision_context = {
    "screen_text": ocr_result,
    "objects": detected_objects
}
response = await unified_chat(UnifiedChatMessage(
    message="What do you see?",
    vision_context=vision_context
))
```

---

## Frontend Integration

### React Hook

```typescript
async function sendUnifiedMessage(message: string, options?: {
  voiceEnabled?: boolean;
  includeLogs?: boolean;
}) {
  const response = await fetch('/api/unified/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      voice_enabled: options?.voiceEnabled || false,
      include_logs: options?.includeLogs || false
    })
  });
  
  const data = await response.json();
  
  // Display text reply
  setMessages([...messages, {
    role: 'assistant',
    content: data.reply
  }]);
  
  // Play voice if present
  if (data.voice_url) {
    const audio = new Audio(data.voice_url);
    audio.play();
  }
  
  // Show approval cards
  if (data.pending_approvals.length > 0) {
    setApprovalCards(data.pending_approvals);
  }
  
  // Update telemetry panels
  if (data.telemetry) {
    setTelemetry(data.telemetry);
  }
  
  // Show log snippets
  if (data.logs.length > 0) {
    setLogPanel(data.logs);
  }
  
  // Show healing options if error
  if (data.error) {
    setErrorDialog({
      message: data.error,
      logs: data.logs,
      healingOptions: data.healing_options
    });
  }
}
```

---

## Status

✅ **Complete:**
- Unified endpoint created
- Log service integrated
- Telemetry panels
- Error surfacing
- Healing options structure
- Voice + text response ready

🔧 **TODO (Future):**
- Integrate real TTS (OpenAI Realtime/ElevenLabs)
- Add mission system telemetry
- Expand healing playbooks
- Add incident tracking

---

## Documentation

- [unified_chat_api.py](file:///c:/Users/aaron/grace_2/backend/routes/unified_chat_api.py) - Unified endpoint
- [log_service.py](file:///c:/Users/aaron/grace_2/backend/services/log_service.py) - Log retrieval
- [FINAL_INTEGRATION_VERIFICATION.md](file:///c:/Users/aaron/grace_2/FINAL_INTEGRATION_VERIFICATION.md) - Complete verification

---

**🎉 The unified chat endpoint is now the single source of truth for all Grace interactions!**
