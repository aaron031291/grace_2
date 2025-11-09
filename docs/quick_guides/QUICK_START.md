# ⚡ Grace Quick Start

## 🚀 One Command to Rule Them All

```powershell
.\RUN_GRACE.ps1
```

That's it! This will:
1. ✅ Test environment
2. ✅ Test all kernels  
3. ✅ Boot complete system
4. ✅ Run until you press Ctrl+C

---

## 📋 Prerequisites

**Required:**
- Windows 10/11
- Python 3.10+
- Node.js 18+ (for frontend)

**Setup (first time only):**
```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r backend\requirements.txt

# 4. Install frontend deps (optional)
cd frontend
npm install
cd ..

# 5. Create .env from example
Copy-Item .env.example .env

# 6. Add your API keys to .env
notepad .env
```

---

## 🎯 What You Get

After running `.\RUN_GRACE.ps1`:

### Services
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173  
- **API Docs:** http://localhost:8000/docs

### 9 Intelligent Kernels
```bash
POST /kernel/memory       # 25 APIs - knowledge, storage
POST /kernel/core         # 47 APIs - system, interaction
POST /kernel/code         # 38 APIs - code gen, execution
POST /kernel/governance   # 50 APIs - policy, safety
POST /kernel/verification # 35 APIs - contracts, benchmarks
POST /kernel/intelligence # 60 APIs - ML, reasoning
POST /kernel/infrastructure # 38 APIs - monitoring, healing
POST /kernel/federation   # 18 APIs - external integrations
```

### 100+ Subsystems
- Agentic Layer
- Self-Healing  
- Coding Agent
- Web Learning
- Cognition
- Constitutional AI
- Parliament
- Temporal Reasoning
- Causal Graphs
- ...and more!

---

## 💡 Quick Examples

### Use a Kernel
```bash
curl -X POST http://localhost:8000/kernel/memory \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Find all documents about sales",
    "context": {}
  }'
```

### Check Health
```bash
curl http://localhost:8000/health
```

### Explore API
Open http://localhost:8000/docs

---

## 🛑 Stop Grace

Press **Ctrl+C** in the terminal

---

## ⚙️ Options

```powershell
# Skip tests (faster start)
.\RUN_GRACE.ps1 -SkipTest

# Backend only (no UI)
.\RUN_GRACE.ps1 -SkipFrontend

# Quick mode (no dependency updates)
.\RUN_GRACE.ps1 -QuickStart

# Show help
.\RUN_GRACE.ps1 -Help
```

---

## 📚 Learn More

- **Architecture:** See `README_KERNELS.md`
- **API Mapping:** See `KERNEL_API_AUDIT_COMPLETE.md`
- **Boot Details:** See `BOOT_README.md`

---

## 🆘 Troubleshooting

### Tests Fail
```powershell
# View detailed output
.\TEST_E2E_BOOT.ps1 -Verbose

# Check Python
.venv\Scripts\python.exe --version

# Reinstall dependencies
pip install -r backend\requirements.txt
```

### Backend Won't Start
```powershell
# Check logs
Get-Content logs\backend.log -Tail 50

# Test imports
python test_kernels_quick.py
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Use custom port
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

---

**That's it! You're ready to run Grace!** 🎉

```powershell
.\RUN_GRACE.ps1
```
