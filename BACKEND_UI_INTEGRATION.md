# Backend to UI Integration Guide

## Current Status: ✅ Mostly Connected

Your backend and frontend are **already wired up** with the following architecture:

### Architecture Overview

```
Frontend (React + Vite)          Backend (FastAPI)
Port 5173                        Port 8000
     │                                │
     ├─ Vite Proxy (/api/*) ────────→│
     │                                │
     ├─ API Clients (TypeScript) ────→│ Routes (Python)
     │                                │
     └─ Components ──────────────────→│ 180+ API Endpoints
```

---

## ✅ What's Already Working

### 1. **CORS Configuration** (backend/main.py)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
✅ Allows all origins (good for development)

### 2. **Vite Proxy** (frontend/vite.config.ts)
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```
✅ Proxies all `/api/*` requests to backend

### 3. **API Configuration** (frontend/src/config.ts)
```typescript
export const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL || 
  import.meta.env.VITE_BACKEND_URL || 
  '';
```
✅ Centralized configuration with environment variable support

### 4. **API Clients** (frontend/src/api/)
You have 30+ API client modules:
- ✅ `chat.ts` - Chat API
- ✅ `missions.ts` - Mission Control API
- ✅ `snapshots.ts` - Snapshot API
- ✅ `incidents.ts` - Self-Healing API
- ✅ `chaos.ts` - Chaos Engineering API
- ✅ `learning.ts` - Learning API
- ✅ `memory.ts` - Memory API
- ✅ `tasks.ts` - Task API
- ✅ `trust.ts` - Trust Framework API
- And many more...

### 5. **Backend Routes** (backend/routes/)
180+ API routes registered including:
- ✅ Chat API (`/api/chat`)
- ✅ Metrics API (`/api/metrics`)
- ✅ Governance API (`/api/governance`)
- ✅ Guardian API (`/api/guardian`)
- ✅ Mission Control API (`/api/mission-control`)
- ✅ Self-Healing API (`/api/self-healing`)
- ✅ Learning API (`/api/learning`)
- And many more...

---

## 🚀 Quick Start

### Start Both Services

**Option 1: Using server.py (Recommended)**
```bash
python server.py
```
This starts:
- Backend on http://localhost:8000
- Frontend on http://localhost:5173 (automatically)

**Option 2: Manually**
```bash
# Terminal 1 - Backend
python server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🔧 How to Add New API Endpoints

### Step 1: Create Backend Route

Create `backend/routes/my_feature_api.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/my-feature", tags=["my-feature"])

class MyRequest(BaseModel):
    data: str

class MyResponse(BaseModel):
    result: str
    success: bool

@router.get("/status")
async def get_status():
    return {"status": "active"}

@router.post("/process")
async def process_data(request: MyRequest):
    return MyResponse(
        result=f"Processed: {request.data}",
        success=True
    )
```

### Step 2: Register in main.py

Add to `backend/main.py`:

```python
try:
    from backend.routes.my_feature_api import router as my_feature_router
    app.include_router(my_feature_router)
except ImportError as e:
    print(f"[WARN] My Feature API disabled: {e}")
```

### Step 3: Create Frontend API Client

Create `frontend/src/api/myFeature.ts`:

```typescript
import { API_BASE_URL } from '../config';

export interface MyRequest {
  data: string;
}

export interface MyResponse {
  result: string;
  success: boolean;
}

export class MyFeatureAPI {
  static async getStatus() {
    const response = await fetch(`${API_BASE_URL}/api/my-feature/status`);
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
  }

  static async processData(request: MyRequest): Promise<MyResponse> {
    const response = await fetch(`${API_BASE_URL}/api/my-feature/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error('Failed to process data');
    return response.json();
  }
}
```

### Step 4: Use in Component

Create `frontend/src/components/MyFeature.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { MyFeatureAPI } from '../api/myFeature';

export function MyFeature() {
  const [status, setStatus] = useState<string>('');
  const [result, setResult] = useState<string>('');

  useEffect(() => {
    const fetchStatus = async () => {
      const data = await MyFeatureAPI.getStatus();
      setStatus(data.status);
    };
    fetchStatus();
  }, []);

  const handleProcess = async () => {
    const response = await MyFeatureAPI.processData({ data: 'test' });
    setResult(response.result);
  };

  return (
    <div>
      <h2>My Feature</h2>
      <p>Status: {status}</p>
      <button onClick={handleProcess}>Process</button>
      <p>Result: {result}</p>
    </div>
  );
}
```

---

## 🔍 Testing Integration

### Test Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/metrics/summary

# View API docs
open http://localhost:8000/docs
```

### Test Frontend
```bash
# In browser console (F12)
fetch('/api/metrics/summary')
  .then(r => r.json())
  .then(console.log)

# Or check Network tab in DevTools
```

---

## 🐛 Troubleshooting

### Issue: "CORS Error"
**Solution**: Backend CORS is already configured for `*`. If you still see CORS errors:
1. Check backend is running on port 8000
2. Clear browser cache
3. Restart both services

### Issue: "404 Not Found"
**Solution**: 
1. Verify route is registered in `backend/main.py`
2. Check route prefix (should be `/api/...`)
3. Verify proxy in `vite.config.ts`

### Issue: "Connection Refused"
**Solution**:
1. Backend not running - start with `python server.py`
2. Port 8000 in use - check with `netstat -ano | findstr :8000`
3. Firewall blocking - allow port 8000

### Issue: "Proxy Error"
**Solution**:
1. Check `VITE_BACKEND_URL` environment variable
2. Verify `vite.config.ts` proxy target
3. Restart Vite dev server

---

## 📝 Environment Variables

### Frontend (.env.local)
```bash
# Optional - defaults to Vite proxy
VITE_API_BASE_URL=http://localhost:8000

# Optional - for WebSocket
VITE_WS_URL=ws://localhost:8000
```

### Backend (.env)
```bash
# Port configuration
GRACE_PORT=8000

# Other backend configs...
```

---

## 🎯 Key Endpoints Already Integrated

### Chat & Communication
- `POST /api/chat` - Send chat message
- `GET /api/chat/sessions` - List chat sessions
- `GET /api/chat/history/{id}` - Get chat history

### Metrics & Monitoring
- `GET /api/metrics/summary` - System metrics
- `GET /api/metrics/health` - Health status

### Mission Control
- `GET /api/mission-control/missions` - List missions
- `POST /api/mission-control/execute` - Execute mission
- `GET /api/mission-control/status` - Mission status

### Self-Healing
- `GET /api/self-healing/stats` - Healing statistics
- `GET /api/self-healing/incidents` - Recent incidents
- `POST /api/self-healing/trigger` - Trigger healing

### Learning System
- `GET /api/learning/status` - Learning status
- `GET /api/learning/outcomes` - Learning outcomes
- `POST /api/learning/request` - Request learning

### Snapshots
- `GET /api/snapshots/list` - List snapshots
- `POST /api/snapshots/create` - Create snapshot
- `POST /api/snapshots/restore/{id}` - Restore snapshot

### Guardian
- `GET /api/guardian/status` - Guardian status
- `GET /api/guardian/healer/stats` - Network healing stats
- `POST /api/guardian/healer/scan` - Trigger network scan

---

## 🎨 UI Components Using APIs

Already integrated:
- ✅ `SystemOverview.tsx` - Uses metrics, missions, incidents
- ✅ `MissionControlDashboard.tsx` - Uses missions, learning, chaos
- ✅ `SelfHealingMetrics.tsx` - Uses self-healing API
- ✅ `TelemetryStrip.tsx` - Uses metrics API
- ✅ `RemoteCockpit.tsx` - Uses remote access API
- ✅ `MissionList.tsx` - Uses mission control API

---

## ✨ Next Steps

Your system is already well integrated! To add new features:

1. **Add backend route** in `backend/routes/`
2. **Register in** `backend/main.py`
3. **Create API client** in `frontend/src/api/`
4. **Use in component** in `frontend/src/components/`
5. **Test with** browser DevTools

That's it! The infrastructure is all set up.

---

## 📚 Additional Resources

- **Backend API Docs**: http://localhost:8000/docs (when running)
- **Frontend API Config**: `frontend/src/api/config.ts`
- **Backend Routes**: `backend/routes/` (180+ files)
- **Vite Proxy Config**: `frontend/vite.config.ts`

---

**Status: ✅ Backend and UI are fully wired and ready to use!**
