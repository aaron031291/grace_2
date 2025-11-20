@echo off
echo.
echo ========================================
echo   Restarting Grace Frontend
echo ========================================
echo.

REM Kill any existing Vite processes
echo [STEP 1] Stopping any running frontend servers...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul
timeout /t 2 /nobreak >nul

REM Navigate to frontend
cd frontend

REM Check dependencies
echo [STEP 2] Checking dependencies...
if not exist node_modules (
    echo Installing dependencies...
    call npm install
) else (
    echo Dependencies OK
)
echo.

REM Clear Vite cache
echo [STEP 3] Clearing Vite cache...
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo Cache cleared
) else (
    echo No cache to clear
)
echo.

REM Start dev server
echo [STEP 4] Starting Vite dev server...
echo.
echo ========================================
echo   Frontend will start on port 5173
echo ========================================
echo.
echo Access at: http://localhost:5173
echo Press Ctrl+C to stop
echo.

call npm run dev

pause
