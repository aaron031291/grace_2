@echo off
echo ======================================
echo Starting Grace Backend and Frontend
echo ======================================
echo.

REM Start backend in new window
echo Starting backend server...
start "Grace Backend" cmd /k "cd backend && ..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend in new window  
echo Starting frontend dev server...
start "Grace Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================
echo Both servers started!
echo ======================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo ======================================
echo.
