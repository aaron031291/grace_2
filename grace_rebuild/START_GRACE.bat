@echo off
echo ========================================
echo Starting Grace Platform
echo ========================================
echo.

echo Checking installation...
python VERIFY_INSTALLATION.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation verification failed
    echo Please fix the errors above before starting
    pause
    exit /b 1
)

echo.
echo ========================================
echo Grace Backend Starting...
echo ========================================
echo.
echo Backend will be available at:
echo   http://localhost:8000
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo.
echo Test endpoints:
echo   http://localhost:8000/api/cognition/status
echo   http://localhost:8000/api/core/heartbeat
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
