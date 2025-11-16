# Unified Console - Quick Start Guide

**Goal**: Get the frontend console running and connected to Grace backend

---

## 🚀 Prerequisites

1. **Backend running** on port 8017
2. **Node.js** installed (v16+)
3. **npm** or **yarn** installed

---

## 📋 Step-by-Step Setup

### Step 1: Start Grace Backend
```bash
cd C:\Users\aaron\grace_2
START_GRACE_APPROVED.bat

# Or manually:
python serve.py
```

**Verify backend is running**:
```bash
curl http://localhost:8017/health
# Should return: {"status": "ok"}
```

---

### Step 2: Navigate to Frontend
```bash
cd frontend/console
```

If `frontend/console/` doesn't exist yet:
```bash
# Create it
cd frontend
npx create-vite console --template react-ts
cd console
```

---

### Step 3: Install Dependencies
```bash
npm install
# or
yarn install
```

**Required packages**:
```bash
npm install tailwindcss postcss autoprefixer
npm install react-split-pane
npm install socket.io-client
npm install @tanstack/react-query
npm install zustand
npm install monaco-editor @monaco-editor/react
npm install recharts
npm install cmdk
```

---

### Step 4: Start Dev Server
```bash
npm run dev
# or
yarn dev
```

**Output**:
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### Step 5: Open in Browser
Navigate to: **http://localhost:5173**

You should see the Grace console interface!

---

## 🔌 Backend CORS Configuration

### Verify CORS Allows Frontend

The backend should already allow all origins:
```python
# backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Already allows localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**If you need to be more specific**:
```python
allow_origins=[
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
    "http://localhost:8017",  # Backend
],
```

---

## 🧪 Test the Connection

### From Browser Console (F12)
```javascript
// Test API connection
fetch('http://localhost:8017/health')
  .then(r => r.json())
  .then(data => console.log('Backend connected:', data));

// Expected: {status: "ok"}
```

### From Frontend Code
```typescript
// App.tsx or useEffect hook
useEffect(() => {
  fetch('http://localhost:8017/health')
    .then(r => r.json())
    .then(data => {
      console.log('✅ Backend connected:', data);
      setBackendStatus('connected');
    })
    .catch(err => {
      console.error('❌ Backend not reachable:', err);
      setBackendStatus('disconnected');
    });
}, []);
```

---

## 🔧 Common Issues & Fixes

### Issue 1: "Cannot connect to backend"
**Cause**: Backend not running or wrong port

**Fix**:
```bash
# Check if backend is running
curl http://localhost:8017/health

# If not, start it:
cd C:\Users\aaron\grace_2
python serve.py
```

---

### Issue 2: "CORS error"
**Cause**: Backend not allowing frontend origin

**Fix**: Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue 3: "Port 5173 already in use"
**Cause**: Another Vite server running

**Fix**:
```bash
# Kill existing process or use different port
npm run dev -- --port 5174
```

---

### Issue 4: "Module not found"
**Cause**: Dependencies not installed

**Fix**:
```bash
# Install all dependencies
npm install

# Or specific package:
npm install socket.io-client
```

---

## 📂 Project Structure

```
frontend/console/
├── public/
├── src/
│   ├── components/
│   │   ├── Console/
│   │   │   ├── ConsoleLayout.tsx
│   │   │   ├── LogsPane.tsx
│   │   │   ├── ChatPane.tsx
│   │   │   └── TaskManagerPane.tsx
│   │   ├── Workspaces/
│   │   └── FileExplorer/
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useMissions.ts
│   │   └── useKnowledge.ts
│   ├── api/
│   │   └── client.ts
│   ├── types/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🎯 Development Workflow

### Terminal 1: Backend
```bash
cd C:\Users\aaron\grace_2
python serve.py

# Keep this running
# Backend on: http://localhost:8017
```

### Terminal 2: Frontend
```bash
cd C:\Users\aaron\grace_2\frontend\console
npm run dev

# Keep this running
# Frontend on: http://localhost:5173
```

