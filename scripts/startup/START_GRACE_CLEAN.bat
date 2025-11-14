@echo off
echo.
echo ========================================
echo  Starting Grace - Clean Restart
echo ========================================
echo.

echo [1/3] Killing any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Checking port 8000 is free...
netstat -ano | findstr :8000 >nul
if %errorlevel%==0 (
    echo Port 8000 still in use, waiting...
    timeout /t 3 /nobreak >nul
)

echo [3/3] Starting Grace backend...
echo.
echo ========================================
echo  Backend Starting...
echo ========================================
echo.
echo Watch for these lines:
echo   - Stub routes registered (librarian + self-healing)
echo   - Test router registered
echo   - Application startup complete
echo.
echo Then open: http://localhost:5173
echo Memory Studio should have 9 tabs!
echo.

python serve.py
