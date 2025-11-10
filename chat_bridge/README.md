# Grace Chat Bridge

Lightweight backend dedicated to the chat UI.

## Purpose

- **WebSocket Bridge**: Translates Grace's internal bus events into chat-friendly messages
- **Intent Detection**: Routes chat messages to appropriate domain APIs
- **Cached State**: Provides denormalized domain state for dashboards
- **Approval Workflows**: Dry-run simulations with user approval before execution
- **Guardrails**: Rate limiting, logging, role enforcement

## Architecture

```
Frontend (Port 5173)
    ↓
Chat Bridge (Port 8001) ← Lightweight, UI-focused
    ↓
Grace Backend (Port 8000) ← Full control plane
```

## Features

### 1. Event Translation
- Subscribes to Grace's event bus (WebSocket)
- Translates internal events to chat messages
- Filters by domain
- Persists conversation transcripts

### 2. Intent Endpoints
- Detects domain from message content
- Routes to appropriate backend service
- Enforces guardrails and logs actions
- Applies rate limits

### 3. Cached State
- Denormalized views of domain health
- Playbook status
- Resource usage
- Refreshed every 30 seconds

### 4. Approval Workflows
- Runs dry-run simulations
- Shows projected outcome in chat
- User approves/rejects
- Passes approval to orchestrator

## Running

```bash
# Install dependencies
cd chat_bridge
pip install -r requirements.txt

# Start bridge
python main.py

# Bridge runs on port 8001
# Access: http://localhost:8001/health
```

## Update Frontend

Point frontend to bridge instead of main backend:

```typescript
const BACKEND_URL = "http://localhost:8001";  // Chat Bridge
```

## Endpoints

### Authentication
- `POST /api/auth/login` - Login (proxied)
- `POST /api/auth/register` - Register (proxied)

### Chat
- `POST /api/chat` - Send message with intent detection
- `POST /api/command` - Execute slash command
- `WS /ws/events` - Real-time event stream

### Approvals
- `POST /api/approval` - Approve/reject recommendation
- `POST /api/simulate` - Dry-run simulation

### State
- `GET /api/state/{domain}` - Cached domain state
- `GET /health` - Bridge health + backend connectivity

## Benefits

1. **Security**: UI doesn't directly access control plane
2. **Performance**: Cached state reduces backend load
3. **Safety**: Approvals required for critical actions
4. **Observability**: All UI actions logged
5. **Scalability**: Can run on separate machine
6. **Multi-tenancy**: Easy to add role-based access

## Next Steps

1. Start the bridge: `python chat_bridge/main.py`
2. Update frontend to use port 8001
3. Test chat with intent detection
4. Test slash commands
5. Monitor event stream
