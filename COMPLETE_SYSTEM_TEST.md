# Grace Memory Studio - Complete System Test 🧪

## 🎯 Automated Testing Suite

Run comprehensive tests to verify all components are working.

---

## 🚀 Quick Test (30 Seconds)

### Method 1: Run Test Script
```bash
python test_memory_workspace.py
```

**This tests:**
- ✓ All 35+ API endpoints
- ✓ Memory file operations
- ✓ Grace autonomous actions
- ✓ Ingestion pipelines
- ✓ Search functionality
- ✓ Complete CRUD workflow

**Expected output:**
```
✓ Logged in successfully
✓ Memory Status - 200
✓ List Files - 200
✓ Grace Categories - 200
✓ Research saved
✓ Insight saved
✓ Action log retrieved
...
TEST SUITE COMPLETE
```

### Method 2: Run Examples
```bash
python grace_memory_examples.py
```

**This demonstrates:**
- ✓ Grace saving research
- ✓ Grace detecting patterns
- ✓ Grace organizing files
- ✓ Complete learning pipeline
- ✓ Contradiction detection
- ✓ Training data preparation

---

## 🧪 Manual Testing Checklist

### Test 1: Backend Health
```bash
# Check server
curl http://localhost:8000/docs
# ✓ Should show Swagger UI

# Check categories
curl http://localhost:8000/api/grace/memory/categories
# ✓ Should return 10 categories

# Check status
curl http://localhost:8000/api/memory/status
# ✓ Should return active status
```

### Test 2: Grace Categories
```bash
# Check if folders created
ls grace_training/
```

**Should show:**
```
research/
learning/
code/
documentation/
conversations/
domain_knowledge/
configuration/
immutable_logs/
crypto/
insights/
```

**Check READMEs:**
```bash
cat grace_training/research/README.md
```

Should be auto-generated with category description.

### Test 3: File Operations
```bash
# Create test file
curl -X POST "http://localhost:8000/api/memory/file?path=test.txt&content=Hello"

# Read it back
curl "http://localhost:8000/api/memory/file?path=test.txt"

# Should return content

# Delete it
curl -X DELETE "http://localhost:8000/api/memory/file?path=test.txt"
```

### Test 4: Grace Actions
```bash
# Grace saves research
curl -X POST http://localhost:8000/api/grace/memory/research \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Finding",
    "content": "Test content",
    "domain": "ml",
    "tags": ["test"]
  }'

# Check action log
curl http://localhost:8000/api/grace/memory/actions?limit=10

# Should show recent action
```

### Test 5: Pipelines
```bash
# List pipelines
curl http://localhost:8000/api/ingestion/pipelines

# Should return 6 pipelines

# Get metrics
curl http://localhost:8000/api/ingestion/metrics

# Should return job statistics
```

### Test 6: Search
```bash
# Search for content
curl "http://localhost:8000/api/memory/search?query=test&limit=10"

# Should return search results

# Get search stats
curl http://localhost:8000/api/memory/search/stats

# Should return index statistics
```

---

## 🎨 UI Testing

### Test 1: Access Memory Studio
```
1. Open: http://localhost:5173
2. Login: admin / admin123
3. Click: "📁 Memory" button
```

**Should see:**
- ✓ 4 tabs at top (Workspace, Pipelines, Dashboard, Grace Activity)
- ✓ Can switch between tabs
- ✓ No errors in console (F12)

### Test 2: Workspace Tab
```
1. Click "Workspace" tab
2. Look for file tree on left
3. Look for editor on right
```

**Should see:**
- ✓ File tree with categories (if backend restarted)
- ✓ Monaco editor placeholder
- ✓ Action buttons at bottom (File, Folder, Upload, Refresh)

### Test 3: Upload a File
```
1. Click "Upload" button
2. Select a .txt file
3. Watch upload progress
```

