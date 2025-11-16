# Console UI - API Integration Status

**Date**: November 16, 2025

---

## ✅ What's Ready

### 1. Logs Pane APIs
**Status**: ✅ **Complete and integrated**

**Endpoints created**:
- ✅ `GET /api/logs/recent` - Fetch recent logs with filters
- ✅ `GET /api/logs/domains` - List available domains
- ✅ `GET /api/logs/levels` - List log levels
- ✅ `WS /api/logs/stream` - Live log streaming WebSocket
- ✅ `GET /api/logs/health` - Health check

**Integration**: Added to `backend/main.py` ✅

**Frontend hook ready**: `useLogsWebSocket()` 

**Usage**:
```typescript
// LogsPane.tsx
const { logs, isConnected } = useLogsWebSocket();
// Logs stream in real-time from mission/follow-up events
```

---

### 2. Chat Pane APIs
**Status**: ✅ **Already exists**

**Endpoints available**:
- ✅ `POST /api/chat` - Send message to Grace (existing)
- ✅ Uses RAG + LLM (Ollama/OpenAI/Anthropic)
- ✅ Fallback responses built-in

**Located in**: `backend/main.py` (lines 200-340)

**Frontend hook ready**: `useChatSend()`

**Usage**:
```typescript
// ChatPane.tsx
const { mutate: sendMessage } = useChatSend();
sendMessage({ message: 'Hello Grace', user_id: 'admin' });
// Wires to existing /api/chat endpoint
```

---

### 3. Console Overview API
**Status**: ✅ **Complete and integrated**

**Endpoints created**:
- ✅ `GET /api/console/overview` - Aggregated dashboard data
- ✅ `GET /api/console/health` - Console health check

**Integration**: Added to `backend/main.py` ✅

**Returns**: Mission counts, log counts, domain health, system status

---

## 🔧 What Needs to Be Created

### Task Manager Pane APIs
**Status**: ⚠️ **Needs endpoints in mission_control_api.py**

**Required endpoints**:
- ⚠️ `GET /api/missions/active` - List active missions
- ⚠️ `GET /api/missions/proactive` - List proactive missions
- ⚠️ `GET /api/missions/followups` - List follow-up missions
- ⚠️ `WS /ws/missions` - Live mission updates (optional)

**Current status**: Need to check/create these in `backend/routes/mission_control_api.py`

---

## 🚀 Integration Steps

### Step 1: Verify Backend Integration ✅
```python
# backend/main.py already includes:
from backend.routes.logs_api import router as logs_router
from backend.routes.console_api import router as console_router

app.include_router(logs_router)
app.include_router(console_router)
```

---

### Step 2: Create Mission Control Endpoints
Add to `backend/routes/mission_control_api.py`:

```python
@router.get("/api/missions/active")
async def get_active_missions():
    """
    Get all active missions
    For Task Manager pane
    """
    # Query from mission database/tracker
    from backend.autonomy.mission_tracker import get_missions_by_status
    
    missions = await get_missions_by_status('active')
    
    return {
        "missions": [
            {
                "id": m.id,
                "type": "active",
                "subsystem": m.subsystem,
                "title": m.title,
                "status": m.status,
                "kpi_delta": m.kpi_delta,
                "started_at": m.started_at.isoformat(),
                "updated_at": m.updated_at.isoformat()
            }
            for m in missions
        ],
        "total": len(missions)
    }


@router.get("/api/missions/proactive")
async def get_proactive_missions():
    """Get all proactive missions"""
    from backend.autonomy.mission_tracker import get_missions_by_type
    
    missions = await get_missions_by_type('proactive')
    
    return {
        "missions": [mission_to_dict(m) for m in missions],
        "total": len(missions)
    }


@router.get("/api/missions/followups")
async def get_followup_missions():
    """Get all follow-up missions"""
    from backend.autonomy.mission_tracker import get_missions_by_type
    
    missions = await get_missions_by_type('followup')
    
    return {
        "missions": [mission_to_dict(m) for m in missions],
        "total": len(missions)
    }
```

