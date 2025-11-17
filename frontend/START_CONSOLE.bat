@echo off
echo ========================================
echo   Grace Console - Starting Frontend
echo ========================================
echo.

cd /d "%~dp0"

echo Installing dependencies...
call npm install
echo.

echo Starting Vite development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