**Should see:**
- ✓ Progress bar appears
- ✓ File appears in tree
- ✓ Can click to open
- ✓ Content shows in Monaco

### Test 4: Grace Activity Tab
```
1. Click "Grace Activity" tab
2. Wait 5 seconds (auto-refresh)
```

**Should see:**
- ✓ List of Grace's actions
- ✓ Icons for each action type
- ✓ Timestamps (e.g., "2m ago")
- ✓ File paths
- ✓ Sync status

### Test 5: Pipelines Tab
```
1. Click "Pipelines" tab
```

**Should see:**
- ✓ Left: Pipeline library (6 workflows)
- ✓ Right: Active jobs panel
- ✓ Each pipeline shows stages, file types

### Test 6: Dashboard Tab
```
1. Click "Dashboard" tab
```

**Should see:**
- ✓ 4 metric cards (Total, Complete, Running, Failed)
- ✓ Pipeline usage chart
- ✓ Recent jobs list

---

## 🔍 Integration Testing

### Test: End-to-End Workflow
```
1. Upload document.txt to Workspace
   ↓
2. Grace auto-analyzes (quality score, tags)
   ↓
3. Grace auto-categorizes (moves to appropriate folder)
   ↓
4. Click Pipelines → Start "Text to Embeddings"
   ↓
5. Watch progress bar fill to 100%
   ↓
6. Grace saves results to learning/embeddings/
   ↓
7. Check Grace Activity - see all actions
   ↓
8. Search for "document" - find it instantly
   ↓
9. Check Dashboard - metrics updated
```

**All steps work?** ✅ **System is fully operational!**

---

## 📊 Performance Testing

### Load Test: Multiple Uploads
```python
# Upload 10 files simultaneously
for i in range(10):
    requests.post(
        "http://localhost:8000/api/memory/file",
        params={"path": f"test_{i}.txt", "content": f"Content {i}"}
    )

# Check all created
response = requests.get("http://localhost:8000/api/memory/files")
# Should show 10 new files
```

### Load Test: Multiple Pipelines
```python
# Start 5 pipelines
for i in range(5):
    requests.post(
        "http://localhost:8000/api/ingestion/start",
        json={
            "pipeline_id": "text_to_embeddings",
            "file_path": f"test_{i}.txt"
        }
    )

# Check all running
response = requests.get("http://localhost:8000/api/ingestion/jobs")
# Should show 5 jobs
```

---

## 🐛 Common Test Failures & Fixes

### Failure: "404 Not Found"
**Cause:** Backend not restarted after code changes
**Fix:**
```bash
# Restart backend
python -m uvicorn backend.main:app --reload --port 8000
```

### Failure: "401 Unauthorized"
**Cause:** Not logged in or token expired
**Fix:**
```bash
# Login again
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}'
```

### Failure: "Connection refused"
**Cause:** Backend not running
**Fix:**
```bash
# Start backend
python -m uvicorn backend.main:app --reload --port 8000
```

### Failure: "Module not found"
**Cause:** Missing dependencies
**Fix:**
```bash
pip install -r backend/requirements.txt
```

### Failure: Frontend blank
**Cause:** Frontend not restarted
**Fix:**
```bash
cd frontend
npm run dev
# Then hard refresh: Ctrl+Shift+R
```

---

## ✅ Success Criteria

### All tests pass when:

**Backend:**
- [x] Server starts without errors
- [x] All endpoints return 200 or 422 (not 404)
- [x] Categories auto-created
- [x] READMEs generated
- [x] Can create/read/update/delete files
- [x] Grace can save research/insights
- [x] Pipelines can be started
- [x] Search returns results

**Frontend:**
- [x] Loads without errors
- [x] All 4 tabs render
- [x] Can switch between tabs
- [x] File tree displays
- [x] Monaco editor works
- [x] Upload button functional
- [x] Grace Activity feed populates

