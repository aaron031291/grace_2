# 🚀 HOW TO START GRACE - 3 WAYS

## Choose Your Method:

---

## 1️⃣ PowerShell (RECOMMENDED) ⚡

### Copy this into PowerShell:
```powershell
cd C:\Users\aaron\grace_2
.\RUN_GRACE.ps1
```

### What happens:
1. ✅ Tests environment & kernels
2. ✅ Boots complete system  
3. ✅ Runs until Ctrl+C

### You get:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- 9 Kernels: `/kernel/*`
- 311 APIs: All available
- 100+ Subsystems: All running

---

## 2️⃣ Docker 🐳

### Copy this into PowerShell:
```powershell
cd C:\Users\aaron\grace_2
docker-compose -f docker-compose.complete.yml up
```

### What happens:
1. ✅ Builds/pulls Docker images
2. ✅ Starts containers
3. ✅ Runs until Ctrl+C

### You get:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Isolated environment
- Easy cleanup

### Stop:
```powershell
docker-compose -f docker-compose.complete.yml down
```

---

## 3️⃣ Kubernetes ☸️

### Copy this into PowerShell:
```powershell
cd C:\Users\aaron\grace_2\kubernetes
kubectl apply -f grace-complete-deployment.yaml
```

### What happens:
1. ✅ Creates namespace
2. ✅ Deploys 2 backend replicas
3. ✅ Deploys 2 frontend replicas
4. ✅ Creates services & volumes
5. ✅ Sets up auto-scaling

### Check status:
```powershell
kubectl get pods -n grace
kubectl get services -n grace
```

### Get URLs:
```powershell
kubectl get service grace-backend-service -n grace
```

### Stop:
```powershell
kubectl delete namespace grace
```

---

## 🎯 After Starting

### Test Backend:
```powershell
curl http://localhost:8000/health
```

### Test a Kernel:
```powershell
curl -X POST http://localhost:8000/kernel/memory `
  -H "Content-Type: application/json" `
  -d '{"intent": "What do you know about sales?"}'
```

### Explore APIs:
Open http://localhost:8000/docs

---

## 📋 First Time Setup (One-Time)

If this is your first time:

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Install dependencies
.venv\Scripts\pip install -r backend\requirements.txt

# 3. Copy .env
Copy-Item .env.example .env

# 4. Edit .env (add API keys)
notepad .env
```

Then run one of the start commands above!

---

## 🆘 Troubleshooting

### PowerShell won't run scripts?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port already in use?
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Or use different port
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

### Dependencies missing?
```powershell
.venv\Scripts\pip install -r backend\requirements.txt
```

---

## 📖 More Help

See these files:
- `START_HERE.md` - Complete copy-paste commands
- `QUICK_START.md` - 5-minute quick start
- `BOOT_README.md` - Boot system details
- `README_KERNELS.md` - Kernel documentation
- `SUBSYSTEM_CHECKLIST.md` - All subsystems
- `kubernetes/DEPLOY.md` - Kubernetes guide

---

## 🎉 That's It!

Pick a method, copy the command, and you're running! 🚀
