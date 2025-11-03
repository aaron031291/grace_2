@echo off
echo ========================================
echo Testing Grace API Endpoints
echo ========================================
echo.

echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend not running!
    echo.
    echo Please start the backend first:
    echo   START_GRACE.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Backend is running
echo.

echo ========================================
echo Test 1: Health Check
echo ========================================
curl -X GET http://localhost:8000/health
echo.
echo.

echo ========================================
echo Test 2: Cognition Status
echo ========================================
curl -X GET http://localhost:8000/api/cognition/status
echo.
echo.

echo ========================================
echo Test 3: Cognition Readiness
echo ========================================
curl -X GET http://localhost:8000/api/cognition/readiness
echo.
echo.

echo ========================================
echo Test 4: Core Heartbeat
echo ========================================
curl -X GET http://localhost:8000/api/core/heartbeat
echo.
echo.

echo ========================================
echo Test 5: Core Governance
echo ========================================
curl -X GET http://localhost:8000/api/core/governance
echo.
echo.

echo ========================================
echo Test 6: Core Metrics
echo ========================================
curl -X GET http://localhost:8000/api/core/metrics
echo.
echo.

echo ========================================
echo All tests complete!
echo ========================================
echo.
echo Check the responses above for any errors
echo All endpoints should return JSON
echo.

pause
