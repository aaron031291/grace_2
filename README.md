# GRACE - Autonomous AI System

**Version:** 2.0  
**Status:** Production Ready

---

## Start Grace (One Command)

```bash
python serve.py
```

Or double-click: **START.cmd**

---

## What You Get

- ✅ **Remote Access** - Zero-trust secure shell
- ✅ **Autonomous Learning** - 11 domains, 25+ projects  
- ✅ **Full REST API** - Complete documentation

---

## Quick Start

### Terminal 1: Start Server
```bash
python serve.py
```

Wait for: "GRACE IS READY" and note the port number

### Terminal 2: Configure & Use

**Configure (one time):**
```bash
python auto_configure.py
```

**Then choose:**

**Remote Access:**
```bash
python remote_access_client.py setup
python remote_access_client.py shell
```

**Autonomous Learning:**
```bash
python start_grace_now.py
```

**Interactive Menu:**
```bash
USE_GRACE.cmd
```

---

## Features

### 1. Remote Access (Zero-Trust)
- Device registration with hardware fingerprints
- Multi-factor authentication
- RBAC enforcement (5 roles: observer, executor, developer, admin, grace_sandbox)
- Complete session recording
- WebSocket real-time shell
- Suspicious activity detection

**API:** `/api/remote/*` (15+ endpoints)

### 2. Autonomous Learning
- 11 knowledge domains
- 25+ learning projects
- Builds real systems (CRM, e-commerce analytics, cloud infrastructure)
- Sandbox experimentation
- Edge case discovery
- KPI tracking with trust scores

**Priority Projects:**
- CRM System (Salesforce-like)
- E-commerce Analytics SaaS (market prediction, ad funnels)
- Cloud Infrastructure from Scratch (VM orchestrator, auto-scaler)

**API:** `/api/learning/*` (8+ endpoints)

---

## API Documentation

Once running: **http://localhost:8000/docs**

(Or whatever port serve.py tells you)

---

## Core Files

| File | Purpose |
|------|---------|
| `serve.py` | **ONLY way to start** (auto port detection) |
| `START.cmd` | Double-click to start |
| `auto_configure.py` | Configure clients for correct port |
| `remote_access_client.py` | Remote shell access |
| `start_grace_now.py` | Start autonomous learning |
| `USE_GRACE.cmd` | Interactive menu |
| `check_server.py` | Check if running |
| `test_integration.py` | Test everything |

---

## Troubleshooting

**Server won't start?**
```bash
python check_server.py  # See what's wrong
```

**Port conflict?**
serve.py automatically finds next available port!

**Already running?**
```bash
python check_server.py  # Shows which port
python auto_configure.py  # Updates clients
```

---

## Architecture

```
serve.py (Entry Point)
  ↓
  Finds available port
  ↓
  Boots minimal Grace systems
  ↓
  Loads backend/main.py
    ↓
    ├─ Remote Access API (/api/remote/*)
    │  ├─ Zero-trust gate
    │  ├─ RBAC enforcer
    │  ├─ Session manager
    │  └─ Session recorder
    │
    └─ Autonomous Learning API (/api/learning/*)
       ├─ Curriculum manager
       └─ Project builder
```

---

## What Grace Does

### Remote Access
1. Register device → Verify identity → MFA
2. Allowlist device → Assign RBAC role
3. Create session → Get token
4. Execute commands → All recorded
5. Full audit trail

### Autonomous Learning
1. Select project (CRM, e-commerce, cloud)
2. Create 5-phase plan
3. Implement in sandbox
4. Discover edge cases
5. Test solutions
6. Calculate KPIs & trust score
7. Record learnings
8. Master domain
9. Next project

---

## Success Looks Like

**Terminal 1:**
```
GRACE - STARTING
✅ Using port 8000

[1/3] Booting core systems...
  ✓ Message Bus: Active
  
[2/3] Loading Grace backend...
  ✓ Remote Access: Ready
  ✓ Autonomous Learning: Ready
  
GRACE IS READY
📡 API: http://localhost:8000
```

**Terminal 2:**
```bash
$ python start_grace_now.py

✅ Started: Full CRM System
Progress: 2.5%
Edge cases found: 1
Grace is learning!
```

---

## Documentation

- **This file** - Quick start
- `README_FINAL.md` - Complete details
- `HOW_TO_USE_GRACE.txt` - Simple guide
- `AUTONOMOUS_LEARNING_SYSTEM.md` - Learning docs
- `REMOTE_ACCESS_LIVE.md` - Remote access guide

---

## Summary

**One command starts everything:**
```bash
python serve.py
```

**Then use Grace for:**
- Secure remote shell access
- Autonomous learning (builds CRM, e-commerce SaaS, cloud infrastructure)
- Full API access

**No more confusion. One clear path.** 🚀

---

**Quick start:** `python serve.py`
