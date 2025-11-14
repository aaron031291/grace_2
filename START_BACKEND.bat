@echo off
REM Start Grace Backend with All Systems

echo ================================================================================
echo GRACE BACKEND - STARTING
echo ================================================================================
echo.

cd backend

echo Starting Grace backend server...
echo Backend will run on: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.
echo Layer 1 (Unbreakable Core) will boot:
echo   - Message Bus
echo   - Immutable Log
echo   - Clarity Framework
echo   - Clarity Kernel
echo   - Verification Framework
echo   - Unified Logic
echo   - Self-Healing Kernel (REAL - executes playbooks)
echo   - Coding Agent Kernel (REAL - generates code)
echo   - Control Plane
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
