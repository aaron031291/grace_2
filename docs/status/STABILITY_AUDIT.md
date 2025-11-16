# Grace E2E Stability Audit & Fix Plan

## Audit Date
Current status as of completion of 10-domain architecture

---

## Issues Found & Fixes Required

### 🔴 CRITICAL - Must Fix Now

#### 1. Import Errors in New Files
**Issue:** New routers may have incorrect imports
- `backend/routers/cognition.py`
- `backend/routers/core_domain.py`
- `backend/routers/transcendence_domain.py`
- `backend/routers/security_domain.py`

**Fix:** Verify all imports resolve correctly

#### 2. Database Dependencies
**Issue:** `cognition_metrics.py` requires database session but may not have correct imports
**Fix:** Add proper database imports and session management

#### 3. Missing Module References
**Issue:** Code references modules that may not exist as expected:
- `backend.governance.governance_engine`
- `backend.self_healing.health_monitor`
- `backend.hunter.hunter_engine`
- `backend.auto_quarantine.quarantine_manager`
- `backend.auto_fix.auto_fix_engine`

**Fix:** Verify these modules exist and have correct exports

#### 4. Circular Import Risks
**Issue:** Metrics service imported by routers, routers imported by main, main may import metrics
**Fix:** Ensure clean import hierarchy

---

### 🟡 IMPORTANT - Fix Soon

#### 5. CLI Import Paths
**Issue:** CLI tries to import from `cli.commands.*` which may not work
**Fix:** Update Python path or use relative imports correctly

#### 6. Async/Sync Mismatches
**Issue:** Some functions may be called with `await` that aren't async
**Fix:** Make all metric publishing properly async

#### 7. Missing Database Models
**Issue:** `cognition_metrics.py` uses DB but doesn't have models defined
**Fix:** Create proper database models or use in-memory only

#### 8. WebSocket Integration
**Issue:** Cognition status should push updates via WebSocket
**Fix:** Wire cognition updates to WebSocket manager

---

### 🟢 NICE TO HAVE - Future

#### 9. Persistence
**Issue:** Metrics are in-memory only
**Fix:** Add database persistence for metrics

#### 10. Authentication
**Issue:** New domain endpoints don't require auth
**Fix:** Add auth decorators to protected endpoints

---

## File-by-File Audit

### ✅ Clean Files (No Issues)
- `DOMAIN_ARCHITECTURE_MAP.md`
- `DOMAIN_WIRING_COMPLETE.md`
- `TRANSCENDENCE_COMPLETE_MAPPING.md`
- `TRANSCENDENCE_WIRED.md`
- `COGNITION_SYSTEM.md`
- `COGNITION_QUICKSTART.md`
- `COGNITION_DELIVERY_SUMMARY.md`
- `FINAL_DOMAIN_STATUS.md`

### 🔧 Needs Fixes

