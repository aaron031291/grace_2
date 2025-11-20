# Chat Endpoint Ready ✅

The `/api/chat` endpoint is **fully wired** and ready for real responses.

## Implementation Status

### ✅ Complete Integration

**File:** [backend/routes/chat_api.py](file:///c:/Users/aaron/grace_2/backend/routes/chat_api.py)

**Flow:**
```
POST /api/chat
  ↓
1. RAG Retrieval (semantic context from vector store)
  ↓
2. World Model Query (canonical facts)
  ↓
3. Conversation History (last 10 messages)
  ↓
4. Trust Context (system trust scores)
  ↓
5. OpenAI Reasoner.generate()
  ↓
6. Action Gateway Processing
  ↓
7. Response with citations, confidence, approvals
```

---

## Endpoints Available

### 1. **POST /api/chat**
Main chat endpoint - sends message to Grace

**Request:**
```json
{
  "message": "Hello Grace, what's your status?",
  "session_id": "optional-session-id",
  "user_id": "user",
  "attachments": []
}
```

**Response:**
```json
{
  "reply": "I'm operating at 87% trust with all core systems healthy...",
  "trace_id": "chat_abc123def456",
  "session_id": "session_xyz789",
  "actions": [],
  "citations": ["world_model:system_status"],
  "confidence": 0.92,
  "requires_approval": false,
  "pending_approvals": [],
  "timestamp": "2025-11-19T00:45:00.000Z"
}
```

---

### 2. **POST /api/chat/approve**
Approve or reject a pending action

**Request:**
```json
{
  "trace_id": "chat_abc123def456",
  "approved": true,
  "user_id": "user"
}
```

**Response:**
```json
{
  "success": true,
  "action": "approved",
  "trace_id": "chat_abc123def456",
  "execution": {
    "success": true,
    "result": "Action completed"
  }
}
```

---

### 3. **GET /api/chat/history/{session_id}**
Get conversation history

**Response:**
```json
{
  "session_id": "session_xyz789",
  "messages": [
    {
      "role": "user",
      "content": "Hello Grace",
      "timestamp": "2025-11-19T00:45:00.000Z"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help?",
      "timestamp": "2025-11-19T00:45:01.000Z",
      "trace_id": "chat_abc123"
    }
  ],
  "total_messages": 2
}
```

---

### 4. **GET /api/chat/sessions**
List all active sessions

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session_xyz789",
      "message_count": 10,
      "last_message": "2025-11-19T00:45:00.000Z"
    }
  ],
  "total_sessions": 1
}
```

---

### 5. **DELETE /api/chat/session/{session_id}**
Delete a chat session

**Response:**
```json
{
  "success": true,
  "session_id": "session_xyz789"
}
```

---

## Testing the Endpoint

### Quick Test (curl)

```bash
# Start backend
python backend/main.py

# In another terminal, test chat
curl -X POST http://localhost:8420/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Grace, what is your current status?",
    "user_id": "test_user"
  }'
