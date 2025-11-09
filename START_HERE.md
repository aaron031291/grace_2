# 🚀 START GRACE - COPY & PASTE COMMANDS

## ⚡ FASTEST WAY - Copy This:

### For PowerShell (Recommended):
```powershell
cd C:\Users\aaron\grace_2
.\RUN_GRACE.ps1
```

That's it! This will:
1. ✅ Test everything
2. ✅ Boot complete system
3. ✅ Run until Ctrl+C

---

## 🐳 DOCKER - Copy This:

### Option 1: Quick Docker Start
```powershell
cd C:\Users\aaron\grace_2
docker-compose -f docker-compose.complete.yml up
```

### Option 2: Build Then Start
```powershell
cd C:\Users\aaron\grace_2
docker-compose -f docker-compose.complete.yml build
docker-compose -f docker-compose.complete.yml up
```

### Stop Docker:
```powershell
docker-compose -f docker-compose.complete.yml down
```

---

## ☸️ KUBERNETES - Copy This:

### Deploy to Kubernetes:
```powershell
cd C:\Users\aaron\grace_2\kubernetes
kubectl apply -f grace-namespace.yaml
kubectl apply -f grace-configmap.yaml
kubectl apply -f grace-backend-deployment.yaml
kubectl apply -f grace-frontend-deployment.yaml
kubectl apply -f grace-services.yaml
```

### Check Status:
```powershell
kubectl get pods -n grace
kubectl get services -n grace
```

### View Logs:
```powershell
kubectl logs -n grace -l app=grace-backend --tail=100 -f
```

### Stop Kubernetes:
```powershell
kubectl delete namespace grace
```

---

## 🎯 What Happens After You Run It?

### Services Available:
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Test a Kernel:
```powershell
curl -X POST http://localhost:8000/kernel/memory `
  -H "Content-Type: application/json" `
  -d '{"intent": "What do you know about sales?"}'
```

---

## 🛑 Stop Grace

### PowerShell:
Press **Ctrl+C** in the terminal

### Docker:
```powershell
docker-compose -f docker-compose.complete.yml down
```

### Kubernetes:
```powershell
kubectl delete namespace grace
```

---

## ❓ Troubleshooting

### PowerShell Won't Run Scripts?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use?
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Or use different port
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

### Dependencies Missing?
```powershell
# Install Python dependencies
.venv\Scripts\pip install -r backend\requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 📋 First Time Setup (One-Time Only)

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Install backend dependencies
.venv\Scripts\pip install -r backend\requirements.txt

# 3. Install frontend dependencies (optional)
cd frontend
npm install
cd ..

# 4. Copy .env.example to .env
Copy-Item .env.example .env

# 5. Edit .env and add your API keys
notepad .env
```

Then run:
```powershell
.\RUN_GRACE.ps1
```

---

**That's all you need!** 🎉
