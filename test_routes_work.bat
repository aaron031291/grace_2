@echo off
echo.
echo Testing if backend is running and routes are registered...
echo.

echo [1] Testing health endpoint...
curl -s http://localhost:8000/health
if errorlevel 1 (
    echo ERROR: Backend not running!
    echo Start with: python serve.py
    pause
    exit /b 1
)

echo.
echo [2] Testing books/stats endpoint...
curl -s http://localhost:8000/api/books/stats
echo.

echo.
echo [3] Testing librarian/file-operations endpoint...
curl -s http://localhost:8000/api/librarian/file-operations
echo.

echo.
echo [4] Testing librarian/organization-suggestions endpoint...
curl -s http://localhost:8000/api/librarian/organization-suggestions
echo.

echo.
echo ========================================
echo If you see JSON responses above: SUCCESS!
echo If you see 404 or "Not Found": Routes not registered yet
echo.
echo SOLUTION: Restart backend
echo   1. Press Ctrl+C in backend terminal
echo   2. Run: python serve.py
echo   3. Wait for "Application startup complete"
echo   4. Run this test again
echo ========================================
echo.
pause
