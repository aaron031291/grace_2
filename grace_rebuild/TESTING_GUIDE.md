# Grace Testing Guide

Complete guide to verify Grace is working correctly.

---

## Quick Start Testing (5 minutes)

### Windows Users

#### Step 1: Verify Installation
```cmd
cd c:\Users\aaron\grace_2\grace_rebuild
python VERIFY_INSTALLATION.py
```

**Expected:** All checks pass ✓

#### Step 2: Start Backend
```cmd
START_GRACE.bat
```

**Expected:** 
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Step 3: Test API (new terminal)
```cmd
TEST_API.bat
```

**Expected:** All endpoints return JSON

#### Step 4: Test CLI (new terminal)
```cmd
cd cli
TEST_CLI.bat
```

**Expected:** Live dashboard displays

---

## Manual Testing

### Prerequisites

1. **Python 3.9+**
   ```cmd
   python --version
   ```

2. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Verify Code**
   ```cmd
   python VERIFY_INSTALLATION.py
   ```

---

## Backend Testing

### 1. Start Backend

```cmd
cd c:\Users\aaron\grace_2\grace_rebuild
python -m uvicorn backend.main:app --reload
```

**Success Indicators:**
- ✓ No import errors
- ✓ "Application startup complete"
- ✓ Listening on port 8000

**Common Issues:**
- Python not found → Install Python 3.9+
- Module not found → Run `pip install -r requirements.txt`
- Port in use → Kill process on 8000 or use `--port 8001`

### 2. Test Health Endpoint

```cmd
curl http://localhost:8000/health
```

**Expected:**
```json
{"status": "ok", "message": "Grace API is running"}
```

### 3. Test Cognition Status

```cmd
curl http://localhost:8000/api/cognition/status
```

**Expected:**
```json
{
  "timestamp": "2025-11-03T...",
  "overall_health": 0.87,
  "overall_trust": 0.85,
  "overall_confidence": 0.83,
  "saas_ready": false,
  "domains": {
    "core": {
      "domain_id": "core",
      "health": 0.95,
      "trust": 0.90,
      "confidence": 0.87,
      "kpis": {...}
    },
    ...
  }
}
```

### 4. Test Readiness Report

```cmd
curl http://localhost:8000/api/cognition/readiness
```

**Expected:**
```json
{
  "ready": false,
  "overall_health": 0.87,
  "benchmarks": {...},
  "domains": {...},
  "next_steps": [...]
}
```

### 5. Test Core Endpoints

```cmd
# Heartbeat
curl http://localhost:8000/api/core/heartbeat

# Governance
curl http://localhost:8000/api/core/governance

# Metrics
curl http://localhost:8000/api/core/metrics
```

### 6. Test Transcendence Endpoints

```cmd
# Plan a task
curl -X POST http://localhost:8000/api/transcendence/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"task_description\": \"build authentication\", \"context\": {}}"

# Get metrics
curl http://localhost:8000/api/transcendence/metrics
```

### 7. Test Security Endpoints

```cmd
# Scan
curl -X POST http://localhost:8000/api/security/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"path\": \"./backend\", \"deep\": false}"

# Get metrics
curl http://localhost:8000/api/security/metrics
```

### 8. Browse API Docs

Open browser: `http://localhost:8000/docs`

**Should see:**
- All endpoints listed
- Interactive testing interface
- 65+ endpoints total

---

## CLI Testing

### 1. Install CLI Dependencies

```cmd
cd cli
pip install httpx rich prompt_toolkit
```

### 2. Test Cognition Dashboard

```cmd
python grace_unified.py cognition
```

**Expected:**
- Live dashboard appears
- Shows all 10 domains
- Updates every 2 seconds
- Press Ctrl+C to exit

**Success Indicators:**
```
┌────────────────────────────────────────────┐
│        Grace Overall Cognition             │
│  Health      87%  ███████████████░░░      │
│  Trust       85%  ██████████████░░░░      │
│  Confidence  83%  █████████████░░░░░      │
└────────────────────────────────────────────┘
```

### 3. Test Readiness Report

```cmd
python grace_unified.py readiness
```

**Expected:**
```
Grace SaaS Readiness Report

┌────────────────┬─────────┬────────┬────────┐
│ Metric         │ Current │ Target │ Status │
├────────────────┼─────────┼────────┼────────┤
│ overall_health │ 87%     │ 90%    │ 🔧     │
│ overall_trust  │ 85%     │ 90%    │ 🔧     │
└────────────────┴─────────┴────────┴────────┘

Next Steps:
  1. Improve overall_health by 3% to reach 90%
  ...
```

### 4. Test Core Commands

```cmd
# Heartbeat
python grace_unified.py core heartbeat

# Governance
python grace_unified.py core governance

# Policies
python grace_unified.py core policies
```

### 5. Test Connection Error Handling

Stop backend, then run:
```cmd
python grace_unified.py cognition
```

**Expected:**
- Red error message
- "Backend not reachable"
- No crash

---

## End-to-End Metric Flow Test

### 1. Publish a Metric

```cmd
curl -X POST http://localhost:8000/api/cognition/domain/core/update ^
  -H "Content-Type: application/json" ^
  -d "{\"uptime\": 0.99, \"governance_score\": 0.95}"
```

