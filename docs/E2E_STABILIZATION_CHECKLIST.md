# E2E Stabilization Checklist

## Status: IN PROGRESS

---

## Phase 1: Fix Imports & Dependencies ⏳

### Backend Core Files
- [x] `backend/metrics_service.py` - Added threading, logging, error handling
- [x] `backend/cognition_metrics.py` - Removed DB dependency
- [x] `backend/routers/cognition.py` - Fixed imports, removed DB deps
- [x] `backend/routers/core_domain.py` - Fixed imports, added error handling
- [ ] `backend/routers/transcendence_domain.py` - Remove DB deps (IN PROGRESS)
- [ ] `backend/routers/security_domain.py` - Remove DB deps (TODO)

### CLI Files
- [x] `cli/requirements.txt` - Created with httpx, rich, prompt_toolkit
- [ ] `cli/grace_unified.py` - Fix import paths (TODO)
- [ ] `cli/commands/cognition_status.py` - Add error handling (TODO)
- [ ] `cli/commands/domain_commands.py` - Add error handling (TODO)

---

## Phase 2: Remove All Database Dependencies from Routers 🔧

**Why:** New routers don't need DB - they call existing services

### Files to Fix:
1. **transcendence_domain.py** (50+ occurrences)
   - Remove: `db: Session = Depends(get_db)` from all 20+ functions
   - Remove: `from sqlalchemy.orm import Session`
   - Remove: `from backend.database import get_db`

2. **security_domain.py** (10+ occurrences)
   - Same as above

### Quick Fix Strategy:
```python
# BEFORE
async def my_endpoint(request: Model, db: Session = Depends(get_db)):
    ...

# AFTER
async def my_endpoint(request: Model):
    ...
```

---

## Phase 3: Add Comprehensive Error Handling ✅

### Pattern to Follow (from core_domain.py):
```python
@router.get("/endpoint")
async def my_endpoint():
    try:
        from ..module import thing
        result = await thing.do_work() if hasattr(thing, 'do_work') else default
    except Exception as e:
        logger.warning(f"Module not available: {e}")
        result = default
    
    await publish_metric("domain", "kpi", value)
    return {"status": "ok", "result": result}
```

### Apply to:
- [x] core_domain.py (DONE)
- [ ] transcendence_domain.py (TODO)
- [ ] security_domain.py (TODO)

---

## Phase 4: Test Backend Startup 🧪

### Steps:
1. Navigate to: `cd /c/Users/aaron/grace_2/grace_rebuild`
2. Start backend: `python -m uvicorn backend.main:app --reload`
3. Check for errors in startup
4. Verify routes registered: Check `/docs`

### Expected Output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Database initialized
✓ Grace API server starting...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Common Errors to Fix:
- [ ] Import errors
- [ ] Module not found
- [ ] Circular imports
- [ ] Missing dependencies

---

## Phase 5: Test API Endpoints 🔌

### Cognition Endpoints
```bash
curl http://localhost:8000/api/cognition/status
curl http://localhost:8000/api/cognition/readiness
```

**Expected:** Valid JSON with domain status

### Core Endpoints
```bash
curl http://localhost:8000/api/core/heartbeat
curl http://localhost:8000/api/core/governance
```

**Expected:** Valid JSON responses

### Transcendence Endpoints
```bash
curl -X POST http://localhost:8000/api/transcendence/plan \
  -H "Content-Type: application/json" \
  -d '{"task_description": "test", "context": {}}'
```

**Expected:** Task plan response

### Security Endpoints
```bash
curl -X POST http://localhost:8000/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"path": "./backend", "deep": false}'
```

**Expected:** Scan results

---

## Phase 6: Fix CLI Import Paths 📦

### Issue:
```python
# CURRENT (doesn't work)
from cli.commands.cognition_status import show_cognition_status

# SHOULD BE
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from commands.cognition_status import show_cognition_status
```

### Files to Fix:
- [ ] `cli/grace_unified.py`
- [ ] Test: `python cli/grace_unified.py cognition`

---

## Phase 7: Test CLI Commands 🖥️

### Prerequisites:
- Backend running
- CLI dependencies installed: `pip install -r cli/requirements.txt`