```

### Full Test Suite

```bash
# Run comprehensive tests
python test_chat_endpoint.py
```

**Tests:**
1. ✅ Simple chat message
2. ✅ Session continuity (conversation history)
3. ✅ Action approval workflow
4. ✅ Chat history retrieval

---

## What Happens Behind the Scenes

### Example: User asks "What files have been uploaded recently?"

**Step 1: RAG Retrieval**
```python
# Searches vector store for similar queries/documents
rag_results = await rag_service.retrieve(
    query="What files have been uploaded recently?",
    top_k=5
)
# Returns: [recent upload records, file metadata, etc.]
```

**Step 2: World Model Query**
```python
# Queries canonical facts
knowledge_items = await grace_world_model.query(
    query="What files have been uploaded recently?"
)
# Returns: [system status, recent ingestion events, memory catalog stats]
```

**Step 3: OpenAI Reasoner**
```python
response = await openai_reasoner.generate(
    user_message="What files have been uploaded recently?",
    conversation_history=[],
    rag_context=[...],          # From step 1
    world_model_facts={...},    # From step 2
    trust_context={...}         # System trust scores
)
```

**Step 4: OpenAI Returns**
```json
{
  "reply": "Based on recent ingestion events, 3 files were uploaded today:\n1. finance_report_2024.pdf (trust: 0.85)\n2. meeting_notes.txt (trust: 0.70)\n3. screenshot_analysis.png (trust: 0.80)\n\nAll files are indexed and available for RAG queries. [Source: memory_catalog]",
  "confidence": 0.92,
  "citations": ["memory_catalog", "world_model:recent_ingestions"],
  "actions": [],
  "requires_approval": false
}
```

**Step 5: Return to User**
- Reply with citations
- Confidence score
- No actions required (read-only query)

---

## Context Sources

Every chat message gets enriched with:

| Source | Purpose | Example |
|--------|---------|---------|
| **RAG Context** | Semantic search | Uploaded PDFs, docs, transcripts |
| **World Model** | Canonical facts | System status, verified knowledge |
| **Conversation History** | Context continuity | Last 10 messages |
| **Trust Context** | Confidence constraints | Trust score 0.87, min confidence 0.7 |

---

## Governance Integration

### Action Tiers

All proposed actions go through the Action Gateway:

```python
# LLM proposes action
action = {
    "type": "approval_request",
    "action": "write_database",
    "tier": 2,
    "justification": "User requested data update"
}

# Action Gateway processes
gateway_response = await action_gateway.request_action(
    action_type="write_database",
    agent="grace_reasoner",
    params={...}
)

# Returns
{
    "trace_id": "action_123",
    "governance_tier": "approval_required",
    "approved": false  # Waiting for user approval
}
```

**Tier 1:** Auto-approved (read-only)  
**Tier 2/3:** Requires user approval (writes, system changes)

---

## Event Bus Integration

All chat interactions publish events for:

- **Audit Trail:** Every message logged
- **Governance:** Action approvals tracked
- **Notifications:** Users notified of approval requests
- **Telemetry:** Confidence and trust scores recorded

```python
# Events published:
EventType.AGENT_ACTION     # Chat message received/sent
EventType.GOVERNANCE_CHECK # Action approval required
EventType.APPROVAL_REQUESTED # User notified
```

---

## Next Steps: Frontend Integration

The backend is ready. Now wire the frontend:

### Frontend Chat Component

```typescript
// Example: GraceChat.tsx

async function sendMessage(text: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: text,
      session_id: currentSessionId,
      user_id: 'user'
    })
  });
  
  const data = await response.json();
  
  // Update UI
  setMessages(prev => [
    ...prev,
    { role: 'user', content: text },
    { 
      role: 'assistant', 
      content: data.reply,
      confidence: data.confidence,
      citations: data.citations
    }
  ]);
  
  // Store session ID
  setCurrentSessionId(data.session_id);
  
  // Show approval dialog if needed
  if (data.requires_approval) {
    showApprovalDialog(data.actions);
  }
}
```

### Approval Dialog

```typescript
async function handleApprove(traceId: string) {
  const response = await fetch('/api/chat/approve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      trace_id: traceId,
      approved: true,
      user_id: 'user'
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    showToast('Action approved and executed');
  }
}
```

---

## Summary

✅ **Backend Ready**
- `/api/chat` fully wired
- OpenAI reasoner integrated
- RAG context retrieval working
- World model facts integrated
- Governance processing active
- Event bus logging complete

✅ **Testing Available**
- `test_chat_endpoint.py` for full suite
- curl commands for quick tests

📋 **Frontend TODO**
- Wire chat component to `/api/chat`
- Add approval dialog
- Show confidence scores
- Display citations

🚀 **Ready for real conversations!**

---

## Troubleshooting

### OPENAI_API_KEY not set

If you get:
```
"I'm unable to respond because my OpenAI API key is not configured"
```

**Fix:**
```bash
# Add to .env file
OPENAI_API_KEY=sk-your-key-here

# Or export in terminal
export OPENAI_API_KEY=sk-your-key-here
```

### Backend not running

```bash
# Start backend
python backend/main.py

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8420
```

### Import errors

```bash
# Ensure dependencies installed
pip install -r backend/requirements.txt
```

---

Ready to chat! 💬
