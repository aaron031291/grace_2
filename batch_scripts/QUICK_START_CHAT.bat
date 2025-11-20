@echo off
echo ================================
echo GRACE CHAT QUICK START
echo ================================
echo.

REM Check if OpenAI API key is set
if not defined OPENAI_API_KEY (
    echo [ERROR] OPENAI_API_KEY not set!
    echo.
    echo Please set your OpenAI API key:
    echo   set OPENAI_API_KEY=sk-your-key-here
    echo.
    echo Or add it to .env file
    pause
    exit /b 1
)

echo [1/3] Starting backend...
start "Grace Backend" cmd /c "python server.py"
timeout /t 5 /nobreak >nul

echo [2/3] Starting frontend...
cd frontend
start "Grace Frontend" cmd /c "npm run dev"
cd ..
timeout /t 3 /nobreak >nul

echo [3/3] Opening chat...
start http://localhost:5173

echo.
echo ================================
echo GRACE CHAT READY!
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs:     http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop
echo.
pause
