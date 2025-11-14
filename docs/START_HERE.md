# 🚀 START GRACE - Single Command

## One Command to Start Everything

```bash
cd C:\Users\aaron\grace_2
python serve.py
```

That's it! This starts the **complete Grace system** with:

✅ All 12 kernels  
✅ Unified orchestrator  
✅ Comprehensive API (60+ endpoints)  
✅ Factory pattern routes  
✅ Log watcher service  
✅ Event bus  
✅ Self-healing engine  
✅ Coding agent integration  
✅ Automation rules  

---

## What Gets Loaded

When you run `python serve.py`, it loads `backend.unified_grace_orchestrator:app` which includes:

### Core Grace System
- All 12 domain kernels
- Elite systems (self-healing, coding agent)
- Mission control
- Parliament engine
- Temporal reasoning

### New Comprehensive API
- Events API (`/events/*`)
- Automation API (`/automation/*`)
- Patches API (`/patches/*`)
- System metrics
- Self-healing with code escalation

### Services
- **Log Watcher**: Monitors errors in real-time
- **Event Bus**: Pub/sub for service communication
- **Playbook Engine**: 6 pre-packaged playbooks
- **Coding Bridge**: Self-healing → coding agent

---

## Access Points

Once started:

- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:5173 (start separately)

---

## Health Check Shows Everything

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "platform": "Windows",
  "imports_successful": true
}
```

---

## Test All Features

### Quick Tests
```bash
# Test comprehensive API
curl http://localhost:8000/self-healing/stats

# Test events
curl http://localhost:8000/events/stats

# Test automation
curl http://localhost:8000/automation/rules

# Test patches
curl http://localhost:8000/patches/stats
```

### Comprehensive Test Suite
```bash
python test_factory_comprehensive.py
```

Expected: **25/25 tests passing**

### Patch Workflow Demo
```bash
DEMO_PATCH_WORKFLOW.bat
```

---

## Frontend Startup

In a **separate terminal**:

```bash
cd frontend
npm run dev
```

Then access: http://localhost:5173

---

## What's Integrated

### ✅ Original Grace Features
- All existing routes and kernels
- Database integrations
- WebSocket connections
- Metrics and monitoring

### ✅ New Comprehensive Features
- Clean factory API architecture
- Real-time log monitoring
- Event-driven automation
- Self-healing → coding agent workflow
- Patch tracking system
- Comprehensive UI layout

### ✅ No Conflicts
- Factory routes registered alongside existing routes
- Services run in parallel
- No circular imports
- Clean separation of concerns

---

## Verify Services Are Running

Check health endpoint for service status:

```bash
curl http://localhost:8000/events/stats
```

Should show:
- Event bus subscribers active
- Events in history
- Subscription types

---

## Stop Grace

Just press **Ctrl+C** in the terminal where `serve.py` is running.

All services shut down gracefully:
- Grace orchestrator stops
- Log watcher stops  
- Event bus clears
- Database connections close

---

## Troubleshooting

### Port Already in Use
```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Wait 2 seconds
ping 127.0.0.1 -n 3 >nul

# Restart
python serve.py
```

### Check Logs
The console shows all logs in real-time. Look for:
- ✅ marks = success
- ❌ marks = failures
- Service startup messages

### Test Individual Endpoints
```bash
# Test if API is responding
curl http://localhost:8000/health

# Test specific domain
curl http://localhost:8000/self-healing/stats
curl http://localhost:8000/librarian/status
curl http://localhost:8000/automation/rules
```

---

## Files Reference

### Main Startup
- `serve.py` - Main launcher (runs unified_grace_orchestrator)

### Backend
- `backend/unified_grace_orchestrator.py` - Complete system orchestration
- `backend/api/*` - 9 clean domain routers
- `backend/services/*` - Shared services (log watcher, event bus, etc.)

### Tests
- `test_factory_comprehensive.py` - 25 comprehensive tests
- `DEMO_PATCH_WORKFLOW.bat` - Patch workflow demo

### Documentation
- `FINAL_SUMMARY.md` - Complete system overview
- `SELF_HEALING_CODE_PATCH_COMPLETE.md` - Patch system details
- `CLEAN_ARCHITECTURE_FINAL.md` - Architecture guide

---

## Summary

**Single command starts everything:**
```bash
python serve.py
```

**All features integrated:**
- Complete Grace system ✅
- Comprehensive API ✅
- Real-time monitoring ✅
- Event automation ✅
- Self-healing with code patches ✅

**No duplication, no conflicts, one unified system!** 🎉
