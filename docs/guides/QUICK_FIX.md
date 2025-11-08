# Database Lock Quick Fix

## Problem
SQLite database locked error during Grace startup due to concurrent writes from multiple systems.

## Solution Applied

### 1. Database Configuration Updates
- **Enabled WAL Mode**: Write-Ahead Logging for better concurrency
- **Increased Timeout**: 30 seconds for lock acquisition
- **Connection Pooling**: pool_size=10, max_overflow=20
- **Busy Timeout**: 30000ms at SQLite level

### 2. Retry Logic Enhanced
- Added retry on "database is locked" errors
- Increased backoff delay from 0.05s to 0.1s
- Better exception handling in immutable_log

## To Restart Grace

### Option 1: Use the Fix Script
```bash
fix_db_and_restart.bat
```

### Option 2: Manual Steps
1. Stop all Grace processes:
   ```bash
   # Kill python processes
   taskkill /F /IM python.exe
   ```

2. Clear lock files:
   ```bash
   del /F /Q databases\*.db-wal
   del /F /Q databases\*.db-shm
   ```

3. Start backend:
   ```bash
   .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. In another terminal, start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

## What Was Fixed

### `backend/base_models.py`
- Added connection args with timeout and check_same_thread=False
- Enabled connection pool with pre-ping

### `backend/main.py`
- Added SQLite PRAGMA commands for WAL mode
- Added busy_timeout pragma
- Applied same settings to metrics database

### `backend/immutable_log.py`
- Catches both IntegrityError and generic Exception for database locks
- Retries on "database is locked" errors
- Increased retry backoff

## Verify It Works

After restart, you should see:
```
✓ Database initialized (WAL mode enabled)
```

No more "database is locked" errors!

## Test the New GPT UI

1. Navigate to http://localhost:5173
2. Login (admin/admin123)
3. Click **⚡ GPT Chat**
4. Try slash commands by pressing `/`
5. Toggle sidebar and activity feed

## Files Modified
- `backend/base_models.py`
- `backend/main.py`
- `backend/immutable_log.py`
- `frontend/src/components/GraceGPT.tsx` (new)
- `frontend/src/components/GraceGPT.css` (new)
- `frontend/src/App.tsx`

## Next Time Grace Won't Start

Run:
```bash
del /F /Q databases\*.db-wal databases\*.db-shm
```

This clears stale lock files from improper shutdowns.
