@echo off
echo Fixing Grace database...

REM Stop all Python processes
taskkill /F /IM python.exe 2>nul

REM Remove SQLite lock files
del databases\grace.db-shm 2>nul
del databases\grace.db-wal 2>nul

REM Fix immutable_log sequence conflicts
sqlite3 databases\grace.db "DELETE FROM immutable_log WHERE id IN (SELECT id FROM immutable_log GROUP BY sequence HAVING COUNT(*) > 1);"

echo Database fixed!
echo.
echo Starting backend...
start "Grace Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Waiting for startup...
timeout /t 30 /nobreak

echo.
echo Testing...
curl http://localhost:8000/health
