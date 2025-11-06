# Next Steps - Get CLI and Localhost Running

**Goal:** Test everything working together - Backend API + Frontend UI + CLI

---

## Current Situation

**What's ready:**
- ✅ Backend code written (minimal_backend.py)
- ✅ Frontend components created
- ✅ CLI test script created
- ✅ All files organized

**What's not tested:**
- ❌ Backend never successfully started and tested
- ❌ Frontend never connected to backend
- ❌ CLI never connected to running backend
- ❌ No end-to-end flow verified

---

## Option 1: Quick Win - Get Backend Running (15 minutes)

**Goal:** Just get the backend API responding so you can test with browser and CLI

### Steps:

1. **Kill any running Python processes**
   ```bash
   taskkill /F /IM python.exe
   ```

2. **Start minimal backend**
   ```bash
   py minimal_backend.py
   ```
   Should see:
   ```
   Starting Grace Minimal Backend
   API: http://localhost:8000
   INFO: Uvicorn running on http://127.0.0.1:8000
   ```

3. **Test in browser** (new terminal)
   ```
   http://localhost:8000/health
   http://localhost:8000/api/status
   http://localhost:8000/docs
   ```

4. **Test with CLI**
   ```bash
   py scripts\cli_test.py status
   ```

5. **Publish test metrics**
   ```bash
   py scripts\demo_working_metrics.py
   ```
   Then refresh http://localhost:8000/api/status to see metrics

**Time:** 15 minutes  
**Benefit:** Backend API working, can test all endpoints  
**Next:** Connect frontend

---

## Option 2: Full Stack - Backend + Frontend (30 minutes)

**Goal:** Get both backend and frontend running and connected

### Steps:

1. **Start backend** (Terminal 1)
   ```bash
   py minimal_backend.py
   ```
   Wait for: "Uvicorn running on http://127.0.0.1:8000"

2. **Test backend works** (Terminal 2)
   ```bash
   py -c "import httpx; print(httpx.get('http://localhost:8000/health').json())"
   ```
   Should show: `{'status': 'ok', 'message': 'Minimal backend running'}`

3. **Start frontend** (Terminal 2)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Wait for: "Local: http://localhost:5173/"

4. **Open in browser**
   ```
   http://localhost:5173
   ```
   Should show CognitionDashboard with domain metrics

5. **Test CLI**
   ```bash
   py scripts\cli_test.py status
   ```

**Time:** 30 minutes (includes npm install)  
**Benefit:** Full UI working, visual dashboard  
**Next:** Wire real metrics into domain code

---

## Option 3: Debug Session - Fix All Blockers (1-2 hours)

**Goal:** Methodically fix every startup issue until everything runs perfectly

### Steps:

1. **Create debug log script**
   ```python
   # debug_startup.py
   import sys
   sys.path.insert(0, '.')
   
   print("Testing backend startup...")
   try:
       from backend.metrics_server import app
       print("✓ Metrics server imports")
   except Exception as e:
       print(f"✗ Error: {e}")
   
   try:
       import uvicorn
       print("✓ Uvicorn available")
   except:
       print("✗ Install: pip install uvicorn")
   
   # Test each component
   ```

2. **Run debug script**
   ```bash
   py debug_startup.py
   ```

3. **Fix each error one by one**
   - Missing dependencies → install
   - Import errors → fix imports
   - Port conflicts → change ports
   - Database errors → recreate DB

4. **Once clean, start everything**

**Time:** 1-2 hours  
**Benefit:** Everything working robustly  
**Next:** Production deployment

---

## Option 4: Standalone First - No Server Needed (5 minutes)

**Goal:** See metrics system working immediately without any server

### Steps:

1. **Run working demo**
   ```bash
   py scripts\demo_working_metrics.py
   ```

2. **See output:**
   ```
   Publishing metrics from all 9 domains...
   [OK] 17 metrics published
   
   Overall Health:     79.3%
   Overall Trust:      75.3%
   Domains tracked:    8
   
   Report generated: 2475 characters
   ```

3. **Integrate into your code** (example)
   ```python
   # your_code.py
   from backend.metric_publishers import OrchestratorMetrics
   
   async def my_task():
       result = do_work()
       await OrchestratorMetrics.publish_task_completed(True, 0.95)
       return result
   ```

