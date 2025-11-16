# Logs Pane - Complete Implementation

**Goal**: Wire logs pane to show real mission/follow-up events with filters

---

## ✅ Backend Already Ready

The backend API is already created and integrated:
- ✅ `GET /api/logs/recent` - Returns latest N events
- ✅ `WS /api/logs/stream` - Live WebSocket streaming
- ✅ Filters: `?subsystem=crm&level=warning&limit=100`

**File**: `backend/routes/logs_api.py` ✅  
**Integrated in**: `backend/main.py` ✅

---

## 🔌 Frontend Implementation

### Step 1: Create the Hook

Create `frontend/console/src/hooks/useLogsWebSocket.ts`:

```typescript
import { useState, useEffect, useCallback } from 'react';

export interface Log {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  domain: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export const useLogsWebSocket = () => {
  const [logs, setLogs] = useState<Log[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;
    
    const connect = () => {
      ws = new WebSocket('ws://localhost:8017/api/logs/stream');
      
      ws.onopen = () => {
        console.log('✅ Logs WebSocket connected');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = (event) => {
        try {
          const log: Log = JSON.parse(event.data);
          
          setLogs(prevLogs => {
            const newLogs = [log, ...prevLogs];
            // Keep only last 1000 logs to prevent memory issues
            return newLogs.slice(0, 1000);
          });
        } catch (err) {
          console.error('Failed to parse log:', err);
        }
      };
      
      ws.onerror = (event) => {
        console.error('❌ Logs WebSocket error');
        setError('Connection error');
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('🔌 Logs WebSocket disconnected');
        setIsConnected(false);
        
        // Auto-reconnect after 5 seconds
        reconnectTimeout = setTimeout(() => {
          console.log('🔄 Reconnecting logs WebSocket...');
          connect();
        }, 5000);
      };
    };
    
    connect();
    
    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, []);
  
  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);
  
  return { logs, isConnected, error, clearLogs };
};
```

---

### Step 2: Create the LogsPane Component

Create `frontend/console/src/components/Console/LogsPane.tsx`:

```typescript
import React, { useState, useMemo } from 'react';
import { useLogsWebSocket, Log } from '../../hooks/useLogsWebSocket';

export const LogsPane: React.FC = () => {
  const { logs, isConnected, error, clearLogs } = useLogsWebSocket();
  
  const [filters, setFilters] = useState({
    level: '',
    domain: '',
    search: ''
  });
  
  const [autoScroll, setAutoScroll] = useState(true);
  
  // Filter logs client-side
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filters.level && log.level !== filters.level) return false;
      if (filters.domain && log.domain !== filters.domain) return false;
      if (filters.search && !log.message.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [logs, filters]);
  
  // Get unique domains for filter dropdown
  const domains = useMemo(() => {
    const uniqueDomains = new Set(logs.map(log => log.domain));
    return Array.from(uniqueDomains).sort();
  }, [logs]);
  
  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Logs</h2>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Filters */}
      <div className="p-4 border-b border-gray-700 space-y-2">
        <div className="flex gap-2">
          {/* Level filter */}
          <select
            value={filters.level}
            onChange={(e) => setFilters({ ...filters, level: e.target.value })}
            className="px-3 py-1 bg-gray-800 text-white border border-gray-700 rounded"
          >
            <option value="">All Levels</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
          
          {/* Domain filter */}
          <select
            value={filters.domain}
            onChange={(e) => setFilters({ ...filters, domain: e.target.value })}
            className="px-3 py-1 bg-gray-800 text-white border border-gray-700 rounded"
          >
            <option value="">All Domains</option>
            {domains.map(domain => (
              <option key={domain} value={domain}>{domain}</option>
            ))}
          </select>
          
          {/* Auto-scroll toggle */}
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
          
          {/* Clear button */}
          <button
            onClick={clearLogs}
            className="px-3 py-1 bg-gray-800 text-white border border-gray-700 rounded hover:bg-gray-700"
          >
            Clear
          </button>
        </div>
        
        {/* Search */}
        <input
          type="text"
          placeholder="Search logs..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-700 rounded"
        />
      </div>
      
      {/* Logs list */}
      <div className="flex-1 overflow-y-auto p-2">
        {error && (
          <div className="p-4 bg-red-900/20 border border-red-700 rounded text-red-400">
            {error}
          </div>
        )}
        
        {filteredLogs.length === 0 && (
          <div className="p-4 text-center text-gray-500">
            {logs.length === 0 ? 'No logs yet...' : 'No logs match filters'}
          </div>
        )}
        
        {filteredLogs.map((log, index) => (
          <LogEntry key={`${log.timestamp}-${index}`} log={log} />
        ))}
      </div>
      
      {/* Footer stats */}
      <div className="p-2 border-t border-gray-700 text-xs text-gray-400">
        Showing {filteredLogs.length} of {logs.length} logs
      </div>
    </div>
  );
};

// LogEntry component
const LogEntry: React.FC<{ log: Log }> = ({ log }) => {
  const levelColors = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400'
  };
  
  const levelIcons = {
    info: '🔵',
    success: '🟢',
    warning: '🟡',
    error: '🔴'
  };
  
  return (
    <div className="flex gap-2 p-2 hover:bg-gray-800/50 rounded font-mono text-sm">
      <span className="flex-shrink-0">{levelIcons[log.level]}</span>
      <span className="flex-shrink-0 text-gray-500 w-20">
        {new Date(log.timestamp).toLocaleTimeString()}
      </span>
      <span className="flex-shrink-0 text-purple-400 w-24">
        [{log.domain}]
      </span>
      <span className={levelColors[log.level]}>
        {log.message}
      </span>
    </div>
  );
};
```

