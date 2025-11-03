# Start and Test - Immediate Action Plan

**Current Status:** All code written, dependencies installed, 20/20 unit tests passing  
**Next:** Start backend and verify with real integration tests

---

## Step 1: Start Backend (NOW)

Open a terminal and run:

```bash
cd grace_rebuild
python -m backend.main
```

**Expected Output:**
```
✓ Database initialized
✓ Grace API server starting...
  Visit: http://localhost:8000/health
  Docs: http://localhost:8000/docs
✓ Benchmark scheduler started (evaluates every hour)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see errors:**
- Check if port 8000 is already in use
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check database file permissions

---

## Step 2: Run Integration Tests (2 minutes later)

Open a **SECOND terminal** and run:

```bash
cd grace_rebuild
python test_integration_real.py
```

**Expected Output:**
```
[1/10] Testing backend health... ✓
[2/10] Testing /api/cognition/status... ✓
[3/10] Testing /api/cognition/readiness... ✓
[4/10] Publishing test metrics... ✓
[5/10] Verifying metrics in API response... ✓
[6/10] Testing domain update endpoint... ✓
[7/10] Testing benchmark endpoint... ✓
[8/10] Testing report generation... ✓
[9/10] Testing database persistence... ✓
[10/10] Testing metrics collection service... ✓

Total Tests: 10
Passed: 10 ✓
Failed: 0 ✗

🎉 ALL INTEGRATION TESTS PASSED!
```

---

## Step 3: Verify in Browser (1 minute)

Open browser and visit:

1. **Health Check:**  
   http://localhost:8000/health
   
   Should show:
   ```json
   {"status":"ok","message":"Grace API is running"}
   ```

2. **Cognition Status:**  
   http://localhost:8000/api/cognition/status
   
   Should show JSON with:
   - `overall_health`
   - `domains` (10 domains)
   - `saas_ready`

3. **API Docs:**  
   http://localhost:8000/docs
   
   Should show interactive API documentation

---

## Step 4: Test CLI Commands (1 minute)

In a third terminal:

```bash
cd grace_rebuild

# Test status
grace cognition status

# Should show table with:
# - Overall Health
# - Overall Trust
# - Overall Confidence
# - SaaS Ready status
```

---

## If Everything Works (30 seconds to celebrate)

You have:
- ✅ Backend running
- ✅ APIs responding
- ✅ Database persisting
- ✅ Metrics flowing
- ✅ CLI working

**Next:** Wire metrics into actual domain code (ENTERPRISE_COMPLETION_PLAN.md)

---

## If Something Fails

### Backend won't start

**Error:** Port already in use
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Error:** Module not found
```bash
pip install -r requirements.txt
```

**Error:** Database locked
```bash
# Delete and recreate
del backend\grace.db
python -m backend.main
```

### Integration tests fail

**Backend not running:**
```
[1/10] Testing backend health... ✗
BACKEND NOT RUNNING
```
Solution: Start backend first (Step 1)

**Timeout errors:**
- Backend might be slow to start
- Wait 30 seconds and try again
- Check backend logs for errors

### CLI doesn't work

**Command not found:**
```bash
# Add to PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%
grace cognition status
```

---

## Success Metrics

After completing Steps 1-4, you should have:

| Metric | Target | Status |
|--------|--------|--------|
| Backend uptime | > 0 seconds | [ ] |
| API endpoints working | 7/7 | [ ] |
| Integration tests passing | 10/10 | [ ] |
| Database tables created | 5 tables | [ ] |
| CLI commands working | All | [ ] |

---

## Next Actions (After Steps 1-4)

1. **Keep backend running** in Terminal 1
2. **Run extended tests** in Terminal 2:
   ```bash
   # Test with actual domain operations
   python test_grace_simple.py
   ```
3. **Monitor metrics** in Terminal 3:
   ```bash
   grace cognition watch
   ```
4. **Begin domain integration** following ENTERPRISE_COMPLETION_PLAN.md

---

**START NOW:** Open terminal, run `python -m backend.main`
