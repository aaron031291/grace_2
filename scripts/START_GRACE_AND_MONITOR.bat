@echo off
cls
echo.
echo ========================================
echo Starting Grace with Visual Monitoring
echo ========================================
echo.
echo This will:
echo   1. Start Grace backend
echo   2. Open visual ingestion log
echo   3. Start terminal monitoring
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting Grace backend...
start "Grace Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for Grace to start...
timeout /t 5 >nul

echo.
echo Opening visual ingestion log...
start logs\ingestion.html

echo.
echo Starting terminal monitor...
start "Ingestion Monitor" cmd /k "cd /d %~dp0 && watch_ingestion.bat"

echo.
echo ========================================
echo ✅ Grace is Running!
echo ========================================
echo.
echo Grace Backend:  http://localhost:8000
echo API Docs:       http://localhost:8000/docs
echo Visual Log:     logs\ingestion.html
echo.
echo To chat with Grace:
echo   grace_terminal.bat
echo.
echo To stop remote access:
echo   Press Ctrl+S in terminal
echo.
echo Press any key to close this window...
pause >nul