**Time:** 5 minutes  
**Benefit:** Metrics working now, can integrate today  
**Limitation:** No API, no UI, no CLI - just programmatic

---

## Option 5: CLI-First Approach (20 minutes)

**Goal:** Get CLI working with lightweight backend

### Steps:

1. **Create ultra-minimal backend**
   ```python
   # tiny_backend.py
   from fastapi import FastAPI
   import sys
   sys.path.insert(0, '.')
   
   app = FastAPI()
   
   @app.get("/health")
   def health():
       return {"status": "ok"}
   
   @app.get("/api/status")
   def status():
       from backend.cognition_metrics import get_metrics_engine
       return get_metrics_engine().get_status()
   
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=8000)
   ```

2. **Start it**
   ```bash
   py tiny_backend.py
   ```

3. **Test CLI immediately**
   ```bash
   py scripts\cli_test.py status
   ```

4. **Build from there**

**Time:** 20 minutes  
**Benefit:** Simple, debuggable, CLI works fast  
**Next:** Expand backend features incrementally

---

## Recommended Path (My Suggestion)

### Phase 1: Option 4 + Option 5 (25 minutes)

**Why:** Get something working immediately, then build up

1. **First 5 min:** Run standalone demo to prove metrics work
   ```bash
   py scripts\demo_working_metrics.py
   ```

2. **Next 20 min:** Get tiny backend + CLI working
   - Create tiny_backend.py (5 min)
   - Start and test (5 min)
   - Test CLI connects (5 min)
   - Publish metrics and verify (5 min)

**Result:** Working CLI + API in 25 minutes

### Phase 2: Add Frontend (15 minutes)

3. **Start frontend**
   ```bash
   cd frontend
   npm install  # May take 5 min
   npm run dev
   ```

4. **Open browser:** http://localhost:5173

**Result:** Full stack working in 40 minutes total

---

## What Each Option Gets You

| Option | Time | Backend | Frontend | CLI | Complexity |
|--------|------|---------|----------|-----|------------|
| **Option 1** | 15min | ✅ API | ❌ | ✅ | Low |
| **Option 2** | 30min | ✅ API | ✅ UI | ✅ | Medium |
| **Option 3** | 2hr | ✅ Robust | ✅ Tested | ✅ Tested | High |
| **Option 4** | 5min | ❌ | ❌ | ❌ | Very Low |
| **Option 5** | 20min | ✅ Minimal | ❌ | ✅ | Low |
| **Recommended** | 40min | ✅ Full | ✅ Full | ✅ Full | Medium |

---

## Immediate Commands to Try

### Test Metrics System (Works Right Now - No server)
```bash
py scripts\demo_working_metrics.py
```

### Start Minimal Backend
```bash
py minimal_backend.py
```

### Test Backend is Running (New terminal)
```bash
py -c "import httpx; print(httpx.get('http://localhost:8000/health').json())"
```

### Test CLI
```bash
py scripts\cli_test.py status
```

### Start Frontend
```bash
cd frontend
npm run dev
```

---

## My Recommendation

**Start with Option 4, then Option 1, then Option 2:**

1. Run `py scripts\demo_working_metrics.py` (5 min)
   - Proves metrics work
   - No dependencies
   - Immediate feedback

2. Start `py minimal_backend.py` (10 min)
   - Get API running
   - Test with browser
   - Test with CLI

3. Start frontend `cd frontend && npm run dev` (15 min)
   - Full visual dashboard
   - Real-time updates
   - Complete experience

**Total: 30 minutes to fully working system**

---

## What Do You Want to Do?

**A.** Quick win - Just get backend API running (Option 1 - 15 min)  
**B.** Full stack - Backend + Frontend + CLI (Option 2 - 30 min)  
**C.** Debug everything - Make it bulletproof (Option 3 - 2 hours)  
**D.** Standalone demo - See it work now (Option 4 - 5 min)  
**E.** CLI-focused - Get CLI working first (Option 5 - 20 min)  
**F.** Recommended path - Build up incrementally (40 min)  

**Choose a letter and I'll execute that path step by step.**