---

### Step 3: Integrate into ConsoleLayout

Update `frontend/console/src/components/Console/ConsoleLayout.tsx`:

```typescript
import { LogsPane } from './LogsPane';
import { ChatPane } from './ChatPane';
import { TaskManagerPane } from './TaskManagerPane';
import SplitPane from 'react-split-pane';

export const ConsoleLayout = () => {
  return (
    <div className="h-screen bg-gray-900">
      <SplitPane
        split="vertical"
        defaultSize="30%"
        minSize={200}
        maxSize={-400}
      >
        {/* Logs Pane - Now with real data! */}
        <LogsPane />
        
        <SplitPane
          split="vertical"
          defaultSize="60%"
          minSize={300}
        >
          {/* Chat Pane */}
          <ChatPane />
          
          {/* Task Manager Pane */}
          <TaskManagerPane />
        </SplitPane>
      </SplitPane>
    </div>
  );
};
```

---

## 🧪 Test the Integration

### Backend Test
```bash
# 1. Start backend
cd C:\Users\aaron\grace_2
python serve.py

# 2. Test logs endpoint
curl http://localhost:8017/api/logs/recent?limit=10

# 3. Test with filters
curl "http://localhost:8017/api/logs/recent?level=error&domain=memory"
```

### Frontend Test
```bash
# 1. Start frontend (separate terminal)
cd C:\Users\aaron\grace_2\frontend\console
npm run dev

# 2. Open browser
# Navigate to: http://localhost:5173

# 3. Open browser console (F12)
# You should see: "✅ Logs WebSocket connected"

# 4. Watch logs appear in real-time!
```

---

## 📨 How to Emit Logs from Backend

### From Anywhere in Backend Code
```python
# Example: In mission completion
from backend.routes.logs_api import add_log

# Success log
add_log(
    level='success',
    message='Mission #123 completed - Memory leak fixed',
    domain='execution',
    metadata={'mission_id': 'mission_123', 'kpi_delta': -45}
)

# Warning log
add_log(
    level='warning',
    message='High latency detected (120ms)',
    domain='ai',
    metadata={'latency_ms': 120, 'threshold': 100}
)

# Error log
add_log(
    level='error',
    message='Connection timeout to Memory Domain',
    domain='integration',
    metadata={'port': 8201, 'timeout_seconds': 5}
)
```

### From Domain Event Bus
```python
# Auto-emit logs when domain events occur
from backend.domains import domain_event_bus
from backend.routes.logs_api import add_log

# Subscribe to all events and convert to logs
async def event_to_log_handler(event):
    level_map = {
        'error': 'error',
        'warning': 'warning',
        'success': 'success',
        'info': 'info'
    }
    
    level = level_map.get(event.event_type.split('.')[0], 'info')
    
    add_log(
        level=level,
        message=f"{event.event_type}: {event.data.get('message', 'Event occurred')}",
        domain=event.source_domain,
        metadata=event.data
    )

# Register handler
domain_event_bus.subscribe('*', event_to_log_handler)
```

---

## 🎨 Expected Result

When you open the console, you should see:

```
┌─────────────────────────────────────────────────────────┐
│  Logs                                    🟢 Connected   │
├─────────────────────────────────────────────────────────┤
│  [All Levels ▼] [All Domains ▼] [☑ Auto-scroll] [Clear]│
│  [Search logs...]                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🟢 10:30:15 [execution]  Mission #123 completed        │
│  🟡 10:30:18 [ai]         High latency detected (120ms) │
│  🔴 10:30:20 [integration] Connection timeout           │
│  🔵 10:30:22 [core]       Processing request...         │
│  🟢 10:30:25 [memory]     Cache cleared successfully    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Showing 5 of 342 logs                                  │
└─────────────────────────────────────────────────────────┘
```

**Live updates**: New logs appear automatically as events occur in backend!

---

## 🔧 Quick Integration Commands

### 1. Ensure Backend Has Logs Router
```bash
# Verify it's in backend/main.py
findstr "logs_router" backend\main.py

# Should see:
# from backend.routes.logs_api import router as logs_router
# app.include_router(logs_router)
```

### 2. Test Logs API
```bash
# Start backend
python serve.py

# Test endpoint
curl http://localhost:8017/api/logs/recent

# Should return:
# {"logs": [], "total": 0, "limit": 100}
```

### 3. Add Test Logs
```python
# In Python console or add to backend startup:
from backend.routes.logs_api import add_log

add_log('success', 'Test message 1', domain='core')
add_log('warning', 'Test warning', domain='memory')
add_log('error', 'Test error', domain='ai')

# Now curl again:
# curl http://localhost:8017/api/logs/recent
# Should show 3 logs
```

### 4. Start Frontend
```bash
cd frontend/console
npm run dev

# Open: http://localhost:5173
# Logs should appear!
```

---

## ✅ Success Criteria

- [ ] Backend returns logs from `/api/logs/recent`
- [ ] WebSocket connects: `ws://localhost:8017/api/logs/stream`
- [ ] Frontend displays logs with color-coding
- [ ] Filters work (level, domain, search)
- [ ] New logs appear automatically (real-time)
- [ ] Auto-scroll works
- [ ] Clear button empties log list

---

## 🎯 Next Steps After Logs

Once logs pane is working:

1. **Task Manager** - Wire to `/api/missions/active` (need to create endpoint)
2. **Chat Pane** - Wire to `/api/chat` (already exists)

---

**Status**: Logs pane fully specified! Backend ready, frontend code provided. Just implement and test! 🚀