**Integration:**
- [x] File upload → appears in tree
- [x] Pipeline start → shows progress
- [x] Grace action → appears in feed
- [x] Search → finds files
- [x] Metrics → display correctly

---

## 🎯 Automated Deployment

### Use Deployment Script
```powershell
.\deploy_memory_studio.ps1
```

**This script:**
1. ✓ Checks prerequisites (Python, Node)
2. ✓ Installs all dependencies
3. ✓ Creates grace_training/ folder
4. ✓ Starts backend server
5. ✓ Starts frontend server
6. ✓ Verifies API endpoints
7. ✓ Runs test suite
8. ✓ Displays status summary

**Outputs:**
```
================================================================
                 DEPLOYMENT COMPLETE!
================================================================

Services Running:
  - Backend:  http://localhost:8000
  - Frontend: http://localhost:5173
  - API Docs: http://localhost:8000/docs

Next Steps:
  1. Open browser: http://localhost:5173
  2. Login: admin / admin123
  3. Click: 📁 Memory button
  4. Explore: 4 tabs
```

---

## 📈 Test Results Interpretation

### All Green (✓) = Perfect
```
✓ Memory Status - 200
✓ Grace Categories - 200
✓ Pipelines - 200
✓ Research saved
✓ File created
...
```
**Action:** Deploy to production!

### Some Red (✗) = Needs Attention
```
✓ Memory Status - 200
✗ Grace Categories - 404
✓ Pipelines - 200
```
**Action:** Restart backend, check logs

### All Red (✗) = Major Issue
```
✗ Cannot connect to server
✗ All endpoints failing
```
**Action:** Check if backend is running, verify port 8000

---

## 🎉 Post-Test Actions

### If All Tests Pass
1. ✅ Mark deployment as successful
2. ✅ Open Memory Studio UI
3. ✅ Start using the platform
4. ✅ Monitor Grace Activity feed
5. ✅ Check Dashboard metrics

### If Some Tests Fail
1. Review error messages
2. Check documentation for fixes
3. Restart services
4. Re-run tests
5. Verify success

### Next Steps
1. Upload real files
2. Configure automations
3. Let Grace learn
4. Monitor analytics
5. Prepare for production

---

## 📚 Additional Tests

### Test: Grace Learning Loop
```bash
# 1. Have conversation with Grace
# 2. Check if conversation saved
curl http://localhost:8000/api/grace/memory/actions | grep conversation

# 3. Check for generated insights
ls grace_training/insights/patterns/

# 4. Verify sync to Memory Fusion
# (Check Fusion logs)
```

### Test: Automation
```bash
# 1. Create schedule
curl -X POST http://localhost:8000/api/ingestion/schedules -d '{...}'

# 2. List schedules
curl http://localhost:8000/api/ingestion/schedules

# 3. Wait for trigger time
# 4. Check jobs created
curl http://localhost:8000/api/ingestion/jobs
```

### Test: Search Performance
```bash
# 1. Upload 100 files
# 2. Index all files
# 3. Run search query
# 4. Measure response time

# Should be < 1 second for 100 files
```

---

## ✅ Final Verification

Run this complete verification sequence:

```bash
# 1. Run automated tests
python test_memory_workspace.py

# 2. Run Grace examples
python grace_memory_examples.py

# 3. Check file system
ls grace_training/
ls grace_training/research/
ls grace_training/insights/

# 4. Test UI
# Open http://localhost:5173
# Click all 4 tabs
# Upload a file
# Check Grace Activity

# 5. Verify sync (if Memory Fusion available)
# Check Fusion status
# Verify files synced
```

**All pass?** 🎉 **You're production-ready!**

---

**Status:** 🟢 COMPREHENSIVE TEST SUITE READY  
**Test Coverage:** Backend, Frontend, Integration, Grace AI  
**Automation:** Deployment script available  
**Documentation:** Complete testing guide  

Run `python test_memory_workspace.py` to verify everything! 🚀
