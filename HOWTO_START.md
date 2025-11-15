# How to Start Grace

## The Problem
- `serve.py` tries to boot 20+ complex kernels (times out)
- Import errors cause crashes
- Port conflicts

## The Solution
Use the fixed startup script!

---

## Quick Start (Recommended)

### Option 1: Auto-Fix and Start
```bash
START_FIXED.cmd
```
This will:
1. ✅ Check Python version
2. ✅ Create required directories
3. ✅ Test all imports
4. ✅ Start Grace automatically

### Option 2: Manual
```bash
python serve_fixed.py
```

### Option 3: With Pre-Check
```bash
python fix_and_start.py
```

---

## What You Get

Once running, Grace provides:

**Terminal 1** - Backend Running
```
Grace available at:
  📡 API: http://localhost:8000
  📖 Docs: http://localhost:8000/docs
  ❤️ Health: http://localhost:8000/health
```

**Terminal 2** - Start Learning
```bash
python start_grace_now.py
```

**Terminal 2** - Remote Access
```bash
python remote_access_client.py setup
python remote_access_client.py shell
```

---

## Files Explained

| File | Purpose |
|------|---------|
| `START_FIXED.cmd` | **Use this!** Auto-fix and start |
| `serve_fixed.py` | Minimal server (no complex boot) |
| `fix_and_start.py` | Check system health, then start |
| `quick_test.py` | Test imports only |
| `serve.py` | ❌ Original (too complex, times out) |
| `serve_simple.py` | Simple server (no checks) |

---

## Troubleshooting

### "Import errors"
Run:
```bash
python quick_test.py
```
This will show exactly what's failing.

### "Port 8000 in use"
Kill the process:
```bash
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### "Still won't start"
Use debug mode:
```bash
python serve_debug.py
```

---

## What Works Now

✅ **Remote Access**
- Zero-trust authentication
- RBAC enforcement
- Session recording
- WebSocket shell

✅ **Autonomous Learning**
- 11 knowledge domains
- 25+ projects
- CRM, E-commerce, Cloud infrastructure

✅ **API Endpoints**
- `/api/remote/*` - Remote access
- `/api/learning/*` - Learning system
- `/health` - Health check
- `/docs` - API documentation

---

## Recommended Workflow

**Terminal 1:**
```bash
START_FIXED.cmd
```
(Leave this running)

**Terminal 2:**
```bash
# Option A: Start learning
python start_grace_now.py

# Option B: Use remote access
python remote_access_client.py setup
python remote_access_client.py shell
```

---

## Success Looks Like

```
======================================================================
GRACE - STARTING
======================================================================

[1/3] Testing imports...
✅ Backend loaded successfully

[2/3] Checking routes...
✅ 45 API routes registered

Available APIs:
  • Remote Access: /api/remote/*
  • Learning: /api/learning/*
  • Health: /health
  • Docs: /docs

[3/3] Starting server...

Grace will be available at:
  📡 API: http://localhost:8000
  📖 Docs: http://localhost:8000/docs
  ❤️ Health: http://localhost:8000/health

Press Ctrl+C to stop
======================================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then Grace is running! ✅

---

**Just run: `START_FIXED.cmd`**