### 2. Verify in API

```cmd
curl http://localhost:8000/api/cognition/status
```

**Expected:** core domain shows new values

### 3. Verify in CLI

```cmd
python grace_unified.py cognition
```

**Expected:** Dashboard shows updated metrics

---

## Performance Testing

### Metric Publishing Load Test

```python
# test_metrics_load.py
import asyncio
from backend.metrics_service import publish_metric

async def test_load():
    for i in range(1000):
        await publish_metric("test", "kpi", 0.9)
    print("Published 1000 metrics")

asyncio.run(test_load())
```

**Expected:** No errors, completes quickly

---

## Integration Testing

### Test All Domains

```python
# test_all_domains.py
import asyncio
import httpx

async def test_all_domains():
    async with httpx.AsyncClient() as client:
        domains = ['core', 'transcendence', 'security']
        
        for domain in domains:
            response = await client.get(
                f'http://localhost:8000/api/{domain}/metrics'
            )
            print(f"{domain}: {response.status_code}")
            assert response.status_code == 200

asyncio.run(test_all_domains())
```

---

## Troubleshooting

### Backend Won't Start

**Problem:** Import errors
**Solution:**
```cmd
pip install -r requirements.txt
python VERIFY_INSTALLATION.py
```

**Problem:** Port in use
**Solution:**
```cmd
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn backend.main:app --port 8001
```

**Problem:** Syntax errors
**Solution:**
```cmd
python VERIFY_INSTALLATION.py
# Will show exact line with error
```

### CLI Won't Connect

**Problem:** Backend not running
**Solution:**
```cmd
# Start backend first
START_GRACE.bat
```

**Problem:** Import errors
**Solution:**
```cmd
cd cli
pip install httpx rich prompt_toolkit
```

**Problem:** Can't find modules
**Solution:**
```cmd
# Run from cli directory
cd cli
python grace_unified.py cognition
```

### API Returns Errors

**Problem:** 500 Internal Server Error
**Solution:**
- Check backend logs for details
- Most errors are expected (modules not implemented yet)
- Should return default values

**Problem:** 404 Not Found
**Solution:**
- Check URL is correct
- Verify route is registered in /docs

---

## Success Checklist

Run through this checklist:

### Backend
- [ ] Backend starts without errors
- [ ] `/health` returns 200
- [ ] `/docs` shows all endpoints
- [ ] `/api/cognition/status` returns JSON
- [ ] `/api/core/heartbeat` returns alive
- [ ] No 500 errors on basic endpoints

### CLI
- [ ] CLI connects to backend
- [ ] `grace cognition` shows dashboard
- [ ] `grace readiness` shows report
- [ ] `grace core heartbeat` works
- [ ] Handles backend down gracefully

### Metrics
- [ ] Can publish metrics via API
- [ ] Metrics appear in status endpoint
- [ ] CLI reflects metric changes
- [ ] No crashes or errors

### Integration
- [ ] All domain routers load
- [ ] All endpoints respond
- [ ] Error handling works
- [ ] Logs show no critical errors

---

## Test Scripts Reference

| Script | Purpose | Location |
|--------|---------|----------|
| `VERIFY_INSTALLATION.py` | Check system setup | Root |
| `START_GRACE.bat` | Start backend | Root |
| `TEST_API.bat` | Test all API endpoints | Root |
| `TEST_CLI.bat` | Test CLI commands | cli/ |
| `TEST_SYSTEM.bat` | Full system test | Root |

---

## Expected Results Summary

### Working (Will Return Data)
- ✓ `/health`
- ✓ `/api/cognition/status`
- ✓ `/api/cognition/readiness`
- ✓ `/api/core/heartbeat`
- ✓ `/api/core/governance`
- ✓ `/api/core/metrics`
- ✓ `/api/transcendence/metrics`
- ✓ `/api/security/metrics`

### Functional (May Use Defaults)
- ⚠ `/api/transcendence/plan` - Returns plan structure
- ⚠ `/api/security/scan` - Returns scan structure
- ⚠ Most POST endpoints - Accept data, return success

### Normal Warnings
- "Module not available" in logs - OK, using fallbacks
- Default KPI values - OK, real values come from usage
- Some functions not implemented - OK, graceful fallback

---

## Next Steps After Testing

1. **If all tests pass:**
   - Start using Grace for development
   - Watch metrics accumulate
   - Monitor for 90% trigger

2. **If some tests fail:**
   - Check error messages
   - Run VERIFY_INSTALLATION.py
   - Review TROUBLESHOOTING section
   - Check documentation

3. **Ready for production:**
   - Add authentication
   - Add database persistence
   - Deploy to server
   - Set up monitoring

---

## Support

**Documentation:**
- STABILITY_ACHIEVED.md - Current status
- QUICK_FIX_GUIDE.md - Common issues
- COMPLETE_E2E_SUMMARY.md - Full overview

**Logs:**
- Backend logs show all operations
- Look for ERROR or CRITICAL messages
- WARNING messages are usually OK (using fallbacks)

**Testing:**
- Run VERIFY_INSTALLATION.py first
- Use TEST_API.bat for quick checks
- Use TEST_CLI.bat for CLI verification
