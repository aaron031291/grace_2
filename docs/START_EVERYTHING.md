# Start Everything - Backend + Frontend + CLI

**Goal:** Get all 3 components running and connected

---

## Step 1: Start Backend (Terminal 1)

```bash
cd grace_rebuild
py minimal_backend.py
```

**Expected output:**
```
============================================================
Starting Grace Minimal Backend
============================================================
API: http://localhost:8000
Docs: http://localhost:8000/docs
Press CTRL+C to stop
============================================================

[OK] Cognition router loaded
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test it works:**
- Open browser: http://localhost:8000/health
- Should show: `{"status":"ok","message":"Minimal backend running"}`

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd grace-frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Test it works:**
- Open browser: http://localhost:5173
- Should show Grace Cognition Dashboard
- If backend running, shows metrics
- If backend not running, shows connection error message

---

## Step 3: Test CLI (Terminal 3)

```bash
cd grace_rebuild
py cli_test.py status
```

**Expected output:**
```
============================================================
GRACE COGNITION STATUS
============================================================

Overall Metrics:
  Health:     79.3%
  Trust:      75.3%
  Confidence: 73.0%
  SaaS Ready: NO

Domain Status (8 domains):
  core            90.0%
  transcendence   83.0%
  knowledge       89.0%
  security        47.8%
  ml              61.4%
  ...

============================================================
```

---

## What Each Component Does

### Backend (`minimal_backend.py`)
- Runs on http://localhost:8000
- Provides metrics API
- Cognition status endpoint
- No complex dependencies
- Just works

### Frontend (`grace-frontend`)
- Runs on http://localhost:5173
- React + Vite
- Connects to backend API
- Shows cognition dashboard
- Auto-refreshes every 5 seconds

### CLI (`cli_test.py`)
- Command line interface
- Fetches data from backend
- Shows status in terminal
- Simple and fast

---

## Troubleshooting

### Backend won't start

**Error: Port already in use**
```bash
netstat -ano | findstr :8000
taskkill /F /PID <pid>
```

**Error: Module not found**
```bash
py -m pip install fastapi uvicorn
```

---

### Frontend won't start

**Error: Command not found**
```bash
npm install
```

**Error: Cannot connect to backend**
- Check backend is running on :8000
- Check CORS is enabled
- Check firewall

---

### CLI shows connection error

**Error: Backend not running**
- Start backend first: `py minimal_backend.py`
- Verify: http://localhost:8000/health

---

## Quick Status Check

**All running:**
```
✓ Terminal 1: Backend on :8000
✓ Terminal 2: Frontend on :5173  
✓ Terminal 3: CLI ready
✓ Browser: http://localhost:5173 shows dashboard
✓ Browser: http://localhost:8000/docs shows API
```

**Success:** Backend + Frontend + CLI all connected!

---

## Files Created

**Backend:**
- `grace_rebuild/minimal_backend.py` - Simple working backend
- `grace_rebuild/demo_working_metrics.py` - Standalone demo

**Frontend:**
- `grace-frontend/src/api/graceApi.ts` - API client
- `grace-frontend/src/components/CognitionDashboard.tsx` - Dashboard component
- `grace-frontend/src/styles/cognition.css` - Styles
- `grace-frontend/src/App.tsx` - Main app

**CLI:**
- `grace_rebuild/cli_test.py` - Simple CLI

**Documentation:**
- `START_EVERYTHING.md` - This guide

---

## Next Steps

After getting all 3 running:

1. **Publish real metrics** - Wire into domain code
2. **Add more UI components** - Task board, knowledge explorer
3. **Add WebSocket** - Live updates
4. **Expand CLI** - More commands

---

**Start now:** Open 3 terminals and run the 3 start commands above.
