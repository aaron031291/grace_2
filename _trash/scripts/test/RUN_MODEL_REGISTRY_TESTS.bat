@echo off
REM Model Registry E2E Test Runner

echo ============================================================
echo MODEL REGISTRY E2E TEST SUITE
echo ============================================================
echo.

echo [1/2] Running Core Integration Tests...
echo ============================================================
python test_model_registry_e2e.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Core integration tests FAILED
    pause
    exit /b 1
)

echo.
echo.
echo [2/2] Running API Tests...
echo ============================================================
echo NOTE: Make sure the backend server is running!
echo       python serve.py
echo.
timeout /t 3

python test_model_registry_api_e2e.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ API tests FAILED
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ ALL TESTS PASSED!
echo ============================================================
pause
