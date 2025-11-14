@echo off
echo.
echo ========================================
echo  Grace UI Status Check
echo ========================================
echo.

echo [1] Checking Backend (port 8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Backend is RUNNING
) else (
    echo ✗ Backend NOT running
    echo   Start: python serve.py
)

echo.
echo [2] Checking Frontend (port 5173)...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Frontend is RUNNING
) else (
    echo ✗ Frontend NOT running
    echo   Start: cd frontend ^&^& npm run dev
)

echo.
echo [3] Testing API endpoints...
curl -s http://localhost:8000/api/kernels >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Kernels API working
) else (
    echo ✗ Kernels API not responding
)

curl -s http://localhost:8000/api/books/stats >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Books API working
) else (
    echo ✗ Books API not responding
)

curl -s http://localhost:8000/api/self-healing/stats >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Self-Healing API working
) else (
    echo ✗ Self-Healing API not responding
)

echo.
echo [4] Available UIs:
echo.
echo   Main UI:       http://localhost:5173
echo   Dashboard:     file:///C:/Users/aaron/grace_2/grace_dashboard.html
echo   API Docs:      http://localhost:8000/docs
echo.
echo ========================================
echo  Summary
echo ========================================
echo.
echo Open grace_dashboard.html to see all features!
echo It works even if main UI has issues.
echo.
pause
