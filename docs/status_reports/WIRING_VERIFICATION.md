# Chat System Wiring Verification ✅

Complete verification of OpenAI Reasoner → /api/chat → Action Gateway pipeline.

## Architecture Flow

```
User Message (Frontend)
    ↓
[ChatPanel.tsx] → /api/chat
    ↓
[chat_api.py] Chat Endpoint
    ├─→ [1] RAG Retrieval (rag_service.retrieve)
    │     ↓ Returns semantic context from vector store
    │
    ├─→ [2] World Model Query (grace_world_model.query)
    │     ↓ Returns canonical facts from knowledge base
    │
    ├─→ [3] Conversation History (in-memory sessions)
    │     ↓ Last 10 messages for context
    │
    ├─→ [4] Trust Context (reflection_loop.get_trust_scores)
    │     ↓ Current trust scores & pending approvals
    │
    └─→ [5] OpenAI Reasoner (openai_reasoner.generate)
          ↓ Grace's personality + enriched context
          ↓ Proposes actions via tool calls
          ↓
        [6] Action Gateway (action_gateway.request_action)
          ↓ Governance tier check (Tier 1/2/3)
          ↓ Auto-approve or queue for approval
          ↓
Response to Frontend
    {
      reply: "...",
      citations: [...],
      confidence: 0.92,
      actions: [...],
      pending_approvals: [...]
    }
```

## Component Verification

