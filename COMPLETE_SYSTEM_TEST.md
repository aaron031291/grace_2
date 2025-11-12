# Grace Complete System Test Checklist

**Run these tests to verify everything works:**

---

## 🧪 Backend Tests

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","imports_successful":true,...}`

### 2. System Status
```bash
curl http://localhost:8000/api/status
```
**Expected:** `{"is_running":true,"domain_kernels":8,...}`

### 3. Clarity Framework
```bash
curl http://localhost:8000/api/clarity/status
curl http://localhost:8000/api/clarity/components
curl http://localhost:8000/api/clarity/events?limit=10
curl http://localhost:8000/api/clarity/mesh
```
**Expected:** JSON with event bus, manifest, mesh config

### 4. Domain Kernels
```bash
curl http://localhost:8000/api/kernels
```
**Expected:** `{"total_kernels":9,"kernels":[...]}`

### 5. Component APIs
```bash
curl http://localhost:8000/api/llm/status
curl http://localhost:8000/api/intelligence/status
curl http://localhost:8000/api/learning/status
curl http://localhost:8000/api/ingestion/status
```
**Expected:** JSON status for each component

### 6. Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Grace"}'
```
**Expected:** `{"response":"Echo: Hello Grace",...}`

### 7. API Documentation
**Visit:** http://localhost:8000/docs  
**Expected:** Swagger UI with all endpoints

---

## 🎨 Frontend Tests

### 1. Main Page Loads
**Visit:** http://localhost:5173  
**Expected:** ChatGPT-style sidebar with Grace Control Center

### 2. Sidebar Navigation
**Check Left Sidebar Shows:**
- Domain Kernels section (9 items with status dots)
- Functions section (9 items with status dots)
- Active item highlighted

### 3. Click Each Tab
**Domain Kernels:**
- Memory → Panel loads
- Core → Panel loads
- Code → Panel loads
- All 9 kernels clickable

**Functions:**
- Overview → System stats display
- Chat → Chat interface with input
- Clarity → Framework dashboard
- Ingestion → Task controls
- Learning → Learning status
- All 9 functions clickable

### 4. Real-Time Updates
- Leave on Overview tab
- Wait 5 seconds
- Stats should auto-refresh

### 5. Chat Functionality
- Click Chat in sidebar
- Type message
- Click Send
- Should see echo response

### 6. Ingestion Controls
- Click Ingestion
- See task form
- Try starting a task (optional)
- Check progress bars (if task running)

---

## 🔍 Integration Tests

### 1. Frontend → Backend Connection
**Open browser DevTools (F12) → Network tab**
- Navigate to Overview
- Should see requests to:
  - `/api/status` - 200 OK
  - `/api/clarity/status` - 200 OK

### 2. CORS Working
**No CORS errors in console**
- Frontend at localhost:5173
- Backend at localhost:8000
- Should communicate without errors

### 3. Event Flow
- Click different tabs
- Check backend logs
- Should see API requests being logged

---

## 📊 Automated Tests

### 1. Clarity Framework
```bash
python -m pytest tests/test_clarity_framework.py -v
```
**Expected:** 15/15 passing

### 2. Smoke Tests
```bash
python scripts/test_clarity_smoke.py
```
**Expected:** 6/6 passing

### 3. Orchestrator Boot
```bash
python backend/unified_grace_orchestrator.py --dry-run --boot
```
**Expected:** "Grace booted successfully"

### 4. Frontend Build
```bash
cd frontend
npm run build
```
**Expected:** Build successful

---

## ✅ Success Criteria

**All Green:**
- [ ] Backend health returns healthy
- [ ] All 18 API endpoints respond
- [ ] Frontend loads ChatGPT-style UI
- [ ] Sidebar shows 18 items
- [ ] Clicking items changes panel
- [ ] Status dots are visible
- [ ] Chat works
- [ ] No console errors
- [ ] Real-time updates work
- [ ] All tests pass
- [ ] Build succeeds

**If all checkboxes pass:** Grace is fully operational! 🎉

---

## 🐛 Common Issues

### White Screen
- Hard refresh: `Ctrl+Shift+R`
- Check console for errors
- Restart dev server

### 404 Errors
- Backend not restarted with new code
- Restart: `python serve.py`

### Type Import Errors
- Dev server cache
- Restart: `Ctrl+C` then `npm run dev`

### CORS Errors
- Backend running on different port
- Check CORS config in orchestrator

---

**Run through this checklist to verify complete system integration!**
