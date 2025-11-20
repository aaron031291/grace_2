@echo off
echo.
echo ================================================================================
echo                        GRACE - Complete System Startup
echo ================================================================================
echo.

REM Step 1: Clean up any existing processes
echo [STEP 1/5] Cleaning up old processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Grace*" 2>nul >nul
taskkill /F /IM node.exe 2>nul >nul
timeout /t 2 /nobreak >nul
echo    Done!
echo.

REM Step 2: Check prerequisites
echo [STEP 2/5] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo    Python: OK

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo    Node.js: OK

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: npm not found. Please install npm
    pause
    exit /b 1
)
echo    npm: OK
echo.

REM Step 3: Install/verify frontend dependencies
echo [STEP 3/5] Verifying frontend dependencies...
cd frontend
if not exist node_modules (
    echo    Installing dependencies... (this may take a minute)
    call npm install
) else (
    echo    Dependencies already installed
)
cd ..
echo.

REM Step 4: Clear caches
echo [STEP 4/5] Clearing caches for fresh start...
if exist frontend\node_modules\.vite (
    rmdir /s /q frontend\node_modules\.vite 2>nul
    echo    Vite cache cleared
) else (
    echo    No cache to clear
)
echo.

REM Step 5: Start services
echo [STEP 5/5] Starting Grace...
echo.
echo ================================================================================
echo   Backend:  Starting on port 8000
echo   Frontend: Starting on port 5173
echo ================================================================================
echo.
echo Starting backend (this will also launch frontend)...
echo.
echo Once started:
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop both services
echo.
echo ================================================================================
echo.

python server.py
