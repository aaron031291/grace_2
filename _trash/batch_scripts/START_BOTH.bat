@echo off
echo Starting Grace - Backend and Frontend
echo.

cd /d "%~dp0"

echo Starting Backend on port 8000...
start "Grace Backend" cmd /k "python scripts\runners\server.py"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend on port 5173...
start "Grace Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Both terminals will open in new windows.
echo Close those windows to stop the servers.
