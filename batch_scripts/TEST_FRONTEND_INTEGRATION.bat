@echo off
echo ========================================
echo  Testing Frontend API Integration
echo ========================================
echo.

REM Check if backend is running
echo [1/5] Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo    FAILED - Backend not running on http://localhost:8000
    echo    Start with: python server.py
    exit /b 1
)
echo    OK - Backend is running

echo.
echo [2/5] Testing /api/chat endpoint...
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"hi\"}" ^
  -s -o chat_response.json
if %errorlevel% neq 0 (
    echo    FAILED - Could not reach /api/chat
    exit /b 1
)
echo    OK - Chat endpoint responding

echo.
echo [3/5] Checking OpenAI integration...
findstr /C:"reply" chat_response.json >nul 2>&1
if %errorlevel% neq 0 (
    echo    WARNING - Response may not include 'reply' field
    echo    Check if OPENAI_API_KEY is set in .env
) else (
    echo    OK - Response includes reply field
)

echo.
echo [4/5] Testing Remote Access endpoint...
curl -X POST http://localhost:8000/api/remote-cockpit/remote/start ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"test\", \"safety_mode\": \"supervised\"}" ^
  -s -o remote_response.json
if %errorlevel% neq 0 (
    echo    WARNING - Remote Access endpoint may not be available
) else (
    echo    OK - Remote Access endpoint responding
)

echo.
echo [5/5] Checking frontend build...
if not exist "frontend\dist" (
    echo    INFO - Frontend not built yet
    echo    Build with: cd frontend ^&^& npm run build
) else (
    echo    OK - Frontend build exists
)

echo.
echo ========================================
echo  Integration Test Summary
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173 (dev)
echo.
echo   Test chat response:
type chat_response.json
echo.
echo.
echo To start the full system:
echo   1. python server.py
echo   2. cd frontend ^&^& npm run dev
echo.
echo Then open: http://localhost:5173
echo.

REM Cleanup
del chat_response.json 2>nul
del remote_response.json 2>nul
