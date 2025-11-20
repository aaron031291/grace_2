@echo off
REM Complete Grace Startup - Backend + Frontend

echo ================================================================================
echo GRACE COMPLETE SYSTEM - STARTUP
echo ================================================================================
echo.
echo Starting Grace with Layer 1 (Unbreakable Core) + Layer 2 (FastAPI)
echo.
echo This will:
echo   1. Boot Layer 1 (Message Bus, Kernels, Self-Healing, Coding Agent)
echo   2. Start FastAPI server (Layer 2)
echo   3. Start Frontend UI
echo.
echo ================================================================================
echo.

REM Start Backend (boots Layer 1 automatically)
echo [1/2] Starting Backend (Layer 1 + Layer 2)...
start "Grace Backend" cmd /k "cd /d %~dp0 && python serve.py"

echo.
echo Waiting for backend to boot...
timeout /t 12 /nobreak >nul

echo.
echo [2/2] Starting Frontend...
start "Grace Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ================================================================================
echo GRACE IS STARTING
echo ================================================================================
echo.
echo Backend (Layer 1 + 2):  http://localhost:8000
echo Frontend:              http://localhost:5173
echo Control Center:        http://localhost:5173/control  
echo Activity Monitor:      http://localhost:5173/activity
echo.
echo Layer 1 (Unbreakable Core):
echo   - Message Bus (kernel communication)
echo   - Self-Healing (4 playbooks - REAL)
echo   - Coding Agent (4 patterns - REAL)
echo   - Control Plane (16 kernels managed)
echo   - Clarity Kernel (component registry)
echo   - Unified Logic (governance)
echo.
echo Layer 2 (FastAPI):
echo   - API endpoints
echo   - WebSocket streams
echo   - User interface
echo.
echo Press Ctrl+C in backend window to stop Grace
echo.
echo ================================================================================
echo.

pause
