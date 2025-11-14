@echo off
REM Quick Start - Everything Enabled

echo ================================================================================
echo GRACE QUICK START - ALL SYSTEMS ENABLED
echo ================================================================================
echo.

REM Set all features
set ENABLE_PC_ACCESS=true
set ENABLE_FIREFOX_ACCESS=true

echo Starting Grace with:
echo   - PC Access: ENABLED
echo   - Firefox Access: ENABLED
echo   - Activity Monitor: ENABLED
echo   - Autonomous Learning: ENABLED
echo.
echo ================================================================================
echo.

REM Start backend
echo Starting backend server...
start "Grace Backend" cmd /k "cd backend && set ENABLE_PC_ACCESS=true && set ENABLE_FIREFOX_ACCESS=true && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo.
echo Starting activity monitor...
echo.

REM Start watcher
python watch_grace_live.py

pause