#### `backend/metrics_service.py`
**Issues:**
- No database imports (uses `Session` in type hints but doesn't import)
- `publish_metric` is async but collectors aren't thread-safe
- No error handling for failed publishes

**Fixes Required:**
```python
# Add at top
from typing import Optional
import asyncio
import logging

# Add error handling
logger = logging.getLogger(__name__)

# Make thread-safe
import threading
lock = threading.Lock()
```

#### `backend/cognition_metrics.py`
**Issues:**
- Imports `Session` from `sqlalchemy.orm` but never uses database
- `get_metrics_engine(db: Session)` requires DB but doesn't use it
- No persistence of benchmark windows

**Fixes Required:**
```python
# Remove unused DB parameter or actually use it
# Add persistence logic
# Add proper initialization
```

#### `backend/routers/cognition.py`
**Issues:**
- Import path may be wrong: `from backend.database import get_db`
- Should be: `from ..database import get_db`

**Fixes Required:**
```python
# Fix relative imports
from ..database import get_db
from ..cognition_metrics import get_metrics_engine
from ..metrics_service import get_metrics_collector, publish_metric
```

#### `backend/routers/core_domain.py`
**Issues:**
- References `governance_engine`, `health_monitor` as global objects
- These may not exist or may need proper imports
- No error handling

**Fixes Required:**
```python
# Import properly
from ..governance import get_governance_engine
from ..self_healing import get_health_monitor

# Add error handling
try:
    result = await health_monitor.run_health_check()
except AttributeError:
    # Fallback
    result = {"status": "ok"}
```

#### `backend/routers/transcendence_domain.py`
**Issues:**
- Long file with many imports that may fail
- References modules that may not have expected functions
- Missing import for `datetime`

**Fixes Required:**
```python
# Add missing import at top
from datetime import datetime

# Wrap all external calls in try/except
# Provide sensible defaults when modules don't exist
```

#### `backend/routers/security_domain.py`
**Issues:**
- Same as core_domain - references global objects
- `hunter_engine`, `quarantine_manager`, etc.

**Fixes Required:**
```python
# Use proper getter functions
# Add error handling
```

#### `cli/grace_unified.py`
**Issues:**
- Import paths assume package is installed
- `from cli.commands.cognition_status import show_cognition_status`
- Won't work unless CLI is installed as package

**Fixes Required:**
```python
# Use relative imports or sys.path manipulation
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from commands.cognition_status import show_cognition_status
```

#### `cli/commands/cognition_status.py`
**Issues:**
- Uses `httpx` which may not be in requirements.txt
- No fallback if backend is down

**Fixes Required:**
```python
# Add connection error handling
try:
    response = await client.get(...)
except httpx.ConnectError:
    console.print("[red]Backend not reachable[/red]")
    return
```

#### `cli/commands/domain_commands.py`
**Issues:**
- Same httpx issue
- No error handling

**Fixes Required:**
```python
# Add comprehensive error handling
```

---

## Missing Dependencies

### Python Packages
```
httpx          # Used by CLI for API calls
rich           # Used by CLI for display
prompt_toolkit # Used by enhanced CLI
```

### Missing Files
None - all referenced files exist

### Missing Functions
Need to verify these exist:
- `governance_engine.get_active_policies()`
- `health_monitor.run_health_check()`
- `hunter_engine.scan_path()`
- `quarantine_manager.quarantine()`
- `auto_fix_engine.fix()`
- `orchestrator.create_plan()`
- `generate_code()`
- `analyze_intent()`
- `search_patterns()`
- `architect_agent.review()`

---

## Integration Points to Test

### 1. Metrics Flow
```
Operation → publish_metric() → MetricsCollector → CognitionEngine → API → CLI
```

**Test:** Publish a metric and verify it appears in cognition status

### 2. API Endpoints
```
CLI → HTTP Request → FastAPI Router → Domain Logic → Response → CLI Display
```

**Test:** Call each endpoint and verify response

### 3. Database
```
Backend Startup → Create Tables → Initialize Engines → Ready
```

**Test:** Start backend without errors

### 4. WebSocket
```
Metric Update → WebSocket Push → Frontend/CLI Update
```

**Test:** WebSocket connections work

---

## Testing Plan

### Phase 1: Syntax & Import Validation ✅
1. Python syntax check all new files
2. Verify all imports resolve
3. Fix import errors

### Phase 2: Module Integration 🔧
1. Create missing getter functions
2. Add proper error handling
3. Ensure modules can be imported

### Phase 3: Backend Startup 🔧
1. Fix main.py integration
2. Start backend without errors
3. Verify all routes registered

### Phase 4: API Testing 🔧
1. Test each domain endpoint
2. Verify responses
3. Check metric publishing

### Phase 5: CLI Testing 🔧
1. Test CLI commands
2. Verify backend communication
3. Check dashboard display

### Phase 6: E2E Flow 🔧
1. Publish metrics from operation
2. Verify in cognition status
3. Check CLI dashboard updates
4. Test readiness report

---

## Success Criteria

### Backend Must:
- ✅ Start without errors
- ✅ Register all routers
- ✅ Connect to database
- ✅ Initialize metrics engine
- ✅ Respond to health check

### APIs Must:
- ✅ Return valid JSON
- ✅ Handle errors gracefully
- ✅ Publish metrics correctly
- ✅ Update cognition state

### CLI Must:
- ✅ Connect to backend
- ✅ Display cognition status
- ✅ Execute domain commands
- ✅ Show readiness report
- ✅ Handle connection errors

### Metrics Must:
- ✅ Publish successfully
- ✅ Aggregate correctly
- ✅ Track rolling windows
- ✅ Trigger at 90%
- ✅ Display in dashboard

---

## Fix Priority

### Immediate (Next 30 min)
1. Fix all import errors
2. Add error handling to routers
3. Make metrics_service thread-safe
4. Fix CLI import paths

### Soon (Next 1 hour)
5. Create getter functions for engines
6. Test backend startup
7. Verify all endpoints work
8. Test CLI commands

### Later (Next 2 hours)
9. Add database persistence
10. Wire WebSocket updates
11. Add authentication
12. Comprehensive testing

---

## Current Status: 🔴 UNSTABLE

**Estimated time to stability: 2-3 hours**

**Blocking issues:**
- Import errors prevent backend startup
- CLI can't run due to import issues
- Missing error handling will cause crashes
- No verification that external modules exist

**Next steps:**
1. Fix import errors (30 min)
2. Add error handling (30 min)
3. Test backend startup (15 min)
4. Test API endpoints (30 min)
5. Test CLI commands (30 min)
6. E2E testing (30 min)

---

## Fix Tracking

- [ ] metrics_service.py imports
- [ ] cognition_metrics.py database usage
- [ ] routers/cognition.py imports
- [ ] routers/core_domain.py error handling
- [ ] routers/transcendence_domain.py datetime import
- [ ] routers/security_domain.py error handling
- [ ] CLI import paths
- [ ] httpx dependency
- [ ] Create getter functions
- [ ] Test backend startup
- [ ] Test all endpoints
- [ ] Test CLI commands
- [ ] E2E verification
