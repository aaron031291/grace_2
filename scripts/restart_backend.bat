@echo off
echo Stopping backend server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Grace Backend*" 2>nul

echo Starting backend server...
cd backend
start "Grace Backend" cmd /k "..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Backend server restarting...
echo Check at: http://localhost:8000/health
echo API Docs: http://localhost:8000/docs
echo.
timeout /t 3 /nobreak >nul

echo Testing connection...
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/health | findstr "status" 

echo.
echo Backend ready!