### Browser
```
Open: http://localhost:5173
```

**Hot Reload**: Both frontend and backend support hot reload
- Frontend: Changes auto-refresh in browser
- Backend: Use `--reload` flag for auto-restart

---

## 🔗 API Base URL Configuration

### Create API Client
```typescript
// src/api/client.ts

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8017';

export const apiClient = {
  async get(path: string) {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },
  
  async post(path: string, data: any) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  }
};
```

### Environment Variables
```bash
# .env.development
VITE_API_URL=http://localhost:8017
VITE_WS_URL=ws://localhost:8017

# .env.production
VITE_API_URL=https://grace.yourdomain.com
VITE_WS_URL=wss://grace.yourdomain.com
```

---

## ✅ Verification Checklist

### Backend Ready
- [ ] Backend running: `python serve.py`
- [ ] Health check works: `curl http://localhost:8017/health`
- [ ] CORS configured: `allow_origins=["*"]`
- [ ] Approvals granted (if needed)

### Frontend Ready
- [ ] Dependencies installed: `npm install`
- [ ] Dev server starts: `npm run dev`
- [ ] Browser loads: `http://localhost:5173`
- [ ] No console errors in browser (F12)

### Connection Working
- [ ] Frontend can fetch backend: `fetch('http://localhost:8017/health')`
- [ ] No CORS errors
- [ ] API requests return data
- [ ] WebSocket connects (for logs/missions)

---

## 🎨 First Load Experience

**What you should see**:
```
┌─────────────────────────────────────────────────────────┐
│  Grace Console                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────┬──────────────┬──────────┐                 │
│  │ LOGS    │ CHAT         │ TASKS    │                 │
│  │         │              │          │                 │
│  │ (empty) │ Say hi to    │ (loading)│                 │
│  │         │ Grace...     │          │                 │
│  └─────────┴──────────────┴──────────┘                 │
│                                                          │
│  Backend: ✅ Connected to http://localhost:8017         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Debugging

### Enable Verbose Logging
```typescript
// In main.tsx
if (import.meta.env.DEV) {
  console.log('🔧 Development mode');
  console.log('📡 API URL:', import.meta.env.VITE_API_URL);
}
```

### Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Reload page
4. Verify API requests to `localhost:8017`
5. Check for CORS errors

### Backend Logs
Watch backend terminal for incoming requests:
```
INFO:     127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "GET /api/logs/recent HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "POST /api/chat/send HTTP/1.1" 200 OK
```

---

## 🚀 Quick Commands Reference

```bash
# Start backend
cd C:\Users\aaron\grace_2
python serve.py

# Start frontend (separate terminal)
cd C:\Users\aaron\grace_2\frontend\console
npm run dev

# Open browser
start http://localhost:5173

# Check backend health
curl http://localhost:8017/health

# Check frontend build
npm run build

# Preview production build
npm run preview
```

---

## 📊 Development Ports

| Service | Port | URL |
|---------|------|-----|
| **Grace Backend** | 8017 | http://localhost:8017 |
| **Vite Dev Server** | 5173 | http://localhost:5173 |
| **React Dev Server** | 3000 | http://localhost:3000 |
| **Core Domain** | 8200 | http://localhost:8200 (internal) |
| **Memory Domain** | 8201 | http://localhost:8201 (internal) |
| **AI Domain** | 8202 | http://localhost:8202 (internal) |

**Note**: Domains 8200-8209 are internal and proxied through main API (8017)

---

## ✅ Ready to Develop!

**Both servers running**:
- ✅ Backend: http://localhost:8017
- ✅ Frontend: http://localhost:5173

**Next steps**:
1. Build three-pane layout
2. Add placeholder data
3. Ensure responsive design
4. Prove the shell works

See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for detailed tasks!

---

**Status**: Development environment ready! Start building the console. 🎨
