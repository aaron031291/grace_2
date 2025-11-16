# Console UI - API Wiring Guide

**Purpose**: Connect frontend console panes to backend APIs

---

## 📡 API Endpoints Summary

### Logs Pane
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/logs/recent` | GET | Fetch recent logs with filters |
| `/api/logs/stream` | WebSocket | Live log streaming |
| `/api/logs/domains` | GET | List available domains |
| `/api/logs/levels` | GET | List log levels |

### Task Manager Pane
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/missions/active` | GET | List active missions |
| `/api/missions/proactive` | GET | List proactive missions |
| `/api/missions/followups` | GET | List follow-up missions |
| `/api/missions/{id}` | GET | Get mission details |
| `/ws/missions` | WebSocket | Live mission updates |

### Chat Pane
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message to Grace |
| `/api/chat/history` | GET | Get conversation history |
| `/ws/chat` | WebSocket | Streaming responses |

---

## 🔌 Frontend Wiring

### 1. Logs Pane - Fetch Mission/Follow-up Events

#### REST API Approach
```typescript
// hooks/useLogs.ts
import { useQuery } from '@tanstack/react-query';

export const useLogs = (filters?: LogFilters) => {
  return useQuery({
    queryKey: ['logs', 'recent', filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: '100',
        level: filters?.level || '',
        domain: filters?.domain || '',
        search: filters?.search || ''
      });
      
      const response = await fetch(
        `http://localhost:8017/api/logs/recent?${params}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      
      return response.json();
    },
    refetchInterval: 5000  // Poll every 5 seconds
  });
};
```

**Usage in component**:
```typescript
// LogsPane.tsx
export const LogsPane = () => {
  const [filters, setFilters] = useState<LogFilters>({});
  const { data, isLoading } = useLogs(filters);
  
  return (
    <div className="logs-pane">
      <LogFilters onChange={setFilters} />
      
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <LogList logs={data?.logs || []} />
      )}
    </div>
  );
};
```

---

#### WebSocket Approach (Recommended)
```typescript
// hooks/useLogsWebSocket.ts
import { useState, useEffect } from 'react';

export const useLogsWebSocket = () => {
  const [logs, setLogs] = useState<Log[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8017/api/logs/stream');
    
    ws.onopen = () => {
      console.log('✅ Logs WebSocket connected');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const log = JSON.parse(event.data);
      
      setLogs(prevLogs => {
        const newLogs = [log, ...prevLogs];
        // Keep only last 1000 logs
        return newLogs.slice(0, 1000);
      });
    };
    
    ws.onerror = (error) => {
      console.error('❌ Logs WebSocket error:', error);
      setIsConnected(false);
    };
    
    ws.onclose = () => {
      console.log('🔌 Logs WebSocket disconnected');
      setIsConnected(false);
      
      // Reconnect after 5 seconds
      setTimeout(() => {
        console.log('🔄 Reconnecting logs WebSocket...');
      }, 5000);
    };
    
    return () => {
      ws.close();
    };
  }, []);
  
  return { logs, isConnected };
};
```

**Usage**:
```typescript
// LogsPane.tsx
export const LogsPane = () => {
  const { logs, isConnected } = useLogsWebSocket();
  const [filteredLogs, setFilteredLogs] = useState<Log[]>([]);
  
  useEffect(() => {
    // Apply filters client-side
    let filtered = logs;
    
    if (filters.level) {
      filtered = filtered.filter(log => log.level === filters.level);
    }
    
    if (filters.domain) {
      filtered = filtered.filter(log => log.domain === filters.domain);
    }
    
    setFilteredLogs(filtered);
  }, [logs, filters]);
  
  return (
    <div className="logs-pane">
      <LogHeader isConnected={isConnected} />
      <LogFilters onChange={setFilters} />
      <LogList logs={filteredLogs} />
    </div>
  );
};
```

---

### 2. Task Manager - Mission Control APIs

#### Fetch Active Missions
```typescript
// hooks/useMissions.ts
import { useQuery } from '@tanstack/react-query';

