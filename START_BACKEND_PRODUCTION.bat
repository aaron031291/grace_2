@echo off
echo Starting Grace Backend (Production)
echo.

cd /d "%~dp0"

echo [1/2] Checking Python environment...
python --version
if %errorlevel% neq 0 (
  echo [ERROR] Python not found
  exit /b 1
)

echo [2/2] Starting backend server on http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
