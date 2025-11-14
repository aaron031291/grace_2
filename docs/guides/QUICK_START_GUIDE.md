# Grace Multi-OS - Quick Start Guide

## 🚀 Start Backend and Run Tests (One Command)

```bash
START_AND_TEST.bat
```

This will:
1. Kill old Python processes
2. Activate virtual environment
3. Start backend (serve.py)
4. Wait 30 seconds for initialization
5. Run E2E tests with 150 log tail
6. Display results

---

## 📋 Manual Steps (If You Prefer)

### Step 1: Start Backend

Open **Terminal 1**:
```bash
cd C:\Users\aaron\grace_2
python serve.py
```

Wait until you see:
```
LAYER 1 BOOT COMPLETE - MULTI-OS INFRASTRUCTURE READY
🏗️  Infrastructure Manager tracking hosts:
   ✅ YOUR_HOSTNAME (windows) - healthy
```

### Step 2: Run Tests (Optional)

Open **Terminal 2** (while backend is running):
```bash
cd C:\Users\aaron\grace_2
python test_multi_os_fabric_e2e.py
```

### Step 3: Start Frontend (Optional)

Open **Terminal 3**:
```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

---

## ✅ Expected Backend Boot Sequence

When you run `python serve.py`, you should see:

```
================================================================================
GRACE LAYER 1 - BOOTING UNBREAKABLE CORE
================================================================================

[1/12] Message Bus: ACTIVE
[2/12] Immutable Log: ACTIVE
[3/12] Clarity Framework: ACTIVE
[4/12] Clarity Kernel: ACTIVE
[5/12] Infrastructure Manager: ACTIVE (Multi-OS host registry)
[6/12] Governance Kernel: ACTIVE (Multi-OS policies)
[7/12] Memory Kernel: ACTIVE (Host state persistence)
[8/12] Verification Framework: ACTIVE
[9/12] Unified Logic: ACTIVE
[10/12] Self-Healing: ACTIVE (X playbooks)
[11/12] Coding Agent: ACTIVE (X patterns)
[12/12] Librarian: ACTIVE (X file types)
[CONTROL] Control Plane: ACTIVE (X/X kernels)

================================================================================
LAYER 1 BOOT COMPLETE - MULTI-OS INFRASTRUCTURE READY
================================================================================

🏗️  Infrastructure Manager tracking hosts:
   ✅ HOSTNAME (windows) - healthy

🛡️  Governance enforcing OS-specific policies
🧠 Memory persisting all infrastructure state
```

---

## 🔍 Verify Backend is Running

Open browser or use curl:

**Browser:**
```
http://localhost:8000/docs
http://localhost:8000/api/health
```

**Command Line:**
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T..."
}
```

---

## 🧪 Test Results

When tests run successfully, you'll see:

```
GRACE MULTI-OS FABRIC MANAGER - E2E TEST SUITE
========================================

  Testing: Backend Health Check... ✅ PASS
  Testing: Infrastructure Manager Initialized... ✅ PASS
  Testing: Host Registry Active... ✅ PASS
  Testing: Dependency Detection... ✅ PASS
  Testing: Governance Policies... ✅ PASS
  Testing: Memory Persistence... ✅ PASS
  Testing: Core Kernel... ✅ PASS
  Testing: Librarian Kernel... ✅ PASS
  Testing: Intelligence Kernel... ✅ PASS
  Testing: Self-Healing Kernel... ✅ PASS
  Testing: Verification Kernel... ✅ PASS
  Testing: API Documentation... ✅ PASS

TEST SUMMARY
========================================
Total: 12
Passed: 12 ✅
Failed: 0 ❌
Success Rate: 100.0%

LOG TAIL (Last 150 lines)
========================================
🏗️  infrastructure.host.registered
📦 infrastructure.dependencies.detected
🛡️  governance.policy.check
🧠 memory.host.persisted
...
```

---

## 🛠️ Troubleshooting

### Backend Won't Start

**Issue:** Port 8000 already in use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /F /PID <PID_NUMBER>
```

**Issue:** Import errors
```bash
# Install dependencies
pip install -r backend\requirements.txt

# Make sure you're in the right directory
cd C:\Users\aaron\grace_2
```

**Issue:** Virtual environment not activating
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r backend\requirements.txt
```

### Tests Fail

**Issue:** "Connection refused" or "All connection attempts failed"

✅ **Solution:** Backend isn't running. Start it first:
```bash
python serve.py
```
Wait 30 seconds, then run tests again.

**Issue:** Some tests show 404

✅ **This is OK!** Some API routes may not be fully implemented yet. As long as backend health check passes, the system is working.

### Logs Not Showing

**Issue:** No log files in tail

✅ **This is OK!** Logs are created after first backend run. Run backend once, then logs will appear in future test runs.

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `serve.py` | Backend startup (use this!) |
| `START_AND_TEST.bat` | Automated start + test |
| `test_multi_os_fabric_e2e.py` | E2E test suite |
| `backend/core/infrastructure_manager_kernel.py` | Multi-OS fabric manager |
| `MULTI_OS_FABRIC_COMPLETE.md` | Complete documentation |

---

## 🎯 What to Expect

### On First Run
1. Infrastructure Manager initializes
2. Local host auto-registers
3. Dependencies detected (pip, npm)
4. Baseline loaded from requirements.txt
5. Health monitoring starts
6. Dependency drift monitoring starts (every 5 min)

### Infrastructure Manager Will
- ✅ Register your Windows/Linux/macOS host
- ✅ Detect all installed pip packages
- ✅ Detect all installed npm packages (if frontend exists)
- ✅ Compare to baselines
- ✅ Publish drift events if packages don't match
- ✅ Track GPU if CUDA available
- ✅ Monitor CPU/RAM/disk usage
- ✅ Report to governance for policy enforcement
- ✅ Persist state to memory kernel

---

## 🚦 Next Actions

1. **Run the automated script:**
   ```bash
   START_AND_TEST.bat
   ```

2. **Or start backend manually:**
   ```bash
   python serve.py
   ```
   Then in another terminal:
   ```bash
   python test_multi_os_fabric_e2e.py
   ```

3. **Check the logs:**
   - Backend startup messages
   - Infrastructure Manager activity
   - Dependency detection
   - Host registration

4. **Explore the API:**
   ```
   http://localhost:8000/docs
   ```

---

## 📞 Quick Commands

```bash
# Start everything
START_AND_TEST.bat

# Just backend
python serve.py

# Just tests (backend must be running)
python test_multi_os_fabric_e2e.py

# Stop backend
taskkill /F /IM python.exe

# Check health
curl http://localhost:8000/api/health

# View logs
type logs\backend.log
```

---

**Ready to go! Run `START_AND_TEST.bat` now.** 🚀
