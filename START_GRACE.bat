@echo off
echo.
echo ================================================================================
echo    GRACE - Autonomous AI System with Always-On Learning
echo ================================================================================
echo.

REM Clean up any processes still using port 8000
echo [PRE-FLIGHT] Checking port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    echo [PRE-FLIGHT] Killing process on port 8000 (PID %%a)
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 1 /nobreak >nul
)

echo [PRE-FLIGHT] Port check complete
echo.
echo Starting Grace...
echo  - Backend + Frontend (Single server.py entry point)
echo  - Proactive Learning Agent (Auto-learning from internet every 60s)
echo  - Continuous Learning Loop (Learning from every action)
echo  - All systems governed by whitelist
echo.
echo Press Ctrl+C to stop Grace
echo ================================================================================
echo.

python server.py

pause
