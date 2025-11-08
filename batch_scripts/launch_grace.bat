@echo off
REM Grace Complete Launcher - Starts all services

echo ========================================
echo   GRACE AI - Complete System Launcher
echo ========================================
echo.

REM Kill existing services
echo [1/4] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend
echo [2/4] Starting backend API...
start "Grace Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak >nul

REM Start frontend
echo [3/4] Starting frontend UI...
start "Grace Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 3 /nobreak >nul

REM Wait for services
echo [4/4] Waiting for services to start...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo   GRACE AI - System Ready!
echo ========================================
echo.
echo Frontend UI:  http://localhost:5173
echo Backend API:  http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo Services are running in separate windows.
echo Close those windows to stop Grace.
echo.
pause
