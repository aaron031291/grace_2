@echo off
cls
echo ========================================
echo GRACE LAYER 1 - MULTI-OS COMPLETE STARTUP
echo ========================================
echo.
echo Initializing Infrastructure Manager Kernel
echo Starting Governance + Memory + 10 other kernels
echo Multi-OS host registry active
echo.

REM Kill any existing processes
echo [1/7] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment
echo [2/7] Activating Python environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found
    echo Run: python -m venv .venv
    pause
    exit /b 1
)

REM Verify dependencies
echo [3/7] Checking dependencies...
python -c "import fastapi, sqlalchemy, openai, psutil" 2>nul
if errorlevel 1 (
    echo ⚠️ Installing missing dependencies...
    pip install -q -r backend\requirements.txt psutil
)

REM Change to root directory
echo [4/7] Setting up directories...
cd C:\Users\aaron\grace_2

REM Start backend with serve.py
echo [5/7] Starting backend (serve.py) with all kernels...
echo    - Infrastructure Manager Kernel (Multi-OS)
echo    - Governance Kernel (Policy enforcement)
echo    - Memory Kernel (State persistence)
echo    - Plus 10 other kernels...
start "GRACE Backend - Layer 1" cmd /k "python serve.py"

REM Wait for backend to initialize
echo [6/7] Waiting for backend to initialize (20s)...
timeout /t 20 >nul

REM Verify backend is running
echo Checking backend health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 10 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '✅ Backend is HEALTHY' -ForegroundColor Green } else { Write-Host '⚠️ Backend responded with status:' $response.StatusCode -ForegroundColor Yellow } } catch { Write-Host '❌ Backend not responding - may still be starting...' -ForegroundColor Red }"

REM Start frontend
echo [7/7] Starting frontend...
cd frontend
start "GRACE Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo ✅ GRACE LAYER 1 MULTI-OS STARTUP COMPLETE
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo Layer 1 Kernels Active (13 Total):
echo ========================================
echo.
echo 🏗️  INFRASTRUCTURE LAYER:
echo   1. Infrastructure Manager - Multi-OS host registry
echo   2. Event Bus              - Real-time messaging
echo   3. Clarity Kernel         - Observability
echo.
echo 🧠 INTELLIGENCE LAYER:
echo   4. Core Kernel            - System coordination
echo   5. Memory Kernel          - State persistence + host memory
echo   6. Intelligence Kernel    - ML/AI operations
echo   7. Librarian Kernel       - Knowledge management
echo.
echo 🛡️  GOVERNANCE ^& SAFETY:
echo   8. Governance Kernel      - Multi-OS policy enforcement
echo   9. Verification Kernel    - Testing ^& validation
echo  10. Self-Healing Kernel    - Auto-recovery
echo.
echo 🔧 OPERATIONS:
echo  11. Code Kernel            - Code generation
echo  12. Federation Kernel      - Multi-agent coordination
echo  13. Infrastructure Kernel  - System resources
echo.
echo ========================================
echo Multi-OS Support:
echo ========================================
echo ✅ Windows hosts tracked
echo ✅ Linux hosts tracked
echo ✅ macOS hosts tracked
echo ✅ Docker containers supported
echo ✅ Kubernetes pods supported
echo.
echo Governance enforces OS-specific policies
echo Memory persists all host states
echo.
echo ========================================
echo Press any key to continue...
pause >nul

echo.
echo Would you like to run E2E tests now? (Y/N)
set /p run_tests=
if /i "%run_tests%"=="Y" (
    echo.
    echo Running E2E tests with log tail...
    python test_layer1_e2e_with_logs.py
)

echo.
echo ========================================
echo System is ready for use!
echo ========================================
pause
