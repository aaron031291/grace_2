# GRACE - General Recursive Autonomous Cognitive Engine

**Version:** 2.0  
**Status:** Production Ready  
**Repository:** Clean & Organized ✅

---

## Quick Start (3 Steps)

### 1. Start Ollama
```bash
ollama serve
```

### 2. Start Grace
```bash
python serve.py
```

### 3. Use Grace (Terminal 2)
```bash
python remote_access_client.py setup
python start_grace_now.py
```

---

## What serve.py Does Now

When you run `python serve.py`, it:

```
[1/5] Booting core systems...
  ✓ Message Bus: Active
  
[2/5] Loading open source LLMs...
  ✓ Ollama: Running
  ✓ Models available: 15
  ✓ Grace models installed: 15/15

  Installed models:
    • qwen2.5:32b - Conversation & reasoning
    • deepseek-coder-v2:16b - Best coding
    • deepseek-r1:70b - Complex reasoning (o1-level)
    • kimi:latest - 128K context
    • llava:34b - Vision + text
    ... and 10 more
    
[3/5] Loading Grace backend...
  ✓ Remote Access: Ready
  ✓ Autonomous Learning: Ready
  
[4/5] System check...
  ✓ 45 API endpoints registered
  
[5/5] Checking databases...
  ✓ 9 databases ready

GRACE IS READY
📡 API: http://localhost:8000
```

---

## Features

### 1. Open Source LLMs (15 Models)
**Automatically detected on boot!**

- **Conversation:** qwen2.5 (32B, 72B)
- **Coding:** deepseek-coder-v2, granite-code, codegemma
- **Reasoning:** deepseek-r1 (o1-level with thinking)
- **Vision:** llava (sees images)
- **Long context:** kimi (128K), command-r+
- **Fast:** phi3.5, gemma2, llama3.2, mistral-nemo
- **Uncensored:** dolphin-mixtral
- **Instructions:** nous-hermes2-mixtral

**Total:** ~313GB, all free, all private!

### 2. Remote Access (Zero-Trust)
- Device registration with MFA
- RBAC enforcement (5 roles)
- Complete session recording
- WebSocket real-time shell
- Suspicious activity detection

**API:** `/api/remote/*` (15+ endpoints)

### 3. Autonomous Learning
- 11 knowledge domains
- 25+ learning projects
- Builds real systems: CRM, E-commerce Analytics, Cloud Infrastructure
- Sandbox experimentation
- KPI tracking & trust scores

**API:** `/api/learning/*` (8+ endpoints)

---

## Install All Models

```bash
scripts/startup/install_all_models.cmd
```

This installs all 15 recommended models (~313GB, 2-3 hours).

Or install essentials only:
```bash
ollama pull qwen2.5:32b
ollama pull deepseek-coder-v2:16b  
ollama pull kimi:latest
```

See: `docs/guides/COMPLETE_MODEL_SETUP.md` for details

---

## Repository Structure (Organized!)

```
grace_2/
├── serve.py                    ← Start here! (checks all 15 models)
├── START.cmd                   ← Or this
├── README.md                   ← This file
├── HOW_TO_USE_GRACE.txt        ← Quick guide
│
├── Client Tools
│   ├── remote_access_client.py ← Remote shell
│   ├── start_grace_now.py      ← Learning
│   └── USE_GRACE.cmd           ← Menu
│
├── backend/                    ← All code
│   ├── main.py                 ← FastAPI app
│   ├── remote_access/          ← Zero-trust remote access
│   ├── learning_systems/       ← Autonomous learning
│   └── routes/                 ← API endpoints
│
├── scripts/                    ← All scripts organized
│   ├── startup/
│   │   └── install_all_models.cmd ← Install all 15 models
│   ├── utilities/
│   │   ├── check_server.py
│   │   └── auto_configure.py
│   ├── test/
│   └── chaos/
│
├── docs/                       ← Documentation
│   ├── guides/
│   │   ├── COMPLETE_MODEL_SETUP.md ← Model guide
│   │   ├── AUTONOMOUS_LEARNING_SYSTEM.md
│   │   └── REMOTE_ACCESS_LIVE.md
│   └── archive/                ← Historical docs (68 files)
│
├── databases/                  ← SQLite databases
├── logs/                       ← Runtime logs
├── frontend/                   ← React UI
└── tests/                      ← Test suites
```

---

## Usage

### Remote Access (Secure Shell)
```bash
# Terminal 1
python serve.py

# Terminal 2
python remote_access_client.py setup
python remote_access_client.py shell

# Now you have a secure remote shell!
remote@grace $ python --version
remote@grace $ echo "Hello Remote!"
remote@grace $ exit
```

### Autonomous Learning
```bash
# Terminal 1  
python serve.py

# Terminal 2
python start_grace_now.py

# Grace starts building:
# - CRM System
# - E-commerce Analytics SaaS
# - Cloud Infrastructure
```

### Interactive Menu
```bash
USE_GRACE.cmd

# Choose:
# 1. Remote Access
# 2. Learning
# 3. Test Integration
```

---

## What's Different Now

**Before:**
- ❌ 80+ files in root (chaos)
- ❌ 10+ ways to start
- ❌ No model checking
- ❌ Duplicates everywhere

**After:**
- ✅ 7 files in root (clean)
- ✅ ONE way to start (serve.py)
- ✅ **Auto-detects all 15 models**
- ✅ Shows install status on boot
- ✅ Everything organized

---

## Model Boot Check (New!)

Grace now checks for all 15 recommended models on boot:

**Installed:** Shows which models are available  
**Missing:** Tells you how to install them  
**Auto-routing:** Uses best model for each task  

This ensures Grace has maximum capabilities!

---

## API Documentation

http://localhost:8000/docs (when running)

**Key Endpoints:**
- `POST /api/remote/session/create` - Create secure session
- `WS /api/remote/shell/{token}` - WebSocket shell
- `POST /api/learning/project/start` - Start learning project
- `POST /api/learning/project/work` - Work on project

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start Grace | `python serve.py` |
| Install models | `scripts/startup/install_all_models.cmd` |
| Remote access | `python remote_access_client.py setup` |
| Learning | `python start_grace_now.py` |
| Check status | `python scripts/utilities/check_server.py` |
| Menu | `USE_GRACE.cmd` |

---

## Summary

**One command:** `python serve.py`

**Checks 15 models** on boot (auto-detects)

**Complete features:**
- Zero-trust remote access
- Autonomous learning system
- Full REST API

**Clean organization:** Everything in proper directories

**Start now:** `python serve.py` 🚀

---

See: `HOW_TO_USE_GRACE.txt` for detailed guide