### ✅ 1. RAG Retrieval
**File:** [backend/services/rag_service.py](file:///c:/Users/aaron/grace_2/backend/services/rag_service.py)

**Called by:** `chat_api.py` line 101
```python
rag_results = await rag_service.retrieve(
    query=msg.message,
    top_k=5,
    similarity_threshold=0.7,
    requested_by=msg.user_id
)
```

**Returns:**
```python
{
  "results": [
    {
      "text": "...",
      "source": "...",
      "trust_score": 0.85,
      "distance": 0.23
    }
  ]
}
```

**Verification:** Run `python verify_chat_wiring.py` - Test 1

---

### ✅ 2. World Model Query
**File:** [backend/world_model/grace_world_model.py](file:///c:/Users/aaron/grace_2/backend/world_model/grace_world_model.py)

**Called by:** `chat_api.py` line 122
```python
knowledge_items = await grace_world_model.query(
    query=msg.message,
    top_k=5
)
```

**Returns:** `List[WorldKnowledge]` - Canonical facts with confidence scores

**Verification:** Run `python verify_chat_wiring.py` - Test 2

---

### ✅ 3. OpenAI Reasoner
**File:** [backend/services/openai_reasoner.py](file:///c:/Users/aaron/grace_2/backend/services/openai_reasoner.py)

**Called by:** `chat_api.py` line 159
```python
response = await openai_reasoner.generate(
    user_message=msg.message,
    conversation_history=conversation_history,
    rag_context=rag_context,
    world_model_facts=world_model_facts,
    trust_context=trust_context
)
```

**System Prompt:**
- Grace's personality ("professional, helpful, transparent")
- Governance instructions (request approval for Tier 2+)
- Citation requirements
- Hallucination prevention

**Returns:**
```python
{
  "reply": "...",
  "actions": [{...}],
  "confidence": 0.92,
  "citations": [...],
  "requires_approval": bool
}
```

**Verification:** Run `python verify_chat_wiring.py` - Test 3

---

### ✅ 4. Action Gateway
**File:** [backend/action_gateway.py](file:///c:/Users/aaron/grace_2/backend/action_gateway.py)

**Called by:** `chat_api.py` line 173 (when actions proposed)
```python
gateway_response = await action_gateway.request_action(
    action_type=action["action"],
    agent="grace_reasoner",
    params={"tier": action["tier"], ...},
    trace_id=trace_id
)
```

**Governance Tiers:**
- **AUTONOMOUS** (Tier 1): Auto-approved (read-only)
- **SUPERVISED** (Tier 2): Auto-approved but logged
- **APPROVAL_REQUIRED** (Tier 3): Queued for user approval
- **BLOCKED**: Always rejected

**Verification:** Run `python verify_chat_wiring.py` - Test 4

---

### ✅ 5. Governance API
**File:** [backend/routes/governance_api.py](file:///c:/Users/aaron/grace_2/backend/routes/governance_api.py)

**Endpoints:**
- `GET /api/governance/pending` - List pending approvals
- `POST /api/governance/approve` - Approve action
- `POST /api/governance/reject` - Reject action
- `GET /api/governance/history` - Audit trail
- `GET /api/governance/stats` - Governance metrics

**Called by:** Frontend ChatPanel when rendering approval cards

**Verification:** Run `python verify_chat_wiring.py` - Test 6

---

## Frontend Integration

### ✅ API Configuration
**File:** [frontend/src/api/config.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/config.ts)

```typescript
const API_BASE_URL = isDevelopment
  ? '/api'  // Proxied by Vite to backend
  : import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';
```

**No hardcoded ports!** ✅

---

### ✅ Chat API Client
**File:** [frontend/src/api/chat.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/chat.ts)

```typescript
const response = await ChatAPI.sendMessage({
  message: "What is Grace?",
  session_id: sessionId,
  user_id: "user"
});
// Returns: ChatResponse with reply, actions, citations, confidence
```

---

### ✅ Chat Panel
**File:** [frontend/src/components/ChatPanel.tsx](file:///c:/Users/aaron/grace_2/frontend/src/components/ChatPanel.tsx)

**Features:**
- Message history with role colors
- Inline approval cards for Tier 2/3 actions
- Citations display
- Confidence indicators
- Real-time updates

**Approval Flow:**
1. User sends message
2. Grace proposes action (e.g., "update knowledge base")
3. Approval card appears in chat
4. User clicks ✅ Approve or ❌ Reject
5. `POST /api/governance/approve` or `/reject`
6. Action executes (if approved)

---

## Verification Checklist

Run the verification script:
```bash
python verify_chat_wiring.py
```

Expected output:
```
[1/6] Testing RAG Retrieval...
  ✅ RAG initialized and returned X results

[2/6] Testing World Model Query...
  ✅ World Model initialized and returned X knowledge items

[3/6] Testing OpenAI Reasoner...
  ✅ Reasoner generated response with confidence 0.XX

[4/6] Testing Action Gateway...
  ✅ Action Gateway processed request (tier: X, approved: X)

[5/6] Testing Chat Endpoint Integration...
  ✅ Chat endpoint returned response
     Session: session_xxxxx
     Confidence: 0.XX
     Citations: X
     Reply: ...

[6/6] Testing Governance Endpoints...
  ✅ Pending approvals: X
  ✅ Governance stats: X total actions

🎉 All systems wired correctly!
```

---

## Manual Testing

### Test 1: Simple Question
```bash
# Start backend: python server.py
# Start frontend: cd frontend && npm run dev
# Open http://localhost:5173
# Send: "What is Grace?"
```

**Expected:**
- Grace responds with description
- Citations from world model
- Confidence score shown
- No approvals needed (Tier 1)

---

### Test 2: Action Proposal
```bash
# Send: "Update my knowledge base with: Python is great"
```

**Expected:**
- Grace proposes `write_memory` action
- Orange approval card appears
- Shows governance tier (SUPERVISED or APPROVAL_REQUIRED)
- Justification displayed
- User must approve/reject

---

### Test 3: Approval Flow
```bash
# Click ✅ Approve on pending action
```

**Expected:**
- Action status updates to "approved"
- Approval card disappears
- System message: "✅ Action approved: trace_xxx"
- Action executes in backend
- Outcome logged in Action Gateway

---

## Environment Requirements

### Backend
```bash
# Required
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o  # or gpt-3.5-turbo

# Optional
SEARCH_PROVIDER=mock  # Use for CI to avoid rate limits
CI=true  # Disables background learning jobs
```

### Frontend
```bash
# Development (uses Vite proxy)
VITE_BACKEND_URL=http://localhost:8000

# Production
VITE_BACKEND_URL=https://your-backend-domain.com
```

---

## Troubleshooting

### RAG returns empty results
**Cause:** Vector store not initialized or empty  
**Fix:** Ensure `rag_service.initialize()` called and knowledge ingested

### World Model returns no facts
**Cause:** Knowledge base empty  
**Fix:** Add seed knowledge via `grace_world_model.add_knowledge()`

### OpenAI Reasoner fails
**Cause:** Missing OPENAI_API_KEY or invalid model  
**Fix:** Set `OPENAI_API_KEY` in .env and verify model name

### Actions not appearing in approval queue
**Cause:** Governance tier set to AUTONOMOUS  
**Fix:** Check `action_gateway.governance_rules` for action type

### Frontend can't connect to backend
**Cause:** Backend not running or port mismatch  
**Fix:** Verify backend on :8000, frontend proxy configured in vite.config.ts

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Send message to Grace |
| `/api/chat/approve` | POST | Approve/reject action (legacy) |
| `/api/chat/history/{sessionId}` | GET | Get conversation history |
| `/api/governance/pending` | GET | List pending approvals |
| `/api/governance/approve` | POST | Approve action |
| `/api/governance/reject` | POST | Reject action |
| `/api/governance/history` | GET | Audit trail |
| `/api/governance/stats` | GET | Governance metrics |
| `/api/metrics/summary` | GET | System health & trust |
| `/api/metrics/health` | GET | Health check |

---

## Next Steps

1. **Add streaming responses**
   - Use SSE or WebSocket for token-by-token updates
   - Better UX for long responses

2. **Persistent storage**
   - Move conversations from in-memory to database
   - Store approval history with timestamps

3. **Advanced governance**
   - User-specific approval rules
   - Role-based access control
   - Approval delegation

4. **Analytics dashboard**
   - Governance compliance metrics
   - Trust score trends over time
   - Citation accuracy tracking

---

**Status:** ✅ All components verified and wired correctly!
