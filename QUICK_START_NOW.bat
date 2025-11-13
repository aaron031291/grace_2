@echo off
echo.
echo ========================================
echo  GRACE - Quick Start
echo ========================================
echo.

echo Stopping any running processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo.

echo Starting backend...
echo (This will open in a new window)
start "Grace Backend" cmd /k "cd /d c:\Users\aaron\grace_2 && python serve.py"

timeout /t 5 /nobreak >nul

echo.
echo Starting frontend...
echo (This will open in a new window)
start "Grace Frontend" cmd /k "cd /d c:\Users\aaron\grace_2\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo  System Starting...
echo ========================================
echo.
echo Backend will be ready in ~10 seconds
echo Frontend will be ready in ~15 seconds
echo.
echo Then open: http://localhost:5173
echo.
echo Look for:
echo   - Memory Studio tab
echo   - Click it -^> See "Organizer" and "Books" tabs
echo   - Bottom-right: Purple co-pilot button
echo.
pause
