# 🚀 START FULL GRACE SYSTEM - COMPLETE INSTRUCTIONS

## ⚡ COPY & PASTE THESE COMMANDS (In Order):

### Step 1: Stop Current Process
Press **Ctrl+C** in PowerShell

### Step 2: Install ALL Dependencies (One-Time)
```
cd C:\Users\aaron\grace_2
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r backend\requirements.txt
```

Wait 2-5 minutes for installation to complete.

### Step 3: Run FULL GRACE System
```
.\RUN_GRACE.ps1
```

---

## 🎯 What You'll Get:

The full system includes:
- ✅ **E2E Tests** - Tests environment & all 9 kernels
- ✅ **Backend** - http://localhost:8000 (FastAPI + all subsystems)
- ✅ **Frontend** - http://localhost:5173 (Vite UI)
- ✅ **9 Domain Kernels** - 311 APIs managed by AI agents
- ✅ **100+ Subsystems** - All autonomous systems
- ✅ **Monitoring** - Logs, healing, metrics

---

## 📋 What Happens When You Run It:

1. **Tests run first** (1-2 minutes)
   - Environment checks
   - Python imports
   - Kernel verification
   - API endpoint tests

2. **If tests pass** - Press any key to continue

3. **System boots** (30-60 seconds)
   - Backend starts with ALL subsystems
   - Frontend starts
   - Monitoring tools open
   - Logs begin

4. **System runs** until you press Ctrl+C

---

## ✅ Success Indicators:

You'll see:
```
[STARTUP] Beginning Grace initialization...
[OK] Database initialized
[OK] Grace API server starting...
[OK] Benchmark scheduler started
[OK] Self-heal scheduler started
[OK] Knowledge discovery scheduler started
[AI] ==================== ADVANCED AI SYSTEMS ====================
[OK] GRACE Agentic Spine activated
[AUTONOMOUS] 🔧 Code Healer started
[AUTONOMOUS] 📖 Log Healer started
[AUTONOMOUS] 🧠 ML/DL Healing started
[WEB-LEARNING] ✅ Web Learning Systems online
✓ Backend: Running | Frontend: Running
```

---

## 🌐 Access Grace:

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### Test a Kernel:
```powershell
curl -X POST http://localhost:8000/kernel/memory `
  -H "Content-Type: application/json" `
  -d '{"intent": "What do you know?"}'
```

---

## 🛑 Stop Full System:

Press **Ctrl+C** in the PowerShell window

---

## ⚙️ Options:

### Skip Tests (Faster Start):
```
.\RUN_GRACE.ps1 -SkipTest
```

### Backend Only (No UI):
```
.\RUN_GRACE.ps1 -SkipFrontend
```

### Quick Mode (No Dependency Updates):
```
.\RUN_GRACE.ps1 -QuickStart
```

### Combine Options:
```
.\RUN_GRACE.ps1 -SkipTest -QuickStart
```

---

## 🔧 If Installation Fails:

Try installing in parts:

```powershell
# Core dependencies
.venv\Scripts\pip install fastapi uvicorn sqlalchemy aiosqlite

# AI/ML dependencies
.venv\Scripts\pip install openai anthropic

# Web dependencies
.venv\Scripts\pip install aiohttp httpx requests beautifulsoup4

# Additional dependencies
.venv\Scripts\pip install pydantic pydantic-settings pyyaml python-dotenv

# Full install
.venv\Scripts\pip install -r backend\requirements.txt
```

---

## 🎉 READY TO RUN!

Just copy these 3 commands:

```powershell
cd C:\Users\aaron\grace_2
.venv\Scripts\pip install -r backend\requirements.txt
.\RUN_GRACE.ps1
```

**That's it!** Full system will start! 🚀
