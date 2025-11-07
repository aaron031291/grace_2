# GRACE Stack Validation Guide

## Overview

Systematic validation from dependencies through meta loop following the proper stack tier approach.

## 🏗️ Stack Tiers

```
Tier 5: Meta Loop / Observability
           ↑
Tier 4: Integration Tier (Frontend ↔ Backend)
           ↑
Tier 3: Service Tier (Backend API)
           ↑
Tier 2: Foundation (Tests, Linting, Migrations)
           ↑
Tier 1: Dependencies (pip, npm, .env)
```

---

## ✅ Tier 1: Dependencies

### 1.1 Python Dependencies
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Verify:**
```bash
pip list | findstr fastapi
pip list | findstr sqlalchemy
pip list | findstr alembic
```

**Expected:** All core packages installed

### 1.2 Frontend Dependencies
```bash
npm install --prefix frontend
```

**Verify:**
```bash
npm list --prefix frontend --depth=0
```

**Expected:** react, typescript, vite, etc.

### 1.3 Environment Configuration
```bash
# Check .env exists
if exist .env (echo .env found) else (echo WARNING: .env missing, using defaults)

# Sanity check critical vars
# SELF_HEAL_OBSERVE_ONLY=True
# SELF_HEAL_EXECUTE=False
```

**Create .env if missing:**
```bash
copy .env.example .env
```

**Checklist:**
- [ ] Python packages installed
- [ ] Frontend packages installed
- [ ] .env file present
- [ ] Critical settings configured

---

## ✅ Tier 2: Foundation Checks

### 2.1 Backend Tests (pytest)
```bash
# Run all tests
.\.venv\Scripts\pytest backend/tests -v

# Or run specific test suites
.\.venv\Scripts\pytest backend/tests/test_self_heal*.py -v
```

**Expected:**
- Tests pass or skip gracefully
- No import errors
- No syntax errors

### 2.2 Linting (ruff)
```bash
# Check code quality
.\.venv\Scripts\ruff check backend

# Auto-fix issues
.\.venv\Scripts\ruff check backend --fix
```

**Expected:**
- No critical errors
- Warnings acceptable
- Clean code style

### 2.3 Frontend Tests (npm)
```bash
# Run frontend tests (if configured)
npm test --prefix frontend -- --watch=false
```

**Expected:**
- Tests pass
- No build errors

### 2.4 Database Migrations
```bash
# Check current migration
.\.venv\Scripts\alembic current

# View migration history
.\.venv\Scripts\alembic history

# Apply migrations
.\.venv\Scripts\alembic upgrade head
```

**Expected:**
```
INFO  [alembic.runtime.migration] Running upgrade -> <revision>, <description>
```

**Verify single head:**
```bash
.\.venv\Scripts\alembic heads
# Should show single head, not multiple branches
```

**Checklist:**
- [ ] Tests run successfully
- [ ] Linting passes or warnings only
- [ ] Migrations applied
- [ ] Single migration head (no branches)

---

## ✅ Tier 3: Service Tier

### 3.1 Launch Backend
```bash
# Start with reload for development
.\.venv\Scripts\uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
✓ Database initialized
✓ Grace API server starting...
✓ Agentic memory broker started
✓ Meta-coordinated healing started
✓ Self-healing predictor started

GRACE AGENTIC SPINE FULLY OPERATIONAL

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 3.2 Health Endpoint Check
```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Grace API is running"
}
```

### 3.3 Background Jobs Verification

**Check logs for:**
```
✓ Trigger mesh started
✓ Health monitor started
✓ Task executor workers started
✓ Meta loop engine started
✓ Self-heal scheduler started
```

**Meta loop cycles:**
```
🔄 Meta Loop Cycle 1 - 14:30:00
  📋 Focus: routine_maintenance
  🛡️ Guardrails: maintain
```

**Self-heal predictor:**
```
  🔮 Prediction: <service> - <issue> (confidence: 0.85)
```

### 3.4 API Documentation
```
Open browser: http://localhost:8000/docs
```

**Verify:**
- [ ] Swagger UI loads
- [ ] New endpoints visible (/api/self_heal/learning, etc.)
- [ ] Can expand and view schemas

**Checklist:**
- [ ] Backend starts without errors
- [ ] Health endpoint responds
- [ ] Background jobs running
- [ ] Meta loop cycling
- [ ] API docs accessible

---

## ✅ Tier 4: Integration Tier

### 4.1 Start Frontend
```bash
# In new terminal
npm run dev --prefix frontend
```

**Expected:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 4.2 Key User Journeys

**Journey 1: View System Health**
```
1. Open http://localhost:5173
2. Navigate to health/monitoring
3. Should see system status
```

**Journey 2: Check Learning Analytics** (via API)
```bash
# Get learning data
curl http://localhost:8000/api/self_heal/learning?time_bucket=24h

# Get scheduler state
curl http://localhost:8000/api/self_heal/scheduler_counters

