@echo off
cls
echo.
echo ====================================================================
echo GRACE - USAGE GUIDE
echo ====================================================================
echo.
echo Step 1: Check if Grace is running
echo ====================================================================
python check_server.py
echo.
echo.
echo ====================================================================
echo Step 2: Auto-configure clients (if server is running)
echo ====================================================================
python auto_configure.py
echo.
echo.
echo ====================================================================
echo Step 3: Choose what to do
echo ====================================================================
echo.
echo   A - Start Remote Access
echo   B - Start Autonomous Learning  
echo   C - Test Integration
echo   D - Exit
echo.
set /p choice="Enter choice (A/B/C/D): "
echo.

if /i "%choice%"=="A" (
    echo Starting Remote Access...
    echo.
    python remote_access_client.py setup
    python remote_access_client.py shell
)

if /i "%choice%"=="B" (
    echo Starting Autonomous Learning...
    echo.
    python start_grace_now.py
)

if /i "%choice%"=="C" (
    echo Testing Integration...
    echo.
    python test_remote_access_integration.py
)

if /i "%choice%"=="D" (
    echo Goodbye!
    exit /b 0
)

pause