---

### Step 3: Test Endpoints

```bash
# Test logs API
curl http://localhost:8017/api/logs/recent?limit=10

# Test console overview
curl http://localhost:8017/api/console/overview

# Test chat (existing)
curl -X POST http://localhost:8017/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Grace"}'

# Test missions (after creating endpoints)
curl http://localhost:8017/api/missions/active
curl http://localhost:8017/api/missions/proactive
curl http://localhost:8017/api/missions/followups
```

---

### Step 4: Frontend Integration

#### Logs Pane - WebSocket Connection
```typescript
// src/hooks/useLogsWebSocket.ts
export const useLogsWebSocket = () => {
  const [logs, setLogs] = useState<Log[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8017/api/logs/stream');
    
    ws.onopen = () => setIsConnected(true);
    
    ws.onmessage = (event) => {
      const log = JSON.parse(event.data);
      setLogs(prev => [log, ...prev].slice(0, 1000));
    };
    
    ws.onclose = () => setIsConnected(false);
    
    return () => ws.close();
  }, []);
  
  return { logs, isConnected };
};
```

#### Task Manager - REST API
```typescript
// src/hooks/useMissions.ts
export const useMissions = (type: 'active' | 'proactive' | 'followups') => {
  return useQuery({
    queryKey: ['missions', type],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8017/api/missions/${type}`);
      return response.json();
    },
    refetchInterval: 5000
  });
};
```

#### Chat Pane - Existing Endpoint
```typescript
// src/hooks/useChat.ts
export const useChatSend = () => {
  return useMutation({
    mutationFn: async (message: string) => {
      const response = await fetch('http://localhost:8017/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      return response.json();
    }
  });
};
```

---

## 📊 Summary Table

| Pane | API Endpoint | Status | Backend File | Frontend Hook |
|------|-------------|--------|--------------|---------------|
| **Logs** | `GET /api/logs/recent` | ✅ Ready | `logs_api.py` | `useLogs()` |
| **Logs** | `WS /api/logs/stream` | ✅ Ready | `logs_api.py` | `useLogsWebSocket()` |
| **Chat** | `POST /api/chat` | ✅ Exists | `main.py` | `useChatSend()` |
| **Tasks** | `GET /api/missions/active` | ⚠️ Create | `mission_control_api.py` | `useMissions('active')` |
| **Tasks** | `GET /api/missions/proactive` | ⚠️ Create | `mission_control_api.py` | `useMissions('proactive')` |
| **Tasks** | `GET /api/missions/followups` | ⚠️ Create | `mission_control_api.py` | `useMissions('followups')` |
| **Console** | `GET /api/console/overview` | ✅ Ready | `console_api.py` | `useOverview()` |

---

## 🎯 Next Steps

### 1. Create Mission Endpoints (15 minutes)
Edit `backend/routes/mission_control_api.py` to add:
- `GET /api/missions/active`
- `GET /api/missions/proactive`
- `GET /api/missions/followups`

### 2. Restart Backend
```bash
# Stop current backend (Ctrl+C)
python serve.py
```

### 3. Test Endpoints
```bash
curl http://localhost:8017/api/logs/recent
curl http://localhost:8017/api/missions/active
curl http://localhost:8017/api/chat -X POST -d '{"message":"hi"}'
```

### 4. Wire Frontend
- Use the hooks provided in [API_WIRING_GUIDE.md](./API_WIRING_GUIDE.md)
- Start dev server: `npm run dev`
- Verify data flows to UI

---

## ✅ Once Complete

**All three panes will have live data**:
- ✅ Logs pane: Real-time mission/follow-up events via WebSocket
- ✅ Task manager: Active/proactive/follow-up missions from Mission Control API
- ✅ Chat: Conversations with Grace via RAG/LLM

**Demo-ready**: Full functional console with real backend integration! 🎉

---

**Status**: 
- Logs API: ✅ Complete
- Console API: ✅ Complete
- Chat API: ✅ Already exists
- Mission APIs: ⚠️ Need to create 3 endpoints
