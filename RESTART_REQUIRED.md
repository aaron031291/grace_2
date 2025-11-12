# ⚠️ Restart Required

## New Endpoints Added

The following endpoints were just added but **require server restart**:

### Ingestion API
- `GET /api/ingestion/status`
- `GET /api/ingestion/tasks`
- `POST /api/ingestion/start`
- `POST /api/ingestion/stop/{task_id}`

### LLM API
- `GET /api/llm/status`

### Intelligence API
- `GET /api/intelligence/status`

### Learning API
- `GET /api/learning/status`

## How to Restart

### Option 1: Manual Restart
1. Go to the terminal running Grace backend
2. Press `Ctrl+C` to stop
3. Run: `python serve.py`

### Option 2: PowerShell Script
```powershell
.\restart_grace.ps1
```

### Option 3: Kill and Start
```powershell
# Find process
netstat -ano | findstr ":8000"

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F

# Start again
python serve.py
```

## Verify New Endpoints

After restart:
```bash
curl http://localhost:8000/api/ingestion/status
curl http://localhost:8000/api/llm/status
curl http://localhost:8000/api/intelligence/status
curl http://localhost:8000/api/learning/status
```

All should return JSON instead of 404.
