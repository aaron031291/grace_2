@echo off
echo ========================================
echo Testing Grace CLI
echo ========================================
echo.

echo Checking Python packages...
python -c "import httpx" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] httpx not installed
    echo Installing CLI dependencies...
    pip install httpx rich prompt_toolkit
    echo.
)

echo Checking if backend is running...
python -c "import httpx; r=httpx.get('http://localhost:8000/health', timeout=2); print('[OK] Backend is running')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Backend not running!
    echo.
    echo Please start the backend first in another terminal:
    echo   cd ..
    echo   START_GRACE.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Running CLI Tests
echo ========================================
echo.

echo Test 1: Cognition Status (one-time)
echo --------------------------------------
python grace_unified.py cognition --backend http://localhost:8000
echo.
echo.

echo Test 2: Readiness Report
echo --------------------------------------
python grace_unified.py readiness --backend http://localhost:8000
echo.
echo.

echo Test 3: Core Heartbeat
echo --------------------------------------
python grace_unified.py core heartbeat
echo.
echo.

echo ========================================
echo CLI tests complete!
echo ========================================
echo.
pause
