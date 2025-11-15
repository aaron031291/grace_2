# GRACE - General Recursive Autonomous Cognitive Engine

**Version:** 2.0  
**Status:** Production Ready  
**Repository:** Clean & Organized

---

## Start Grace (One Command)

```bash
python serve.py
```

Or double-click: **START.cmd**

---

## Root Directory (Essential Files Only)

```
grace_2/
├── serve.py                    ← Start server (main entry point)
├── START.cmd                   ← Double-click to start
├── USE_GRACE.cmd               ← Interactive menu
├── README.md                   ← This file
├── HOW_TO_USE_GRACE.txt        ← Quick reference
├── remote_access_client.py     ← Remote shell client
└── start_grace_now.py          ← Learning starter
```

**Everything else is organized in subdirectories!**

---

## What Grace Does

### 1. Remote Access (Zero-Trust Secure Shell)
- Device registration with hardware fingerprints
- Multi-factor authentication
- RBAC enforcement (5 roles)
- Complete session recording
- WebSocket real-time shell
- Suspicious activity detection

**15+ API endpoints:** `/api/remote/*`

### 2. Autonomous Learning
- 11 knowledge domains
- 25+ learning projects
- Builds real systems from scratch

**Priority Projects:**
- **CRM System** - Salesforce-like platform
- **E-commerce Analytics SaaS** - Market prediction & ad funnels
- **Cloud Infrastructure** - VM orchestrator, auto-scaler, cost optimizer

**8+ API endpoints:** `/api/learning/*`

---

## Quick Start Guide

### Step 1: Start Server (Terminal 1)
```bash
python serve.py
```

Wait for:
```
GRACE IS READY
📡 API: http://localhost:8000
📖 Docs: http://localhost:8000/docs
```

### Step 2: Use Grace (Terminal 2)

**Option A - Remote Access:**
```bash
python remote_access_client.py setup
python remote_access_client.py shell

# Now you have a secure remote shell!
remote@grace $ python -c "print('Hello!')"
remote@grace $ dir
remote@grace $ exit
```

**Option B - Autonomous Learning:**
```bash
python start_grace_now.py

# Grace starts building real projects:
# - CRM System
# - E-commerce Analytics
# - Cloud Infrastructure
```

**Option C - Interactive Menu:**
```bash
USE_GRACE.cmd

# Choose from menu:
# 1. Remote Access
# 2. Learning
# 3. Test Integration
```

---

## Directory Organization

### backend/ - All Code
```
backend/
├── main.py                    ← FastAPI app
├── routes/                    ← API endpoints
│   ├── remote_session_api.py  ← Remote access API
│   └── autonomous_learning_api.py ← Learning API
├── remote_access/             ← Remote access system
│   ├── zero_trust_gate.py     ← Device verification
│   ├── rbac_enforcer.py       ← Permission system
│   ├── remote_session_manager.py ← Session management
│   └── session_recorder.py    ← Audit logging
└── learning_systems/          ← Autonomous learning
    ├── autonomous_curriculum.py ← 11 domains, 25+ projects
    └── project_builder.py      ← Project execution
```

### docs/ - All Documentation
```
docs/
├── guides/                    ← User guides (18 docs)
│   ├── AUTONOMOUS_LEARNING_SYSTEM.md
│   ├── REMOTE_ACCESS_LIVE.md
│   └── README_FINAL.md
└── archive/                   ← Historical docs (68 docs)
```

### scripts/ - All Scripts
```
scripts/
├── utilities/                 ← Utility scripts (8 files)
│   ├── auto_configure.py      ← Configure clients
│   └── check_server.py        ← Check status
├── test/                      ← Test scripts (6 files)
│   └── test_integration.py    ← Integration tests
├── chaos/                     ← Chaos testing (6 files)
└── startup/                   ← Startup commands (6 files)
```

### Other Directories
```
frontend/          ← React UI
tests/             ← Test suites
databases/         ← SQLite databases
logs/              ← Runtime logs
storage/           ← File storage
sandbox/           ← Sandbox environments
```

---

## API Endpoints

Once running: **http://localhost:8000/docs**

**Key Endpoints:**
- `GET /health` - System health
- `POST /api/remote/devices/register` - Register device
- `POST /api/remote/session/create` - Create session
- `POST /api/remote/execute` - Execute command
- `WS /api/remote/shell/{token}` - WebSocket shell
- `GET /api/learning/curriculum/overview` - Get curriculum
- `POST /api/learning/project/start` - Start project
- `POST /api/learning/project/work` - Work on project

---

## Utilities

**Check server status:**
```bash
python scripts/utilities/check_server.py
```

**Auto-configure clients:**
```bash
python scripts/utilities/auto_configure.py
```

**Run integration test:**
```bash
python scripts/test/test_integration.py
```

**Monitor Grace:**
```bash
python scripts/utilities/monitor_grace.py
```

---

## Configuration

**Environment:**
`.env` file (copy from `.env.example`)

**Databases:**
`databases/` - SQLite databases for Grace state

**Logs:**
`logs/` - All runtime logs
`logs/remote_sessions/` - Remote access recordings

---

## What Got Fixed

✅ **Removed duplicates** - 21 duplicate files deleted  
✅ **Organized structure** - Files in proper directories  
✅ **Single entry point** - Only serve.py  
✅ **Clean root** - 8 essential files  
✅ **Clear documentation** - One main README  
✅ **No confusion** - One way to do everything  

---

## Summary

**Root directory:** 8 essential files  
**Backend:** Clean organized code  
**Docs:** All in docs/ subdirectories  
**Scripts:** All in scripts/ subdirectories  

**One command:** `python serve.py`  
**One guide:** `README.md`  
**One start:** `START.cmd`

**The repository is now clean and organized!** 🎉

---

**Start Grace:** `python serve.py`

See: `HOW_TO_USE_GRACE.txt` for quick reference
