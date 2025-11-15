# GRACE - Autonomous AI System

**Version:** 2.0  
**Status:** Production Ready

---

## Quick Start

```bash
python serve.py
```

Or double-click: **START.cmd**

That's it! Everything starts from one command.

---

## What You Get

- ✅ **Remote Access** - Zero-trust secure shell with RBAC
- ✅ **Autonomous Learning** - 11 domains, 25+ projects
- ✅ **REST API** - Full API with documentation

---

## After Server Starts

**Terminal 1:** (serve.py running)
```
GRACE IS READY
📡 API: http://localhost:8000
📖 Docs: http://localhost:8000/docs
```

**Terminal 2:** Use Grace
```bash
# Remote Access
python remote_access_client.py setup
python remote_access_client.py shell

# Autonomous Learning
python start_grace_now.py

# Or use menu
USE_GRACE.cmd
```

---

## Repository Structure

```
grace_2/
├── serve.py              ← Start here!
├── START.cmd             ← Or double-click this
├── README.md             ← You are here
├── HOW_TO_USE_GRACE.txt  ← Quick guide
│
├── Client Tools (use after server starts)
│   ├── remote_access_client.py  ← Remote shell
│   ├── start_grace_now.py       ← Start learning
│   └── USE_GRACE.cmd            ← Interactive menu
│
├── backend/              ← Grace core code
│   ├── main.py           ← FastAPI app
│   ├── remote_access/    ← Remote access system
│   ├── learning_systems/ ← Autonomous learning
│   ├── routes/           ← API endpoints
│   └── ...
│
├── scripts/              ← Organized scripts
│   ├── startup/          ← Startup commands
│   ├── utilities/        ← Utility scripts
│   ├── test/             ← Test scripts
│   └── chaos/            ← Chaos testing
│
└── docs/                 ← All documentation
    ├── guides/           ← User guides
    ├── archive/          ← Old status docs
    └── ...
```

---

## Features

### Remote Access (Zero-Trust)
- Device registration with MFA
- 5 RBAC roles (observer, executor, developer, admin, grace_sandbox)
- Complete session recording
- WebSocket real-time shell
- Suspicious activity detection

**Endpoints:** `/api/remote/*`

### Autonomous Learning
- 11 knowledge domains (Programming, Cloud, ML/AI, Security, etc.)
- 25+ learning projects
- Builds real systems: CRM, E-commerce Analytics SaaS, Cloud Infrastructure
- Sandbox experimentation with edge case discovery
- KPI tracking and trust scores

**Priority Projects:**
1. **CRM System** - Salesforce-like platform
2. **E-commerce Analytics** - Market prediction, ad funnel optimization
3. **Cloud Infrastructure** - VM orchestrator, auto-scaler

**Endpoints:** `/api/learning/*`

---

## Key Files (Root Directory)

| File | Purpose |
|------|---------|
| `serve.py` | **Main entry point** - starts everything |
| `START.cmd` | Double-click to start |
| `README.md` | This file |
| `HOW_TO_USE_GRACE.txt` | Quick reference |
| `remote_access_client.py` | Remote shell client |
| `start_grace_now.py` | Learning starter |
| `USE_GRACE.cmd` | Interactive menu |

**Everything else is in subdirectories.**

---

## Documentation

**Quick Reference:**
- `HOW_TO_USE_GRACE.txt` - Simple steps

**Detailed Guides:** (in `docs/guides/`)
- `AUTONOMOUS_LEARNING_SYSTEM.md` - Complete learning docs
- `REMOTE_ACCESS_LIVE.md` - Remote access guide
- `README_FINAL.md` - Comprehensive system guide

**API Documentation:**
- http://localhost:8000/docs (when running)

---

## Troubleshooting

**Check if Grace is running:**
```bash
python scripts/utilities/check_server.py
```

**Port conflict?**
serve.py auto-detects available port!

**Need to configure clients?**
```bash
python scripts/utilities/auto_configure.py
```

---

## Project Organization

All files are now organized:
- ✅ **Root** - Only essential files (serve.py, START.cmd, clients, README)
- ✅ **docs/** - All documentation (guides, archives, specs)
- ✅ **scripts/** - All scripts (utilities, tests, chaos, startup)
- ✅ **backend/** - All code (routes, systems, kernels)
- ✅ **No duplicates** - One clear path for everything

---

## Development

**Start backend:**
```bash
python serve.py
```

**Run tests:**
```bash
python scripts/test/test_integration.py
```

**View logs:**
```bash
dir logs
```

---

## Summary

**One command to start:** `python serve.py`

**Clean structure:** Everything organized

**Full featured:**
- Remote access with zero-trust security
- Autonomous learning system
- Complete REST API

**No confusion:** One entry point, clear documentation

---

**Start now:** `python serve.py` 🚀
