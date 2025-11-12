# Manual Start Instructions - FOLLOW THESE STEPS

## ✅ Step 1: Open PowerShell

1. Press `Win + X`
2. Click "Windows PowerShell" or "Terminal"
3. Navigate to grace folder:
   ```
   cd c:\Users\aaron\grace_2
   ```

## ✅ Step 2: Start Backend

Run this command:
```powershell
python backend\unified_grace_orchestrator.py --serve
```

## ✅ Step 3: Wait for Startup

You should see:
```
Starting Grace API server...
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ✅ Step 4: Test It Works

Open a NEW PowerShell window and run:
```powershell
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","timestamp":"...","platform":"Windows"}
```

## ✅ Step 5: Access API

Open your browser:
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
- **Status:** http://localhost:8000/api/status
- **Clarity:** http://localhost:8000/api/clarity/status

## Alternative: Use Batch File

Double-click `start_grace.bat` in the grace_2 folder.

## Troubleshooting

### "Port already in use"
```powershell
netstat -ano | findstr ":8000"
# Note the PID number, then:
taskkill /PID <NUMBER> /F
```

### "Module not found"
```powershell
pip install -r backend\requirements.txt
pip install psutil pyyaml pytest pytest-asyncio
```

### Check Logs
```powershell
type logs\orchestrator.log | more
```

## Stop Grace

In the PowerShell window where it's running, press `Ctrl+C`

---

**If you see "Uvicorn running on http://0.0.0.0:8000" - Grace is working! ✅**
