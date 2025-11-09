@echo off
cls
echo.
echo ========================================
echo Starting Grace Backend
echo ========================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Grace with all systems...
echo.
echo Grace will start with:
echo   * Web Learning (83+ domains)
echo   * GitHub Mining
echo   * YouTube Learning
echo   * Reddit Learning (38+ subreddits)
echo   * API Discovery
echo   * Amp API (Last Resort + Verification)
echo   * Visual Ingestion Logs
echo   * ML/DL Reliability Learning
echo   * Complete Governance
echo.
echo Backend will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Grace stopped.
echo.
pause
