@echo off
echo ========================================
echo GRACE - Live Log Viewer
echo ========================================
echo.

cd /d C:\Users\aaron\grace_2

echo Checking for log files...
echo.

if exist backend_live.log (
    echo [LOG] backend_live.log:
    echo ----------------------------------------
    type backend_live.log
    echo.
    echo ----------------------------------------
)

if exist backend_run.log (
    echo.
    echo [LOG] backend_run.log:
    echo ----------------------------------------
    type backend_run.log
    echo.
    echo ----------------------------------------
)

if exist serve.log (
    echo.
    echo [LOG] serve.log:
    echo ----------------------------------------
    type serve.log
    echo.
    echo ----------------------------------------
)

if exist logs\backend.log (
    echo.
    echo [LOG] logs\backend.log (last 100 lines):
    echo ----------------------------------------
    powershell -Command "Get-Content logs\backend.log -Tail 100"
    echo.
    echo ----------------------------------------
)

echo.
echo ========================================
echo End of Logs
echo ========================================
pause
