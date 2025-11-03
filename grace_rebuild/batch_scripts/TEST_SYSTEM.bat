@echo off
echo ========================================
echo Grace System Test Suite
echo ========================================
echo.

echo Step 1: Checking Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.9+ or add to PATH
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo Step 2: Checking required packages...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] FastAPI not installed
    echo Installing backend dependencies...
    pip install -r requirements.txt
)
echo [OK] Backend packages ready
echo.

echo Step 3: Verifying backend code...
python -m py_compile backend\metrics_service.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax error in metrics_service.py
    pause
    exit /b 1
)

python -m py_compile backend\cognition_metrics.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax error in cognition_metrics.py
    pause
    exit /b 1
)

python -m py_compile backend\routers\cognition.py 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Syntax error in routers\cognition.py
    pause
    exit /b 1
)
echo [OK] Backend code syntax valid
echo.

echo Step 4: Testing imports...
python -c "from backend.metrics_service import get_metrics_collector; print('[OK] metrics_service imports')" 2>nul
python -c "from backend.cognition_metrics import get_metrics_engine; print('[OK] cognition_metrics imports')" 2>nul
echo.

echo Step 5: Starting backend server...
echo.
echo [INFO] Backend will start on http://localhost:8000
echo [INFO] Press Ctrl+C to stop
echo [INFO] Open http://localhost:8000/docs to see API
echo.
python -m uvicorn backend.main:app --reload

pause
