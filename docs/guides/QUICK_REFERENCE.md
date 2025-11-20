# Grace API Quick Reference 🚀

## Environment Setup

```bash
# Required
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Search Provider (choose one)
SEARCH_PROVIDER=google  # Use Google API
SEARCH_PROVIDER=ddg     # Use DuckDuckGo  
SEARCH_PROVIDER=mock    # Use mock (CI/testing)

# CI Mode (auto-enables mock)
CI=true

# Backend URL (frontend)
VITE_BACKEND_URL=http://localhost:8000
```

---

## Start Services

```bash
# Backend
python server.py
# → http://localhost:8000

# Frontend
cd frontend && npm run dev
# → http://localhost:5173

# Quick start (Windows)
QUICK_START_CHAT.bat
```

---

## Core Endpoints

### Chat
```bash
POST /api/chat
{
  "message": "What is Grace?",
  "session_id": "optional",
  "user_id": "user"
}
```

### Governance
```bash
GET  /api/governance/pending      # List pending approvals
POST /api/governance/approve      # Approve action
POST /api/governance/reject       # Reject action
GET  /api/governance/stats        # Governance metrics
```

### Voice
```bash
POST /api/voice/start             # Start voice session
POST /api/voice/stop              # Stop voice session  
POST /api/voice/toggle            # Toggle voice on/off
GET  /api/voice/status            # Get voice status
POST /api/voice/process           # Process transcript
```

### Metrics
```bash
GET /api/metrics/summary          # Health & trust metrics
GET /api/metrics/health           # Simple health check
```

---

## Response Formats

### Chat Response
```json
{
  "reply": "I am Grace...",
  "trace_id": "chat_abc123",
  "session_id": "session_xyz",
  "citations": ["source1"],
  "confidence": 0.92,
  "requires_approval": false,
  "pending_approvals": [...],
  "actions": [...]
}
```

### Metrics Summary
```json
{
  "success": true,
  "data": {
    "health": "healthy",
    "trust": 0.85,
    "confidence": 0.87,
    "pending_approvals": 2,
    "active_tasks": 10,
    "system_status": "healthy"
  }
}
```

### Voice Session
```json
{
  "success": true,
  "session": {
    "session_id": "voice_abc123",
    "user_id": "user",
    "status": "active",
    "language": "en-US",
    "started_at": "2024-01-15T10:30:00"
  }
}
```

---

## Governance Tiers

| Tier | Name | Auto-Approved? | Example |
|------|------|----------------|---------|
| 1 | AUTONOMOUS | ✅ Yes | read_memory |
| 2 | SUPERVISED | ✅ Yes (logged) | write_memory |
| 3 | APPROVAL_REQUIRED | ❌ No | execute_code |
| 4 | BLOCKED | ❌ Always denied | delete_data |

---

## Common Tasks

### Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Grace!"}'
```

### Check Health
```bash
curl http://localhost:8000/api/metrics/summary | jq '.data.health'
```

### Start Voice
```bash
curl -X POST http://localhost:8000/api/voice/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user"}'
```

### Approve Action
```bash
curl -X POST http://localhost:8000/api/governance/approve \
  -H "Content-Type: application/json" \
  -d '{"trace_id": "chat_abc123", "approved": true}'
```

---

## Testing

### Verify Wiring
```bash
python verify_chat_wiring.py
```

### Run Smoke Tests
```bash
pytest tests/e2e/test_chat_smoke.py -v
```

### Test Mock Search
```bash
export SEARCH_PROVIDER=mock
python -c "
import asyncio
from backend.services.google_search_service import google_search_service
asyncio.run(google_search_service.initialize())
print(google_search_service.current_provider)
# Should print: mock
"
```

---

## API Endpoints List

### Chat & Conversation
- `POST /api/chat` - Send message to Grace
- `GET /api/chat/history/{sessionId}` - Get conversation history
- `GET /api/chat/sessions` - List sessions

### Governance & Approvals
- `GET /api/governance/pending` - Pending actions
- `POST /api/governance/approve` - Approve action
- `POST /api/governance/reject` - Reject action  
- `GET /api/governance/history` - Audit trail
- `GET /api/governance/stats` - Governance metrics

### Voice Control
- `POST /api/voice/start` - Start voice session
- `POST /api/voice/stop` - Stop voice session
- `POST /api/voice/toggle` - Toggle voice
- `GET /api/voice/status` - Voice status
- `GET /api/voice/sessions` - List sessions
- `POST /api/voice/process` - Process transcript

### System Health
- `GET /api/metrics/summary` - Full metrics
- `GET /api/metrics/health` - Health check
- `GET /api/phase7/health` - Phase 7 health
- `GET /api/phase8/health` - Phase 8 health

---

## Troubleshooting

### CORS Errors
✅ **Fixed:** CORS middleware configured for `localhost:5173`

### DuckDuckGo 403
✅ **Fixed:** Use `SEARCH_PROVIDER=mock` or `CI=true`

### Metrics Format Wrong
✅ **Fixed:** Returns `{ success: true, data: {...} }`

### Voice Not Persistent
✅ **Fixed:** Sessions now persist with `session_id` token

---

## Documentation

- [CHAT_SYSTEM_COMPLETE.md](file:///c:/Users/aaron/grace_2/CHAT_SYSTEM_COMPLETE.md) - User guide
- [WIRING_VERIFICATION.md](file:///c:/Users/aaron/grace_2/WIRING_VERIFICATION.md) - Technical details
- [FIXES_APPLIED.md](file:///c:/Users/aaron/grace_2/FIXES_APPLIED.md) - Recent fixes
- [COMPLETE_WIRING_SUMMARY.md](file:///c:/Users/aaron/grace_2/COMPLETE_WIRING_SUMMARY.md) - Architecture

---

## Status: ✅ Production Ready

All critical issues resolved:
- ✅ Mock search service (no API rate limits in CI)
- ✅ CORS configured
- ✅ Phase 7/8 endpoints registered
- ✅ Metrics API format fixed
- ✅ Voice endpoints implemented
