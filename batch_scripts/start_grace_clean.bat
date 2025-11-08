@echo off
echo.
echo ========================================
echo   Starting Grace AI System
echo ========================================
echo.

.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
