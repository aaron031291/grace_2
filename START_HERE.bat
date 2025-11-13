@echo off
REM Grace Complete Startup
REM Starts all Grace systems with proper initialization

echo ================================================================================
echo GRACE COMPLETE SYSTEM - STARTUP
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11+
    pause
    exit /b 1
)

echo [STEP 1] Initializing Grace systems...
python scripts/start_grace.py

if errorlevel 1 (
    echo.
    echo [ERROR] Grace initialization failed!
    echo Check logs for details
    pause
    exit /b 1
)

echo.
echo [STEP 2] Starting backend server...
echo.

cd backend
start "Grace Backend" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [INFO] Backend starting on http://localhost:8000
echo.

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

echo [STEP 3] Starting frontend...
echo.

cd ..\frontend
start "Grace Frontend" npm run dev

echo.
echo ================================================================================
echo GRACE IS STARTING!
echo ================================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Control:  http://localhost:5173/control
echo.
echo Press ESC in frontend for emergency stop
echo.
echo ================================================================================
echo.

pause
