@echo off
echo ================================================================================
echo GRACE COMPLETE END-TO-END TEST
echo ================================================================================
echo.
echo Starting comprehensive E2E test of all Grace components...
echo.

python test_grace_e2e_complete.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! All tests passed.
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo FAILED! Check logs for details.
    echo ================================================================================
)

pause
