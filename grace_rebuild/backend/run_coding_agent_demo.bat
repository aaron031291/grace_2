@echo off
echo ================================
echo Grace AI Coding Agent - Demo
echo ================================
echo.

echo Step 1: Seeding Grace's Code Memory...
python seed_code_memory.py
if errorlevel 1 (
    echo Error: Failed to seed code memory
    pause
    exit /b 1
)

echo.
echo ================================
echo Step 2: Starting Grace Server...
echo ================================
echo.
echo Server will start at: http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Coding Agent Endpoints:
echo   - POST /api/code/parse
echo   - POST /api/code/understand
echo   - POST /api/code/suggest
echo   - POST /api/code/generate/function
echo   - POST /api/code/generate/class
echo   - POST /api/code/generate/tests
echo   - GET  /api/code/patterns
echo   - POST /api/code/task
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
