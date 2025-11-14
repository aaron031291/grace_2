@echo off
REM Start Grace Backend and Watch Activity in Real-Time

echo ================================================================================
echo GRACE - START AND WATCH
echo ================================================================================
echo.
echo This will:
echo 1. Start Grace backend server
echo 2. Open activity monitor to watch Grace work
echo.
echo ================================================================================
echo.

REM Start backend in new window
echo [1/2] Starting Grace backend server...
start "Grace Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [INFO] Backend starting... waiting 10 seconds for it to be ready
timeout /t 10 /nobreak >nul

echo.
echo [2/2] Starting activity monitor...
echo.

REM Start activity watcher
python watch_grace_live.py

echo.
echo ================================================================================
echo Grace stopped
echo ================================================================================
pause
