# 🚀 Grace E2E Boot System

## Quick Start

### 1. Test Everything First
```powershell
.\TEST_E2E_BOOT.ps1
```
This will:
- ✅ Check environment
- ✅ Test Python imports
- ✅ Start backend temporarily
- ✅ Test all 9 kernel endpoints
- ✅ Verify all systems
- ✅ Report results

**Expected:** All tests pass ✅

---

### 2. Boot Complete System
```powershell
.\BOOT_GRACE_COMPLETE_E2E.ps1
```

This boots ALL Grace subsystems:
- Backend API (FastAPI)
- Frontend UI (Vite)
- 9 Domain Kernels (311+ APIs)
- Agentic Layer
- Self-Healing Systems
- Coding Agent
- Web Learning
- Monitoring & Logs

**Options:**
```powershell
# Skip frontend
.\BOOT_GRACE_COMPLETE_E2E.ps1 -SkipFrontend

# Quick start (skip dependency installs)
.\BOOT_GRACE_COMPLETE_E2E.ps1 -QuickStart

# Development mode
.\BOOT_GRACE_COMPLETE_E2E.ps1 -DevMode

# Custom ports
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000 -FrontendPort 4000
```

---

## What Gets Started

### Core Services
- ✅ Backend API Server (http://localhost:8000)
- ✅ Frontend UI (http://localhost:5173)
- ✅ API Documentation (http://localhost:8000/docs)

### 9 Domain Kernels
1. ✅ Memory Kernel (25 APIs) - `/kernel/memory`
2. ✅ Core Kernel (47 APIs) - `/kernel/core`
3. ✅ Code Kernel (38 APIs) - `/kernel/code`
4. ✅ Governance Kernel (50 APIs) - `/kernel/governance`
5. ✅ Verification Kernel (35 APIs) - `/kernel/verification`
6. ✅ Intelligence Kernel (60 APIs) - `/kernel/intelligence`
7. ✅ Infrastructure Kernel (38 APIs) - `/kernel/infrastructure`
8. ✅ Federation Kernel (18 APIs) - `/kernel/federation`
9. ✅ Base Kernel (Foundation)

### Subsystems
- ✅ Agentic Layer (Orchestrator, Planner, Subagents)
- ✅ Self-Healing (Scheduler, Runner, ML/DL, Log-based)
- ✅ Coding Agent (Code Healer, Generator, Architect)
- ✅ Web Learning (83+ domains, GitHub, YouTube, Reddit)
- ✅ Cognition (Loop Memory, Quorum Engine)
- ✅ Constitutional AI (Verifier, Engine)
- ✅ Parliament System
- ✅ Temporal Reasoning
- ✅ Causal Graph
- ✅ Monitoring & Logging

**Total:** 100+ subsystems managing 311+ APIs

---

## Health Checks

### After Boot, Verify:
```powershell
# Check backend health
curl http://localhost:8000/health

# Test a kernel
curl -X POST http://localhost:8000/kernel/memory `
  -H "Content-Type: application/json" `
  -d '{"intent": "What do you know?"}'

# View API docs
Start-Process "http://localhost:8000/docs"
```

---

## Monitoring

### View Logs:
```powershell
# Watch all logs
.\watch_all_logs.ps1

# Watch healing activity
.\watch_healing.ps1

# View specific logs
.\view_logs.ps1
```

### Visual Logs:
- **Ingestion Log:** `logs/ingestion.html` (clickable links!)
- **Terminal Log:** `logs/ingestion_visual.log`
- **Healing Log:** `logs/healing.log`

---

## Troubleshooting

### Backend Won't Start
```powershell
# Check Python
.venv\Scripts\python.exe --version

# Check dependencies
.venv\Scripts\pip list

# Check database
Test-Path "backend\grace.db"

# View backend output
Get-Job | Receive-Job
```

### Kernel Errors
```powershell
# Test kernel imports
python test_kernels_quick.py

# Check logs
Get-Content logs\backend.log -Tail 50
```

### Port Conflicts
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

---

## Stop Grace

**Ctrl+C** in the boot script terminal

Or manually:
```powershell
# Stop all jobs
Get-Job | Stop-Job
Get-Job | Remove-Job
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GRACE E2E SYSTEM                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │◄────────┤   Backend    │             │
│  │  (Vite UI)   │         │  (FastAPI)   │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                    ┌──────────────┴──────────────┐      │
│                    │                             │      │
│         ┌──────────▼──────────┐   ┌─────────────▼────┐ │
│         │  9 Domain Kernels   │   │  100+ Subsystems │ │
│         │  (311+ APIs)        │   │  (Autonomous)    │ │
│         │                     │   │                  │ │
│         │ • Memory            │   │ • Self-Healing   │ │
│         │ • Core              │   │ • Coding Agent   │ │
│         │ • Code              │   │ • Web Learning   │ │
│         │ • Governance        │   │ • Cognition      │ │
│         │ • Verification      │   │ • Parliament     │ │
│         │ • Intelligence      │   │ • Temporal       │ │
│         │ • Infrastructure    │   │ • Causal         │ │
│         │ • Federation        │   │ • Monitoring     │ │
│         │ • Base              │   │ • ...and more    │ │
│         └─────────────────────┘   └──────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Success Indicators

After boot, you should see:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ API docs accessible
- ✅ Health check returns "healthy"
- ✅ All 9 kernels responding
- ✅ Logs being written
- ✅ Monitoring windows open

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `.\TEST_E2E_BOOT.ps1` | Test everything |
| `.\BOOT_GRACE_COMPLETE_E2E.ps1` | Start full system |
| `.\watch_all_logs.ps1` | Monitor logs |
| `.\watch_healing.ps1` | Monitor healing |
| `Ctrl+C` | Stop system |

---

## Support

For issues:
1. Check `KERNEL_API_AUDIT_COMPLETE.md` - API mapping
2. Check `README_KERNELS.md` - Kernel usage
3. Check `KERNEL_ARCHITECTURE_COMPLETE.md` - Architecture
4. View logs in `logs/` directory

---

**🎉 Grace is ready to run!**
