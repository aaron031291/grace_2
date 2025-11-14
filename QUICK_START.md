# GRACE - Quick Start Guide

**Version:** 2.0  
**Last Updated:** November 14, 2025

---

## 🚀 Starting GRACE

### Method 1: Manual Start (Recommended for Development)

Open **two terminals**:

#### Terminal 1: Backend
```bash
cd C:\Users\aaron\grace_2
python serve.py
```

Wait for: `✓ Grace backend started on http://localhost:8000`

#### Terminal 2: Frontend
```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

Wait for: `Local: http://localhost:5173/`

---

### Method 2: Auto-Restart (Production)

```bash
cd C:\Users\aaron\grace_2
scripts\startup\start_grace.cmd
```

This starts with:
- Auto-restart on crashes
- Process watchdog
- System service integration

---

## 🔍 Verifying System

### Check Status
```bash
scripts\startup\grace.cmd status
```

### Quick Test
```bash
python tests\e2e\FINAL_COMPLETE_TEST.py
```

Expected output:
```
[OK] Message bus started
[PASS] Message bus publishes events
[PASS] Infrastructure Manager
[PASS] Governance Kernel
[PASS] Memory Kernel
```

---

## 🌐 Accessing GRACE

Once both services are running:

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 🧪 Running Tests

### Core Systems Test
```bash
set PYTHONPATH=C:\Users\aaron\grace_2
python tests\e2e\test_core_simple.py
```

### Layer 1 Kernels Test
```bash
set PYTHONPATH=C:\Users\aaron\grace_2
python tests\e2e\test_clarity_kernel.py
python tests\e2e\test_librarian_kernel.py
```

### Full E2E Test (requires backend running)
```bash
python tests\e2e\test_multi_os_fabric_e2e.py
```

---

## 🛑 Stopping GRACE

### Manual Stop
Press `Ctrl+C` in both terminal windows

### Auto-Restart Stop
```bash
scripts\startup\stop_grace.cmd
```

Or:
```bash
scripts\startup\grace.cmd stop
```

---

## 📋 System Requirements

- **Python:** 3.11+
- **Node.js:** 18+
- **RAM:** 8GB+ recommended
- **Disk:** 20GB+ free space
- **OS:** Windows, Linux, macOS

---

## ⚙️ Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
copy .env.example .env
```

Required variables:
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///databases/grace.db
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Check port 8000:**
```bash
netstat -ano | findstr :8000
```

**Kill existing process:**
```bash
taskkill /F /PID <PID>
```

**Run diagnostics:**
```bash
python scripts\utilities\DIAGNOSE_BACKEND.py
```

### Frontend Won't Start

**Check port 5173:**
```bash
netstat -ano | findstr :5173
```

**Clear cache and reinstall:**
```bash
cd frontend
rmdir /s /q node_modules
npm install
npm run dev
```

### Database Corruption

**Rebuild database:**
```bash
del databases\grace_system.db
python -c "import sqlite3; conn = sqlite3.connect('databases/grace_system.db'); conn.execute('CREATE TABLE IF NOT EXISTS verification_events (id INTEGER PRIMARY KEY, event_type TEXT, timestamp TEXT, passed INTEGER DEFAULT 1)'); conn.commit(); conn.close()"
```

---

## 📚 Next Steps

- **Documentation:** See `docs/` folder
- **Architecture:** Read `docs/architecture/FINAL_COMPREHENSIVE_SYSTEM_DOCUMENT.md`
- **API Guide:** Visit http://localhost:8000/docs when backend is running
- **Complete Test Report:** See `E2E_TEST_REPORT_20251114.md`

---

## ✅ Verification Checklist

After starting GRACE, verify:

- [ ] Backend responds: http://localhost:8000/api/health
- [ ] Frontend loads: http://localhost:5173
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Quick test passes: `python tests\e2e\FINAL_COMPLETE_TEST.py`
- [ ] 16 kernels running (check status command)
- [ ] No errors in backend logs: `logs\backend.log`

---

**Need Help?**
- Check `docs/guides/` for detailed guides
- Review `README.md` for comprehensive documentation
- See `E2E_TEST_REPORT_20251114.md` for latest test results
