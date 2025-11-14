@echo off
cls
echo ========================================
echo GRACE LAYER 1 - COMPLETE SYSTEM STARTUP
echo ========================================
echo.
echo Initializing all kernels with SDK...
echo Starting backend and frontend...
echo.

REM Kill any existing processes
echo [1/6] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment
echo [2/6] Activating Python environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Run: python -m venv .venv
    pause
    exit /b 1
)

REM Verify dependencies
echo [3/6] Checking dependencies...
python -c "import fastapi, sqlalchemy, openai" 2>nul
if errorlevel 1 (
    echo ⚠️ Installing missing dependencies...
    pip install -q -r backend\requirements.txt
)

REM Start backend with all kernels
echo [4/6] Starting backend with all 12 kernels...
start "GRACE Backend" cmd /k "cd backend && python -m uvicorn app_factory:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to initialize
echo [5/6] Waiting for backend to initialize (15s)...
timeout /t 15 >nul

REM Verify backend is running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '✅ Backend is running' -ForegroundColor Green } else { Write-Host '❌ Backend health check failed' -ForegroundColor Red } } catch { Write-Host '❌ Backend not responding' -ForegroundColor Red }"

REM Start frontend
echo [6/6] Starting frontend...
start "GRACE Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo ✅ GRACE LAYER 1 COMPLETE STARTUP
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo All 12 Kernels Active:
echo  1. Core Kernel         - System & user interaction
echo  2. Memory Kernel       - Fusion memory management
echo  3. Intelligence Kernel - ML/AI operations
echo  4. Code Kernel         - Code generation
echo  5. Self-Healing Kernel - Auto-repair
echo  6. Librarian Kernel    - Knowledge management
echo  7. Governance Kernel   - Policy & ethics
echo  8. Verification Kernel - Testing & validation
echo  9. Infrastructure      - System resources
echo 10. Federation Kernel   - Multi-agent coordination
echo 11. Clarity Kernel      - Observability
echo 12. Event Bus           - Real-time events
echo.
echo ========================================
echo Press any key to view live logs...
pause >nul

REM Show live log tailing
echo.
echo Starting log viewer (last 150 lines)...
timeout /t 2 >nul
python watch_grace_live.py --lines 150

REM Keep window open
pause
