# GRACE - Complete System

## Single Command Start

```bash
python serve.py
```

**That's it!** Everything starts from `serve.py`

---

## What serve.py Does

1. ✅ Finds available port (8000, 8001, 8002...)
2. ✅ Boots minimal Grace systems
3. ✅ Loads Remote Access
4. ✅ Loads Autonomous Learning
5. ✅ Starts API server
6. ✅ Shows you the port number

---

## Quick Start Options

### Option 1: Command Line
```bash
python serve.py
```

### Option 2: Double-Click
- `START.cmd`
- `RUN.cmd`
- `START_FIXED.cmd`

All run `serve.py`

### Option 3: VS Code
Press `F5` or Run > Start Debugging

---

## After Server Starts

You'll see:
```
✅ Using port 8000

GRACE IS READY
📡 API: http://localhost:8000
📖 Docs: http://localhost:8000/docs
❤️  Health: http://localhost:8000/health
```

### Then in Terminal 2:

**1. Configure clients (one time):**
```bash
python auto_configure.py
```

**2. Use Grace:**
```bash
# Remote Access
python remote_access_client.py setup
python remote_access_client.py shell

# Autonomous Learning
python start_grace_now.py

# Interactive Menu
USE_GRACE.cmd
```

---

## Features

### Remote Access (Zero-Trust)
- Device registration with MFA
- RBAC enforcement (5 roles)
- Complete session recording
- WebSocket real-time shell
- Suspicious activity detection

**15+ API endpoints at `/api/remote/*`**

### Autonomous Learning
- 11 knowledge domains
- 25+ learning projects
- Project-based learning
- Sandbox experimentation
- KPI tracking with trust scores

**Priority Projects:**
- CRM System (Salesforce-like)
- E-commerce Analytics SaaS
- Cloud Infrastructure from Scratch

**8+ API endpoints at `/api/learning/*`**

---

## Troubleshooting

### Port Already in Use?
serve.py automatically finds next available port!

### Still Having Issues?
```bash
# Kill specific port
kill_port_8001.cmd

# Test integration
python test_integration.py

# Check server
python check_server.py
```

---

## File Organization

| File | Purpose |
|------|---------|
| `serve.py` | **Main entry point** (use this!) |
| `auto_configure.py` | Auto-configure clients |
| `remote_access_client.py` | Remote shell client |
| `start_grace_now.py` | Start learning |
| `USE_GRACE.cmd` | Interactive menu |
| `test_integration.py` | Test everything |

---

## API Documentation

Once running: http://localhost:8000/docs

**Key Endpoints:**
- `/health` - System health
- `/api/remote/*` - Remote access
- `/api/learning/*` - Autonomous learning
- `/docs` - OpenAPI docs

---

## Complete Workflow

**Terminal 1:**
```bash
python serve.py
```
(Wait for "GRACE IS READY")

**Terminal 2:**
```bash
python auto_configure.py
python remote_access_client.py setup
python remote_access_client.py shell
```

Now you have a live remote shell with zero-trust security!

**Or use learning:**
```bash
python start_grace_now.py
```

Grace starts building real projects (CRM, e-commerce, etc.)

---

## What Got Fixed

✅ **Single entry point** - Everything from serve.py  
✅ **Auto port detection** - No more port conflicts  
✅ **Minimal boot** - No timeouts  
✅ **Import fixes** - All dependencies resolved  
✅ **Remote access** - Fully wired and working  
✅ **Autonomous learning** - Complete curriculum ready  

---

## Success Looks Like

```
================================================================================
GRACE - STARTING
================================================================================

Finding available port...
✅ Using port 8000

[1/3] Booting core systems...
  ✓ Message Bus: Active
  ✓ Immutable Log: Active

[2/3] Loading Grace backend...
  ✓ Backend loaded
  ✓ Remote Access: Ready
  ✓ Autonomous Learning: Ready

[3/3] System check...
  ✓ 45 API endpoints registered

================================================================================
GRACE IS READY
================================================================================

📡 API: http://localhost:8000
📖 Docs: http://localhost:8000/docs
❤️  Health: http://localhost:8000/health

Press Ctrl+C to stop
================================================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then Grace is running! ✅

---

**Everything starts from: `python serve.py`** 🚀

That's the only command you need to remember!
