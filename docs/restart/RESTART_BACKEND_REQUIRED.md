# Backend Restart Required

## Issue
The memory file API endpoints have been added to `backend/routes/memory_api.py` and registered in `backend/main.py`, but the server needs to be restarted for the changes to take effect.

## Current 404 Errors
- `GET /api/memory/tree` → 404
- `GET /api/memory/files` → 404  
- `GET /api/hunter/alerts` → 404

## What Changed
1. ✅ Added 6 new file system endpoints to `memory_api.py`:
   - `/api/memory/files` - List files
   - `/api/memory/file` - Read/save file
   - `/api/memory/folder` - Create folder
   - `/api/memory/status` - Get status

2. ✅ Registered `memory_api.router` in `backend/main.py` (line 561)

## How to Fix

### Restart the Backend Server

**Option 1: Using PowerShell script**
```powershell
.\GRACE.ps1
```

**Option 2: Manual restart**
```powershell
# Stop current server (Ctrl+C)
# Then restart:
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: Using batch file**
```bash
.\start_grace.bat
```

## Verification
After restart, test the endpoint:
```bash
curl http://localhost:8000/api/memory/status
```

You should see:
```json
{
  "component_id": "...",
  "status": "active",
  "root_path": "grace_training",
  "total_files": 0,
  "total_size_bytes": 0,
  "total_size_mb": 0.0
}
```

## Note on Hunter Alerts
The `/api/hunter/alerts` endpoint exists but may fail if:
- Database tables not created yet
- No security events in the database

This is normal on first run.
