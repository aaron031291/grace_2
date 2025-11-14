@echo off
cls
echo ========================================
echo GRACE LAYER 1 - E2E TEST WITH LOGS
echo ========================================
echo.
echo Running full system test...
echo Will display last 150 log lines
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run the test
python test_layer1_e2e_with_logs.py

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
pause
