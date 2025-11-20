@echo off
echo.
echo ========================================
echo   Starting Frontend Only
echo ========================================
echo.

echo Stopping any running frontend servers...
taskkill /F /IM node.exe 2>nul >nul
timeout /t 1 /nobreak >nul

echo Clearing Vite cache...
if exist frontend\node_modules\.vite (
    rmdir /s /q frontend\node_modules\.vite
)

cd frontend

echo.
echo ========================================
echo   Frontend Dev Server
echo ========================================
echo.
echo Starting on: http://localhost:5173
echo Backend at:  http://localhost:8000
echo.
echo Make sure backend is running!
echo   Run: python server.py
echo.
echo Press Ctrl+C to stop
echo.

npm run dev
