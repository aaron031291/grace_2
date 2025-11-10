@echo off
echo.
echo ========================================
echo   GRACE - Autonomous AI System
echo ========================================
echo.
echo Starting Grace with full agentic capabilities...
echo.

REM Kill any existing processes
echo [1/5] Stopping existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Clear database locks
echo [2/5] Clearing database locks...
del /F /Q databases\*.db-wal 2>nul
del /F /Q databases\*.db-shm 2>nul

REM Start backend
echo [3/5] Starting Grace backend...
start "Grace Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo [4/5] Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start frontend
echo [5/5] Starting Grace UI...
start "Grace Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo   GRACE IS NOW RUNNING!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Docs:     http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo GPT Chat: http://localhost:5173 (login then click "GPT Chat")
echo.
echo Login: admin / admin123
echo.
echo Features:
echo   - Instant agentic error handling
echo   - Multi-agent parallel execution (6 shards)
echo   - Expert AI knowledge preloaded
echo   - 3-tier autonomy with governance
echo   - Modern GPT-style UI
echo   - Real-time activity monitoring
echo.
echo Press Ctrl+C in each window to stop Grace
echo.
pause
