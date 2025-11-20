@echo off
cls
echo.
echo ========================================
echo   RESTARTING GRACE - COMPLETE SYSTEM
echo ========================================
echo.

echo [1/3] Stopping all processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Grace*" 2>nul >nul
taskkill /F /IM node.exe 2>nul >nul
timeout /t 2 /nobreak >nul
echo Done!

echo.
echo [2/3] Clearing frontend cache...
cd frontend
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo Cache cleared!
)
cd ..

echo.
echo [3/3] Starting backend (frontend will auto-start)...
echo.
echo ========================================
echo   Services Starting
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Wait 10 seconds after backend starts,
echo then refresh browser with Ctrl+Shift+R
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python server.py
