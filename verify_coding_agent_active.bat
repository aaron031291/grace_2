@echo off
echo ========================================
echo   Coding Agent Verification
echo ========================================
echo.

echo [1] Checking if Coding Agent API is registered...
curl -s http://localhost:8000/openapi.json | findstr "/api/coding" >nul && (
    echo   [OK] Coding Agent endpoints found in OpenAPI
) || (
    echo   [FAIL] Coding Agent endpoints NOT in OpenAPI
)

echo.
echo [2] Testing Coding Agent Parse endpoint...
curl -X POST http://localhost:8000/api/coding/parse ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"def hello(): return 'world'\",\"language\":\"python\"}"
echo.

echo.
echo [3] Testing Coding Agent Context endpoint...
curl -X POST http://localhost:8000/api/coding/context ^
  -H "Content-Type: application/json" ^
  -d "{\"file_path\":\"test.py\",\"code\":\"import os\",\"language\":\"python\"}"
echo.

echo.
echo [4] Listing all Coding Agent endpoints...
curl -s http://localhost:8000/openapi.json | findstr "/api/coding"
echo.

echo.
echo [5] Checking API docs for Coding Agent...
echo   Visit: http://localhost:8000/docs
echo   Search for: "Coding Agent"
echo.
pause