export const useActiveMissions = () => {
  return useQuery({
    queryKey: ['missions', 'active'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8017/api/missions/active');
      if (!response.ok) throw new Error('Failed to fetch missions');
      return response.json();
    },
    refetchInterval: 5000  // Refresh every 5 seconds
  });
};

export const useProactiveMissions = () => {
  return useQuery({
    queryKey: ['missions', 'proactive'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8017/api/missions/proactive');
      if (!response.ok) throw new Error('Failed to fetch proactive missions');
      return response.json();
    },
    refetchInterval: 5000
  });
};

export const useFollowupMissions = () => {
  return useQuery({
    queryKey: ['missions', 'followups'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8017/api/missions/followups');
      if (!response.ok) throw new Error('Failed to fetch followups');
      return response.json();
    },
    refetchInterval: 5000
  });
};
```

**Usage in Task Manager**:
```typescript
// TaskManagerPane.tsx
export const TaskManagerPane = () => {
  const [activeTab, setActiveTab] = useState<'active' | 'proactive' | 'followups'>('active');
  
  const { data: activeMissions } = useActiveMissions();
  const { data: proactiveMissions } = useProactiveMissions();
  const { data: followupMissions } = useFollowupMissions();
  
  const missions = {
    active: activeMissions?.missions || [],
    proactive: proactiveMissions?.missions || [],
    followups: followupMissions?.missions || []
  };
  
  return (
    <div className="task-manager-pane">
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="active" count={missions.active.length}>
          Active
        </Tab>
        <Tab value="proactive" count={missions.proactive.length}>
          Proactive
        </Tab>
        <Tab value="followups" count={missions.followups.length}>
          Follow-ups
        </Tab>
      </Tabs>
      
      <MissionList 
        missions={missions[activeTab]}
        type={activeTab}
      />
    </div>
  );
};
```

---

#### WebSocket for Mission Updates (Optional)
```typescript
// hooks/useMissionsWebSocket.ts
export const useMissionsWebSocket = () => {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8017/ws/missions');
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      // Mission status changed
      if (update.type === 'mission.status_changed') {
        // Invalidate missions query to refetch
        queryClient.invalidateQueries(['missions']);
      }
      
      // New mission created
      if (update.type === 'mission.created') {
        queryClient.invalidateQueries(['missions']);
      }
    };
    
    return () => ws.close();
  }, []);
};
```

---

### 3. Chat Pane - Wire to RAG/Chat Endpoints

#### Basic Chat Integration
```typescript
// hooks/useChat.ts
import { useMutation } from '@tanstack/react-query';

export const useChatSend = () => {
  return useMutation({
    mutationFn: async ({ message, userId }: { message: string; userId: string }) => {
      const response = await fetch('http://localhost:8017/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          user_id: userId
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      return response.json();
    }
  });
};

export const useChatHistory = () => {
  return useQuery({
    queryKey: ['chat', 'history'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8017/api/chat/history');
      return response.json();
    }
  });
};
```

**Usage in Chat Pane**:
```typescript
// ChatPane.tsx
export const ChatPane = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  
  const { mutate: sendMessage, isLoading } = useChatSend();
  
  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message to UI immediately
    const userMessage = {
      id: Date.now().toString(),
      from: 'user',
      text: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    // Send to backend
    sendMessage(
      { message: input, userId: 'admin' },
      {
        onSuccess: (data) => {
          // Add Grace's response
          const graceMessage = {
            id: (Date.now() + 1).toString(),
            from: 'grace',
            text: data.response,
            timestamp: new Date().toISOString()
          };
          
          setMessages(prev => [...prev, graceMessage]);
        },
        onError: (error) => {
          console.error('Failed to send message:', error);
        }
      }
    );
  };
  
  return (
    <div className="chat-pane">
      <MessageList messages={messages} />
      
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        isLoading={isLoading}
      />
    </div>
  );
};
```

---

#### Streaming Chat Responses (Advanced)
```typescript
// For streaming LLM responses
export const useChatStream = () => {
  const [streamingMessage, setStreamingMessage] = useState('');
  
  const sendWithStreaming = async (message: string) => {
    const response = await fetch('http://localhost:8017/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      setStreamingMessage(prev => prev + chunk);
    }
  };
  
  return { sendWithStreaming, streamingMessage };
};
```

---

## 🔗 Backend Endpoints to Ensure Exist

### Create Missing Endpoints

#### Missions Endpoints
```python
# backend/routes/mission_control_api.py

