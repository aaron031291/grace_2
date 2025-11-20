@echo off
cd frontend
echo Starting Vite dev server...
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend should be at: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.
start /B npm run dev
timeout /t 3 /nobreak >nul
start http://localhost:5173