### Commands to Test:
```bash
cd cli

# Test cognition dashboard
python grace_unified.py cognition

# Test readiness
python grace_unified.py readiness

# Test core commands
python grace_unified.py core heartbeat
python grace_unified.py core governance

# Test transcendence
python grace_unified.py transcendence plan "test task"

# Test security
python grace_unified.py security scan ./backend
```

### Expected Results:
- Connects to backend
- Displays formatted output
- No crash on errors
- Graceful error messages if backend down

---

## Phase 8: E2E Metric Flow Test 🔄

### Test Flow:
1. **Publish metric** from API
```bash
curl -X POST http://localhost:8000/api/cognition/domain/core/update \
  -H "Content-Type: application/json" \
  -d '{"uptime": 0.99, "governance_score": 0.92}'
```

2. **Check cognition status**
```bash
curl http://localhost:8000/api/cognition/status
```

3. **Verify in CLI**
```bash
python grace_unified.py cognition
```

### Success Criteria:
- Metric appears in status
- Domain health updated
- CLI displays updated value

---

## Phase 9: Integration Testing 🧩

### Backend Integration
- [ ] All routers load without errors
- [ ] Metrics service initializes
- [ ] Cognition engine initializes
- [ ] No circular import issues
- [ ] All endpoints respond

### CLI Integration
- [ ] Connects to backend
- [ ] Displays cognition status
- [ ] Handles connection errors
- [ ] Shows formatted output

### Metric Integration
- [ ] Metrics publish successfully
- [ ] Aggregates update
- [ ] Benchmarks track
- [ ] Status API reflects changes

---

## Phase 10: Documentation & Cleanup 📚

- [ ] Update STABILITY_AUDIT.md with current status
- [ ] Create STABILITY_VERIFIED.md when complete
- [ ] Document any workarounds
- [ ] List known limitations
- [ ] Create quick-start guide for testing

---

## Current Status Summary

### ✅ Completed
1. metrics_service.py - Thread-safe, error handling
2. cognition_metrics.py - No DB dependency
3. routers/cognition.py - Clean imports
4. routers/core_domain.py - Error handling
5. cli/requirements.txt - Created

### 🔧 In Progress
1. Removing DB deps from transcendence_domain.py
2. Removing DB deps from security_domain.py

### ⏳ Todo
1. Fix CLI import paths
2. Test backend startup
3. Test all API endpoints
4. Test CLI commands
5. E2E testing
6. Documentation

---

## Estimated Time to Stability

**Current:** 40% complete  
**Remaining Work:** ~2 hours  
**ETA:** Stable system ready for testing

---

## Blocking Issues

### Critical (Must Fix Now)
1. **DB dependencies** in transcendence_domain.py - prevents startup
2. **DB dependencies** in security_domain.py - prevents startup

### Important (Fix Soon)
3. CLI import paths - CLI won't run
4. Missing error handling - will crash on errors

### Nice to Have (Fix Later)
5. Database persistence for metrics
6. WebSocket integration
7. Authentication on endpoints

---

## Quick Fix Commands

### Remove DB deps from transcendence_domain.py:
```bash
# Manual: Edit file and remove all "db: Session = Depends(get_db)"
# Automated: Run FIX_ALL_ROUTERS.py (if Python available)
```

### Test backend:
```bash
cd /c/Users/aaron/grace_2/grace_rebuild
python -m uvicorn backend.main:app --reload
```

### Test CLI:
```bash
cd cli
pip install -r requirements.txt
python grace_unified.py cognition --backend http://localhost:8000
```

---

## Success Metrics

System is stable when:
- ✅ Backend starts without errors
- ✅ All routes registered (/docs shows all endpoints)
- ✅ API endpoints return valid JSON
- ✅ CLI connects and displays status
- ✅ Metrics flow from API → Engine → CLI
- ✅ No crashes on missing modules
- ✅ Graceful error handling throughout

---

## Next Steps (Priority Order)

1. **Fix transcendence_domain.py** - Remove all DB deps (30 min)
2. **Fix security_domain.py** - Remove all DB deps (15 min)
3. **Test backend startup** - Verify no errors (10 min)
4. **Fix CLI imports** - Make CLI runnable (15 min)
5. **Test endpoints** - Verify all work (20 min)
6. **Test CLI** - End-to-end verification (20 min)
7. **Document** - Update status files (10 min)

**Total Estimated Time: ~2 hours to fully stable system**
