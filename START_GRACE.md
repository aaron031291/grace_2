# Starting Grace - Quick Guide

## Option 1: Start Backend Only

Open PowerShell in `c:/Users/aaron/grace_2` and run:

```powershell
python backend/unified_grace_orchestrator.py --serve
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify it's running:**
```powershell
# In another PowerShell window
curl http://localhost:8000/
```

## Option 2: Start Both Backend + Frontend

**Terminal 1 - Backend:**
```powershell
cd c:/Users/aaron/grace_2
python backend/unified_grace_orchestrator.py --serve
```

**Terminal 2 - Frontend:**
```powershell
cd c:/Users/aaron/grace_2/frontend
npm install  # First time only
npm run dev
```

## Quick Test Backend

```powershell
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/status

# Clarity framework status
curl http://localhost:8000/api/clarity/status

# View components
curl http://localhost:8000/api/clarity/components

# View events
curl http://localhost:8000/api/clarity/events?limit=10
```

## Troubleshooting

### Port Already in Use
```powershell
# Find what's using port 8000
netstat -ano | findstr ":8000"

# Kill the process (replace PID with the actual number)
taskkill /PID <PID> /F
```

### Import Errors
```powershell
# Reinstall dependencies
pip install -r backend/requirements.txt
pip install psutil pyyaml pytest pytest-asyncio
```

### Check Logs
```powershell
# View latest logs
powershell -Command "Get-Content logs\orchestrator.log -Tail 50"
```

## Frontend Integration

Once backend is running on port 8000, the frontend can:

1. **Chat Interface** - `POST http://localhost:8000/api/chat`
2. **Clarity Status** - `GET http://localhost:8000/api/clarity/status`
3. **Component Manifest** - `GET http://localhost:8000/api/clarity/components`
4. **Event History** - `GET http://localhost:8000/api/clarity/events`
5. **Kernel Status** - `GET http://localhost:8000/api/kernels`

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Stop Grace

Press `Ctrl+C` in the terminal where it's running, or:

```powershell
python backend/unified_grace_orchestrator.py --stop
```