# Get meta focus
curl http://localhost:8000/api/meta/focus
```

### 4.3 WebSocket / Real-time Callbacks

**Check for WebSocket connections in logs:**
```
INFO: WebSocket connection established
INFO: Client connected to /ws/...
```

**If WebSocket configured:**
- [ ] Connection establishes
- [ ] Messages flow
- [ ] No disconnects

### 4.4 Frontend-Backend Integration

**Verify:**
- [ ] Frontend loads without errors
- [ ] API calls succeed
- [ ] CORS configured correctly
- [ ] Auth working (if applicable)

**Checklist:**
- [ ] Frontend starts successfully
- [ ] API endpoints accessible
- [ ] WebSocket connections (if applicable)
- [ ] User journeys work

---

## ✅ Tier 5: Meta Loop / Observability

### 5.1 Orchestration Scripts

**Check meta loop is running:**
```bash
# View backend logs, should see:
🔄 Meta Loop Cycle X - HH:MM:SS
  📋 Focus: <focus_area>
  🛡️ Guardrails: <adjustment>
```

**Verify via API:**
```bash
curl http://localhost:8000/api/meta/focus
```

**Expected:**
```json
{
  "current_cycle": {
    "cycle_id": "cycle_...",
    "focus_area": "routine_maintenance",
    "guardrail_adjustment": "maintain"
  }
}
```

### 5.2 Monitoring Hooks

**Check agentic memory is tracking:**
```python
# In Python REPL
from backend.agentic_memory import agentic_memory
stats = agentic_memory.get_stats()
print(stats)
```

**Expected:**
```python
{
    'total_requests': 0,
    'by_domain': {},
    'working_memory_size': 0,
    'patterns_learned': 0
}
```

### 5.3 Async Loops Running

**Check logs for periodic activity:**

**Meta loop:** Every 2 minutes
```
🔄 Meta Loop Cycle 1 - 14:30:00
🔄 Meta Loop Cycle 2 - 14:32:00
🔄 Meta Loop Cycle 3 - 14:34:00
```

**Self-heal predictor:** Every 30 seconds (if trends detected)
```
  🔮 Prediction: api_service - Latency Spike Predicted
```

**Log analyzer:** Every 60 seconds (if patterns detected)
```
  📜 Pattern: Recurring auth_validate errors (3x)
```

**Scheduler:** Every 30 seconds (if issues detected)
```
[self-heal:scheduler] Proposing playbook for service=api diagnosis=latency_spike
```

### 5.4 Cron / Scheduled Jobs

**Check for:**
- [ ] Meta loop cycles every 2min
- [ ] Predictorscan every 30sec
- [ ] Log analysis every 60sec
- [ ] Scheduler polls every 30sec

**All should run automatically via asyncio tasks**

**Checklist:**
- [ ] Meta loop cycling
- [ ] Monitoring hooks active
- [ ] Async loops running
- [ ] Logs show periodic activity

---

## 🎯 Full Validation Flow

### Quick Validation (5 minutes)
```bash
# Run automated script
.\scripts\validate_stack.ps1
```

### Manual Validation (15 minutes)

**Step-by-step:**
1. ✅ Install dependencies
2. ✅ Run tests & migrations
3. ✅ Start backend
4. ✅ Check health endpoint
5. ✅ Test new endpoints
6. ✅ Verify meta loop logs
7. ✅ Stop services

---

## 📊 Success Criteria

### Tier 1: Dependencies ✓
- Python packages installed
- Frontend packages installed
- .env configured

### Tier 2: Foundation ✓
- Tests pass (or skip)
- Linting clean
- Migrations applied
- Single migration head

### Tier 3: Service ✓
- Backend starts without errors
- Health endpoint responds
- Background jobs running
- API docs accessible

### Tier 4: Integration ✓
- Endpoints respond (or require auth)
- Frontend starts
- CORS working
- No integration errors

### Tier 5: Meta Loop ✓
- Meta loop cycles every 2min
- Predictor analyzes trends
- Log analyzer runs
- Scheduler polls services

---

## 🚀 Next Steps

### After Validation Passes

**Document Results:**
```markdown
# Create VALIDATION_RESULTS.md
- Date tested
- All tiers passed
- Any warnings noted
- System ready for: [pilot/sprint2/etc]
```

**Add Missing Tests:**
```python
# Add smoke tests for new features
tests/
├── test_learning_endpoint.py
├── test_scheduler_counters.py
├── test_meta_focus.py
└── test_governance_hardening.py
```

**Automate via CI:**
```yaml
# .github/workflows/validate.yml
name: Stack Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest backend/tests
      - run: alembic upgrade head
      - run: # ... rest of validation
```

---

## 🐛 Troubleshooting

### Backend won't start
- Check databases/ folder exists
- Run `alembic upgrade head`
- Check for port conflicts (8000)
- Review error logs

### Tests failing
- Check test database exists
- Verify imports work
- Check pytest.ini configuration
- Update test dependencies

### Migrations conflict
- Check `alembic heads` (should be single)
- If multiple heads: `alembic merge heads`
- Create new migration if needed

### Endpoints return 404
- Check feature flags (SELF_HEAL_OBSERVE_ONLY)
- Verify routes registered in main.py
- Check auth requirements

---

## 📋 Validation Checklist

**Before declaring "production-ready":**

- [ ] All dependencies installed
- [ ] Tests pass (or documented why skipped)
- [ ] Linting clean
- [ ] Migrations applied (single head)
- [ ] Backend starts and health responds
- [ ] All 6 new endpoints registered
- [ ] Meta loop cycles visible in logs
- [ ] Self-heal predictor running
- [ ] No errors in startup
- [ ] Frontend builds and runs
- [ ] Documentation complete

**When all checked:** System ready for production pilot! 🚀

---

**Use `scripts/validate_stack.ps1` for automated validation or follow manual steps above.**
