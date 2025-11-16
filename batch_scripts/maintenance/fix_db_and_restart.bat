@echo off
echo Fixing database locks and restarting Grace...

REM Kill any existing Grace processes
echo Killing existing processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Delete WAL files to reset locks
echo Clearing database locks...
del /F /Q databases\*.db-wal 2>nul
del /F /Q databases\*.db-shm 2>nul

REM Wait a moment
timeout /t 1 /nobreak >nul

REM Start backend
echo Starting Grace backend...
start "Grace Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo Grace is starting with database lock fixes applied!
echo Backend: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press any key to start frontend...
pause >nul

REM Start frontend
cd frontend
start "Grace Frontend" cmd /k "npm run dev"

echo.
echo Grace is now running!
echo Frontend: http://localhost:5173
echo.
