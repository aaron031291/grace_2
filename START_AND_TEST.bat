@echo off
cls
echo ========================================
echo GRACE - START BACKEND AND RUN TESTS
echo ========================================
echo.

REM Change to project directory
cd /d C:\Users\aaron\grace_2

REM Kill any existing processes
echo [1/5] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment if exists
echo [2/5] Checking virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo    Virtual environment activated
) else (
    echo    No virtual environment found, using global Python
)

REM Start backend in background
echo [3/5] Starting backend (serve.py)...
start "GRACE Backend" /MIN cmd /k "python serve.py"

REM Wait for backend to initialize
echo [4/5] Waiting for backend to start (30 seconds)...
timeout /t 30 >nul

REM Check if backend is responding
echo [5/5] Checking backend health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ Backend is HEALTHY' -ForegroundColor Green } catch { Write-Host '❌ Backend not responding yet' -ForegroundColor Red; Write-Host 'You may need to wait a bit longer and run tests manually' -ForegroundColor Yellow }"

echo.
echo ========================================
echo Running E2E Tests with Log Tail (150 lines)
echo ========================================
echo.

REM Run tests
python test_multi_os_fabric_e2e.py

echo.
echo ========================================
echo Tests Complete
echo ========================================
echo.
echo To view backend logs, check: logs\backend.log
echo To stop backend: taskkill /F /IM python.exe
echo.
pause
