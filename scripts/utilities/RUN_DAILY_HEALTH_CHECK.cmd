@echo off
REM Daily Automated Health Check for TRUST Framework
REM Schedule this with Task Scheduler for daily monitoring

echo ============================================================
echo GRACE TRUST FRAMEWORK - DAILY HEALTH CHECK
echo ============================================================
echo.

python scripts/utilities/automated_health_check.py

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] All systems healthy
    echo.
) ELSE IF %ERRORLEVEL% EQU 2 (
    echo.
    echo [WARNING] Some issues detected - review report
    echo.
) ELSE (
    echo.
    echo [CRITICAL] Critical issues found - immediate attention required
    echo.
)

echo Report saved to: reports/trust_health_*.json
echo.

pause