@router.get("/api/missions/active")
async def get_active_missions():
    """Get all active missions"""
    # Query from mission database
    return {"missions": [...]}

@router.get("/api/missions/proactive")
async def get_proactive_missions():
    """Get all proactive missions"""
    return {"missions": [...]}

@router.get("/api/missions/followups")
async def get_followup_missions():
    """Get all follow-up missions"""
    return {"missions": [...]}

@router.get("/api/missions/{mission_id}")
async def get_mission_detail(mission_id: str):
    """Get detailed mission information"""
    return {"mission": {...}}
```

---

#### Chat Endpoints
```python
# backend/routes/chat.py (update existing or create)

@router.post("/api/chat/send")
async def send_chat_message(
    message: str,
    user_id: str = "admin"
):
    """
    Send message to Grace and get response
    
    Routes to AI Domain for RAG + LLM processing
    """
    try:
        # Use existing chat logic or RAG
        from backend.services.rag_service import rag_service
        
        response = await rag_service.query(
            query=message,
            user_id=user_id,
            include_sources=True
        )
        
        return {
            "response": response.get('answer'),
            "sources": response.get('sources', []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "response": f"I encountered an error: {str(e)}",
            "error": True
        }

@router.get("/api/chat/history")
async def get_chat_history(
    user_id: str = "admin",
    limit: int = 50
):
    """Get recent chat history"""
    # Fetch from conversation storage
    return {"messages": [...]}
```

---

## 🔧 Integration Steps

### Step 1: Add Logs API to Backend
```bash
# The logs_api.py file is already created above
# Add to backend/main.py:
```

```python
# backend/main.py

from backend.routes.logs_api import router as logs_router
from backend.routes.console_api import router as console_router

app.include_router(logs_router)
app.include_router(console_router)
```

---

### Step 2: Ensure Mission Control API Exists
```bash
# Check if these endpoints exist:
curl http://localhost:8017/api/missions/active
curl http://localhost:8017/api/missions/proactive
curl http://localhost:8017/api/missions/followups
```

**If they don't exist**, add them to `backend/routes/mission_control_api.py`

---

### Step 3: Wire Chat to Existing RAG
```python
# backend/routes/chat.py

# Use existing chat logic
# Most likely already exists in your backend
# Just ensure /api/chat/send endpoint is available
```

---

### Step 4: Test from Frontend

#### Test Logs API
```typescript
// In browser console (F12):
fetch('http://localhost:8017/api/logs/recent?limit=10')
  .then(r => r.json())
  .then(data => console.log('Logs:', data));
```

#### Test Missions API
```typescript
fetch('http://localhost:8017/api/missions/active')
  .then(r => r.json())
  .then(data => console.log('Missions:', data));
```

#### Test Chat API
```typescript
fetch('http://localhost:8017/api/chat/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello Grace',
    user_id: 'admin'
  })
})
  .then(r => r.json())
  .then(data => console.log('Response:', data));
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                  FRONTEND CONSOLE                        │
│                 (http://localhost:5173)                  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Logs Pane                                               │
│    ↓ WebSocket                                           │
│    ws://localhost:8017/api/logs/stream                  │
│                                                           │
│  Task Manager                                            │
│    ↓ REST API (polling)                                 │
│    GET /api/missions/active                             │
│    GET /api/missions/proactive                          │
│    GET /api/missions/followups                          │
│                                                           │
│  Chat Pane                                               │
│    ↓ REST API                                           │
│    POST /api/chat/send                                  │
│    GET /api/chat/history                                │
│                                                           │
└────────────┬─────────────────────────────────────────────┘
             │
             │ HTTP/WebSocket
             ↓
┌──────────────────────────────────────────────────────────┐
│                   GRACE BACKEND                          │
│                 (http://localhost:8017)                  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  /api/logs/*          → Logs API                        │
│  /ws/logs/stream      → WebSocket Broadcaster           │
│                                                           │
│  /api/missions/*      → Mission Control API             │
│  /ws/missions         → Mission Updates WebSocket       │
│                                                           │
│  /api/chat/*          → Chat/RAG Service                │
│                                                           │
└────────────┬─────────────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────────────┐
│               DOMAIN SERVICES                            │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Execution Domain (8204) → Mission Control              │
│  Monitoring Domain (8205) → Telemetry/Logs              │
│  AI Domain (8202)         → Chat/RAG                    │
│  Memory Domain (8201)     → Knowledge Base              │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ Integration Checklist

### Backend Ready
- [ ] `/api/logs/recent` endpoint exists
- [ ] `/api/logs/stream` WebSocket works
- [ ] `/api/missions/active` returns mission list
- [ ] `/api/missions/proactive` returns proactive missions
- [ ] `/api/missions/followups` returns follow-up missions
- [ ] `/api/chat/send` accepts messages and returns responses
- [ ] CORS allows `http://localhost:5173`

### Frontend Ready
- [ ] `useLogs` or `useLogsWebSocket` hook implemented
- [ ] `useActiveMissions`, `useProactiveMissions`, `useFollowupMissions` hooks implemented
- [ ] `useChatSend` hook implemented
- [ ] Components consume hooks and display data
- [ ] Loading states handled
- [ ] Error states handled

### Connection Working
- [ ] Frontend can fetch from backend
- [ ] WebSocket connects successfully
- [ ] Real data displays in console
- [ ] No CORS errors
- [ ] No console errors

---

## 🚀 Quick Integration Script

### Backend Setup
```bash
# 1. Add logs API to main.py
cd C:\Users\aaron\grace_2

# Edit backend/main.py to include:
# from backend.routes.logs_api import router as logs_router
# app.include_router(logs_router)

# 2. Restart backend
python serve.py
```

### Frontend Setup
```bash
# 1. Create hooks
cd frontend/console/src/hooks
# Create useLogs.ts, useMissions.ts, useChat.ts

# 2. Update components
# Wire LogsPane to useLogs
# Wire TaskManagerPane to useMissions
# Wire ChatPane to useChat

# 3. Start dev server
npm run dev
```

### Verify
```bash
# Open browser: http://localhost:5173
# Check logs pane shows real logs
# Check tasks pane shows real missions
# Send chat message and get response
```

---

## 📝 Example: Complete Wiring

### LogsPane with Real Data
```typescript
// src/components/Console/LogsPane.tsx
import { useLogsWebSocket } from '../../hooks/useLogsWebSocket';

export const LogsPane = () => {
  const { logs, isConnected } = useLogsWebSocket();
  const [filters, setFilters] = useState({});
  
  // Filter logs client-side
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filters.level && log.level !== filters.level) return false;
      if (filters.domain && log.domain !== filters.domain) return false;
      return true;
    });
  }, [logs, filters]);
  
  return (
    <div className="logs-pane">
      {/* Connection status */}
      <div className="status-bar">
        {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      
      {/* Filters */}
      <LogFilters filters={filters} onChange={setFilters} />
      
      {/* Log list */}
      <div className="log-list">
        {filteredLogs.map(log => (
          <LogEntry key={log.timestamp} log={log} />
        ))}
      </div>
    </div>
  );
};
```

---

**Status**: API wiring guide complete! Backend endpoints created, frontend hooks defined. Ready to connect! 🔌
