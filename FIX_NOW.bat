@echo off
cls
echo.
echo ========================================
echo   FIXING MODULE LOADING ERRORS
echo ========================================
echo.

echo [1/4] Stopping all Node processes...
taskkill /F /IM node.exe 2>nul >nul
timeout /t 2 /nobreak >nul
echo Done!

echo.
echo [2/4] Clearing Vite cache...
cd frontend
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo Cache cleared!
) else (
    echo No cache found
)

echo.
echo [3/4] Starting fresh Vite server...
echo.
start "Grace Frontend" cmd /c "npm run dev -- --force --host 127.0.0.1"

timeout /t 5 /nobreak >nul

echo.
echo [4/4] IMPORTANT - Do this in your browser:
echo.
echo ========================================
echo   1. Close ALL browser tabs for localhost:5173
echo   2. Wait 5 seconds
echo   3. Open NEW tab: http://localhost:5173
echo   4. Press: Ctrl + Shift + R (hard refresh)
echo ========================================
echo.
echo If still broken:
echo   - Open DevTools (F12)
echo   - Right-click refresh button
echo   - Click "Empty Cache and Hard Reload"
echo.

timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Frontend starting in separate window...
echo Check the "Grace Frontend" window for any errors
echo.
pause
